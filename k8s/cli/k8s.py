import argparse
import subprocess
import sys
import yaml
import os

# Get the current system username as pks_user
pks_user = os.getlogin()

# Function to get inventory file based on instance input
def get_inventory_file(instance):
    if instance == "ejen":
        return "path/to/ejen_inventory.yaml"
    elif instance == "gitact":
        return "path/to/gitact_inventory.yaml"
    else:
        print(f"Unknown instance: {instance}")
        sys.exit(1)

# Function to log into a cluster using PKS
def login_to_cluster(cluster, pks_api):
    print(f"Logging into cluster: {cluster} with API: {pks_api}")
    cmd = f"pks get-kubeconfig {cluster} -u {pks_user} -a {pks_api} -k"
    if subprocess.call(cmd, shell=True) != 0:
        print(f"Failed to log into cluster: {cluster}")
        sys.exit(1)

# Function to run any bash command in specific or all namespaces of a cluster
def run_bash_command(cluster, bash_command, target_namespace_aliases, inventory_file):
    pks_api = get_cluster_details(cluster, 'api', inventory_file)
    login_to_cluster(cluster, pks_api)

    namespaces = get_namespaces(cluster, target_namespace_aliases, inventory_file)

    for namespace in namespaces:
        print(f"Running bash command in namespace: {namespace} in cluster: {cluster}")
        full_command = f"kubectl -n {namespace} {bash_command}"
        subprocess.run(full_command, shell=True)
        print(f"Bash command executed successfully in namespace: {namespace} in cluster: {cluster}")

# Helper function to get cluster details from the inventory
def get_cluster_details(cluster, detail, inventory_file):
    with open(inventory_file, 'r') as f:
        inventory = yaml.safe_load(f)
    for item in inventory['clusters']:
        if item['name'] == cluster:
            return item.get(detail)
    return None

# Helper function to get namespaces from the inventory
def get_namespaces(cluster, target_namespace_aliases, inventory_file):
    with open(inventory_file, 'r') as f:
        inventory = yaml.safe_load(f)
    for item in inventory['clusters']:
        if item['name'] == cluster:
            if not target_namespace_aliases:
                return [ns['name'] for ns in item['namespaces']]
            else:
                return [ns['name'] for ns in item['namespaces'] if ns['alias'] in target_namespace_aliases]
    return []

# Main function to parse arguments and call the appropriate function
def main():
    parser = argparse.ArgumentParser(description='Utility script for managing clusters.')
    
    # Added flags for cluster alias, namespace alias, and the command to run
    parser.add_argument('-c', '--cluster', required=True, help='Cluster alias')
    parser.add_argument('-i', '--instance', choices=['ejen', 'gitact'], required=True, help='Instance name (ejen or gitact)')
    parser.add_argument('-n', '--namespace', nargs='+', help='Namespace alias (can specify multiple)')
    parser.add_argument('-m', '--command', required=True, help='Command to execute (e.g., "kubectl get pods")')

    args = parser.parse_args()

    # Get the correct inventory file based on the instance
    inventory_file = get_inventory_file(args.instance)

    # Get the actual cluster name based on the alias from the inventory
    cluster = get_cluster_details(args.cluster, 'name', inventory_file)
    if not cluster:
        print(f"Cluster alias {args.cluster} not found in inventory")
        sys.exit(1)

    # Command execution logic
    bash_command = args.command
    namespace_aliases = args.namespace if args.namespace else []
    run_bash_command(cluster, bash_command, namespace_aliases, inventory_file)

if __name__ == '__main__':
    main()