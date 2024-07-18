Certainly! Here are the usage steps for the updated script:

### Usage Examples

#### Apply Configuration to Specific Namespaces Using Aliases
```sh
./k8s_utility.sh apply-config <cluster-alias> <yaml-file> [namespace-alias...]
```
**Example:**
```sh
./k8s_utility.sh apply-config alias1 path/to/your/secret.yaml ns1 ns2
```

#### Apply Configuration to All Namespaces in a Cluster
```sh
./k8s_utility.sh apply-config <cluster-alias> <yaml-file>
```
**Example:**
```sh
./k8s_utility.sh apply-config alias1 path/to/your/secret.yaml
```

#### Run Kubectl Command in Specific Namespaces Using Aliases
```sh
./k8s_utility.sh run-command <cluster-alias> <kubectl-command> [namespace-alias...]
```
**Example:**
```sh
./k8s_utility.sh run-command alias1 get pods ns1 ns2
```

#### Run Kubectl Command in All Namespaces in a Cluster
```sh
./k8s_utility.sh run-command <cluster-alias> <kubectl-command>
```
**Example:**
```sh
./k8s_utility.sh run-command alias1 get pods
```

#### Add a New Registry to Docker JSON Secret
```sh
./k8s_utility.sh add-registry <cluster-alias> <new-registry-json> <secret-name> [namespace-alias...]
```
**Example:**
```sh
./k8s_utility.sh add-registry alias1 '{"new-registry.com": {"auth": "new-auth-token"}}' my-docker-secret ns1 ns2
```

#### Run Any Bash Command in Cluster Context and Process the Output
```sh
./k8s_utility.sh run-bash-command <cluster-alias> <bash-command>
```
**Example:**
```sh
./k8s_utility.sh run-bash-command alias1 "kubectl get secret my-secret -o json | jq .data | base64 --decode"
```

### Full Script

Here’s the full script with the added functionality for running any bash command and processing the output:

```bash
#!/bin/bash

# Define the path to your inventory file and PKS username
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
    
    # Create a temporary YAML file with the correct namespace
    tmp_yaml=$(mktemp)
    yq e ".metadata.namespace = \"$namespace\"" "$yaml_file" > "$tmp_yaml"
    
    kubectl apply -f "$tmp_yaml" -n "$namespace"
    
    if [ $? -ne 0 ]; then
      echo "Failed to apply config in namespace: $namespace in cluster: $cluster"
    fi

    # Remove the temporary file
    rm -f "$tmp_yaml"
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

# Function to add a new registry to an existing Docker JSON secret in specific or all namespaces of a cluster
add_registry_to_docker_secret() {
  local cluster="$1"
  local new_registry="$2"
  local secret_name="$3"
  shift 3
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

# Function to run a generic bash command in a cluster's context
run_bash_command() {
  local cluster="$1"
  shift 1
  local bash_command=("$@")

  # Get the PKS API endpoint for the target cluster
  pks_api=$(yq e ".clusters[] | select(.name == \"$cluster\") | .api" "$inventory_file")

  login_to_cluster "$cluster" "$pks_api"

  echo "Running bash command in cluster: $cluster"
  eval "${bash_command[@]}"

  if [ $? -ne 0 ]; then
    echo "Failed to run bash command in cluster: $cluster"
  else
    echo "Bash command executed successfully in cluster: $cluster"
  fi
}

# Function to get the cluster name by alias
get_cluster_name_by_alias() {
  local alias="$1"
  yq e ".clusters[] | select(.alias == \"$alias\") | .name" "$inventory_file"
}

# Main function to parse arguments and call the appropriate function
main() {
  if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <