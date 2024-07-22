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

# Parse the JSON file and get the full_name values
REPOS=$(jq -r '.repository_cache_usages[].full_name' repositories.json)

# Iterate over each repository and make an API call
for REPO in $REPOS; do
  OWNER=$(echo $REPO | cut -d'/' -f1)
  REPO_NAME=$(echo $REPO | cut -d'/' -f2)

  echo "Processing repository: $REPO"

  # Make API call to GitHub Actions cache for the repository
  CACHE_RESPONSE=$(curl -s -L \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer $TOKEN" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "https://api.github.com/repos/$OWNER/$REPO_NAME/actions/caches")

  # Extract the key values from the response JSON
  CACHE_KEYS=$(echo $CACHE_RESPONSE | jq -r '.actions_caches[].key')

  for KEY in $CACHE_KEYS; do
    echo "Found cache key: $KEY for repository: $REPO"
  done

  echo "API call completed for repository: $REPO"
done