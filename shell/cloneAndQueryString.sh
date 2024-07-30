#!/bin/bash

# Define the patterns to search for
PATTERN1="your_first_pattern"
PATTERN2="your_second_pattern"

# Input file containing the list of repositories
REPO_FILE="repos.txt"

# Output report file
REPORT_FILE="pattern_report.txt"
echo "Repository,File,Pattern,Match" > $REPORT_FILE

# Temporary directory for cloning repositories
WORKSPACE_DIR=$(mktemp -d)

# Function to search for patterns in a repository
search_patterns() {
    local repo=$1
    local repo_name=$(basename $repo .git)
    local repo_dir="$WORKSPACE_DIR/$repo_name"

    git clone $repo $repo_dir

    if [ $? -ne 0 ]; then
        echo "Failed to clone $repo"
        return
    fi

    cd $repo_dir

    grep -r "$PATTERN1" . | while read -r line; do
        echo "$repo,$line,$PATTERN1" >> $REPORT_FILE
    done

    grep -r "$PATTERN2" . | while read -r line; do
        echo "$repo,$line,$PATTERN2" >> $REPORT_FILE
    done

    cd $WORKSPACE_DIR
    rm -rf $repo_dir
}

# Process each repository from the file
while IFS= read -r repo; do
    search_patterns $repo
done < "$REPO_FILE"

# Clean up
rm -rf $WORKSPACE_DIR

echo "Report generated: $REPORT_FILE"