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