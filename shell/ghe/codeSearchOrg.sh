#!/bin/bash

# GitHub token and organization details
GITHUB_TOKEN="YOUR_GITHUB_TOKEN"
GITHUB_ORG="app-tst"
SEARCH_PATTERN="com.gradle.enterprise"
PER_PAGE=100
OUTPUT_FILE="search_results.csv"

# Initialize page number and more results flag
page=1
has_more=true

# CSV header
echo "Repository,File Name,File URL" > $OUTPUT_FILE

# Loop to handle pagination
while $has_more; do
    # Fetch search results for the current page
    response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/search/code?q=%22${SEARCH_PATTERN}%22+in:file+org:${GITHUB_ORG}&per_page=${PER_PAGE}&page=${page}")

    # Check if there are items in the response
    item_count=$(echo "$response" | jq '.items | length')

    if [[ "$item_count" -gt 0 ]]; then
        # Filter for exact matches and append results to the CSV
        echo "$response" | jq -r '.items[] | select(.text_matches[].fragment | contains("'"${SEARCH_PATTERN}"'")) | [.repository.full_name, .name, .html_url] | @csv' >> $OUTPUT_FILE
        ((page++))  # Move to the next page
    else
        has_more=false  # No more results, stop the loop
    fi
done

echo "Search completed. Results saved to $OUTPUT_FILE"