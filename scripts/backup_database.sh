#!/bin/sh
set -eu

required_vars="DATABASE_HOST DATABASE_NAME DATABASE_USER PGPASSWORD BACKUP_DIR"
for variable in $required_vars; do
  eval "value=\${$variable:-}"
  [ -n "$value" ] || { echo "Missing required environment variable: $variable" >&2; exit 1; }
done

mkdir -p "$BACKUP_DIR"
stamp=$(date -u +%Y%m%dT%H%M%SZ)
backup="$BACKUP_DIR/postgres-$stamp.sql.gz"
pg_dump --host="$DATABASE_HOST" --dbname="$DATABASE_NAME" --username="$DATABASE_USER" --format=plain --no-owner | gzip -9 > "$backup"
echo "Created encrypted-storage-compatible backup: $backup"
