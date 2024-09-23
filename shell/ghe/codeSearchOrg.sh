#!/bin/bash

# GitHub API token and organization details
GITHUB_TOKEN="your_github_token_here"
GITHUB_ORG="your_org_here"
SEARCH_PATTERN="your_search_pattern_here"
OUTPUT_FILE="search_results.csv"
PER_PAGE=100  # Number of items per page for pagination

# Function to search GitHub repositories and extract matches
search_github() {
    local repo=$1
    local page=1
    local has_more=true

    while $has_more; do
        # Call GitHub Code Search API for the exact matching pattern within a repository with pagination
        response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
            "https://api.github.com/search/code?q=${SEARCH_PATTERN}+in:file+repo:${GITHUB_ORG}/${repo}&per_page=${PER_PAGE}&page=${page}")

        # Check if there are items in the response
        item_count=$(echo "$response" | jq '.items | length')

        if [[ "$item_count" -gt 0 ]]; then
            # Parse the response to extract file names and matching snippets
            echo "$response" | jq -r '.items[] | [.repository.full_name, .name, .text_matches[0].fragment] | @csv' >> $OUTPUT_FILE
            ((page++))  # Go to the next page
        else
            has_more=false  # No more results
        fi
    done
}

# Function to fetch repositories from the organization with pagination
fetch_repositories() {
    local page=1
    local has_more=true

    while $has_more; do
        # Fetch the list of repositories in the organization with pagination
        repos=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
            "https://api.github.com/orgs/$GITHUB_ORG/repos?per_page=${PER_PAGE}&page=${page}" | jq -r '.[].name')

        # Check if any repositories were returned
        if [[ -n "$repos" ]]; then
            for repo in $repos; do
                echo "Searching in repository: $repo"
                search_github $repo
            done
            ((page++))  # Go to the next page
        else
            has_more=false  # No more repositories
        fi
    done
}

# Main script execution
echo "Repository,File Name,Match" > $OUTPUT_FILE

# Fetch and search repositories with pagination
fetch_repositories

echo "Search completed. Results saved to $OUTPUT_FILE"