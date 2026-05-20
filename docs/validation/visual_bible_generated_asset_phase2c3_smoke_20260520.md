# Validación Real Fase 2C.3 — Visual Bible → Storyboard → RenderJob → ComfyUI → Asset Final

**Fecha:** 2026-05-20  
**Commit:** `5b4fd10` (feat: propagate visual bible metadata to generated assets)  
**Branch:** `main`  
**Tag referencia:** `cid-dev-stable-visual-bible-generated-asset-metadata-phase2c2-20260519`  

---

## 1. Configuración de validación

| Parámetro | Valor |
|-----------|-------|
| API_BASE | `http://127.0.0.1:80` (vía Caddy reverse proxy) |
| ComfyUI Still | `http://172.24.174.31:8188` (WSL host, reachable desde Docker) |
| Backend container | `ailinkcinema_backend` (Docker, puerto interno 8000) |
| Base de datos | `/app/ailinkcinema_s2.db` (SQLite, dentro del contenedor) |
| PROJECT_ID | `ee9c8b9fa2714accbffc75c3346cb1f2` |
| SEQUENCE_ID | `seq_001` |

## 2. Endpoints reales utilizados

| Propósito | Endpoint |
|-----------|----------|
| Registro usuario | `POST /api/auth/register` |
| Login | `POST /api/auth/login` |
| Crear proyecto | `POST /api/projects` |
| Subir guion | `POST /api/projects/{pid}/intake/script` |
| Análisis | `POST /api/projects/{pid}/analysis/run` |
| Visual Bible GET | `GET /api/projects/{pid}/visual-bible` |
| Visual Bible PUT | `PUT /api/projects/{pid}/visual-bible` |
| Storyboard generate | `POST /api/projects/{pid}/storyboard/sequences/{seq}/generate` |
| Listar jobs | `GET /api/projects/{pid}/jobs` |
| Listar assets | `GET /api/projects/{pid}/assets` |
| Queue status | `GET /api/queue/status` |
| Render jobs | `GET /api/render/jobs` |

## 3. Curls ejecutados

### 3.1 Login
```bash
curl -s -X POST "$API/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"ailinkcinema@ailinkcinema.com","password":"Producer123"}'
```

### 3.2 Crear proyecto
```bash
curl -s -X POST "$API/api/projects" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Smoke Visual Bible Phase 2C3","description":"Validacion metadata pipeline"}'
```

### 3.3 Activar Visual Bible noir_classic
```bash
curl -s -X PUT "$API/api/projects/$PID/visual-bible" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"active_preset_id":"noir_classic","is_active":true}'
```

**Respuesta:**
```json
{
  "active_preset_id": "noir_classic",
  "is_active": true,
  ...
}
```

### 3.4 Generar storyboard
```bash
curl -s -X POST "$API/api/projects/$PID/storyboard/sequences/$SEQ/generate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"mode":"SEQUENCE","style_preset":"cinematic_realistic","shots_per_scene":1,"overwrite":true,"use_cinematic_intelligence":true}'
```

**Respuesta:**
```json
{
  "job_id": "6dfcb043d5bc42c5b65fc0ea67b31a27",
  "status": "completed",
  "total_shots": 2,
  ...
}
```

## 4. Queries SQLite ejecutadas y resultados

### 4.1 Storyboard shots — metadata Visual Bible

```sql
SELECT id,
       json_extract(metadata_json, '$.visual_bible.enabled') as vb_enabled,
       json_extract(metadata_json, '$.visual_bible.applied') as vb_applied,
       json_extract(metadata_json, '$.visual_bible.active_preset_id') as vb_preset
FROM storyboard_shots 
WHERE project_id='ee9c8b9fa2714accbffc75c3346cb1f2'
ORDER BY created_at DESC;
```

**Resultados (shots con VB):**
```
111cbb85... | vb_enabled=1 | vb_applied=1 | vb_preset=noir_classic
11dd06a7... | vb_enabled=1 | vb_applied=1 | vb_preset=noir_classic
```

Metadata incluye `enriched_prompt`, `negative_prompt`, `applied_tags` con tags noir_classic, y `base_prompt`.

### 4.2 Project jobs — metadata Visual Bible en render jobs

```sql
SELECT id, status, job_type,
       json_extract(result_data, '$.metadata.visual_bible_enabled') as vb_enabled,
       json_extract(result_data, '$.metadata.visual_bible_applied') as vb_applied,
       json_extract(result_data, '$.metadata.visual_bible_preset') as vb_preset
FROM project_jobs 
WHERE project_id='ee9c8b9fa2714accbffc75c3346cb1f2' AND job_type='render:still';
```

**Resultados:**
```
af18a716 | timeout | render:still | vb_enabled=1 | vb_applied=1 | vb_preset=noir_classic
894be6a6 | timeout | render:still | vb_enabled=1 | vb_applied=0 | vb_preset=null
```

Nota: El primer intento (894be6a6) no tenía VB applied porque el VB no estaba activado correctamente en ese momento. El segundo intento (af18a716) muestra la metadata completa.

