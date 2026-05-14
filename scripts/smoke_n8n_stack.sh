#!/usr/bin/env bash
# =============================================================================
# AILinkCinema — n8n Stack Smoke Test
# =============================================================================
# Usage:
#   ./scripts/smoke_n8n_stack.sh          — run smoke test and cleanup
#   ./scripts/smoke_n8n_stack.sh --keep   — keep stack running after success
#   ./scripts/smoke_n8n_stack.sh --help   — show this help
# =============================================================================

set -euo pipefail
cd "$(dirname "$0")/.."

COMPOSE_N8N="-f compose.base.yml -f compose.data.yml -f compose.n8n.yml"
KEEP_STACK=0
STARTED_STACK=0

usage() {
    head -20 "$0" | grep '^#   \./' | sed 's/^#   //'
}

cleanup() {
    if [ "$STARTED_STACK" -eq 1 ] && [ "$KEEP_STACK" -eq 0 ]; then
        echo ">> Cleaning up n8n smoke stack ..."
        POSTGRES_USER="ailinkcinema" \
        POSTGRES_PASSWORD="smoke-test-password" \
        POSTGRES_DB="ailinkcinema" \
        N8N_ENCRYPTION_KEY="smoke-test-key-12345678901234567890123456789012" \
        N8N_DB_TABLE_PREFIX="n8n_smoke_" \
        N8N_PORT="5678" \
        docker compose $COMPOSE_N8N \
            --profile with-postgres \
            --profile with-n8n \
            down
    fi
}

wait_postgres() {
    echo ">> Waiting for PostgreSQL ..."
    local i
    for i in $(seq 1 30); do
        if docker exec ailinkcinema_postgres pg_isready -U "ailinkcinema" -d "ailinkcinema" >/dev/null 2>&1; then
            echo "   PostgreSQL ready"
            return 0
        fi
        sleep 2
    done
    echo "ERROR: PostgreSQL did not become ready in time."
    return 1
}

wait_n8n() {
    echo ">> Waiting for n8n ..."
    local i
    local n8n_port="5678"
    for i in $(seq 1 45); do
        if curl -sf "http://127.0.0.1:${n8n_port}/healthz" >/dev/null 2>&1; then
            echo "   n8n ready (/healthz)"
            return 0
        fi
        if curl -sf "http://127.0.0.1:${n8n_port}/" >/dev/null 2>&1; then
            echo "   n8n ready (/ fallback)"
            return 0
        fi
        sleep 2
    done
    echo "ERROR: n8n did not become reachable in time."
    return 1
}

while [ "$#" -gt 0 ]; do
    case "$1" in
        --help|-h)
            usage
            exit 0
            ;;
        --keep)
            KEEP_STACK=1
            shift
            ;;
        *)
            echo "Unknown argument: $1"
            usage
            exit 1
            ;;
    esac
done

trap cleanup EXIT

echo ">> Starting PostgreSQL + n8n for smoke test ..."
POSTGRES_USER="ailinkcinema" \
POSTGRES_PASSWORD="smoke-test-password" \
POSTGRES_DB="ailinkcinema" \
N8N_ENCRYPTION_KEY="smoke-test-key-12345678901234567890123456789012" \
N8N_DB_TABLE_PREFIX="n8n_smoke_" \
N8N_PORT="5678" \
docker compose $COMPOSE_N8N \
    --profile with-postgres \
    --profile with-n8n \
    up -d postgres n8n
STARTED_STACK=1

wait_postgres
wait_n8n

echo ">> Smoke test passed: PostgreSQL + n8n are reachable."

if [ "$KEEP_STACK" -eq 1 ]; then
    echo ">> --keep enabled. Stack remains running."
    echo "   To stop it manually:"
    echo "   Export POSTGRES_PASSWORD and N8N_ENCRYPTION_KEY, then run:"
    echo "   docker compose $COMPOSE_N8N --profile with-postgres --profile with-n8n down"
fi
