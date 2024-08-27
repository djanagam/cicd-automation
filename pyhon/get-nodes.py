import requests
from requests.auth import HTTPBasicAuth
import sys
import csv

# Base URL pattern for Jenkins instances
BASE_URL = 'https://jenkins-{}.company.net'

# Endpoint to get the list of nodes/agents
NODES_ENDPOINT_TEMPLATE = '{}/computer/api/json'

# List of patterns to filter node names
NODE_NAME_PATTERNS = ['cpvra', 'crvra', 'cuvra', 'ccvra']

def get_jenkins_nodes(instance_name, username, api_token):
    jenkins_url = BASE_URL.format(instance_name)
    nodes_endpoint = NODES_ENDPOINT_TEMPLATE.format(jenkins_url)
    
    try:
        # Make the API call, bypassing SSL verification
        response = requests.get(nodes_endpoint, auth=HTTPBasicAuth(username, api_token), verify=False)

        # Check if the request was successful
        if response.status_code == 200:
            nodes = response.json()['computer']
            print(f"List of Jenkins Nodes/Agents for {instance_name} with 'launchSupported': true and matching name patterns:")

            # Create a CSV file with the instance name in the filename
            csv_filename = f'jenkins_nodes_{instance_name}.csv'
            with open(csv_filename, mode='w', newline='') as file:
                writer = csv.writer(file)
                # Write the header
                writer.writerow(['Node Name', 'Number of Executors', 'Jenkins URL', 'FQDN', 'Executor SubDir'])

                for node in nodes:
                    node_name = node['displayName']
                    if node.get('launchSupported', False) and any(node_name.startswith(pattern) for pattern in NODE_NAME_PATTERNS):
                        # Construct the FQDN
                        fqdn = f"{node_name.split('-')[0]}.company.net"
                        
                        # Extract the executor sub-directory
                        executorsubDir = node_name.split('-')[1] if '-' in node_name else ''
                        
                        # Write the node details, FQDN, and executorsubDir to the CSV file
                        writer.writerow([node_name, node['numExecutors'], jenkins_url, fqdn, executorsubDir])
                        
                        # Print the node details to the console (optional)
                        print(f"Node Name: {node_name}")
                        print(f"Is Offline: {node['offline']}")
                        print(f"Number of Executors: {node['numExecutors']}")
                        print(f"FQDN: {fqdn}")
                        print(f"Executor SubDir: {executorsubDir}")
                        print('-' * 40)

            print(f"Node details have been written to '{csv_filename}'.")

        else:
            print(f"Failed to retrieve nodes. Status Code: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <instance_name> <username> <api_token>")
        sys.exit(1)
    
    instance_name = sys.argv[1]
    username = sys.argv[2]
    api_token = sys.argv[3]

    get_jenkins_nodes(instance_name, username, api_token)