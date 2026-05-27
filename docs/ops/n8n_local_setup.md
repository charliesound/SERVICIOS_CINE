# CID / AILinkCinema - n8n local setup

## Purpose

n8n is an optional automation bridge for CID.

Use it to:
- receive webhooks and events from CID
- automate email, Telegram, Drive, CRM, backups, or notifications
- test the external automation connection from CID
- prepare future event hooks such as `storyboard.render.succeeded`

Do not use it to:
- replace critical FastAPI backend logic
- write directly into the main CID database
- block CID storyboard, analysis, or render flows when n8n is down

## Start command

Use the existing compose overlays and profiles:

```bash
cd /opt/SERVICIOS_CINE

docker compose \
  -f compose.data.yml \
  -f compose.n8n.yml \
  --profile with-postgres \
  --profile with-n8n \
  up -d postgres n8n
```

Required profiles:
- `with-postgres`
- `with-n8n`

## Access URL

Local n8n UI:

```text
http://127.0.0.1:5678
```

## Quick checks

Check containers:

```bash
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "n8n|postgres" || true
```

Check n8n responds:

```bash
curl -I --max-time 10 http://127.0.0.1:5678
```

## Safety warnings

- Do not use `--remove-orphans` for this stack.
- Do not delete n8n or postgres volumes.
- Do not commit `.env`, local secrets, or real credentials.
- Do not rotate or replace `N8N_ENCRYPTION_KEY` casually.

`N8N_ENCRYPTION_KEY` protects n8n-stored credentials at rest. If it changes unexpectedly, existing n8n credentials can become unreadable.

## CID backend environment knobs

Documented in `.env.example`:

```bash
N8N_ENABLED=false
N8N_BASE_URL=http://127.0.0.1:5678
N8N_WEBHOOK_SECRET=
N8N_DEFAULT_TIMEOUT_SECONDS=10
N8N_TEST_WEBHOOK_PATH=/webhook/cid-test
```

Notes:
- keep `N8N_ENABLED=false` unless you want CID to call n8n
- CID must continue working if n8n is disabled or unreachable
- `N8N_WEBHOOK_SECRET` is optional and sent as `X-CID-Webhook-Secret`

## Example test webhook in n8n

Import or recreate the sample workflow:

```text
docs/workflows/n8n/cid_test_webhook_v1.json
```

It listens on:

```text
POST /webhook/cid-test
```

## Source workflows reviewed

Reviewed in read-only mode from:

```text
/mnt/g/COMFYUI_HUB/workflows-N8N
```

Inventory reviewed:
- `prueba disparo n8n a comfyui.json`
- `crear imagenes con comfyui.json`
- `crear imagenes con comfyui_V2.json`
- `crear imagenes con comfyui_V3.json`
- `crear imagenes con comfyui_V3a.json`
- `WORKING_restauracion_cine_GUI.json`
- `WORKING_restauracion_animacion_GUI.json`
- `SUPIR_API.json`
- `SUPIR EXR Restore Queue.json`
- `n8n corregido restaurar.json`
- `n8n corregido restaurar_V2.json`
- `Escalar con CUGAN.json`
- `Unisoft_3D.json`

## Workflows selected for CID templates

- `prueba disparo n8n a comfyui.json`
  - Useful as the base for a minimal ComfyUI trigger from n8n.
  - Uses manual trigger + prompt build + HTTP POST to ComfyUI.
- `crear imagenes con comfyui_V2.json`
  - Useful as a webhook-driven CID -> n8n -> ComfyUI pattern.
  - Has webhook input and ComfyUI nodes, but must be cleaned from real credentials.
- `crear imagenes con comfyui_V3.json`
  - Similar to V2, good as a reference for a structured dashboard-style webhook payload.
- `SUPIR EXR Restore Queue.json`
  - Useful as a restoration queue reference.
  - Contains scheduling, polling, and batch concepts relevant for future restoration automation.
- `n8n corregido restaurar_V2.json`
  - Useful as a leaner restoration queue reference.
  - Easier to adapt into a placeholder-safe template than the larger queue workflow.

## Workflows discarded or not copied directly

- `crear imagenes con comfyui.json`
  - Not webhook-first; oriented to chat trigger and includes real credential wiring.
- `crear imagenes con comfyui_V3a.json`
  - Only a parameter/demo scaffold; no actual HTTP or ComfyUI execution path.
- `WORKING_restauracion_cine_GUI.json`
  - ComfyUI graph, not an n8n automation workflow.
- `WORKING_restauracion_animacion_GUI.json`
  - ComfyUI graph, not an n8n automation workflow.
- `SUPIR_API.json`
  - Not a standard n8n export with `nodes[]`; not safe to treat as importable automation without manual review.
- `n8n corregido restaurar.json`
  - Adaptable but contains Gmail credential references and local path assumptions.
- `Escalar con CUGAN.json`
  - ComfyUI graph, not an n8n automation workflow.
- `Unisoft_3D.json`
  - ComfyUI graph focused on generation pipeline, not on CID webhook/event automation.

## Risks found in source workflows

- Several source workflows reference local absolute paths.
- Several source workflows reference real n8n credentials or credential slots.
- Some workflows are ComfyUI graphs exported as JSON, not true n8n workflows.
- `SUPIR_API.json` did not expose a normal `nodes[]` structure in this audit and should be manually reviewed before any production use.

CID templates in this repo intentionally replace any such values with placeholders.

## CID test endpoints

Authenticated CID endpoints:

- `GET /api/integrations/n8n/status`
- `POST /api/integrations/n8n/test`

Example payload:

```json
{
  "event_type": "cid.integration.test",
  "project_id": "optional-project-id",
  "message": "Smoke test from CID"
}
```

Example curl with bearer token:

```bash
export CID_TOKEN="your-jwt"

curl -s http://127.0.0.1:8010/api/integrations/n8n/status \
  -H "Authorization: Bearer $CID_TOKEN"

curl -s http://127.0.0.1:8010/api/integrations/n8n/test \
  -H "Authorization: Bearer $CID_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "cid.integration.test",
    "project_id": "demo-project",
    "message": "Smoke test from CID"
  }'
```

Expected behavior:
- if `N8N_ENABLED=false`, CID returns `status=skipped`
- if n8n is up and the webhook exists, CID returns `status=sent`
- if n8n fails, CID returns `status=failed` without breaking the rest of CID

## Importing workflow templates

Template folder:

```text
docs/workflows/n8n/
```

Recommended import flow:
1. Open n8n UI at `http://127.0.0.1:5678`
2. Create or open a workspace
3. Use `Import from File`
4. Import one template JSON from `docs/workflows/n8n/`
5. Replace placeholders before activating
6. Add credentials only inside n8n UI, never in git
