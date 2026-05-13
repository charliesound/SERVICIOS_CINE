#!/usr/bin/env bash
set -euo pipefail

BACKUP_FILE="${1:-}"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file.sql>"
    exit 1
fi

echo "Restoring from $BACKUP_FILE..."
cat "$BACKUP_FILE" | docker compose exec -T postgres psql -U dubbing dubbing_legal
echo "Restore complete."
