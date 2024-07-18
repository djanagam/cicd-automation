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
      if [ "$#" -lt 2]; then
        echo "Usage: $0 add-registry <cluster-alias> <new-registry-json> <secret-name> [namespace-alias...]"
        exit 1
      fi
      local new_registry="$1"
      local secret_name="$2"
      shift 2
      add_registry_to_docker_secret "$cluster" "$new_registry" "$secret_name" "$@"
      ;;
    run-bash)
      if [ "$#" -lt 1 ]; then
        echo "Usage: $0 run-bash <cluster-alias> <bash-command> [namespace-alias...]"
        exit 1
      fi
      local bash_command="$1"
      shift
      run_bash_command "$cluster" "$bash_command" "$@"
      ;;
    *)
      echo "Unknown command: $command"
      echo "Available commands: apply-config, run-command, add-registry, run-bash"
      exit 1
      ;;
  esac
}

main "$@"