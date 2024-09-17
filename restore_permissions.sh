#!/bin/bash

# Check if a directory is passed as an argument
if [ -z "$1" ]; then
  echo "Usage: $0 <directory>"
  exit 1
fi

TARGET_DIR="$1"

# Restore permissions for the passed directory itself
chmod 755 "$TARGET_DIR"

# Restore directory and file permissions recursively
find "$TARGET_DIR" -type d -exec chmod 755 {} \;
find "$TARGET_DIR" -type f -exec chmod 644 {} \;

echo "Permissions restored successfully."
