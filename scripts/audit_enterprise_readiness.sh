#!/usr/bin/env bash
set -euo pipefail

# Enterprise Readiness Audit — CID Budget Estimator
# Usage: from repo root: bash scripts/audit_enterprise_readiness.sh

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'
PASS=0; FAIL=0; WARN=0
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPORT="audit_report_$(date +%Y%m%d_%H%M%S).log"
exec > >(tee -a "$REPORT") 2>&1

echo "============================================"
echo " Enterprise Readiness Audit"
echo " Date: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo " Repo: $(basename "$ROOT")"
echo "============================================"; echo ""

check() {
    local desc="$1"; local cmd="$2"; local severity="${3:-WARN}"
    echo -n "  [ ] $desc ... "
    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC}"; PASS=$((PASS + 1))
    else
        if [ "$severity" = "FAIL" ]; then
            echo -e "${RED}FAIL${NC}"; FAIL=$((FAIL + 1))
        else
            echo -e "${YELLOW}WARN${NC}"; WARN=$((WARN + 1))
        fi
    fi
}
heading() { echo ""; echo "─── $1 ───"; }

# ─── 1. COMPILATION ─────────────────────────────────────
heading "1. COMPILATION & SYNTAX"
check "Python compilation (cid-budget)" "python -m compileall '$ROOT/cid-budget/backend/' -q" "FAIL"
check "Python compilation (app_registry)" "python -m compileall '$ROOT/src/services/app_registry.py' '$ROOT/src/routes/app_registry_routes.py' -q" "FAIL"

# ─── 2. TESTS ────────────────────────────────────────────
heading "2. TESTS"
check "Test suite (13 tests)" "cd '$ROOT/cid-budget' && python -m pytest tests/ -q --tb=line 2>&1 | tail -1 | grep -q 'passed$'" "FAIL"

# ─── 3. ALEMBIC ──────────────────────────────────────────
heading "3. ALEMBIC MIGRATIONS"
check "alembic.ini exists" "test -f '$ROOT/cid-budget/backend/alembic.ini'" "FAIL"
check "Migration files exist" "ls '$ROOT/cid-budget/backend/alembic/versions/'*.py 2>/dev/null | head -1 | grep -q '.py$'" "FAIL"
check "env.py syntax" "python -m py_compile '$ROOT/cid-budget/backend/alembic/env.py'" "FAIL"

# ─── 4. DOCKER ───────────────────────────────────────────
heading "4. DOCKER"
check "Dockerfile exists" "test -f '$ROOT/cid-budget/backend/Dockerfile'" "FAIL"
check "Dockerfile has EXPOSE" "grep -q 'EXPOSE' '$ROOT/cid-budget/backend/Dockerfile'" "FAIL"
check "Dockerfile has non-root USER" "grep -q '^USER' '$ROOT/cid-budget/backend/Dockerfile'" "WARN"
check "Dockerfile has HEALTHCHECK" "grep -q HEALTHCHECK '$ROOT/cid-budget/backend/Dockerfile'" "WARN"
check "Frontend nginx security headers" "grep -q 'X-Frame-Options\|CSP\|HSTS' '$ROOT/cid-budget/frontend/Dockerfile'" "WARN"
check "Compose PG healthcheck" "grep -q pg_isready '$ROOT/cid-budget/docker-compose.yml'" "FAIL"
check "Compose API healthcheck" "grep -q 'healthcheck:' '$ROOT/cid-budget/docker-compose.yml'" "FAIL"

# ─── 5. CONFIGURATION ────────────────────────────────────
heading "5. CONFIGURATION & SECURITY"
check "No Pydantic BaseSettings" "grep -q BaseSettings '$ROOT/cid-budget/backend/app/core.py' 2>/dev/null; test \$? -eq 1" "WARN"
check "JWT has ExpiredSignatureError" "grep -q ExpiredSignatureError '$ROOT/cid-budget/backend/app/core.py'" "FAIL"
check "No bare except:pass" "grep -rn 'except\s*:\s*pass' '$ROOT/cid-budget/backend/app/' --include='*.py' 2>/dev/null | grep -v test; test \$? -eq 1" "WARN"
check "No broad except Exception in main" "grep -n 'except Exception' '$ROOT/cid-budget/backend/app/main.py' | grep -v 'logger\|raise'; test \$? -eq 1" "WARN"