### 4.3 Media assets

```sql
SELECT id, asset_type, file_name, asset_source, status
FROM media_assets WHERE project_id='ee9c8b9fa2714accbffc75c3346cb1f2';
```

**Resultados:**
```
f024ed52 | document | storyboard_v2.json | script_storyboard | indexed
53fbde53 | document | storyboard_v1.json | script_storyboard | indexed
```

No hay assets de tipo imagen. Los assets son solo documentos de storyboard (JSON).  
No hay filas en `visual_assets`.

## 5. Evidencia de la cadena de metadata

### ✅ Visual Bible → StoryboardShot
- `storyboard_shots.metadata_json` contiene:
  - `visual_bible.enabled: true`
  - `visual_bible.applied: true`
  - `visual_bible.active_preset_id: "noir_classic"`
  - `applied_tags` con `source: "preset:noir_classic"`
  - `enriched_prompt` incluye tags: `"film noir aesthetic | classic noir | shadowy crime | detective feel | 1940s cinema"`

### ✅ StoryboardShot → RenderJob (vía submit_job metadata)
- `project_jobs.result_data.metadata` contiene:
  - `visual_bible_enabled: true`
  - `visual_bible_applied: true`
  - `visual_bible_preset: "noir_classic"`

### ⚠️ RenderJob → ComfyUI
- ComfyUI **sí recibió el trabajo** (queue mostró items durante los intentos 1-4)
- El render job pasó de `queued` → `running` (confirmando que la petición HTTP llegó a ComfyUI)
- ComfyUI no completó la generación dentro del timeout (30s), resultando en `timeout`

### ❌ ComfyUI → Asset final
- No se crearon assets de imagen en `media_assets` ni `visual_assets`
- El timeout puede deberse a:
  - Workflow demasiado complejo para el tiempo límite
  - Modelos faltantes en ComfyUI (primera ejecución)
  - Configuración de timeout del backend insuficiente

## 6. Conclusión: NO-GO

### Criterios cumplidos (4/6):
| Criterio | Estado | Evidencia |
|----------|--------|-----------|
| 1. VB noir_classic activa | ✅ | `project_visual_bibles.active_preset_id=noir_classic` |
| 2. Storyboard shot con metadata VB | ✅ | `storyboard_shots.metadata_json` con `enabled=true, applied=true, preset=noir_classic` |
| 3. Render job con metadata VB | ✅ | `project_jobs.result_data.metadata` con `visual_bible_enabled=true, visual_bible_applied=true, visual_bible_preset=noir_classic` |
| 4. ComfyUI recibió trabajo | ✅ | Queue mostró items; job pasó a `running` |
| 5. Asset final creado | ❌ | No hay image asset en `media_assets` ni `visual_assets` |
| 6. metadata_json final con VB | ❌ | No hay asset final para verificar |

### Decisión: **NO-GO**

La cadena de metadata funciona correctamente desde Visual Bible hasta el RenderJob. El pipeline se rompe en la generación ComfyUI por timeout, impidiendo la creación del asset final. La metadata Visual Bible **no llega al asset final** porque este no se genera.

## 7. Riesgos detectados

| Riesgo | Impacto | Recomendación |
|--------|---------|---------------|
| **Schema drift**: `storyboard_shots.metadata_json` no existía en la DB original | Alto | Migración o `create_all` necesario para schemas nuevos |
| **Env var faltante**: `VISUAL_BIBLE_STORYBOARD_ENRICHMENT_ENABLED` no llegaba al contenedor | Alto | Verificar que `docker compose up -d --force-recreate` recoja cambios de `.env` |
| **ComfyUI timeout**: El render job timeout sin completar | Alto | Revisar workflow de ComfyUI, modelos disponibles, y timeout del backend |
| **host.docker.internal**: No resuelve desde Docker en WSL2 | Medio | Usar IP del host WSL explícitamente o configurar `extra_hosts` |
| **Contenedor efímero**: SQLite se pierde al recrear contenedor | Medio | Migrar a PostgreSQL o montar volumen para SQLite |
| **Roles JWT**: `access_level` vs `role` inconsistente | Bajo | Unificar lógica de roles entre DB, JWT y dependencias |

## 8. Próximos pasos

1. Investigar por qué ComfyUI timeout en la generación:
   - Revisar logs de ComfyUI en la instancia WSL
   - Verificar que el workflow `still_storyboard_frame` existe y tiene los modelos necesarios
   - Aumentar `COMFYUI_TIMEOUT_SECONDS` en `.env`
2. Una vez ComfyUI genere imágenes, verificar que el asset final en `media_assets` contenga `metadata_json` con Visual Bible
3. Verificar que `visual_assets` (tabla alternativa) recibe la metadata
4. Validar escenario completo con PostgreSQL (datos persistentes)
5. Agregar prueba automatizada que verifique la cadena de metadata de extremo a extremo

---

*Documento generado como parte de la validación real Fase 2C.3*
