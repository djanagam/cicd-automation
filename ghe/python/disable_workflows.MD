Great! Here’s an updated script that reads a list of repositories from an input file (repos.txt), then iterates through each repo to check for and disable workflows with invalid runner labels.

Steps to Use the Script
	1.	Create an input file repos.txt (one repo per line in owner/repo format):

org1/repo1
org1/repo2
user1/repo3


	2.	Run the script, and it will process all repositories in the file.

Updated Script

import requests
import yaml

# GitHub API Token (Ensure it has 'workflow' scope)
GITHUB_TOKEN = "your_github_token"

# List of invalid runner labels
INVALID_RUNNER_LABELS = {"invalid-runner-1", "invalid-runner-2", "deprecated-runner"}

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Read repositories from input file
with open("repos.txt", "r") as f:
    repositories = [line.strip() for line in f if line.strip()]

for repo in repositories:
    print(f"\nProcessing repository: {repo}")
    
    # Get all workflows in the repository
    workflow_url = f"https://api.github.com/repos/{repo}/actions/workflows"
    response = requests.get(workflow_url, headers=headers)

    if response.status_code != 200:
        print(f"❌ Failed to fetch workflows for {repo}: {response.text}")
        continue

    workflows = response.json().get("workflows", [])

    for workflow in workflows:
        workflow_id = workflow["id"]
        workflow_name = workflow["name"]
        workflow_yaml_path = workflow["path"]  # Path to the workflow YAML file

        # Get raw YAML content
        raw_yaml_url = f"https://raw.githubusercontent.com/{repo}/main/{workflow_yaml_path}"
        yaml_response = requests.get(raw_yaml_url, headers=headers)

        if yaml_response.status_code == 200:
            workflow_content = yaml.safe_load(yaml_response.text)

            # Extract runner labels if available
            runner_labels = set()
            if "jobs" in workflow_content:
                for job in workflow_content["jobs"].values():
                    if "runs-on" in job:
                        if isinstance(job["runs-on"], list):
                            runner_labels.update(job["runs-on"])
                        else:
                            runner_labels.add(job["runs-on"])

            # Check if any invalid runner label is used
            if runner_labels & INVALID_RUNNER_LABELS:
                print(f"⚠️ Disabling workflow '{workflow_name}' in {repo} due to invalid runner labels: {runner_labels & INVALID_RUNNER_LABELS}")

                # Disable the workflow
                disable_url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow_id}/disable"
                disable_response = requests.put(disable_url, headers=headers)

                if disable_response.status_code == 204:
                    print(f"✅ Successfully disabled workflow: {workflow_name}")
                else:
                    print(f"❌ Failed to disable workflow: {workflow_name} - {disable_response.text}")
        else:
            print(f"❌ Failed to fetch YAML for workflow: {workflow_name} in {repo}")

How This Works

✔ Reads repos from repos.txt
✔ Iterates through each repo, fetching workflows
✔ Checks if workflows use invalid runner labels
✔ Disables the workflows if needed
✔ Prints status for each repo & workflow

Next Steps
	•	Run the script:

python disable_invalid_workflows.py


	•	If you want to run it across all repos in an organization, you can modify it to fetch repos dynamically from GitHub API.

Would you like it to support fetching all repositories from an organization automatically? Let me know!