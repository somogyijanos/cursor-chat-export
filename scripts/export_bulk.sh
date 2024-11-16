#!/bin/bash

# Directory containing state.vscdb files
BASE_DIR="/Users/user/Library/Application Support/Cursor/User/workspaceStorage"
OUTPUT_DIR="_outputs/workspaces_export"
LIMIT=0  # 0 means no limit, positive number will limit processing

# Check if --test flag is provided
if [[ "$1" == "--test" ]]; then
    LIMIT=5
    echo "Test mode: Processing only first 5 workspaces"
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Read workspace hashes and process each one
while IFS= read -r hash || [[ -n "$hash" ]]; do
    # Skip empty lines
    [[ -z "$hash" ]] && continue
    
    # Skip lines that don't look like hashes
    [[ ! $hash =~ ^[a-f0-9]+$ ]] && continue
    
    # Create unique output directory for this workspace
    WORKSPACE_DIR="${OUTPUT_DIR}/workspace-${hash}"
    mkdir -p "$WORKSPACE_DIR"
    
    echo "Processing workspace: $hash"
    
    # Run the export command
    poetry run python chat.py export \
        --output-dir "$WORKSPACE_DIR" \
        "${BASE_DIR}/${hash}/state.vscdb"
    
    # Increment counter and check limit
    ((COUNT++))
    if [[ $LIMIT -gt 0 && $COUNT -ge $LIMIT ]]; then
        echo "Reached limit of $LIMIT workspaces"
        break
    fi
    
done < "_outputs/chats_discovery1.md"

echo "Processing complete. Exported to $OUTPUT_DIR"