#!/bin/bash

# Define paths
EXPORT_DIR="_outputs/workspaces_export"
STATS_FILE="${EXPORT_DIR}/workspaces_statistic.csv"

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
    
    # Calculate directory size in MB (rounded to 2 decimal places)
    size_mb=$(du -sm "$workspace_dir" | cut -f1)
    
    # Count number of tab files (*.md files)
    tabs_count=$(find "$workspace_dir" -name "*.md" | wc -l)
    
    # Write to CSV (with empty fields for title, codepath, and comment)
    echo "${workspace_id},,,,${size_mb},${tabs_count}," >> "$STATS_FILE"
done

echo "Statistics have been written to: $STATS_FILE"