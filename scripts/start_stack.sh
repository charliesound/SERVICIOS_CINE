#!/usr/bin/env bash
# =============================================================================
# AILinkCinema — Data Stack Launcher
# =============================================================================
# Usage:
#   ./scripts/start_stack.sh help              — show this help
#   ./scripts/start_stack.sh data              — PostgreSQL + Qdrant
#   ./scripts/start_stack.sh data-full         — PostgreSQL + Qdrant + Redis
#   ./scripts/start_stack.sh docker-data       — alias for data
#   ./scripts/start_stack.sh docker-data-full  — alias for data-full
#   ./scripts/start_stack.sh status            — run healthcheck
# =============================================================================

set -euo pipefail
cd "$(dirname "$0")/.."

COMPOSE_BASE="-f compose.base.yml -f compose.data.yml"
SCRIPT_NAME="$(basename "$0")"

# ── helpers ──────────────────────────────────────────────────────────────
usage() {
    head -20 "$0" | grep '^#   \./' | sed 's/^#   //'
    exit 0
}

require_env_password() {
    local pw="${POSTGRES_PASSWORD:-}"
    if [ -z "$pw" ] && [ -f .env ]; then
        pw="$(grep -E '^POSTGRES_PASSWORD=' .env | head -1 | cut -d= -f2-)"
    fi
    if [ -z "$pw" ]; then
        echo "ERROR: POSTGRES_PASSWORD is not set."
        echo "  Set it via environment or add to .env:"
        echo "    cp .env.example .env"
        echo "  Then edit .env and set POSTGRES_PASSWORD."
        exit 1
    fi
    echo "$pw"
}

# ── commands ─────────────────────────────────────────────────────────────
cmd_data() {
    local pw; pw="$(require_env_password)"
    export POSTGRES_PASSWORD="$pw"
    echo ">> Starting PostgreSQL + Qdrant ..."
    docker compose $COMPOSE_BASE \
        --profile with-postgres \
        --profile with-qdrant \
        up -d postgres qdrant
    echo ">> Done. Run healthcheck:"
    echo "    ./scripts/healthcheck_stack.sh"
}

cmd_data_full() {
    local pw; pw="$(require_env_password)"
    export POSTGRES_PASSWORD="$pw"
    echo ">> Starting PostgreSQL + Qdrant + Redis ..."
    docker compose $COMPOSE_BASE \
        --profile with-postgres \
        --profile with-qdrant \
        --profile with-redis \
        up -d postgres qdrant redis
    echo ">> Done. Run healthcheck:"
    echo "    ./scripts/healthcheck_stack.sh"
}

cmd_status() {
    if [ -x scripts/healthcheck_stack.sh ]; then
        exec scripts/healthcheck_stack.sh
    else
        echo "healthcheck_stack.sh not found. Run from project root."
        exit 1
    fi
}

# ── main ─────────────────────────────────────────────────────────────────
case "${1:-help}" in
    help|--help|-h)
        usage
        ;;
    data|docker-data)
        cmd_data
        ;;
    data-full|docker-data-full)
        cmd_data_full
        ;;
    status)
        cmd_status
        ;;
    *)
        echo "Unknown command: $1"
        usage
        ;;
esac
