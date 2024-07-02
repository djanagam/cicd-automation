#!/bin/bash

sed -i 's/\(^\|[^a-zA-Z0-9_-]\)Ubuntu-latest\([^a-zA-Z0-9_-]\|$\)/\1Ubuntu-latest-medium\2/g' yourfile.txt

# Define the file containing the string replacements
replacements_file="replacements.txt"

# Define the folder containing the YAML files
yaml_folder="path_to_yaml_folder"

# Read the replacements file line by line
while IFS=: read -r current_string replace_string; do
    # Escape spaces for the current_string
    escaped_current_string=$(printf '%s\n' "$current_string" | sed 's:[][\/.^$*]:\\&:g')
    
    # Find all YAML files in the specified folder and subfolders
    find "$yaml_folder" -type f -name "*.yaml" | while read -r yaml_file; do
        # Replace the exact current_string with replace_string in the YAML file
        sed -i "s/$escaped_current_string/$replace_string/g" "$yaml_file"
    done
done < "$replacements_file"



#!/bin/bash

# Define the file containing the string replacements
replacements_file="replacements.txt"

# Define the folder containing the YAML files
yaml_folder="path_to_yaml_folder"

# Read the replacements file line by line
while IFS=: read -r current_string replace_string; do
    # Escape special characters except spaces in the current_string
    escaped_current_string=$(printf '%s\n' "$current_string" | sed 's/[&/\]/\\&/g')
    
    # Find all YAML files in the specified folder and subfolders
    find "$yaml_folder" -type f -name "*.yaml" | while read -r yaml_file; do
        # Replace the exact current_string with replace_string in the YAML file
        sed -i "s/$escaped_current_string/$replace_string/g" "$yaml_file"
    done
done < "$replacements_file"



#!/bin/bash

# Function to escape special characters [ and ]
escape_special_characters() {
    local input="$1"
    # Escape [ and ]
    local escaped_input=$(echo "$input" | sed 's/\[/\\[/g; s/\]/\\]/g')
    echo "$escaped_input"
}

# Define the file containing the string replacements
replacements_file="replacements.txt"

# Define the folder containing the YAML files
yaml_folder="path_to_yaml_folder"

# Read the replacements file line by line
while IFS=: read -r current_string replace_string; do
    # Escape special characters in the current_string
    escaped_current_string=$(escape_special_characters "$current_string")
    
    # Find all YAML files in the specified folder and subfolders
    find "$yaml_folder" -type f -name "*.yaml" | while read -r yaml_file; do
        # Replace the exact current_string with replace_string in the YAML file
        sed -i "s/$escaped_current_string/$replace_string/g" "$yaml_file"
    done
done < "$replacements_file"
