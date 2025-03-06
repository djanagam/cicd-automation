import os
import json
import logging
import shutil
import random
import string
import requests
from github import Github  # GitHub Client for cloning, committing, pushing

# Constants for JSON keys
REPOSITORY_KEY = "repository"
BRANCH_KEY = "branch"
FOLDER_NAME_KEY = "folderName"
TEAM_NAME_KEY = "teamName"
MEMBERS_KEY = "members"
PR_DETAILS_KEY = "prDetails"
PR_TITLE_KEY = "title"
PR_DESCRIPTION_KEY = "description"
DEFAULT_BRANCH = "main"  # Define your default branch

# GitHub Token
GITHUB_TOKEN = "your_github_token_here"
g = Github(GITHUB_TOKEN)

# Function to create random workspace names
def generate_workspace_name():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

# Function to fetch default branch using GitHub API
def get_default_branch(repo_name):
    repo = g.get_repo(repo_name)
    return repo.default_branch

# Function to process JSON and handle different scenarios
def process_json_and_extract_yaml(json_file, report_file):
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)

        for record in data:
            repo = record.get(REPOSITORY_KEY)
            branch = record.get(BRANCH_KEY, DEFAULT_BRANCH)
            folder_name = record.get(FOLDER_NAME_KEY, "default_folder")
            pr_details = record.get(PR_DETAILS_KEY, {})
            pr_title = pr_details.get(PR_TITLE_KEY, "Default Title")
            pr_description = pr_details.get(PR_DESCRIPTION_KEY, "Default Description")
            team_name = record.get("githubTeam", {}).get(TEAM_NAME_KEY, "Unknown")
            members = record.get("githubTeam", {}).get(MEMBERS_KEY, [])

            # Handle missing branch, default to repo's default branch
            if not branch:
                branch = get_default_branch(repo)

            # Handle missing folder name
            if not folder_name:
                folder_name = "default_folder"

            # Generate workspace name to avoid conflicts when cloning
            workspace_name = generate_workspace_name()

            # Clone repo and copy YAML files (function call will handle multiple scenarios)
            clone_and_copy_yaml_files(repo, branch, folder_name, workspace_name)

            # Process PR details (create PR using GitHub API)
            create_pull_request(repo, branch, pr_title, pr_description)

            # Generate CSV Report
            members_str = "|".join(members)
            csv_row = f"{repo},{branch},{folder_name},{team_name},{members_str}\n"

            write_mode = 'w' if not os.path.exists(report_file) else 'a'
            with open(report_file, write_mode) as f:
                if write_mode == 'w':
                    f.write("repository,branch,folderName,teamName,members\n")
                f.write(csv_row)

            logging.info(f"Processed record for repo: {repo}, branch: {branch}, folder: {folder_name}")

    except FileNotFoundError:
        logging.error(f"Error: The JSON file '{json_file}' was not found.")
    except json.JSONDecodeError:
        logging.error(f"Error: The JSON file '{json_file}' is not valid JSON.")
    except KeyError as e:
        logging.error(f"Error: Missing key in JSON data - {e}")

# Function to clone repo, checkout branch, and copy YAML files into workspace
def clone_and_copy_yaml_files(repo, branch, folder_name, workspace_name):
    try:
        # Create a random workspace to avoid conflicts
        workspace_dir = os.path.join(os.getcwd(), workspace_name)
        os.makedirs(workspace_dir, exist_ok=True)

        # Clone the repo and checkout the branch
        repo_obj = g.get_repo(repo)
        repo_obj.clone_to(workspace_dir, branch=branch)  # This is a placeholder. Replace with actual clone logic using GitHub client

        # Handle YAML copying (assuming you are extracting from the repo or JSON)
        db_config_file = os.path.join(workspace_dir, f"{repo}_db_config.yml")
        workflow_file = os.path.join(workspace_dir, f"{repo}_workflow.yml")

        shutil.copy(db_config_file, os.path.join(workspace_dir, f"{folder_name}_db_config.yml"))
        shutil.copy(workflow_file, os.path.join(workspace_dir, f"{folder_name}_workflow.yml"))

        logging.info(f"Cloned repo {repo} and copied YAML files to {workspace_dir}")

    except Exception as e:
        logging.error(f"Error cloning repo {repo} and copying YAML files: {e}")

# Function to create a pull request on GitHub using the GitHub API
def create_pull_request(repo, branch, pr_title, pr_description):
    try:
        # Placeholder: create a pull request using the GitHub REST API
        repo_obj = g.get_repo(repo)
        pr = repo_obj.create_pull(
            title=pr_title,
            body=pr_description,
            head=branch,  # Specify the branch you want to merge
            base="main"  # The base branch, typically the main branch
        )
        logging.info(f"Pull request created for {repo} on branch {branch}")

    except Exception as e:
        logging.error(f"Error creating pull request for {repo} on branch {branch}: {e}")

# Example usage
if __name__ == "__main__":
    json_file = "api_result.json"  # Replace with the actual path to your JSON file
    report_file = "report.csv"  # Output CSV report

    # Process JSON data and generate the report
    process_json_and_extract_yaml(json_file, report_file)