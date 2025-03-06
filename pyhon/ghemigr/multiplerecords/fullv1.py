import argparse
import os
import random
import string
import time
import subprocess
import requests
import logging
import csv
import json

# Configure logger to write to both a file and print in terminal
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('execution.log')
file_handler.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Argument parser setup
def parse_arguments():
    parser = argparse.ArgumentParser(description="GitHub Pull Request Automation Script")
    parser.add_argument('--api-url', required=True, help="Base URL for the API")
    parser.add_argument('--input-payload', required=True, help="Input payload for the API in JSON format")
    parser.add_argument('--json-output-file', required=True, help="Path to output JSON file")
    parser.add_argument('--report-file', required=True, help="Path to CSV report file")
    parser.add_argument('--api-token', required=True, help="GitHub API token for authentication")
    
    return parser.parse_args()

# Function to generate a random workspace name
def generate_random_workspace_name():
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    workspace_name = f"workspace-{random_string}"
    return workspace_name

# Function to clone a repository using subprocess
def clone_repository(repo_url, clone_path):
    try:
        if not os.path.exists(clone_path):
            logger.info(f"Cloning repository: {repo_url} to {clone_path}")
            subprocess.check_call(["git", "clone", repo_url, clone_path])
        else:
            logger.info(f"Repository already cloned at {clone_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error cloning repository {repo_url}: {e}")

# Function to create directories if not exist
def create_directories(path):
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info(f"Created directory: {path}")

# Function to copy multiple YAML files to the cloned repository
def copy_yaml_files_to_repo(clone_path, yaml_data):
    try:
        for yaml_type, yaml_list in yaml_data.items():
            for yaml_info in yaml_list:
                # Determine target directory for YAML files
                if yaml_type == 'workflowYaml':
                    target_dir = os.path.join(clone_path, '.github', 'workflows')
                else:
                    # For dbConfigYaml, use the provided folderName structure
                    target_dir = os.path.join(clone_path, yaml_info['folderName'])
                
                # Create target directory if it doesn't exist
                create_directories(target_dir)
                
                # Define the full file path
                file_path = os.path.join(target_dir, yaml_info['fileName'])
                
                # Write YAML content to the file
                with open(file_path, 'w') as yaml_file:
                    yaml_file.write(yaml_info['content'])
                
                logger.info(f"Copied {yaml_info['fileName']} to {target_dir}")
    except Exception as e:
        logger.error(f"Error copying YAML files to {clone_path}: {e}")

# Function to create GitHub team and add members
def create_github_team_and_add_members(org, github_team, api_key):
    try:
        url = f"https://api.github.com/orgs/{org}/teams"
        headers = {'Authorization': f'token {api_key}'}
        payload = {
            "name": github_team['teamName'],
            "description": f"Team {github_team['teamName']} created via API",
            "privacy": "closed"
        }
        
        # Create team
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        team_id = response.json()['id']
        logger.info(f"GitHub team {github_team['teamName']} created.")
        
        # Add members to team
        for member in github_team['members']:
            member_url = f"https://api.github.com/orgs/{org}/teams/{team_id}/memberships/{member}"
            response = requests.put(member_url, headers=headers)
            response.raise_for_status()
            logger.info(f"Added member {member} to team {github_team['teamName']}.")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating GitHub team or adding members: {e}")

# Function to create a pull request using GitHub REST API
def create_pull_request(repo, pr_title, pr_description, base_branch, head_branch, api_key):
    try:
        url = f"https://api.github.com/repos/{repo}/pulls"
        headers = {'Authorization': f'token {api_key}'}
        payload = {
            "title": pr_title,
            "body": pr_description,
            "head": head_branch,
            "base": base_branch
        }
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        pr_url = response.json()['_links']['html']['href']
        logger.info(f"Pull request created: {pr_url}")
        
        return pr_url
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating pull request for repo {repo}: {e}")
        return None

# Function to generate unique branch name
def generate_unique_branch_name(base_branch_name="main"):
    timestamp = int(time.time())
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    unique_branch_name = f"{base_branch_name}-pr-{timestamp}-{random_string}"
    return unique_branch_name

# Function to update CSV with pull request URL
def update_csv_report(csv_file, repo, branch, folder_name, pr_url):
    try:
        rows = []
        with open(csv_file, mode='r', newline='') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        updated = False
        for row in rows:
            if row[0] == repo and row[1] == branch and row[2] == folder_name:
                row.append(pr_url)
                updated = True
                break
        
        if not updated:
            rows.append([repo, branch, folder_name, '', '', pr_url])
        
        with open(csv_file, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        
        logger.info(f"CSV report updated with PR URL for {repo} and {branch}")
    
    except Exception as e:
        logger.error(f"Error updating CSV report: {e}")

# Function to process each record and create pull request
def process_record_and_create_pr(record, api_key, org, csv_file):
    try:
        workspace_name = generate_random_workspace_name()
        logger.info(f"Processing record for repo: {record['repository']}, branch: {record['branch']}, folder: {record.get('folderName', 'default')}")
        
        clone_path = os.path.join('/path/to/clone', workspace_name)
        clone_repository(record['repository'], clone_path)
        
        # Extract dbConfigYaml and workflowYaml and group them into lists
        yaml_data = {
            "dbConfigYaml": [value for key, value in record.items() if key.startswith("dbConfigYaml")],
            "workflowYaml": [value for key, value in record.items() if key.startswith("workflowYaml")]
        }
        
        copy_yaml_files_to_repo(clone_path, yaml_data)
        
        if 'githubTeam' in record:
            create_github_team_and_add_members(org, record['githubTeam'], api_key)
        
        unique_branch_name = generate_unique_branch_name(record.get('branch', 'main'))
        
        pr_url = create_pull_request(
            record['repository'], 
            record['prDetails']['title'], 
            record['prDetails']['description'],
            record['branch'], 
            unique_branch_name,
            api_key
        )
        
        if pr_url:
            update_csv_report(csv_file, record['repository'], record['branch'], record['folderName'], pr_url)
        
    except Exception as e:
        logger.error(f"Error processing record {record['repository']} with branch {record['branch']}: {e}")

# Main function to run the script
if __name__ == '__main__':
    args = parse_arguments()
    
    api_key = args.api_token  # API token
    org = 'your-org-name'  # GitHub organization
    csv_file = args.report_file  # Path to the CSV report file
    
    # Load the input payload (JSON) as a list of records
    try:
        input_payload = json.loads(args.input_payload)
        json_data = input_payload  # Assuming this is the format of input
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding input payload: {e}")
        exit(1)

    # Process each record
    for record in json_data:
        process_record_and_create_pr(record, api_key, org, csv_file)