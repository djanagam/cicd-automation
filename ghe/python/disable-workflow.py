import requests
import yaml
import argparse
import base64

# Default GitHub URL (can be overridden via CLI)
DEFAULT_GITHUB_URL = "https://github.company.com"

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Disable GitHub workflows with invalid runner labels on self-hosted GitHub.")
parser.add_argument("--token", required=True, help="GitHub API token with workflow scope")
parser.add_argument("--github-url", default=DEFAULT_GITHUB_URL, help=f"Base URL of self-hosted GitHub (default: {DEFAULT_GITHUB_URL})")
parser.add_argument("--repos-file", default="repos.txt", help="File containing list of repositories (default: repos.txt)")
args = parser.parse_args()

GITHUB_TOKEN = args.token
GITHUB_URL = args.github_url.rstrip("/")  # Remove trailing slash if present
REPOS_FILE = args.repos_file

# List of invalid runner labels
INVALID_RUNNER_LABELS = {"invalid-runner-1", "invalid-runner-2", "deprecated-runner"}

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# Read repositories from input file
with open(REPOS_FILE, "r") as f:
    repositories = [line.strip() for line in f if line.strip()]

for repo in repositories:
    print(f"\nProcessing repository: {repo}")
    
    # Get all workflows in the repository
    workflow_url = f"{GITHUB_URL}/api/v3/repos/{repo}/actions/workflows"
    response = requests.get(workflow_url, headers=headers)

    if response.status_code != 200:
        print(f"❌ Failed to fetch workflows for {repo}: {response.text}")
        continue

    workflows = response.json().get("workflows", [])

    for workflow in workflows:
        workflow_id = workflow["id"]
        workflow_name = workflow["name"]
        workflow_yaml_url = f"{GITHUB_URL}/api/v3/repos/{repo}/contents/{workflow['path']}"

        # Get workflow YAML content using GitHub API
        yaml_response = requests.get(workflow_yaml_url, headers=headers)

        if yaml_response.status_code == 200:
            workflow_content_encoded = yaml_response.json().get("content", "")
            workflow_content_decoded = base64.b64decode(workflow_content_encoded).decode("utf-8")
            workflow_content = yaml.safe_load(workflow_content_decoded)

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
                disable_url = f"{GITHUB_URL}/api/v3/repos/{repo}/actions/workflows/{workflow_id}/disable"
                disable_response = requests.put(disable_url, headers=headers)

                if disable_response.status_code == 204:
                    print(f"✅ Successfully disabled workflow: {workflow_name}")
                else:
                    print(f"❌ Failed to disable workflow: {workflow_name} - {disable_response.text}")
        else:
            print(f"❌ Failed to fetch YAML for workflow: {workflow_name} in {repo}")