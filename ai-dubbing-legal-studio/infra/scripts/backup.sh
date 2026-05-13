#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="./infra/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"

echo "=== Backup $TIMESTAMP ==="

docker compose exec -T postgres pg_dump -U dubbing dubbing_legal > "$BACKUP_DIR/db_$TIMESTAMP.sql"
echo "DB backup: $BACKUP_DIR/db_$TIMESTAMP.sql"

echo "=== Backup complete ==="
