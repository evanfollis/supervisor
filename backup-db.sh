#!/bin/bash
# Nightly PostgreSQL backup — keeps last 7 days
BACKUP_DIR=/opt/backups
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/mentor_$TIMESTAMP.sql.gz"

docker exec mentor-db-1 pg_dump -U mentor mentor | gzip > "$BACKUP_FILE"

# Keep only last 7 backups
ls -tp "$BACKUP_DIR"/mentor_*.sql.gz | tail -n +8 | xargs -I {} rm -- {} 2>/dev/null

echo "Backup created: $BACKUP_FILE ($(du -h "$BACKUP_FILE" | cut -f1))"
