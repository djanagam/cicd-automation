#!/bin/bash

# Output report file
REPORT="ssh_files_report.csv"

# Hostname
HOSTNAME=$(hostname)

# Files to validate
FILES=(
    "$HOME/.ssh/config"
    "$HOME/.ssh/id_rsa1"
    "$HOME/.ssh/id_rsa2"
)

# Keywords to look for in ~/.ssh/config
KEYWORDS=(
    "github.com"
    "Second-github.com"
    "artifactory.com"
    "uat-artifactory.com"
)

# Initialize the report
echo "Hostname,File,Found" > "$REPORT"

# Check each file for existence
for FILE in "${FILES[@]}"; do
    if [ -f "$FILE" ]; then
        echo "$HOSTNAME,$FILE,Found" >> "$REPORT"
    else
        echo "$HOSTNAME,$FILE,Not Found" >> "$REPORT"
    fi
done

# Check for keywords in ~/.ssh/config
CONFIG_FILE="$HOME/.ssh/config"
if [ -f "$CONFIG_FILE" ]; then
    for KEYWORD in "${KEYWORDS[@]}"; do
        if grep -q "$KEYWORD" "$CONFIG_FILE"; then
            echo "$HOSTNAME,$CONFIG_FILE contains $KEYWORD,Found" >> "$REPORT"
        else
            echo "$HOSTNAME,$CONFIG_FILE contains $KEYWORD,Not Found" >> "$REPORT"
        fi
    done
else
    for KEYWORD in "${KEYWORDS[@]}"; do
        echo "$HOSTNAME,$CONFIG_FILE contains $KEYWORD,Not Found" >> "$REPORT"
    done
fi

# Display the report
cat "$REPORT"
