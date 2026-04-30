#!/usr/bin/env bash
set -euo pipefail

echo "=== DB Commit Guard ==="

BLOCKED=0

echo "--- Checking staged ailinkcinema_s2.db ---"
if git diff --cached --name-only | grep -qx 'ailinkcinema_s2.db'; then
  echo "BLOCKED: ailinkcinema_s2.db esta staged. No debe entrar en commit."
  BLOCKED=1
else
  echo "PASS: ailinkcinema_s2.db no esta staged."
fi

echo "--- Checking working-tree ailinkcinema_s2.db ---"
if git status --short -- ailinkcinema_s2.db | grep -q '^ M\|^M '; then
  echo "WARN: ailinkcinema_s2.db esta modificado localmente. Estado permitido solo para runtime local, no para commit."
else
  echo "PASS: ailinkcinema_s2.db no aparece modificado."
fi

echo "--- Checking staged DB files ---"
STAGED_DBS="$(git diff --cached --name-only | grep -E '\.db$' || true)"

if [ -n "$STAGED_DBS" ]; then
  while IFS= read -r DB; do
    case "$DB" in
      OLD/sensitive_review/db_snapshots/*)
        echo "INFO: DB staged dentro de snapshot sensible: $DB"
        ;;
      *)
        echo "BLOCKED: DB staged fuera de snapshot sensible: $DB"
        BLOCKED=1
        ;;
    esac
  done <<< "$STAGED_DBS"
fi

if [ "$BLOCKED" -ne 0 ]; then
  echo "RESULT: BLOCKED"
  exit 1
fi

echo "RESULT: PASS"
