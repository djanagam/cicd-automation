import argparse
import subprocess
import os
import tempfile
from kubernetes import client, config
import yaml

# Global variable to hold inventory file path and pks_user
inventory_file = None
pks_user = os.getlogin()

# Load the inventory file (YAML) based on instance
def load_inventory(instance):
    global inventory_file
    if instance == 'ejen':
        inventory_file = 'path/to/ejen_inventory.yaml'
    elif instance == 'gitact':
        inventory_file = 'path/to/gitact_inventory.yaml'
    else:
        raise ValueError(f"Unknown instance: {instance}")
    with open(inventory_file, 'r') as file:
        return yaml.safe_load(file)

# Function to login to PKS cluster
def login_to_pks(cluster_name, api_url):
    cmd = f"pks get-kubeconfig {cluster_name} -u {pks_user} -a {api_url} -k"
    result = subprocess.run(cmd, shell=True, check=True)
    if result.returncode == 0:
        print(f"Successfully logged into PKS cluster: {cluster_name}")
    else:
        print(f"Failed to login to PKS cluster: {cluster_name}")
        raise Exception("PKS login failed")

# Function to authenticate to a Kubernetes cluster using the Kubernetes Python client
def authenticate_to_cluster():
    try:
        config.load_kube_config()  # Load kubeconfig from default location
        print("Authenticated to Kubernetes cluster.")
    except Exception as e:
        print(f"Failed to authenticate to Kubernetes: {e}")
        raise

# Function to get cluster name from alias in inventory
def get_cluster_name_by_alias(cluster_alias, inventory):
    for cluster in inventory['clusters']:
        if cluster['alias'] == cluster_alias:
            return cluster['name']
    raise ValueError(f"Cluster alias {cluster_alias} not found in inventory")

# Function to get namespaces from inventory by cluster name
def get_namespaces_for_cluster(cluster_name, namespace_aliases, inventory):
    namespaces = []
    for cluster in inventory['clusters']:
        if cluster['name'] == cluster_name:
            if namespace_aliases:
                for alias in namespace_aliases:
                    for namespace in cluster['namespaces']:
                        if namespace['alias'] == alias:
                            namespaces.append(namespace['name'])
            else:
                namespaces = [ns['name'] for ns in cluster['namespaces']]
    if not namespaces:
        raise ValueError(f"No namespaces found for cluster: {cluster_name}")
    return namespaces

# Function to apply a configuration to specific or all namespaces
def apply_config_to_namespaces(cluster_name, yaml_file, namespaces):
    v1 = client.CoreV1Api()
    for namespace in namespaces:
        print(f"Applying config to namespace: {namespace} in cluster: {cluster_name}")
        with open(yaml_file, 'r') as stream:
            yaml_content = yaml.safe_load(stream)
            yaml_content['metadata']['namespace'] = namespace  # Set the namespace in YAML
            # Write to a temporary file
            with tempfile.NamedTemporaryFile('w', delete=False) as tmp_yaml:
                yaml.dump(yaml_content, tmp_yaml)
                tmp_yaml_path = tmp_yaml.name
        # Apply the config using Kubernetes API (replace with your logic)
        with open(tmp_yaml_path, 'r') as f:
            print(f"Applied config: {f.read()}")  # Placeholder for actual apply logic
        os.remove(tmp_yaml_path)

# Function to run a command in all namespaces of a cluster
def run_command_in_namespaces(cluster_name, command, namespaces):
    v1 = client.CoreV1Api()
    for namespace in namespaces:
        print(f"Running command in namespace: {namespace}")
        # Here you can execute kubectl command logic programmatically
        # or define other logic using Kubernetes API
        print(f"Command output: Placeholder for {command} in {namespace}")

# Main function to parse arguments and execute commands
def main():
    parser = argparse.ArgumentParser(description="Kubernetes Cluster Utility")
    parser.add_argument("-i", "--instance", required=True, help="Select the app instance: ejen or gitact")
    parser.add_argument("-c", "--cluster", required=True, help="Cluster alias to operate on")
    parser.add_argument("-n", "--namespace", nargs='*', help="Namespace alias(es) to operate on")
    parser.add_argument("-m", "--command", required=True, help="Command to run: apply-config or run-command")
    parser.add_argument("-f", "--file", help="YAML file to apply (required for apply-config)")
    args = parser.parse_args()

    # Load the correct inventory based on instance
    inventory = load_inventory(args.instance)

    # Get the cluster name based on the provided alias
    cluster_name = get_cluster_name_by_alias(args.cluster, inventory)

    # Get namespaces to target based on the provided aliases (or all namespaces if none specified)
    namespaces = get_namespaces_for_cluster(cluster_name, args.namespace, inventory)

    # Authenticate to the cluster (Kubernetes API)
    authenticate_to_cluster()

    # Execute the selected command
    if args.command == 'apply-config':
        if not args.file:
            raise ValueError("YAML file required for apply-config command")
        apply_config_to_namespaces(cluster_name, args.file, namespaces)
    elif args.command == 'run-command':
        run_command_in_namespaces(cluster_name, args.command, namespaces)
    else:
        raise ValueError(f"Unknown command: {args.command}")

if __name__ == "__main__":
    main()