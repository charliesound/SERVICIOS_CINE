#!/usr/bin/env bash
# =============================================================================
# AILinkCinema — Data Stack Launcher
# =============================================================================
# Usage:
#   ./scripts/start_stack.sh help              — show this help
#   ./scripts/start_stack.sh data              — PostgreSQL + Qdrant
#   ./scripts/start_stack.sh data-full         — PostgreSQL + Qdrant + Redis
#   ./scripts/start_stack.sh n8n               — PostgreSQL + n8n
#   ./scripts/start_stack.sh n8n-full          — PostgreSQL + Qdrant + Redis + n8n
#   ./scripts/start_stack.sh ollama            — Ollama CPU only
#   ./scripts/start_stack.sh ollama-gpu        — Ollama GPU only
#   ./scripts/start_stack.sh ai                — Qdrant + Ollama CPU
#   ./scripts/start_stack.sh ai-gpu            — Qdrant + Ollama GPU
#   ./scripts/start_stack.sh all               — Postgres + Qdrant + Redis + n8n + Ollama CPU
#   ./scripts/start_stack.sh all-gpu           — Postgres + Qdrant + Redis + n8n + Ollama GPU
#   ./scripts/start_stack.sh comfyui-config    — validate ComfyUI compose config only
#   ./scripts/start_stack.sh comfyui-gpu-config — validate ComfyUI compose + GPU override only
#   ./scripts/start_stack.sh docker-data       — alias for data
#   ./scripts/start_stack.sh docker-data-full  — alias for data-full
#   ./scripts/start_stack.sh docker-n8n        — alias for n8n
#   ./scripts/start_stack.sh docker-n8n-full   — alias for n8n-full
#   ./scripts/start_stack.sh status            — run healthcheck
# =============================================================================

set -euo pipefail
cd "$(dirname "$0")/.."

COMPOSE_BASE="-f compose.base.yml -f compose.data.yml"
COMPOSE_N8N="-f compose.base.yml -f compose.data.yml -f compose.n8n.yml"
COMPOSE_OLLAMA="-f compose.base.yml -f compose.ollama.yml"
COMPOSE_AI="-f compose.base.yml -f compose.data.yml -f compose.ollama.yml"
COMPOSE_ALL="-f compose.base.yml -f compose.data.yml -f compose.n8n.yml -f compose.ollama.yml"
COMPOSE_OLLAMA_GPU="-f compose.base.yml -f compose.ollama.yml -f compose.ollama.gpu.yml"
COMPOSE_AI_GPU="-f compose.base.yml -f compose.data.yml -f compose.ollama.yml -f compose.ollama.gpu.yml"
COMPOSE_ALL_GPU="-f compose.base.yml -f compose.data.yml -f compose.n8n.yml -f compose.ollama.yml -f compose.ollama.gpu.yml"
COMPOSE_COMFYUI="-f compose.base.yml -f compose.comfyui.yml"
COMPOSE_COMFYUI_GPU="-f compose.base.yml -f compose.comfyui.yml -f compose.comfyui.gpu.yml"
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

