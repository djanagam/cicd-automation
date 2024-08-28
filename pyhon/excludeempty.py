import requests
from requests.auth import HTTPBasicAuth
import sys
import csv
import os
import paramiko

# Base URL pattern for Jenkins instances
BASE_URL = 'https://jenkins-{}.company.net'

# Endpoint to get the list of nodes/agents
NODES_ENDPOINT_TEMPLATE = '{}/computer/api/json'

# List of patterns to filter node names
NODE_NAME_PATTERNS = ['cpvra', 'crvra', 'cuvra', 'ccvra']

def get_jenkins_nodes(instance_name, username, api_token, pod):
    jenkins_url = BASE_URL.format(instance_name)
    nodes_endpoint = NODES_ENDPOINT_TEMPLATE.format(jenkins_url)
    
    try:
        # Make the API call, bypassing SSL verification
        response = requests.get(nodes_endpoint, auth=HTTPBasicAuth(username, api_token), verify=False)

        if response.status_code == 200:
            nodes = response.json()['computer']

            # Create a CSV file with the instance name in the filename
            csv_filename = f'jenkins_nodes_{instance_name}.csv'
            with open(csv_filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Node Name', 'Number of Executors', 'URL String', 'FQDN', 'Executor SubDir'])

                for node in nodes:
                    node_name = node['displayName']
                    if node.get('launchSupported', False) and any(node_name.startswith(pattern) for pattern in NODE_NAME_PATTERNS):
                        fqdn = f"{node_name.split('-')[0]}.company.net"
                        executorsubDir = node_name.split('-')[1] if '-' in node_name else ''
                        
                        # Skip processing if executorsubDir is empty
                        if not executorsubDir:
                            continue
                        
                        url_string = f"Jenkins-{instance_name}"

                        writer.writerow([node_name, node['numExecutors'], url_string, fqdn, executorsubDir])

            return csv_filename
        else:
            print(f"Failed to retrieve nodes. Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def ssh_and_manage_directories(csv_filename, privkey_path, pod, action):
    try:
        with open(csv_filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                fqdn = row['FQDN']
                url_string = row['URL String']
                executorsubDir = row['Executor SubDir']
                
                # Skip processing if executorsubDir is empty
                if not executorsubDir:
                    print(f"Skipping node {row['Node Name']} as Executor SubDir is empty.")
                    continue
                
                remote_workspace = f"/workerfs{pod}/workspace/{url_string}"
                symlink_target = f"/apps/jenkins/pipeline-worker/executors/{executorsubDir}/workspace/{url_string}"

                # Establish SSH connection
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(fqdn, username='ejen', key_filename=privkey_path)

                # Validate or execute based on the action argument
                if action == 'validate':
                    stdin, stdout, stderr = ssh.exec_command(f'if [ -L {symlink_target} ]; then echo "OK - Link exists: {symlink_target}"; elif [ -d {symlink_target} ]; then echo "DIR - Directory exists: {symlink_target}"; else echo "MISSING"; fi')
                    result = stdout.read().decode().strip()
                    print(f"{fqdn}: {result}")
                elif action == 'execute':
                    ssh.exec_command(f'mkdir -p {remote_workspace}')
                    stdin, stdout, stderr = ssh.exec_command(f'if [ -L {symlink_target} ]; then echo "OK - Link exists: {symlink_target}"; elif [ -d {symlink_target} ]; then rm -rf {symlink_target}; ln -s {remote_workspace} {symlink_target}; echo "Created symlink: {symlink_target} -> {remote_workspace}"; elif [ ! -d {remote_workspace} ]; then ln -s {remote_workspace} {symlink_target}; echo "Created target and symlink: {symlink_target} -> {remote_workspace}"; else echo "MISSING"; fi')
                    result = stdout.read().decode().strip()
                    print(f"{fqdn}: {result}")

                ssh.close()
    except Exception as e:
        print(f"An error occurred during SSH operations: {e}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Manage Jenkins nodes and directories.")
    parser.add_argument('--instance', required=True, help="Jenkins instance name, e.g., build1")
    parser.add_argument('--user', required=True, help="Jenkins username")
    parser.add_argument('--token', required=True, help="Jenkins API token")
    parser.add_argument('--privkey', required=True, help="Path to the SSH private key")
    parser.add_argument('--pod', required=True, help="Pod name for workspace directory")
    parser.add_argument('--action', required=True, choices=['execute', 'validate'], help="Action to perform: execute or validate")

    args = parser.parse_args()

    csv_file = get_jenkins_nodes(args.instance, args.user, args.token, args.pod)
    if csv_file:
        ssh_and_manage_directories(csv_file, args.privkey, args.pod, args.action)