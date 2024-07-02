#!/bin/bash

# Number of lines per split
LINES_PER_SPLIT=100
# Input file path
INPUT_FILE="path/to/your/file.txt"
# Prefix for output files
PREFIX="batch_"

# Split the file
split -l $LINES_PER_SPLIT $INPUT_FILE temp_

# Rename the split files
count=1
for file in temp_*
do
    mv "$file" "${PREFIX}${count}.txt"
    count=$((count + 1))
done