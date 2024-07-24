#!/bin/bash

# GitHub personal access token
TOKEN="your-github-token"

# Save JSON content to a file
cat <<EOF > repositories.json
{
  "total_count": 2,
  "repository_cache_usages": [
    {
      "full_name": "octo-org/Hello-World",
      "active_caches_size_in_bytes": 2322142,
      "active_caches_count": 3
    },
    {
      "full_name": "octo-org/server",
      "active_caches_size_in_bytes": 1022142,
      "active_caches_count": 2
    }
  ]
}
EOF

# Function to delete cache by key and capture response code
delete_cache() {
  local repo=$1
  local key=$2
  local response

  echo "Deleting cache with key: $key for repository: $repo"

  # Perform the DELETE request and capture response code
  response=$(curl -s -w "%{http_code}" -o /dev/null -X DELETE \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer $TOKEN" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "https://api.github.com/repos/$repo/actions/caches?key=$key")

  # Print the response code
  echo "Response code: $response"
}

# Function to fetch caches with pagination
fetch_caches() {
  local repo=$1
  local url=$2

  while [[ -n "$url" ]]; do
    echo "Fetching caches from URL: $url"
    response=$(curl -s -D - -L \
      -H "Accept: application/vnd.github+json" \
      -H "Authorization: Bearer $TOKEN" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      "$url")

    # Extract the body and headers
    body=$(echo "$response" | sed -n '/^\r$/,$p')
    headers=$(echo "$response" | sed -n '1,/^\r$/p')

    # Extract cache keys from the response body
    CACHE_KEYS=$(echo "$body" | jq -r '.actions_caches[].key')

    for KEY in $CACHE_KEYS; do
      echo "Found cache key: $KEY for repository: $repo"
      delete_cache "$repo" "$KEY"
    done

    # Check for the next page URL from the headers
    url=$(echo "$headers" | grep -oP '(?<=<)[^>]+(?=>; rel="next")')
  done
}

# Parse the JSON file and get the full_name values
REPOS=$(jq -r '.repository_cache_usages[].full_name' repositories.json)

# Iterate over each repository and make an API call
for REPO in $REPOS; do
  OWNER=$(echo $REPO | cut -d'/' -f1)
  REPO_NAME=$(echo $REPO | cut -d'/' -f2)

  echo "Processing repository: $REPO"

  # Initial API call to GitHub Actions cache for the repository
  INITIAL_URL="https://api.github.com/repos/$OWNER/$REPO_NAME/actions/caches"

  # Fetch caches with pagination
  fetch_caches "$REPO" "$INITIAL_URL"

  echo "API call completed for repository: $REPO"
done