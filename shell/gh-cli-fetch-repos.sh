#!/bin/bash

# Replace with your GitHub organization name
ORG_NAME="your-org-name"

# Number of repositories per page
PER_PAGE=100

# Initialize page number
page=1

# Fetch all repositories in the organization
repos=()
while true; do
  current_page_repos=$(gh repo list "$ORG_NAME" --limit $PER_PAGE --page $page --json name --jq '.[].name')
  
  if [[ -z "$current_page_repos" ]]; then
    break
  fi
  
  repos+=($current_page_repos)
  ((page++))
done

# Loop through each repository to check if GitHub Actions is enabled
for repo in "${repos[@]}"; do
  # Fetch GitHub Actions settings for the repository
  actions_enabled=$(gh api "/repos/$ORG_NAME/$repo/actions/permissions" --jq '.enabled')

  if [[ "$actions_enabled" == "true" ]]; then
    echo "$repo has GitHub Actions enabled"
  fi
done