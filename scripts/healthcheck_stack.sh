#!/usr/bin/env bash
# =============================================================================
# AILinkCinema — Data Stack Health Check
# =============================================================================
# Checks PostgreSQL, Redis (optional), and Qdrant.
# =============================================================================

set -euo pipefail
cd "$(dirname "$0")/.."

FAIL=0
HAS_WARN=0

# ── helpers ──────────────────────────────────────────────────────────────
pass() { echo "  PASS  $1"; }
warn() { echo "  WARN  $1"; HAS_WARN=1; }
fail() { echo "  FAIL  $1"; FAIL=1; }

container_health() {
    local name="$1" label="$2"
    local inspect
    inspect="$(docker inspect --format='{{.State.Health.Status}}' "$name" 2>/dev/null)" || return 1
    case "$inspect" in
        healthy)   pass "$label"; return 0 ;;
        unhealthy) fail "$label — container unhealthy"; return 0 ;;
        starting)  warn "$label — container still starting"; return 0 ;;
        "")        return 1 ;;  # no healthcheck defined
        *)         warn "$label — status: $inspect"; return 0 ;;
    esac
}

# ── 1. PostgreSQL ────────────────────────────────────────────────────────
echo "--- PostgreSQL ---"
if container_health ailinkcinema_postgres "postgres"; then
    : # ok from container
elif command -v pg_isready &>/dev/null; then
    pg_isready -h 127.0.0.1 -p "${POSTGRES_PORT:-5432}" -q 2>/dev/null && \
        pass "postgres (pg_isready)" || \
        warn "postgres not reachable via pg_isready"
else
    warn "postgres — no container and no pg_isready"
fi

# ── 2. Redis (optional) ──────────────────────────────────────────────────
echo "--- Redis ---"
if container_health ailinkcinema_redis "redis"; then
    : # ok from container
elif command -v redis-cli &>/dev/null; then
    redis-cli -p "${REDIS_PORT:-6379}" ping 2>/dev/null | grep -q "PONG" && \
        pass "redis (redis-cli)" || \
        warn "redis not reachable (optional)"
else
    warn "redis not reachable (optional)"
fi

# ── 3. Qdrant ────────────────────────────────────────────────────────────
echo "--- Qdrant ---"
if container_health ailinkcinema_qdrant "qdrant"; then
    : # ok from container
elif command -v curl &>/dev/null; then
    qport="${QDRANT_PORT:-6333}"
    if curl -sf "http://127.0.0.1:${qport}/collections" >/dev/null 2>&1; then
        pass "qdrant (HTTP)"
    elif curl -sf "http://127.0.0.1:${qport}/health" >/dev/null 2>&1; then
        pass "qdrant (HTTP health)"
    else
        warn "qdrant not reachable (optional)"
    fi
else
    warn "qdrant — no container and no curl"
fi

# ── Summary ──────────────────────────────────────────────────────────────
echo "=============================="
if [ "$FAIL" -eq 1 ]; then
    echo "RESULT: FAIL  — some services are unhealthy"
    exit 1
elif [ "$HAS_WARN" -eq 1 ]; then
    echo "RESULT: WARN  — some services are unavailable (may be optional)"
    exit 0
else
    echo "RESULT: PASS  — all services healthy"
    exit 0
fi
