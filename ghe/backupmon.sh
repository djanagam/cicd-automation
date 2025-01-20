#!/bin/bash

# Configuration
LOG_DIR="/apps/ghe/cron-logs"
LOG_PATTERN="*.github-backup_utils_cron.log"
ERROR_STRING="Error: Snapshot incomplete"
STATE_FILE="/tmp/processed_backup_logs.txt"
API_URL="https://example.com/api/notify"
API_KEY="your_api_key" # Optional, if the API requires authentication
PAYLOAD_FILE="/tmp/backup_failure_payload.json"

# Function to send API notification
notify_failure() {
    local log_file=$1
    local log_content

    # Read the log file content and escape for JSON
    log_content=$(<"$log_file")
    log_content=$(echo "$log_content" | jq -R -s '.')

    echo "$(date): Preparing failure payload for log file: $log_file"
    cat <<EOF > $PAYLOAD_FILE
{
  "event": "ghe-backup-failure",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "log_file": "$log_file",
  "error": "$ERROR_STRING",
  "description": $log_content
}
EOF

    echo "$(date): Sending notification to API..."
    curl -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $API_KEY" \
        --data @"$PAYLOAD_FILE"

    if [ $? -eq 0 ]; then
        echo "$(date): Notification sent successfully."
    else
        echo "$(date): Failed to send notification."
    fi

    # Clean up payload file
    rm -f $PAYLOAD_FILE
}

# Main monitoring function
monitor_logs() {
    # Find the most recent non-empty log file
    local latest_log=$(find "$LOG_DIR" -type f -name "$LOG_PATTERN" -size +0c -print0 | xargs -0 ls -t | head -n 1)

    if [ -z "$latest_log" ]; then
        echo "$(date): No non-empty log file found. Exiting."
        exit 0
    fi

    echo "$(date): Most recent log file: $latest_log"

    # Check if this log file has already been processed
    if grep -qF "$latest_log" "$STATE_FILE" 2>/dev/null; then
        echo "$(date): Log file $latest_log has already been processed. Skipping."
        exit 0
    fi

    # Search for the error string in the log file
    if grep -q "$ERROR_STRING" "$latest_log"; then
        echo "$(date): Error found in log file: $latest_log"
        notify_failure "$latest_log"

        # Mark this log file as processed
        echo "$latest_log" >> "$STATE_FILE"
    else
        echo "$(date): No error found in log file: $latest_log"
    fi
}

# Ensure the state file exists
if [ ! -f "$STATE_FILE" ]; then
    touch "$STATE_FILE"
fi

# Run the monitoring function
monitor_logs