# ─── 6. ROUTES & AUTH ────────────────────────────────────
heading "6. ROUTES & AUTH"
check "No duplicate routes" "grep -n '@router\.\(get\|post\)' '$ROOT/cid-budget/backend/app/routes.py' | cut -d'@' -f2- | sort | uniq -d | wc -l | grep -q '^0$'" "FAIL"

echo ""
cd "$ROOT/cid-budget/backend" && python -c "
import sys; sys.path.insert(0,'.');
from app.main import app;
routes = [r for r in app.routes if hasattr(r,'methods')]
api = [r for r in routes if '/api/' in str(r.path)]
print(f'  Total routes: {len(routes)}, API: {len(api)}')
for r in routes:
    if hasattr(r,'methods') and '/api/' in str(r.path):
        ms = ','.join(sorted(r.methods - {'HEAD'}) or ['?'])
        print(f'    {ms:8s} {r.path}')
"

# ─── 7. FRONTEND ─────────────────────────────────────────
heading "7. FRONTEND"
check "package.json" "test -f '$ROOT/cid-budget/frontend/package.json'" "FAIL"
check "VITE_API_URL build arg" "grep -q VITE_API_URL '$ROOT/cid-budget/frontend/Dockerfile'" "FAIL"
check "nginx gzip enabled" "grep -q gzip '$ROOT/cid-budget/frontend/Dockerfile'" "WARN"

# ─── 8. DATABASE ─────────────────────────────────────────
heading "8. DATABASE"
check "created_at/updated_at" "grep -q created_at '$ROOT/cid-budget/backend/app/models.py'" "FAIL"
check "organization_id column" "grep -q organization_id '$ROOT/cid-budget/backend/app/models.py'" "FAIL"
check "org_id nullable (should be False)" "grep -q 'nullable=False' '$ROOT/cid-budget/backend/app/models.py' && grep 'organization_id' '$ROOT/cid-budget/backend/app/models.py' | grep -q 'nullable=True'; test \$? -eq 1" "WARN"
check "FK constraint on line_items" "grep -q ForeignKey '$ROOT/cid-budget/backend/app/models.py' 2>/dev/null; test \$? -eq 1" "WARN"

# ─── 9. CID APP REGISTRY ────────────────────────────────
heading "9. CID APP REGISTRY"
check "async httpx client" "grep -q 'httpx.AsyncClient' '$ROOT/src/services/app_registry.py'" "FAIL"
check "async routes" "grep -q 'async def' '$ROOT/src/routes/app_registry_routes.py'" "FAIL"
check "startup await load_all()" "grep -q 'await load_all()' '$ROOT/src/app.py'" "FAIL"
check "refresh endpoint" "grep -q refresh '$ROOT/src/routes/app_registry_routes.py'" "FAIL"

# ─── SUMMARY ─────────────────────────────────────────────
heading "SUMMARY"
TOTAL=$((PASS + FAIL + WARN))
echo ""
echo "  PASSED:  $PASS/$TOTAL"
echo "  FAILED:  $FAIL/$TOTAL  (blocking)"
echo "  WARN:    $WARN/$TOTAL  (advisory)"
echo ""
if [ "$FAIL" -gt 0 ]; then
    echo -e "${RED}❌ NO-GO for production${NC}"
    echo "    $FAIL blocking issues — see docs/enterprise_audit.md"
    exit 1
elif [ "$WARN" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  CONDITIONAL GO${NC}"
    exit 0
else
    echo -e "${GREEN}✅ GO for production${NC}"
    exit 0
fi
