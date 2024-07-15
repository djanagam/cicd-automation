Let's ensure that the script properly handles all namespaces in a cluster when no specific namespace aliases are provided. To fix the issue of namespace values being read in one line, we'll use a `readarray` (or `mapfile`) command to read the namespace names into an array correctly.

Here's the updated script:

```bash
#!/bin/bash

# Define the path to your inventory file and YAML file
inventory_file="path/to/your/inventory.yaml"
pks_user="your_pks_username"

# Function to log into a cluster using PKS
login_to_cluster() {
  local cluster="$1"
  local pks_api="$2"
  
  echo "Logging into cluster: $cluster with API: $pks_api"
  pks get-kubeconfig "$cluster" -u "$pks_user" -a "$pks_api" -k
  
  if [ $? -ne 0 ]; then
    echo "Failed to log into cluster: $cluster"
    exit 1
  fi
}

# Function to apply a configuration file to specific or all namespaces in a cluster
apply_config() {
  local cluster="$1"
  local yaml_file="$2"
  shift 2
  local target_namespace_aliases=("$@")

  # Get the PKS API endpoint for the target cluster
  pks_api=$(yq e ".clusters[] | select(.name == \"$cluster\") | .api" "$inventory_file")

  login_to_cluster "$cluster" "$pks_api"

  if [ ${#target_namespace_aliases[@]} -eq 0 ]; then
    readarray -t namespaces < <(yq e ".clusters[] | select(.name == \"$cluster\") | .namespaces[].name" "$inventory_file")
  else
    namespaces=()
    for alias in "${target_namespace_aliases[@]}"; do
      namespace=$(yq e ".clusters[] | select(.name == \"$cluster\") | .namespaces[] | select(.alias == \"$alias\") | .name" "$inventory_file")
      namespaces+=("$namespace")
    done
  fi

  for namespace in "${namespaces[@]}"; do
    echo "Applying config to namespace: $namespace in cluster: $cluster"
    kubectl apply -f "$yaml_file" -n "$namespace"
    
    if [ $? -ne 0 ]; then
      echo "Failed to apply config in namespace: $namespace in cluster: $cluster"
    fi
  done

  echo "Config applied to specified namespaces in cluster: $cluster."
}

# Function to run a kubectl command in specific or all namespaces of a cluster
run_kubectl_command() {
  local cluster="$1"
  local kubectl_command="$2"
  shift 2
  local target_namespace_aliases=("$@")

  # Get the PKS API endpoint for the target cluster
  pks_api=$(yq e ".clusters[] | select(.name == \"$cluster\") | .api" "$inventory_file")

  login_to_cluster "$cluster" "$pks_api"

  if [ ${#target_namespace_aliases[@]} -eq 0 ]; then
    readarray -t namespaces < <(yq e ".clusters[] | select(.name == \"$cluster\") | .namespaces[].name" "$inventory_file")
  else
    namespaces=()
    for alias in "${target_namespace_aliases[@]}"; do
      namespace=$(yq e ".clusters[] | select(.name == \"$cluster\") | .namespaces[] | select(.alias == \"$alias\") | .name" "$inventory_file")
      namespaces+=("$namespace")
    done
  fi

  for namespace in "${namespaces[@]}"; do
    echo "Running kubectl command in namespace: $namespace in cluster: $cluster"
    kubectl $kubectl_command -n "$namespace"
    
    if [ $? -ne 0 ]; then
      echo "Failed to run kubectl command in namespace: $namespace in cluster: $cluster"
    fi
  done

  echo "Kubectl command executed in specified namespaces in cluster: $cluster."
}

# Function to get the cluster name by alias
get_cluster_name_by_alias() {
  local alias="$1"
  yq e ".clusters[] | select(.alias == \"$alias\") | .name" "$inventory_file"
}

# Main function to parse arguments and call the appropriate function
main() {
  if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <command> <cluster-alias> [additional-args] [namespace-alias...]"
    exit 1
  fi

  local command="$1"
  local cluster_alias="$2"
  shift 2

  local cluster=$(get_cluster_name_by_alias "$cluster_alias")
  if [ -z "$cluster" ]; then
    echo "Cluster alias $cluster_alias not found in inventory"
    exit 1
  fi

  case "$command" in
    apply-config)
      if [ "$#" -lt 1 ]; then
        echo "Usage: $0 apply-config <cluster-alias> <yaml-file> [namespace-alias...]"
        exit 1
      fi
      local yaml_file="$1"
      shift
      apply_config "$cluster" "$yaml_file" "$@"
      ;;
    run-command)
      if [ "$#" -lt 1 ]; then
        echo "Usage: $0 run-command <cluster-alias> <kubectl-command> [namespace-alias...]"
        exit 1
      fi
      local kubectl_command="$1"
      shift
      run_kubectl_command "$cluster" "$kubectl_command" "$@"
      ;;
    *)
      echo "Unknown command: $command"
      echo "Available commands: apply-config, run-command"
      exit 1
      ;;
  esac
}

main "$@"
```

### Key Changes
1. **Using `readarray` to Properly Parse Namespace Names**:
   - Use `readarray -t namespaces` to read the output of `yq` into an array properly, ensuring that each namespace is a separate element.

### Running the Script

#### Apply Configuration to Specific Namespaces Using Aliases
To apply a configuration file to specific namespaces in a cluster using namespace aliases:
```sh
./k8s_utility.sh apply-config alias1 path/to/your/secret.yaml ns1 ns2
```

To apply a configuration file to all namespaces in a cluster using the cluster alias:
```sh
./k8s_utility.sh apply-config alias1 path/to/your/secret.yaml
```

#### Run Kubectl Command in Specific Namespaces Using Aliases
To run a kubectl command in specific namespaces in a cluster using namespace aliases:
```sh
./k8s_utility.sh run-command alias1 get pods ns1 ns2
```

To run a kubectl command in all namespaces in a cluster using the cluster alias:
```sh
./k8s_utility.sh run-command alias1 get pods
```