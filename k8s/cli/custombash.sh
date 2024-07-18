#!/bin/bash

# Define the path to your inventory file and PKS user
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

# Function to add a new registry to an existing Docker JSON secret
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
    echo "Adding registry to secret in namespace: $namespace in cluster: $cluster"
    kubectl get secret "$secret_name" -n "$namespace" -o json | \
      jq --argjson new_registry "$new_registry" '.data[".dockerconfigjson"] | @base64d | fromjson | .auths |= . + $new_registry | @base64 | {"data":{".dockerconfigjson":.}}' | \
      kubectl apply -f - -n "$namespace"
    
    if [ $? -ne 0 ]; then
      echo "Failed to add registry to secret in namespace: $namespace in cluster: $cluster"
    fi
  done

  echo "Registry added to secret in specified namespaces in cluster: $cluster."
}

# Function to run a generic bash command in specific or all namespaces of a cluster
run_bash_command() {
  local cluster="$1"
  local bash_command="$2"
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
    echo "Running bash command in namespace: $namespace in cluster: $cluster"
    # Sourcing the path environment variable and running the command
    eval "source /etc/profile; $bash_command -n $namespace"
    
    if [ $? -ne 0 ]; then
      echo "Failed to run bash command in namespace: $namespace in cluster: $cluster"
    fi
  done

  echo "Bash command executed in specified namespaces in cluster: $cluster."
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
    add-registry)
      if [ "$#" -lt 2 ]; then
        echo "Usage: $0 add-registry <cluster-alias> <new-registry-json> <secret-name> [namespace-alias...]"
        exit 1
      fi
      local new_registry="$1"
     
    