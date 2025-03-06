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

# ----------------- Logger Setup ----------------- #
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

# ----------------- Argument Parsing ----------------- #
def parse_arguments():
    parser = argparse.ArgumentParser(description="GitHub Pull Request Automation Script")
    parser.add_argument('--api-url', required=True, help="API URL to fetch JSON data")
    parser.add_argument('--input-payload', required=True, help="Input payload (JSON string) to send to the API, e.g. '{\"Template\": \"skinneddrjfj\"}'")
    parser.add_argument('--json-output-file', required=True, help="Path to write the returned JSON data")
    parser.add_argument('--report-file', required=True, help="Path to CSV report file")
    parser.add_argument('--api-token', required=True, help="GitHub API token for authentication")
    return parser.parse_args()

# ----------------- API Call Function ----------------- #
def fetch_json_data(api_url, input_payload):
    try:
        headers = {'Content-Type': 'application/json'}
        logger.info(f"Calling API: {api_url} with payload: {input_payload}")
        response = requests.post(api_url, json=input_payload, headers=headers)
        response.raise_for_status()
        json_data = response.json()
        logger.info("API call successful.")
        return json_data
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching JSON data: {e}")
        return None

# ----------------- Utility Functions ----------------- #
def generate_random_workspace_name():
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return f"workspace-{random_string}"

def generate_unique_branch_name(base_branch_name="main"):
    timestamp = int(time.time())
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    return f"{base_branch_name}-pr-{timestamp}-{random_string}"

def create_directories(path):
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info(f"Created directory: {path}")

# ----------------- Git Operations ----------------- #
def clone_repository(repo, clone_path):
    repo_url = f"git@github.com:{repo}.git"
    try:
        if not os.path.exists(clone_path):
            logger.info(f"Cloning repository: {repo_url} to {clone_path}")
            subprocess.check_call(["git", "clone", repo_url, clone_path])
        else:
            logger.info(f"Repository already cloned at {clone_path}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error cloning repository {repo_url}: {e}")

# ----------------- YAML File Handling ----------------- #
def copy_yaml_files_to_repo(clone_path, yaml_data):
    """
    For each YAML entry, create the target directory (if needed) and create a file
    with the given fileName, writing the provided content.
    For workflow YAML files, the target directory is fixed to .github/workflows.
    For others (e.g. dbConfigYaml), we use the folderName provided in the record.
    """
    try:
        for yaml_type, yaml_list in yaml_data.items():
            for yaml_info in yaml_list:
                if yaml_type.startswith("workflowYaml"):
                    # Always use .github/workflows for workflow YAMLs.
                    target_dir = os.path.join(clone_path, ".github", "workflows")
                else:
                    # For other YAML files, use the folderName specified in the YAML info.
                    # The record should supply this via the folderName field.
                    target_dir = os.path.join(clone_path, yaml_info.get("folderName", "default"))
                create_directories(target_dir)
                file_path = os.path.join(target_dir, yaml_info["fileName"])
                with open(file_path, 'w') as f:
                    f.write(yaml_info["content"])
                logger.info(f"Created file {file_path} with provided content.")
    except Exception as e:
        logger.error(f"Error copying YAML files to {clone_path}: {e}")

# ----------------- GitHub API Functions ----------------- #
def create_github_team_and_add_members(org, github_team, api_key):
    try:
        url = f"https://api.github.com/orgs/{org}/teams"
        headers = {'Authorization': f'token {api_key}'}
        payload = {
            "name": github_team["teamName"],
            "description": f"Team {github_team['teamName']} created via API",
            "privacy": "closed"
        }
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        team_slug = response.json()["slug"]
        logger.info(f"GitHub team {github_team['teamName']} created with slug {team_slug}.")
        for member in github_team["members"]:
            member_url = f"https://api.github.com/orgs/{org}/teams/{team_slug}/memberships/{member}"
            response = requests.put(member_url, headers=headers)
            response.raise_for_status()
            logger.info(f"Added member {member} to team {github_team['teamName']}.")
        return team_slug
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating GitHub team or adding members: {e}")
        return None

