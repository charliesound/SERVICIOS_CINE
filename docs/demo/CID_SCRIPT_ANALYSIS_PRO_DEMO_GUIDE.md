# CID Script Analysis Pro — Demo Guide

## Objective

Demostrar CID Script Analysis Pro como módulo vendible: desde la entrada del usuario hasta la descarga de un informe JSON/Markdown con el análisis completo de guion.

---

## Prerequisites

| Recurso | Requisito |
|---------|-----------|
| Backend | Running on `http://127.0.0.1:8010` |
| Frontend | Running on `http://127.0.0.1:5173` |
| Auth | Token JWT válido (usuario existente) |
| Proyecto | Un proyecto con guion cargado (texto plano) |
| Plan | `demo`, `free`, `creator`, `producer`, `studio` o `enterprise` (todos incluyen `module_script_analysis`) |

### Script de ejemplo para cargar

```bash
#!/usr/bin/env bash
# upload_sample_script.sh
# Carga un guion de ejemplo en un proyecto existente
# Uso: TOKEN=<token> PROJECT_ID=<id> ./upload_sample_script.sh

set -euo pipefail
BASE_URL="${CID_BASE_URL:-http://127.0.0.1:8010}"

curl -sS -X PUT "$BASE_URL/api/projects/$PROJECT_ID/script" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "script_text": "INT. CAFE - DIA\n\nMARIA, 30, periodista, esta sentada sola mirando su telefono. Una taza de cafe humea frente a ella.\n\nMARIA\n(para si misma)\nOtra nota mas. Otra historia que nadie va a leer.\n\nEntra ALEX, 35, fotografo. Lleva una camara colgada al hombro. Mira alrededor, sus ojos se encuentran con los de Maria. Hesita un segundo y luego se acerca.\n\nALEX\nDisculpa, ¿esta libre esta silla?\n\nMARIA\n(sin mirarlo)\nSi.\n\nAlex se sienta. Pausa incomoda.\n\nALEX\nMala tarde?\n\nMARIA\n(levantando la vista)\nLa peor.\n\nAlex sonrie. No una sonrisa forzada, sino genuina.\n\nALEX\nEntonces tenemos algo en común.\n\nINT. REDACCION - NOCHE\n\nMaria y Alex caminan entre escritorios vacios. Luces fluorescentes parpadean.\n\nMARIA\nNo entiendo por que te importa esta historia.\n\nALEX\nPorque alguien tiene que contar las que duelen.\n\nMaria lo mira. Por primera vez en el dia, parece considerar algo mas alla del cinismo."
  }'
```

---

## Demo Flow

### Step 1: Start the stack

```bash
cd /opt/SERVICIOS_CINE

# Backend
source .venv/bin/activate
export PYTHONPATH="$PWD/src"
python src/main.py &
# Or use: ./scripts/start_cid_backend_dev.sh

# Frontend (separate terminal)
cd src_frontend && npm run dev
```

### Step 2: Login

Open `http://localhost:5173/login` in a browser. Use a valid user account (register via `/register/cid` if none exists).

### Step 3: Entry from Modules Catalog

1. Navigate to **Módulos** in the sidebar.
2. Find **CID Script Analysis Pro** in the "Disponibles en tu plan" section.
3. Click **Abrir módulo** → navigates to `/projects`.
4. Select an existing project (or create one via **Nuevo proyecto**).

### Step 4: Entry from Project

1. Navigate to **Proyectos** in the sidebar.
2. Select a project.
3. In the project header, click **Script Analysis Pro** (amber link).
4. You arrive at `/projects/{projectId}/script-analysis`.

### Step 5: Check current state

- If the project already has a script and analysis: you'll see the summary grid with scenes, characters, locations, sequences.
- If no script: the page shows "Sin análisis todavía" with a link to go to the project and upload a script.
- If no analysis but script exists: the page shows "Sin análisis todavía" with instructions to click "Analizar guion".

### Step 6: Upload a script (if needed)

1. Go back to the project (`/projects/{projectId}`).
2. In the **Guion** tab, paste or upload a script text.
3. Click **Guardar guion**.
4. Return to **Script Analysis Pro** via the header link.

### Step 7: Run analysis

1. Click **Analizar guion**.
2. Wait for the analysis to complete (polling every 2s, may take 10-30s depending on backend).
3. Once completed, the summary grid appears with:
   - Scene count
   - Character count
   - Location count
   - Sequence count
   - Raw analysis summary (expandable)

### Step 8: Export JSON

1. Click **Exportar JSON**.
2. A file named `CID_script_analysis_{projectId}.json` downloads.
3. Open the file to verify: `logline`, `synopsis_short`, `genre`, `tone`, `characters`, `locations`, `scenes`, etc.

