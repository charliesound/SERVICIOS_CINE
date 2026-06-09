#!/usr/bin/env bash
# guard_no_sqlite_regressions.sh
# Scans staged or working-tree diffs for new SQLite introductions outside the allowlist.
# Run from repo root. Does not delete or modify anything.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO_ROOT"

# --- Determine diff source ---
if git diff --cached --quiet 2>/dev/null; then
  DIFF_SRC="working tree"
  DIFF_CMD="git diff"
else
  DIFF_SRC="staged"
  DIFF_CMD="git diff --cached"
fi

# --- Collect diff lines ---
DIFF_LINES=$($DIFF_CMD)

if [ -z "$DIFF_LINES" ]; then
  echo "[guard_no_sqlite_regressions] PASS: no changes to scan."
  exit 0
fi

# --- Allowlist: files where SQLite mentions are permitted ---
ALLOWLIST=(
  "docs/architecture/cid_postgresql_only_policy_v1.md"
  "docs/architecture/cid_database_canonical_policy_v1.md"
  "scripts/dev/guard_no_sqlite_regressions.sh"
  "scripts/db/migrate_sqlite_to_postgres_cid.py"
)

is_allowlisted() {
  local file="$1"
  for allowed in "${ALLOWLIST[@]}"; do
    if [ "$file" = "$allowed" ]; then
      return 0
    fi
  done
  case "$file" in
    docs/validation/*|docs/fase*) return 0 ;;
  esac
  return 1
}

# --- Skip patterns for generated/vendored dirs ---
SKIP_PATTERN='(__pycache__|node_modules|\.pytest_cache|\.venv|backups)/'

# --- Patterns to detect in added lines ---
PATTERNS=(
  'sqlite'
  'SQLite'
  'aiosqlite'
  'sqlite://'
  'sqlite+aiosqlite'
  '_is_sqlite'
  'IS_SQLITE'
  'SQLITE_LEGACY_BOOTSTRAP'
)

# --- Scan ---
VIOLATIONS=()
CURRENT_FILE=""

while IFS= read -r line; do
  # Extract file path from diff headers (these lines don't start with +)
  if [[ "$line" =~ ^diff\ --git\ a/(.*)\ b/(.*) ]]; then
    CURRENT_FILE="${BASH_REMATCH[2]}"
    continue
  elif [[ "$line" =~ ^---\ a/(.*) ]]; then
    continue
  elif [[ "$line" =~ ^\+\+\+\ b/(.*) ]]; then
    # +++ line marks the start of added content for this file
    # Skip pattern check on this line itself
    continue
  elif [[ "$line" =~ ^@@ ]]; then
    continue
  fi

  # Only scan lines that start with + (added content)
  if [[ ! "$line" =~ ^\+ ]]; then
    continue
  fi

  # Skip if file is allowlisted
  if [ -n "${CURRENT_FILE:-}" ] && is_allowlisted "$CURRENT_FILE"; then
    continue
  fi

  # Skip generated/vendored dirs
  if [ -n "${CURRENT_FILE:-}" ] && echo "$CURRENT_FILE" | grep -qE "$SKIP_PATTERN"; then
    continue
  fi

  # Check added line against patterns
  CONTENT="${line:1}"
  for pattern in "${PATTERNS[@]}"; do
    if echo "$CONTENT" | grep -qiE "$pattern"; then
      VIOLATIONS+=("[$DIFF_SRC] $CURRENT_FILE: $line")
      break
    fi
  done

done <<< "$DIFF_LINES"

# --- Report ---
if [ ${#VIOLATIONS[@]} -gt 0 ]; then
  echo ""
  echo "================================================================"
  echo " GUARD FAIL: SQLite regression detected in $DIFF_SRC diff"
  echo "================================================================"
  echo ""
  for v in "${VIOLATIONS[@]}"; do
    echo "  $v"
  done
  echo ""
  echo "Policy: docs/architecture/cid_postgresql_only_policy_v1.md"
  echo "PostgreSQL is the only allowed backend for new CID SaaS phases."
  echo ""
  echo "If this is intentional (e.g., legacy quarantine, migration script,"
  echo "or policy doc), add the file to the allowlist in this script."
  echo ""
  exit 1
fi

echo "[guard_no_sqlite_regressions] PASS: no SQLite regressions in $DIFF_SRC diff."
exit 0
