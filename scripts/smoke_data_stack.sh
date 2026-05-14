#!/usr/bin/env bash
# =============================================================================
# AILinkCinema — Data Stack Smoke Test
# =============================================================================
# Usage:
#   ./scripts/smoke_data_stack.sh          — run smoke test and cleanup
#   ./scripts/smoke_data_stack.sh --keep   — keep stack running after success
#   ./scripts/smoke_data_stack.sh --help   — show this help
# =============================================================================

set -euo pipefail
cd "$(dirname "$0")/.."

COMPOSE_BASE="-f compose.base.yml -f compose.data.yml"
KEEP_STACK=0
STARTED_STACK=0

usage() {
    head -20 "$0" | grep '^#   \./' | sed 's/^#   //'
}

cleanup() {
    if [ "$STARTED_STACK" -eq 1 ] && [ "$KEEP_STACK" -eq 0 ]; then
        echo ">> Cleaning up smoke stack ..."
        POSTGRES_PASSWORD="smoke-test-password" docker compose $COMPOSE_BASE \
            --profile with-postgres \
            --profile with-qdrant \
            --profile with-redis \
            down
    fi
}

wait_postgres() {
    echo ">> Waiting for PostgreSQL ..."
    local i
    for i in $(seq 1 30); do
        if docker exec ailinkcinema_postgres pg_isready -U "${POSTGRES_USER:-ailinkcinema}" -d "${POSTGRES_DB:-ailinkcinema}" >/dev/null 2>&1; then
            echo "   PostgreSQL ready"
            return 0
        fi
        sleep 2
    done
    echo "ERROR: PostgreSQL did not become ready in time."
    return 1
}

wait_qdrant() {
    echo ">> Waiting for Qdrant ..."
    local i
    local qport="${QDRANT_PORT:-6333}"
    for i in $(seq 1 30); do
        if curl -sf "http://127.0.0.1:${qport}/collections" >/dev/null 2>&1; then
            echo "   Qdrant ready"
            return 0
        fi
        sleep 2
    done
    echo "ERROR: Qdrant did not become ready in time."
    return 1
}

wait_redis() {
    echo ">> Waiting for Redis ..."
    local i
    for i in $(seq 1 30); do
        if docker exec ailinkcinema_redis redis-cli ping >/dev/null 2>&1; then
            echo "   Redis ready"
            return 0
        fi
        sleep 2
    done
    echo "ERROR: Redis did not become ready in time."
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

echo ">> Starting data stack for smoke test ..."
POSTGRES_PASSWORD="smoke-test-password" docker compose $COMPOSE_BASE \
    --profile with-postgres \
    --profile with-qdrant \
    --profile with-redis \
    up -d postgres qdrant redis
STARTED_STACK=1

wait_postgres
wait_qdrant
wait_redis

echo ">> Smoke test passed: PostgreSQL + Qdrant + Redis are reachable."

if [ "$KEEP_STACK" -eq 1 ]; then
    echo ">> --keep enabled. Stack remains running."
    echo "   To stop it manually:"
    echo "   POSTGRES_PASSWORD=smoke-test-password docker compose $COMPOSE_BASE --profile with-postgres --profile with-qdrant --profile with-redis down"
fi
