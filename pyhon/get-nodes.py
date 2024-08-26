import requests
from requests.auth import HTTPBasicAuth
import sys

# Base URL pattern for Jenkins instances
BASE_URL = 'https://jenkins-{}.company.net'

# Endpoint to get the list of nodes/agents
NODES_ENDPOINT_TEMPLATE = '{}/computer/api/json'

def get_jenkins_nodes(instance_name, username, api_token):
    jenkins_url = BASE_URL.format(instance_name)
    nodes_endpoint = NODES_ENDPOINT_TEMPLATE.format(jenkins_url)
    
    try:
        # Make the API call
        response = requests.get(nodes_endpoint, auth=HTTPBasicAuth(username, api_token))

        # Check if the request was successful
        if response.status_code == 200:
            nodes = response.json()['computer']
            print(f"List of Jenkins Nodes/Agents for {instance_name}:")
            for node in nodes:
                print(f"Node Name: {node['displayName']}")
                print(f"Is Offline: {node['offline']}")
                print(f"Number of Executors: {node['numExecutors']}")
                print('-' * 40)
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