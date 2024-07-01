#!/bin/bash

# Determine the OS version
if grep -q "release 8" /etc/redhat-release; then
    OS_VERSION="RHEL8"
elif grep -q "release 7" /etc/redhat-release; then
    OS_VERSION="RHEL7"
else
    echo "Unsupported OS version"
    exit 1
fi

# Set environment variables based on the OS version
if [ "$OS_VERSION" == "RHEL8" ]; then
    export VAR1="value_for_rhel8"
    export VAR2="another_value_for_rhel8"
    # Add more environment variables for RHEL8
elif [ "$OS_VERSION" == "RHEL7" ]; then
    export VAR1="value_for_rhel7"
    export VAR2="another_value_for_rhel7"
    # Add more environment variables for RHEL7
fi

# Add common environment variables if any
export COMMON_VAR="common_value"