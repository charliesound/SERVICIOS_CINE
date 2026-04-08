#!/bin/bash
# ================================================
# Setup automatico - CID + CINE_AI_PLATFORM
# Ejecucion: bash setup.sh
# =============================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_DIR="$SCRIPT_DIR"
PROJECT_ROOT="$(dirname "$COMPOSE_DIR")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

TOTAL_STEPS=6
CURRENT_STEP=0

log_step()  { echo -e "\n${CYAN}>>> $1${NC}"; }
log_ok()    { echo -e "    [OK] $1"; }
log_warn()  { echo -e "    [WARN] $1"; }
log_fail()  { echo -e "    [FAIL] $1"; }
log_info()  { echo -e "    $1"; }

ERRORS=0

# ─── PASO 1: Verificar Docker ───
CURRENT_STEP=$((CURRENT_STEP+1))
log_step "($CURRENT_STEP/$TOTAL_STEPS) Verificando Docker"

if ! command -v docker &> /dev/null; then
    log_fail "Docker no encontrado. Instala Docker Desktop."
    ERRORS=$((ERRORS+1))
else
    log_ok "Docker: $(docker --version)"
fi

DOCKER_RUNNING=$(docker info &>/dev/null && echo "yes" || echo "no")
if [ "$DOCKER_RUNNING" != "yes" ]; then
    log_fail "Docker no esta corriendo. Inicia Docker Desktop."
    ERRORS=$((ERRORS+1))
else
    log_ok "Docker daemon corriendo"
fi

COMPOSE_CMD=""
if docker compose version &>/dev/null; then
    COMPOSE_CMD="docker compose"
    log_ok "Docker Compose: $(docker compose version)"
elif command -v docker-compose &>/dev/null; then
    COMPOSE_CMD="docker-compose"
    log_ok "Docker Compose (legacy): $(docker-compose --version)"
else
    log_fail "docker compose no disponible"
    ERRORS=$((ERRORS+1))
fi

if [ $ERRORS -gt 0 ]; then
    echo -e "\n${RED}Corrige los errores antes de continuar.${NC}"
    exit 1
fi

# ─── PASO 2: Verificar estructura ───
CURRENT_STEP=$((CURRENT_STEP+1))
log_step "($CURRENT_STEP/$TOTAL_STEPS) Verificando estructura de carpetas"

declare -A REQUIRED_PATHS=(
    ["CID_SERVER/automation-engine"]="$PROJECT_ROOT/CID_SERVER/automation-engine"
    ["CINE_AI_PLATFORM"]="$PROJECT_ROOT/CINE_AI_PLATFORM"
    ["Web Ailink_Cinema"]="$PROJECT_ROOT/Web Ailink_Cinema"
    ["PROYECTO FINAL V1"]="$COMPOSE_DIR"
)

for label in "${!REQUIRED_PATHS[@]}"; do
    path="${REQUIRED_PATHS[$label]}"
    if [ -d "$path" ]; then
        log_ok "$label"
    else
        log_fail "$label no encontrado: $path"
        ERRORS=$((ERRORS+1))
    fi
done

# ─── PASO 3: Configurar .env ───
CURRENT_STEP=$((CURRENT_STEP+1))
log_step "($CURRENT_STEP/$TOTAL_STEPS) Configurando variables de entorno"

ENV_FILE="$COMPOSE_DIR/.env"
CID_ENV_FILE="$COMPOSE_DIR/env/cid.env"
CINE_ENV_FILE="$COMPOSE_DIR/env/cine.env"

check_env_var() {
    local file=$1
    local var=$2
    local placeholder="${3:-REEMPLAZAR}"
    if [ -f "$file" ]; then
        value=$(grep "^${var}=" "$file" | cut -d'=' -f2- | tr -d ' \r')
        if [ -n "$value" ] && [ "$value" != "$placeholder" ]; then
            echo "yes"
        else
            echo "no"
        fi
    else
        echo "no"
    fi
}

