#!/bin/bash

ORG="your_organization_name"
TOKEN="your_github_personal_access_token"
REPO_LIST="repos.txt"
ARCHIVED_REPOS=()
NON_ARCHIVED_REPOS=()

while read -r REPO; do
  RESPONSE=$(curl -s -H "Authorization: token $TOKEN" "https://api.github.com/repos/$ORG/$REPO")
  IS_ARCHIVED=$(echo "$RESPONSE" | jq -r '.archived')
  
  if [ "$IS_ARCHIVED" = "true" ]; then
    ARCHIVED_REPOS+=("$REPO")
  else
    NON_ARCHIVED_REPOS+=("$REPO")
  fi
done < "$REPO_LIST"

echo "Archived Repositories:"
for REPO in "${ARCHIVED_REPOS[@]}"; do
  echo "$REPO"
done

echo
echo "Non-Archived Repositories:"
for REPO in "${NON_ARCHIVED_REPOS[@]}"; do
  echo "$REPO"
done