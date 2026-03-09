#!/usr/bin/env bash
set -euo pipefail

DB_URL="${AUDIOBOOK_DATABASE_URL:-postgresql://audiobook:audiobook123@localhost:5432/audiobook_manager}"
MIGRATION_FILE="${1:-database/migrations/0001_sprint1_foundations.sql}"

if [[ ! -f "$MIGRATION_FILE" ]]; then
  echo "Migration file not found: $MIGRATION_FILE" >&2
  exit 1
fi

psql "$DB_URL" -v ON_ERROR_STOP=1 -f "$MIGRATION_FILE"
echo "Sprint 1 bootstrap completed with $MIGRATION_FILE"
