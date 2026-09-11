#!/bin/bash
set -euo pipefail

if [ -z "${1:-}" ]; then
  echo "Usage: $0 <directory>" >&2
  exit 1
fi

TARGET_DIR="$1"

if [ ! -e "$TARGET_DIR" ]; then
  echo "Error: '$TARGET_DIR' does not exist." >&2
  exit 1
fi

if [ ! -d "$TARGET_DIR" ]; then
  echo "Error: '$TARGET_DIR' is not a directory." >&2
  exit 1
fi

# Restore permissions for the passed directory itself
chmod 755 "$TARGET_DIR"

# Restore directory and file permissions recursively.
# chmod failures abort the script via `set -e`, so the success message
# below is only reached if every file and directory was handled.
find "$TARGET_DIR" -type d -exec chmod 755 {} +
find "$TARGET_DIR" -type f -exec chmod 644 {} +

echo "Permissions restored successfully."