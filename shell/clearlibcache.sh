#!/bin/bash

# Base directory
base_dir="/apps/jenkins/caches"

# Iterate over each directory in the base directory
for dir in "$base_dir"/*; do
    if [ -d "$dir" ]; then
        # Check if any of the 'src', 'vars', or 'resources' subdirectories are missing
        if [ ! -d "$dir/src" ] || [ ! -d "$dir/vars" ] || [ ! -d "$dir/resources" ]; then
            # Recursively delete the top-level directory
            echo "Deleting directory: $dir"
            rm -rf "$dir"
        fi
    fi
done