require_n8n_encryption_key() {
    local key="${N8N_ENCRYPTION_KEY:-}"
    if [ -z "$key" ] && [ -f .env ]; then
        key="$(grep -E '^N8N_ENCRYPTION_KEY=' .env | head -1 | cut -d= -f2-)"
    fi
    if [ -z "$key" ]; then
        echo "ERROR: N8N_ENCRYPTION_KEY is not set."
        echo "  Set it via environment or add to .env."
        exit 1
    fi
    echo "$key"
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

cmd_n8n() {
    local pw key
    pw="$(require_env_password)"
    key="$(require_n8n_encryption_key)"
    export POSTGRES_PASSWORD="$pw"
    export N8N_ENCRYPTION_KEY="$key"
    echo ">> Starting PostgreSQL + n8n ..."
    docker compose $COMPOSE_N8N \
        --profile with-postgres \
        --profile with-n8n \
        up -d postgres n8n
    echo ">> Done. Run healthcheck:"
    echo "    ./scripts/healthcheck_stack.sh"
}

cmd_n8n_full() {
    local pw key
    pw="$(require_env_password)"
    key="$(require_n8n_encryption_key)"
    export POSTGRES_PASSWORD="$pw"
    export N8N_ENCRYPTION_KEY="$key"
    echo ">> Starting PostgreSQL + Qdrant + Redis + n8n ..."
    docker compose $COMPOSE_N8N \
        --profile with-postgres \
        --profile with-qdrant \
        --profile with-redis \
        --profile with-n8n \
        up -d postgres qdrant redis n8n
    echo ">> Done. Run healthcheck:"
    echo "    ./scripts/healthcheck_stack.sh"
}

cmd_ollama() {
    echo ">> Starting Ollama (CPU) ..."
    docker compose $COMPOSE_OLLAMA \
        --profile with-ollama \
        up -d ollama
    echo ">> Done. Run healthcheck:"
    echo "    ./scripts/healthcheck_stack.sh"
}

cmd_ollama_gpu() {
    echo ">> Starting Ollama (GPU) ..."
    docker compose $COMPOSE_OLLAMA_GPU \
        --profile with-ollama \
        up -d ollama
    echo ">> Done. Run healthcheck:"
    echo "    ./scripts/healthcheck_stack.sh"
}

cmd_ai() {
    echo ">> Starting Qdrant + Ollama (CPU) ..."
    docker compose $COMPOSE_AI \
        --profile with-qdrant \
        --profile with-ollama \
        up -d qdrant ollama
    echo ">> Done. Run healthcheck:"
    echo "    ./scripts/healthcheck_stack.sh"
}

cmd_ai_gpu() {
    echo ">> Starting Qdrant + Ollama (GPU) ..."
    docker compose $COMPOSE_AI_GPU \
        --profile with-qdrant \
        --profile with-ollama \
        up -d qdrant ollama
    echo ">> Done. Run healthcheck:"
    echo "    ./scripts/healthcheck_stack.sh"
}

cmd_all() {
    local pw key
    pw="$(require_env_password)"
    key="$(require_n8n_encryption_key)"
    export POSTGRES_PASSWORD="$pw"
    export N8N_ENCRYPTION_KEY="$key"
    echo ">> Starting Postgres + Qdrant + Redis + n8n + Ollama (CPU) ..."
    docker compose $COMPOSE_ALL \
        --profile with-postgres \
        --profile with-qdrant \
        --profile with-redis \
        --profile with-n8n \
        --profile with-ollama \
        up -d postgres qdrant redis n8n ollama
    echo ">> Done. Run healthcheck:"
    echo "    ./scripts/healthcheck_stack.sh"
}

cmd_all_gpu() {
    local pw key
    pw="$(require_env_password)"
    key="$(require_n8n_encryption_key)"
    export POSTGRES_PASSWORD="$pw"
    export N8N_ENCRYPTION_KEY="$key"
    echo ">> Starting Postgres + Qdrant + Redis + n8n + Ollama (GPU) ..."
    docker compose $COMPOSE_ALL_GPU \
        --profile with-postgres \
        --profile with-qdrant \
        --profile with-redis \
        --profile with-n8n \
        --profile with-ollama \
        up -d postgres qdrant redis n8n ollama
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

cmd_comfyui_config() {
    local img
    img="${COMFYUI_IMAGE:-local/comfyui-placeholder:latest}"
    export COMFYUI_IMAGE="$img"
    echo ">> Validating ComfyUI compose config with COMFYUI_IMAGE=$COMFYUI_IMAGE ..."
    docker compose $COMPOSE_COMFYUI --profile with-comfyui config >/dev/null
    echo ">> PASS: ComfyUI compose config is valid."
}

cmd_comfyui_gpu_config() {
    local img
    img="${COMFYUI_IMAGE:-local/comfyui-placeholder:latest}"
    export COMFYUI_IMAGE="$img"
    echo ">> Validating ComfyUI compose GPU config with COMFYUI_IMAGE=$COMFYUI_IMAGE ..."
    docker compose $COMPOSE_COMFYUI_GPU --profile with-comfyui config >/dev/null
    echo ">> PASS: ComfyUI compose GPU config is valid."
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
    n8n|docker-n8n)
        cmd_n8n
        ;;
    n8n-full|docker-n8n-full)
        cmd_n8n_full
        ;;
    ollama)
        cmd_ollama
        ;;
    ollama-gpu)
        cmd_ollama_gpu
        ;;
    ai)
        cmd_ai
        ;;
    ai-gpu)
        cmd_ai_gpu
        ;;
    all)
        cmd_all
        ;;
    all-gpu)
        cmd_all_gpu
        ;;
    status)
        cmd_status
        ;;
    comfyui-config)
        cmd_comfyui_config
        ;;
    comfyui-gpu-config)
        cmd_comfyui_gpu_config
        ;;
    *)
        echo "Unknown command: $1"
        usage
        ;;
esac
