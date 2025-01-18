#!/usr/bin/env bash

# Exit on error
set -e

# Function to display usage
usage() {
  echo "Usage: $0 -u <username> -t <token> -f <file_url>"
  echo
  echo "  -u    Artifactory username"
  echo "  -t    Artifactory token"
  echo "  -f    URL to the tar file in Artifactory"
  exit 1
}

# Parse input arguments
while getopts "u:t:f:" opt; do
  case $opt in
    u) ARTIFACTORY_USERNAME="$OPTARG" ;;
    t) ARTIFACTORY_TOKEN="$OPTARG" ;;
    f) FILE_URL="$OPTARG" ;;
    *) usage ;;
  esac
done

# Check if all arguments are provided
if [[ -z "$ARTIFACTORY_USERNAME" || -z "$ARTIFACTORY_TOKEN" || -z "$FILE_URL" ]]; then
  usage
fi

# Temporary directory for the download
TMP_DIR=$(mktemp -d)
trap "rm -rf $TMP_DIR" EXIT

# Download the tar file using curl
echo "Downloading tar file from Artifactory..."
curl -u "$ARTIFACTORY_USERNAME:$ARTIFACTORY_TOKEN" -L "$FILE_URL" -o "$TMP_DIR/archive.tar"

# Extract the tar file
echo "Extracting tar file..."
EXTRACTED_DIR="$TMP_DIR/extracted"
mkdir -p "$EXTRACTED_DIR"
tar -xf "$TMP_DIR/archive.tar" -C "$EXTRACTED_DIR"

# Find the bin directory and add it to PATH
BIN_DIR=$(find "$EXTRACTED_DIR" -type d -name "bin" | head -n 1)
if [[ -z "$BIN_DIR" ]]; then
  echo "Error: No 'bin' directory found in the extracted files."
  exit 1
fi

echo "Adding $BIN_DIR to PATH..."
export PATH="$BIN_DIR:$PATH"

# Print success message
echo "Setup completed successfully."
echo "New PATH: $PATH"

# Optional: Keep PATH change in the current shell (or comment this out if not desired)
echo "export PATH=\"$BIN_DIR:\$PATH\"" >> ~/.bashrc
echo "To persist the PATH update, restart your shell or run 'source ~/.bashrc'."