### Step 9: Export Markdown

1. Click **Exportar Markdown**.
2. A file named `CID_script_analysis_{projectId}.md` downloads.
3. Open the file to verify sections: Logline, Synopsis, Genre, Characters, Locations, Scenes, etc.

### Step 10: Verify blocked state (if applicable)

If the user's plan does not include `module_script_analysis`:
1. Access `/projects/{projectId}/script-analysis`.
2. The page shows a lock icon with "Módulo bloqueado" and a link to upgrade.
3. API returns 403 MODULE_ACCESS_BLOCKED.

---

## What the user should see

| Screen | Expected content |
|--------|-----------------|
| Modules catalog | Card with "CID Script Analysis Pro", CTA "Abrir módulo" |
| Project detail | Header link "Script Analysis Pro" (amber) |
| Script Analysis Pro (no script) | Empty state, guidance to upload script |
| Script Analysis Pro (no analysis) | Empty state, button "Analizar guion" enabled |
| Script Analysis Pro (loading) | Spinner while loading project data |
| Script Analysis Pro (analysis) | Summary grid: scenes, characters, locations, sequences |
| Script Analysis Pro (exports) | Downloaded JSON or MD file with full analysis |
| Script Analysis Pro (blocked) | Lock icon, "Módulo bloqueado", link to plans |
| Error state | Error message + "Reintentar" button |

---

## GO/NO-GO checks

### GO criteria
- [ ] Backend responds to `/health`
- [ ] Modules catalog loads with `script_analysis` visible
- [ ] Project detail page shows "Script Analysis Pro" link
- [ ] Analysis page loads without errors
- [ ] "Analizar guion" button works
- [ ] Analysis summary grid updates after completion
- [ ] JSON export downloads valid JSON
- [ ] Markdown export downloads valid MD
- [ ] Blocked state correctly renders when module is locked
- [ ] `npm run build` passes
- [ ] Backend tests pass (`pytest tests/unit/ tests/integration/`)

### NO-GO criteria
- [ ] Backend health fails
- [ ] Module not visible in catalog
- [ ] Analysis page shows 500 or blank screen
- [ ] Export returns non-downloadable content (inline JSON instead of attachment)
- [ ] Exports fail for projects without analysis (should return 200 with warnings, not 404)
- [ ] npm build fails

---

## Troubleshooting

| Problem | Likely cause | Solution |
|---------|-------------|----------|
| 403 on analysis page | JWT expired or invalid | Login again, get new token |
| "Módulo bloqueado" | Plan without `module_script_analysis` | Use admin user or check `plans.yml` |
| 404 on project load | Wrong project ID | Verify project exists in DB or via API |
| Analysis never completes | Backend LLM unavailable | Check backend logs, verify Ollama/LLM endpoint |
| Export returns no content | No `script_text` or no `ProductionBreakdown` | Upload script and run analysis first |
| `npm run build` fails | TypeScript error | Run `tsc --noEmit` to diagnose |
| Backend not starting | Missing env vars | Check `.env` has `AUTH_SECRET_KEY`, `APP_SECRET_KEY` |

---

## Curl commands (for API-level demo)

```bash
# Health
curl -sS http://127.0.0.1:8010/health | jq .

# Module catalog
curl -sS http://127.0.0.1:8010/api/modules/catalog | jq '.modules[] | select(.key=="script_analysis")'

# My modules
curl -sS -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8010/api/modules/me | jq .

# Project analysis summary
curl -sS -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8010/api/projects/$PROJECT_ID/analysis/summary" | jq .

# Export JSON
curl -sS -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8010/api/projects/$PROJECT_ID/analysis/export?format=json" -o "CID_script_analysis_${PROJECT_ID}.json"

# Export Markdown
curl -sS -H "Authorization: Bearer $TOKEN" "http://127.0.0.1:8010/api/projects/$PROJECT_ID/analysis/export?format=md" -o "CID_script_analysis_${PROJECT_ID}.md"
```

---

## Routes summary

| Route | Method | Purpose |
|-------|--------|---------|
| `/api/health` | GET | Backend health |
| `/api/modules/catalog` | GET | Module catalog |
| `/api/modules/me` | GET | User module access |
| `/api/projects/{id}` | GET | Project details |
| `/api/projects/{id}/analysis/run` | POST | Trigger analysis |
| `/api/projects/{id}/analysis/summary` | GET | Analysis status/summary |
| `/api/projects/{id}/analysis/export?format=json\|md` | GET | Export analysis |
| `/projects/:projectId/script-analysis` | — | Frontend page |
