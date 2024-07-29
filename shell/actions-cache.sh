#!/bin/bash

# GitHub personal access token
TOKEN="your-github-token"
ORG="your-organization"  # Replace with your organization name
LOG_FILE="script_output.log"

# Function to delete cache by key and capture response code
delete_cache() {
  local repo=$1
  local key=$2
  local response

  echo "Deleting cache with key: $key for repository: $repo" | tee -a $LOG_FILE

  # Perform the DELETE request and capture response code
  response=$(curl -s -w "%{http_code}" -o /dev/null -X DELETE \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer $TOKEN" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "https://api.github.com/repos/$repo/actions/caches?key=$key")

  # Print the response code
  echo "Response code: $response" | tee -a $LOG_FILE
}

# Function to fetch caches with pagination
fetch_caches() {
  local repo=$1
  local url=$2

  while [[ -n "$url" ]]; do
    echo "Fetching caches from URL: $url" | tee -a $LOG_FILE
    response=$(curl -s -D - -L \
      -H "Accept: application/vnd.github+json" \
      -H "Authorization: Bearer $TOKEN" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      "$url")

    # Extract the body and headers
    body=$(echo "$response" | sed -n '/^\r$/,$p')
    headers=$(echo "$response" | sed -n '1,/^\r$/p')

    # Extract cache metadata from the response body
    CACHE_METADATA=$(echo "$body" | jq -r '.actions_caches[] | [.key, .created_at, .last_accessed_at] | @csv')

    while IFS=, read -r KEY CREATED_AT LAST_ACCESSED_AT; do
      echo "Found cache key: $KEY, created at: $CREATED_AT, last accessed at: $LAST_ACCESSED_AT for repository: $repo" | tee -a $LOG_FILE
      delete_cache "$repo" "$KEY"
    done <<< "$CACHE_METADATA"

    # Check for the next page URL from the headers
    url=$(echo "$headers" | grep -oP '(?<=<)[^>]+(?=>; rel="next")')
  done
}

# Function to fetch repositories using actions cache with pagination
fetch_repositories() {
  local url=$1

  while [[ -n "$url" ]]; do
    echo "Fetching repositories from URL: $url" | tee -a $LOG_FILE
    response=$(curl -s -D - -L \
      -H "Accept: application/vnd.github+json" \
      -H "Authorization: Bearer $TOKEN" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      "$url")

    # Extract the body and headers
    body=$(echo "$response" | sed -n '/^\r$/,$p')
    headers=$(echo "$response" | sed -n '1,/^\r$/p')

    # Extract repository full_name values from the response body
    REPOS=$(echo "$body" | jq -r '.repository_cache_usages[].full_name')

    for REPO in $REPOS; do
      echo "Processing repository: $REPO" | tee -a $LOG_FILE

      # Initial API call to GitHub Actions cache for the repository
      INITIAL_URL="https://api.github.com/repos/$REPO/actions/caches"

      # Fetch caches with pagination
      fetch_caches "$REPO" "$INITIAL_URL"

      echo "API call completed for repository: $REPO" | tee -a $LOG_FILE
    done

    # Check for the next page URL from the headers
    url=$(echo "$headers" | grep -oP '(?<=<)[^>]+(?=>; rel="next")')
  done
}

# Initial API call to fetch repositories using actions cache
INITIAL_URL="https://api.github.com/orgs/$ORG/actions/cache/usage-by-repository"
fetch_repositories "$INITIAL_URL"