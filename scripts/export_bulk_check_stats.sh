#!/bin/bash

# Define paths
EXPORT_DIR="_outputs/workspaces_export"
STATS_FILE="${EXPORT_DIR}/workspaces_statistic.csv"
WORKSPACE_BASE="/Users/user/Library/Application Support/Cursor/User/workspaceStorage"

# Create or overwrite the CSV file with headers
echo "workspaceID,workspaceTitle,workspaceCodePath,workspaceSizeMb,workspaceTabsN,comment" > "$STATS_FILE"

# Check if export directory exists
if [ ! -d "$EXPORT_DIR" ]; then
    echo "Error: Export directory not found!"
    exit 1
fi

# Process each workspace directory
for workspace_dir in "$EXPORT_DIR"/workspace-*; do
    # Skip if no matching directories
    [ -d "$workspace_dir" ] || continue
    
    # Extract workspace ID from directory name
    workspace_id=$(basename "$workspace_dir" | sed 's/workspace-//')
    
    # Get workspace info from workspace.json if it exists
    workspace_json="${WORKSPACE_BASE}/${workspace_id}/workspace.json"
    if [ -f "$workspace_json" ]; then
        # Extract folder path from workspace.json
        workspace_path=$(grep -o '"folder": *"[^"]*"' "$workspace_json" | cut -d'"' -f4 | sed 's|file://||')
        # Extract title (last part of the path)
        workspace_title=$(basename "$workspace_path")
    else
        workspace_path=""
        workspace_title=""
    fi
    
    # Calculate directory size in KB
    size_kb=$(du -sk "$workspace_dir" | cut -f1)
    
    # Count number of tab files (*.md files)
    tabs_count=$(find "$workspace_dir" -name "*.md" | wc -l)
    
    # Write to CSV
    echo "${workspace_id},${workspace_title},${workspace_path},${size_kb},${tabs_count}," >> "$STATS_FILE"
done

echo "Statistics have been written to: $STATS_FILE"