#!/usr/bin/env bash
# ============================================================
# demo_cid_leads_curl_test.sh
# ============================================================
# Prueba el webhook n8n para el formulario /demo-cid
#
# Uso:
#   export WEBHOOK_URL="https://tu-n8n.cloud/webhook/cid-demo"
#   bash docs/n8n/demo_cid_leads_curl_test.sh
#
# O en una línea:
#   WEBHOOK_URL="https://tu-n8n.cloud/webhook/cid-demo" bash docs/n8n/demo_cid_leads_curl_test.sh
# ============================================================

set -euo pipefail

PAYLOAD_FILE="docs/n8n/demo_cid_leads_payload_example.json"

if [ -z "${WEBHOOK_URL:-}" ]; then
  echo "ERROR: Variable WEBHOOK_URL no definida."
  echo ""
  echo "  export WEBHOOK_URL=\"https://tu-n8n.cloud/webhook/cid-demo\""
  echo "  bash $0"
  exit 1
fi

if [ ! -f "$PAYLOAD_FILE" ]; then
  echo "ERROR: No se encuentra $PAYLOAD_FILE"
  echo "Ejecuta este script desde la raíz del repositorio."
  exit 1
fi

echo "→ Enviando payload a: $WEBHOOK_URL"
echo "→ Payload: $PAYLOAD_FILE"
echo ""

RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" \
  -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d @"$PAYLOAD_FILE")

echo "→ HTTP Status: $RESPONSE"

if [ "$RESPONSE" = "200" ]; then
  echo "✅ Lead enviado correctamente."
else
  echo "❌ Error al enviar lead. Status: $RESPONSE"
fi

echo ""
echo "Para ver el body completo de la respuesta:"
echo "  curl -X POST \"\$WEBHOOK_URL\" -H \"Content-Type: application/json\" -d @$PAYLOAD_FILE"
