You can extend the existing script to handle the addition of a new registry to an existing Docker JSON secret. This requires reading the current secret, merging the new registry information, and then updating the secret in the cluster. Here's how you can achieve that:

### Extend the Script

1. **Function to Add a New Registry to Docker JSON Secret**

```bash
# Function to add a new registry to an existing Docker JSON secret in specific or all namespaces of a cluster
add_registry_to_docker_secret() {
  local cluster="$1"
  local new_registry="$2"
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
    echo "Adding new registry to Docker JSON secret in namespace: $namespace in cluster: $cluster"
    
    # Get the existing Docker JSON secret
    secret_name=$(kubectl get secrets -n "$namespace" | grep 'docker-registry' | awk '{print $1}')
    if [ -z "$secret_name" ]; then
      echo "No existing Docker registry secret found in namespace: $namespace"
      continue
    fi

    existing_secret=$(kubectl get secret "$secret_name" -n "$namespace" -o json | jq -r '.data[".dockerconfigjson"]' | base64 -d)
    
    # Merge the new registry information
    updated_secret=$(echo "$existing_secret" | jq --argjson new_registry "$new_registry" '.auths |= . + $new_registry')

    # Update the secret in the cluster
    kubectl patch secret "$secret_name" -n "$namespace" --type='json' -p="[{'op': 'replace', 'path': '/data/.dockerconfigjson', 'value':\"$(echo $updated_secret | base64 -w 0)\"}]"
    
    if [ $? -ne 0 ]; then
      echo "Failed to add new registry to Docker JSON secret in namespace: $namespace in cluster: $cluster"
    fi
  done

  echo "New registry added to Docker JSON secret in specified namespaces in cluster: $cluster."
}
```

2. **Add the New Command to the Main Function**

```bash
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
    add-registry)
      if [ "$#" -lt 1 ]; then
        echo "Usage: $0 add-registry <cluster-alias> <new-registry-json> [namespace-alias...]"
        exit 1
      fi
      local new_registry="$1"
      shift
      add_registry_to_docker_secret "$cluster" "$new_registry" "$@"
      ;;
    *)
      echo "Unknown command: $command"
      echo "Available commands: apply-config, run-command, add-registry"
      exit 1
      ;;
  esac
}

main "$@"
```

### Usage Examples

#### Apply Configuration to Specific Namespaces Using Aliases

```sh
./k8s_utility.sh apply-config alias1 path/to/your/secret.yaml ns1 ns2
```

#### Apply Configuration to All Namespaces in a Cluster

```sh
./k8s_utility.sh apply-config alias1 path/to/your/secret.yaml
```

#### Run Kubectl Command in Specific Namespaces Using Aliases

```sh
./k8s_utility.sh run-command alias1 get pods ns1 ns2
```

#### Run Kubectl Command in All Namespaces in a Cluster

```sh
./k8s_utility.sh run-command alias1 get pods
```

#### Add a New Registry to Docker JSON Secret

```sh
./k8s_utility.sh add-registry alias1 '{"new-registry.com": {"auth": "new-auth-token"}}' ns1 ns2
```

#### Add a New Registry to Docker JSON Secret in All Namespaces

```sh
./k8s_utility.sh add-registry alias1 '{"new-registry.com": {"auth": "new-auth-token"}}'
```

This should enable you to add new registry information to existing Docker JSON secrets across specific or all namespaces within a cluster using the provided script.