SUPABASE_URL_OK=$(check_env_var "$ENV_FILE" "NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY_OK=$(check_env_var "$ENV_FILE" "NEXT_PUBLIC_SUPABASE_ANON_KEY")

if [ "$SUPABASE_URL_OK" != "yes" ] || [ "$SUPABASE_KEY_OK" != "yes" ]; then
    log_warn "Credenciales Supabase no configuradas en $ENV_FILE"
    log_info "1. Ve a https://supabase.com y crea un proyecto"
    log_info "2. Project Settings > API > copia URL y anon key"
    log_info "3. Edita: $ENV_FILE y $CID_ENV_FILE"
    echo ""
    read -p "Presiona Enter cuando hayas configurado los .env... "
fi

# ─── PASO 4: ComfyUI ───
CURRENT_STEP=$((CURRENT_STEP+1))
log_step "($CURRENT_STEP/$TOTAL_STEPS) Verificando ComfyUI"

if curl -s --max-time 5 http://127.0.0.1:8188/system_stats &>/dev/null; then
    log_ok "ComfyUI respondiendo en http://127.0.0.1:8188"
else
    log_warn "ComfyUI no esta corriendo - los renders no funcionaran"
    log_info "Opcional: inicia ComfyUI o agregalo como servicio en docker-compose.yml"
fi

# ─── PASO 5: Build y up ───
CURRENT_STEP=$((CURRENT_STEP+1))
log_step "($CURRENT_STEP/$TOTAL_STEPS) Construyendo y levantando contenedores"

cd "$COMPOSE_DIR"

log_info "Deteniendo contenedores anteriores..."
$COMPOSE_CMD down --remove-orphans 2>/dev/null || true

log_info "Construyendo imagenes (5-15 min primera vez)..."
if ! $COMPOSE_CMD build 2>&1 | tail -5; then
    log_fail "Build fallo"
    exit 1
fi
log_ok "Build completado"

log_info "Levantando contenedores..."
if ! $COMPOSE_CMD up -d 2>&1; then
    log_fail "docker compose up fallo"
    exit 1
fi
log_ok "Contenedores levantados"

# ─── PASO 6: Health checks ───
CURRENT_STEP=$((CURRENT_STEP+1))
log_step "($CURRENT_STEP/$TOTAL_STEPS) Verificando salud de servicios"

LOCAL_IP="localhost"
sleep 5

check_service() {
    local name=$1
    local url=$2
    local expected=${3:-200}
    log_info "Verificando $name..."
    for i in {1..10}; do
        status=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 "$url" 2>/dev/null || echo "000")
        if [ "$status" = "$expected" ]; then
            log_ok "$name respondio ($status)"
            return 0
        fi
        sleep 2
    done
    log_warn "$name no respondio en 20s"
    return 1
}

check_service "Caddy (CID Web)" "http://${LOCAL_IP}:8080" 200
check_service "CINE API" "http://${LOCAL_IP}:8080/api/cine/health" 200
check_service "Automation Engine" "http://${LOCAL_IP}:8000/health" 200

# ─── Resumen ───
echo ""
echo -e "${CYAN}══════════════════════════════════════════════${NC}"
echo -e "${CYAN}  RESUMEN DE LA INSTALACION${NC}"
echo -e "${CYAN}══════════════════════════════════════════════${NC}"

echo -e "\n  ${WHITE}URLs de acceso:${NC}"
echo -e "  ┌─────────────────────────────────────────────┐"
echo -e "  │  CID / App Web:     http://${LOCAL_IP}:8080     │"
echo -e "  │  CINE API:          http://${LOCAL_IP}:8080/api/cine  │"
echo -e "  │  Automation Engine: http://${LOCAL_IP}:8000     │"
echo -e "  └─────────────────────────────────────────────┘"

echo -e "\n  ${WHITE}Credenciales CINE_AI_PLATFORM:${NC}"
echo -e "  ┌─────────────────────────────────────────────┐"
echo -e "  │  admin:   admin@cine.local / CHANGE_ME     │"
echo -e "  │  editor:  editor@cine.local / editor1234   │"
echo -e "  │  viewer:  viewer@cine.local / viewer1234    │"
echo -e "  └─────────────────────────────────────────────┘"

echo -e "\n  ${WHITE}Comandos utiles:${NC}"
echo -e "  Ver logs:     ${CYAN}cd $COMPOSE_DIR && $COMPOSE_CMD logs -f${NC}"
echo -e "  Detener:      ${CYAN}cd $COMPOSE_DIR && $COMPOSE_CMD down${NC}"
echo -e "  Reiniciar:    ${CYAN}cd $COMPOSE_DIR && $COMPOSE_CMD restart${NC}"
echo -e "  Status:       ${CYAN}cd $COMPOSE_DIR && $COMPOSE_CMD ps${NC}"
echo ""
