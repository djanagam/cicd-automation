#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <input_file> <mappings_file>"
  exit 1
fi

input_file="$1"
mappings_file="$2"

# Make a temporary copy of the input file
temp_file=$(mktemp)
cp "$input_file" "$temp_file"

# Function to escape special characters in a string for sed
escape_sed() {
  printf '%s\n' "$1" | sed -e 's/[\/&]/\\&/g' -e 's/[][]/\\&/g'
}

# Read the mappings file line by line
while IFS=: read -r search replace; do
  # Escape special characters in search and replace strings
  escaped_search=$(escape_sed "$search")
  escaped_replace=$(escape_sed "$replace")
  # Apply the replacement only if the exact match is found
  sed -i "s/\b$escaped_search\b/$escaped_replace/g" "$temp_file"
done < "$mappings_file"

# Overwrite the input file with the modified content
mv "$temp_file" "$input_file"




#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <input_file> <mappings_file>"
  exit 1
fi

input_file="$1"
mappings_file="$2"

# Make a temporary copy of the input file
temp_file=$(mktemp)
cp "$input_file" "$temp_file"

# Read the mappings file line by line
while IFS=: read -r search replace; do
  # Escape special characters in search and replace strings
  escaped_search=$(printf '%s\n' "$search" | sed 's/[&/\]/\\&/g')
  escaped_replace=$(printf '%s\n' "$replace" | sed 's/[&/\]/\\&/g')
  # Apply the replacement only if the exact match is found
  sed -i "s/\b$escaped_search\b/$escaped_replace/g" "$temp_file"
done < "$mappings_file"

# Overwrite the input file with the modified content
mv "$temp_file" "$input_file"






sed -e 's/\(^\| \)aexp-medium\( \|,\|$\)/\1aexp-ubuntu-latest-medium\2/g' \
    -e 's/\(^\| \)aexp-ubuntu-latest\( \|,\|$\)/\1aexp-ubuntu-latest-medium\2/g' input_file