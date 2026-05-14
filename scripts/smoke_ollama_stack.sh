#!/usr/bin/env bash
# =============================================================================
# AILinkCinema — Ollama Stack Smoke Test (CPU)
# =============================================================================
# Usage:
#   ./scripts/smoke_ollama_stack.sh          — run smoke test and cleanup
#   ./scripts/smoke_ollama_stack.sh --keep   — keep stack running after success
#   ./scripts/smoke_ollama_stack.sh --help   — show this help
# =============================================================================

set -euo pipefail
cd "$(dirname "$0")/.."

COMPOSE_OLLAMA="-f compose.base.yml -f compose.ollama.yml"
KEEP_STACK=0
STARTED_STACK=0

usage() {
    head -20 "$0" | grep '^#   \./' | sed 's/^#   //'
}

cleanup() {
    if [ "$STARTED_STACK" -eq 1 ] && [ "$KEEP_STACK" -eq 0 ]; then
        echo ">> Cleaning up Ollama smoke stack ..."
        docker compose $COMPOSE_OLLAMA \
            --profile with-ollama \
            down
    fi
}

wait_ollama() {
    echo ">> Waiting for Ollama API ..."
    local i
    local oport="${OLLAMA_PORT:-11434}"
    for i in $(seq 1 45); do
        if curl -sf "http://127.0.0.1:${oport}/api/tags" >/dev/null 2>&1; then
            echo "   Ollama ready"
            return 0
        fi
        sleep 2
    done
    echo "ERROR: Ollama did not become reachable in time."
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

echo ">> Starting Ollama (CPU) for smoke test ..."
docker compose $COMPOSE_OLLAMA \
    --profile with-ollama \
    up -d ollama
STARTED_STACK=1

wait_ollama

if [ -n "${OLLAMA_SMOKE_MODEL:-}" ]; then
    echo ">> OLLAMA_SMOKE_MODEL defined. Pulling requested model ..."
    docker exec ailinkcinema_ollama ollama pull "$OLLAMA_SMOKE_MODEL"
fi

echo ">> Smoke test passed: Ollama API is reachable."

if [ "$KEEP_STACK" -eq 1 ]; then
    echo ">> --keep enabled. Stack remains running."
    echo "   To stop it manually:"
    echo "   docker compose $COMPOSE_OLLAMA --profile with-ollama down"
fi
