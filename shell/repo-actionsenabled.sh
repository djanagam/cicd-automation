#!/bin/bash

ORG="your_organization_name"
TOKEN="your_github_personal_access_token"
REPO_LIST="repos.txt"
ACTIONS_ENABLED_REPOS=()
ACTIONS_DISABLED_REPOS=()

while read -r REPO; do
  REPO_RESPONSE=$(curl -s -H "Authorization: token $TOKEN" "https://api.github.com/repos/$ORG/$REPO")
  ACTIONS_ENABLED=$(curl -s -H "Authorization: token $TOKEN" "https://api.github.com/repos/$ORG/$REPO/actions/permissions" | jq -r '.enabled')

  if [ "$ACTIONS_ENABLED" = "true" ]; then
    ACTIONS_ENABLED_REPOS+=("$REPO")
  else
    ACTIONS_DISABLED_REPOS+=("$REPO")
  fi
done < "$REPO_LIST"

echo "Repositories with Actions Enabled:"
for REPO in "${ACTIONS_ENABLED_REPOS[@]}"; do
  echo "$REPO"
done

echo
echo "Repositories with Actions Disabled:"
for REPO in "${ACTIONS_DISABLED_REPOS[@]}"; do
  echo "$REPO"
done