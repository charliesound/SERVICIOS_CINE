#!/usr/bin/env bash
# guard_wsl_repo.sh — CID pre-commit safety guard
# Checks: WSL execution, repo path, nested copy, git status, staged secrets
set -uo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
FAIL=0

echo ""
echo "=== CID GUARD: WSL + Repo + Secrets Check ==="
echo ""

# --- 1. PWD check ---
echo "--- [1] PWD check ---"
if [ "$(pwd)" != "/opt/SERVICIOS_CINE" ]; then
    echo -e "${RED}FAIL: pwd is $(pwd), expected /opt/SERVICIOS_CINE${NC}"
    FAIL=1
else
    echo -e "${GREEN}PASS: pwd = /opt/SERVICIOS_CINE${NC}"
fi

# --- 2. Windows path detection ---
echo "--- [2] Windows path detection ---"
case "$(pwd)" in
    */mnt/c/*|/mnt/c/*|C:*|*wsl.localhost*)
        echo -e "${RED}FAIL: detected Windows/UNC path in pwd${NC}"
        FAIL=1
        ;;
    *)
        echo -e "${GREEN}PASS: no Windows path in pwd${NC}"
        ;;
esac

EXTRA_CHECK=$(echo "$(pwd)" | grep -iE '^/mnt/[a-z]|^[A-Z]:|wsl\.localhost' || true)
if [ -n "$EXTRA_CHECK" ]; then
    echo -e "${RED}FAIL: detected Windows mount in pwd: $EXTRA_CHECK${NC}"
    FAIL=1
fi

# --- 3. Nested copy ---
echo "--- [3] Nested copy check ---"
if [ -d /opt/SERVICIOS_CINE/opt ]; then
    echo -e "${RED}FAIL: /opt/SERVICIOS_CINE/opt exists (nested copy)${NC}"
    FAIL=1
else
    echo -e "${GREEN}PASS: no nested copy${NC}"
fi

# --- 4. Git status ---
echo "--- [4] Git status ---"
git status --short --untracked-files=all
echo ""

# --- 5. .env staged? ---
echo "--- [5] .env staged check ---"
STAGED_DOTENV=$(git diff --cached --name-only | grep -E '^\.env$|^\.env\.local$' || true)
if [ -n "$STAGED_DOTENV" ]; then
    echo -e "${RED}FAIL: .env file is STAGED:${NC}"
    echo "$STAGED_DOTENV"
    FAIL=1
else
    echo -e "${GREEN}PASS: .env not staged${NC}"
fi

# --- 6. *.db / *.sqlite / *.sqlite3 staged? ---
echo "--- [6] DB file staged check ---"
STAGED_DB=$(git diff --cached --name-only | grep -E '\.db$|\.sqlite$|\.sqlite3$' || true)
if [ -n "$STAGED_DB" ]; then
    echo -e "${RED}FAIL: DB files are STAGED:${NC}"
    echo "$STAGED_DB"
    FAIL=1
else
    echo -e "${GREEN}PASS: no DB files staged${NC}"
fi

# --- 7. Sensitive JSON files staged? ---
echo "--- [7] Sensitive JSON staged check ---"
STAGED_JSON=$(git diff --cached --name-only | grep -iE '.*(export|inventory|credentials|secret).*\.json$' || true)
if [ -n "$STAGED_JSON" ]; then
    echo -e "${RED}FAIL: potential sensitive JSON files are STAGED:${NC}"
    echo "$STAGED_JSON"
    FAIL=1
else
    echo -e "${GREEN}PASS: no sensitive JSON files staged${NC}"
fi

# --- 8. Sensitive patterns in staged diff (outside policy dirs) ---
echo "--- [8] Staged diff sensitive pattern check ---"
SENSITIVE_PATTERNS="DATABASE_URL|SECRET_KEY|AUTH_SECRET|POSTGRES_PASSWORD|GOOGLE_DRIVE_CLIENT_SECRET|N8N_ENCRYPTION_KEY|OPENAI_API_KEY|ANTHROPIC_API_KEY|TOKEN|PASSWORD|PRIVATE_KEY"
ALLOWED_DIRS="^docs/ops/|^docs/architecture/|^docs/business/|^directivas/"
HAS_FAIL=0

# Get list of staged files (excluding deleted)
STAGED_FILES=$(git diff --cached --diff-filter=ACMRT --name-only 2>/dev/null || true)
for f in $STAGED_FILES; do
    # Check if file is in an allowed policy directory
    if echo "$f" | grep -qiE "$ALLOWED_DIRS"; then
        # File is in policy dir — skip (allowed to reference secret variable names)
        continue
    fi
    # Check diff for sensitive patterns
    MATCHES=$(git diff --cached 2>/dev/null -- "$f" | grep -iE "$SENSITIVE_PATTERNS" | grep -v "^[+-]{3}" | grep -v "^[+-]import" | grep -v "^[+-]from" | grep -v 'SENSITIVE_PATTERNS=' | head -10 || true)
    if [ -n "$MATCHES" ]; then
        echo -e "${RED}FAIL: sensitive pattern found in $f:${NC}"
        echo "$MATCHES"
        HAS_FAIL=1
    fi
done

if [ "$HAS_FAIL" -eq 1 ]; then
    FAIL=1
else
    echo -e "${GREEN}PASS: no sensitive patterns in staged diff outside policy dirs${NC}"
fi

echo ""
# --- Summary ---
if [ "$FAIL" -ne 0 ]; then
    echo -e "${RED}=== GUARD FAILED: $FAIL check(s) failed ===${NC}"
    exit 1
else
    echo -e "${GREEN}=== GUARD PASSED: all checks OK ===${NC}"
    exit 0
fi
