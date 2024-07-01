#!/bin/bash

ORG="your_organization_name"
TOKEN="your_github_personal_access_token"
PAGE=1
PER_PAGE=100
REPOS=()

while :; do
  RESPONSE=$(curl -s -H "Authorization: token $TOKEN" "https://api.github.com/orgs/$ORG/repos?per_page=$PER_PAGE&page=$PAGE")
  REPOS_PAGE=$(echo "$RESPONSE" | jq -r '.[].full_name')
  
  if [ -z "$REPOS_PAGE" ]; then
    break
  fi
  
  REPOS+=($REPOS_PAGE)
  PAGE=$((PAGE + 1))
done

for REPO in "${REPOS[@]}"; do
  echo "$REPO"
done