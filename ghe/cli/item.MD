To achieve your goal, you can build a GitHub CLI (gh) extension combined with a GitHub Action workflow to execute operations on repositories within an organization. Here’s a step-by-step approach to implement this solution:

1. Create the GitHub CLI Utility

You can create a GitHub CLI extension using gh to perform the required operations. Below is the structure and implementation:

Structure
	•	Utility Name: gh-org-workflows
	•	Commands:
	•	list-workflows: Get a list of workflows for all repos in the org.
	•	list-cron-workflows: Get workflows with cron enabled.
	•	in-progress: List workflows currently in progress.

Setup

# Initialize CLI extension
gh extension create gh-org-workflows
cd gh-org-workflows

Code Implementation (gh-org-workflows script)

Here’s the shell script that handles the commands:

#!/usr/bin/env bash

ORG=""
COMMAND=""
TOKEN=$(gh auth token)

function list_workflows() {
  echo "Fetching workflows for org: $ORG"
  repos=$(gh repo list "$ORG" --json name --jq '.[].name')
  for repo in $repos; do
    workflows=$(gh api "/repos/$ORG/$repo/actions/workflows" --jq '.workflows[] | {name: .name, id: .id}')
    echo "Workflows for $repo:"
    echo "$workflows"
  done
}

function list_cron_workflows() {
  echo "Fetching workflows with cron schedules for org: $ORG"
  repos=$(gh repo list "$ORG" --json name --jq '.[].name')
  for repo in $repos; do
    cron_workflows=$(gh api "/repos/$ORG/$repo/actions/workflows" \
      --jq '.workflows[] | select(.schedule != null) | {name: .name, schedule: .schedule}')
    if [ -n "$cron_workflows" ]; then
      echo "Cron-enabled workflows for $repo:"
      echo "$cron_workflows"
    fi
  done
}

function list_in_progress_workflows() {
  echo "Fetching in-progress workflows for org: $ORG"
  repos=$(gh repo list "$ORG" --json name --jq '.[].name')
  for repo in $repos; do
    in_progress=$(gh api "/repos/$ORG/$repo/actions/runs" \
      --jq '.workflow_runs[] | select(.status == "in_progress") | {id: .id, name: .name, status: .status}')
    if [ -n "$in_progress" ]; then
      echo "In-progress workflows for $repo:"
      echo "$in_progress"
    fi
  done
}

while [[ $# -gt 0 ]]; do
  case $1 in
    --org)
      ORG="$2"
      shift
      shift
      ;;
    --list-workflows)
      COMMAND="list_workflows"
      shift
      ;;
    --list-cron-workflows)
      COMMAND="list_cron_workflows"
      shift
      ;;
    --in-progress)
      COMMAND="list_in_progress_workflows"
      shift
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

if [ -z "$ORG" ]; then
  echo "Error: --org is required."
  exit 1
fi

case $COMMAND in
  list_workflows)
    list_workflows
    ;;
  list_cron_workflows)
    list_cron_workflows
    ;;
  list_in_progress_workflows)
    list_in_progress_workflows
    ;;
  *)
    echo "No valid command provided."
    exit 1
    ;;
esac

2. GitHub Action Workflow

You can create a GitHub Action workflow to automate running this utility and generate reports.

Workflow File (.github/workflows/run-gh-org-workflows.yml)

name: Run GitHub CLI Utility

on:
  workflow_dispatch:
    inputs:
      org:
        description: "GitHub Organization Name"
        required: true
      command:
        description: "Command to run (list-workflows, list-cron-workflows, in-progress)"
        required: true

jobs:
  run-gh-cli:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up GitHub CLI
        uses: gh-cli/install@v2

      - name: Install custom CLI extension
        run: |
          mkdir -p ~/.local/share/gh/extensions
          gh extension install ./gh-org-workflows

      - name: Run CLI Command
        run: |
          gh org-workflows --org "${{ github.event.inputs.org }}" --${{ github.event.inputs.command }}

3. Trigger and Generate Reports
	1.	Trigger Workflow:
Use the “Run Workflow” button in the GitHub Actions UI to provide inputs like org and command.
	2.	Output Report:
Save the output of the command to an artifact or push it to a specific repo for reports.

Save Output as Artifact

Add the following step to the workflow to save the command output:

      - name: Save Output
        run: |
          gh org-workflows --org "${{ github.event.inputs.org }}" --${{ github.event.inputs.command }}" > output.txt
        shell: bash

      - name: Upload Artifact
        uses: actions/upload-artifact@v3
        with:
          name: gh-org-workflows-report
          path: output.txt

4. Testing
	•	Install and test the utility locally:

./gh-org-workflows --org my-org --list-workflows


	•	Test the workflow on a test repository.

Let me know if you’d like further guidance or enhancements!