def ensure_environments(repo, org, team_slug, api_key):
    headers = {'Authorization': f'token {api_key}', 'Accept': 'application/vnd.github.v3+json'}
    for env in ["e2", "e3"]:
        url = f"https://api.github.com/repos/{org}/{repo}/environments/{env}"
        payload = {"reviewers": [team_slug]}
        try:
            response = requests.put(url, json=payload, headers=headers)
            if response.status_code in [200, 201]:
                logger.info(f"Environment '{env}' ensured for repo {repo} with reviewer {team_slug}.")
            else:
                logger.error(f"Failed to ensure environment '{env}' for repo {repo}: {response.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error ensuring environment '{env}' for repo {repo}: {e}")

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
        pr_url = response.json()["_links"]["html"]["href"]
        logger.info(f"Pull request created: {pr_url}")
        return pr_url
    except requests.exceptions.RequestException as e:
        logger.error(f"Error creating pull request for repo {repo}: {e}")
        return None

# ----------------- CSV Report Handling ----------------- #
def update_csv_report(csv_file, repo, branch, folder_name, team_name, members, pr_url):
    try:
        rows = []
        if os.path.exists(csv_file):
            with open(csv_file, mode="r", newline="") as f:
                reader = csv.reader(f)
                rows = list(reader)
        else:
            rows.append(["repository", "branch", "folderName", "teamName", "members", "prUrl"])
        updated = False
        for row in rows:
            if row[0] == repo and row[1] == branch and row[2] == folder_name:
                row[3] = team_name
                row[4] = members
                row[5] = pr_url
                updated = True
                break
        if not updated:
            rows.append([repo, branch, folder_name, team_name, members, pr_url])
        with open(csv_file, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        logger.info(f"CSV report updated with PR URL for {repo} and {branch}")
    except Exception as e:
        logger.error(f"Error updating CSV report: {e}")

# ----------------- Main Processing Function ----------------- #
def process_record_and_create_pr(record, api_key, org, csv_file):
    try:
        workspace_name = generate_random_workspace_name()
        logger.info(f"Processing record for repo: {record['repository']}, branch: {record['branch']}, folder: {record.get('folderName', 'default')}")
        
        clone_path = os.path.join("/path/to/clone", workspace_name)
        clone_repository(record["repository"], clone_path)
        
        # Prepare YAML data.
        # We assume keys starting with "dbConfigYaml" and "workflowYaml".
        # For each dbConfigYaml, we inject folderName from the record.
        yaml_data = {"dbConfigYaml": [], "workflowYaml": []}
        for key, value in record.items():
            if key.startswith("dbConfigYaml"):
                value["folderName"] = record.get("folderName", "default")
                yaml_data["dbConfigYaml"].append(value)
            elif key.startswith("workflowYaml"):
                yaml_data["workflowYaml"].append(value)
        
        copy_yaml_files_to_repo(clone_path, yaml_data)
        
        team_slug = None
        team_name = ""
        members_str = ""
        if "githubTeam" in record:
            team_slug = create_github_team_and_add_members(org, record["githubTeam"], api_key)
            team_name = record["githubTeam"].get("teamName", "")
            members_str = "|".join(record["githubTeam"].get("members", []))
        
        if team_slug:
            ensure_environments(record["repository"], org, team_slug, api_key)
        
        unique_branch_name = generate_unique_branch_name(record.get("branch", "main"))
        
        pr_url = create_pull_request(
            record["repository"],
            record["prDetails"]["title"],
            record["prDetails"]["description"],
            record["branch"],
            unique_branch_name,
            api_key
        )
        
        update_csv_report(csv_file, record["repository"], record["branch"], record["folderName"], team_name, members_str, pr_url)
        
    except Exception as e:
        logger.error(f"Error processing record {record['repository']} with branch {record['branch']}: {e}")

# ----------------- Main Entry Point ----------------- #
if __name__ == "__main__":
    args = parse_arguments()
    
    api_key = args.api_token
    org = "your-org-name"  # Replace with your GitHub organization name
    csv_file = args.report_file
    
    # Fetch JSON data from the API using the input payload
    try:
        input_payload = json.loads(args.input_payload)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding input payload: {e}")
        exit(1)
    
    json_data = fetch_json_data(args.api_url, input_payload)
    if json_data is None:
        logger.error("No JSON data returned from API. Exiting.")
        exit(1)
    
    # Write the JSON output file for record keeping
    with open(args.json_output_file, "w") as f:
        json.dump(json_data, f, indent=4)
    
    # Process each record in the JSON data (expected to be a list)
    for record in json_data:
        process_record_and_create_pr(record, api_key, org, csv_file)