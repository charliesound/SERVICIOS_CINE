# Smoke Test FASE 2B.1 — Visual Bible → Storyboard → metadata_json

## Metadata

| Campo | Valor |
|---|---|
| **Commit validado** | `64a1de3` feat: integrate Visual Bible enrichment into storyboard prompts phase 2b |
| **Tag validado** | `cid-dev-stable-visual-bible-storyboard-enrichment-phase2b-20260519` |
| **Fecha** | 2026-05-19 |
| **Backend port** | `http://127.0.0.1:8010` |
| **DB path real** | `/opt/SERVICIOS_CINE/ailinkcinema_s2.db` |
| **URL de env** | `sqlite+aiosqlite:////opt/SERVICIOS_CINE/ailinkcinema_s2.db` (runtime legacy config) |
| **TOKEN** | JWT generado mediante login `smoke_vb@ailinkcinema.io` (prefijo: `eyJhbGciOiJIUzI1...`) |
| **PROJECT_ID** | `68e3a92e982640319064e2b3f973b6c8` (SmokeTest FASE 2B) |
| **Usuario** | `smoke_vb@ailinkcinema.io` (creado via `/api/auth/register/cid`) |

## Endpoints usados

| Endpoint | Método |
|---|---|
| `/api/auth/login` | `POST` |
| `/api/projects/{pid}` | `GET` |
| `/api/projects/{pid}/visual-bible` | `GET`, `PUT` |
| `/api/projects/{pid}/visual-bible/preview-prompt` | `POST` |
| `/api/projects/{pid}/visual-bible/reset` | `POST` |
| `/api/projects/{pid}/storyboard/sequences` | `GET` |
| `/api/projects/{pid}/storyboard/sequences/{seq}/plan` | `POST` |
| `/api/projects/{pid}/storyboard/sequences/{seq}/generate` | `POST` |
| `/api/projects/{pid}/storyboard` | `GET` |
| `/api/projects/{pid}/jobs/{job_id}` | `GET` |

## 1. Configuración inicial

Se agregó al `.env` la variable para habilitar la feature:

```
VISUAL_BIBLE_STORYBOARD_ENRICHMENT_ENABLED=true
```

Para autenticación se usó un usuario CID real registrado vía `/api/auth/register/cid` con:
- `account_status=active`
- `cid_enabled=true`
- `access_level=standard`

Se actualizó su `organization_id` a `dev-org` para acceder al proyecto existente.

## 2. Visual Bible — actualización

**PUT** `/api/projects/{pid}/visual-bible` con `noir_classic`:

```json
{
  "active_preset_id": "noir_classic",
  "is_active": true,
  "prompt_mode": "tag_soup",
  "target_model": "SDXL"
}
```

**Respuesta:** `200 OK` — `active_preset_id="noir_classic", is_active=true`

## 3. Preview Prompt — verificación

**POST** `/api/projects/{pid}/visual-bible/preview-prompt`

```json
{"base_prompt": "A detective walking down a rainy street"}
```

**Respuesta:** `200 OK`
- `enriched_prompt` contenía etiquetas noir: `film noir aesthetic | classic noir | shadowy crime | detective feel | 1940s cinema`
- `applied_tags` incluía 5 tags positivos + 6 tags negativos
- `active_preset_id` correctamente referenciado

## 4. Storyboard — generación (caso positivo)

Se generó storyboard para `seq_001` (DETECTIVE OFFICE — 3 escenas, 12 shots):

1. **Plan:** `POST /api/projects/{pid}/storyboard/sequences/{seq_id}/plan` → `200 OK`
2. **Generate:** `POST /api/projects/{pid}/storyboard/sequences/{seq_id}/generate` → `200 OK`
3. **Job completado** en modo `SEQUENCE`, 12 shots generados

### metadata_json.visual_bible — validación SQLite

```sql
SELECT
  id,
  json_extract(metadata_json, '$.visual_bible.enabled') AS vb_enabled,
  json_extract(metadata_json, '$.visual_bible.applied') AS vb_applied,
  json_extract(metadata_json, '$.visual_bible.visual_bible_id') AS vb_id,
  json_extract(metadata_json, '$.visual_bible.active_preset_id') AS vb_preset,
  json_extract(metadata_json, '$.visual_bible.enriched_prompt') AS enriched_prompt,
  json_extract(metadata_json, '$.visual_bible.negative_prompt') AS vb_negative_prompt,
  json_extract(metadata_json, '$.visual_bible.applied_tags') AS applied_tags,
  json_extract(metadata_json, '$.visual_bible.warnings') AS vb_warnings,
  json_extract(metadata_json, '$.visual_bible.base_prompt') AS base_prompt
FROM storyboard_shots
WHERE project_id='68e3a92e982640319064e2b3f973b6c8'
  AND sequence_id='seq_001'
ORDER BY sequence_order;
```

**Resultado en todos los shots verificados:**

| Campo | Valor |
|---|---|
| `enabled` | `true` |
| `applied` | `true` |
| `visual_bible_id` | `e0c721da47de42b29252dba8e6392281` |
| `active_preset_id` | `noir_classic` |
| `prompt_mode` | `tag_soup` |
| `target_model` | `SDXL` |
| `base_prompt` | Prompt completo pre-enriquecimiento |
| `enriched_prompt` | `base_prompt` + `. film noir aesthetic \| classic noir \| shadowy crime \| detective feel \| 1940s cinema` |
| `negative_prompt` | `bright, colorful, high key, romantic comedy, daylight, vibrant` |
| `applied_tags` | Array con 11 tags (5 positivos + 6 negativos) |
| `warnings` | `["enriched_prompt_length_exceeds_recommended_sdxl_attention_zone"]` |

**Ejemplo de enriched_prompt (shot 10, seq_001):**
```
cinematic storyboard frame. model family: wan22. MS. CLERK, MARLOWE. 
I'm looking for Eleanor Vance. She been here? (hand_drawn_storyboard)...
continuity constraints: ... film noir aesthetic | classic noir | shadowy crime | 
detective feel | 1940s cinema
```

**Conclusión caso positivo:** ✅ Visual Bible activa con `noir_classic` se aplicó correctamente a todos los shots del storyboard, el prompt enriquecido tiene las etiquetas de cinematografía noir, el negative_prompt contiene los tags negativos del preset, y el array warnings documenta que el prompt excede la zona de atención recomendada para SDXL.

## 5. Caso negativo: feature flag `false`

Se cambió temporalmente:
```
VISUAL_BIBLE_STORYBOARD_ENRICHMENT_ENABLED=false
```

Se reinició el backend y se generó storyboard para `seq_002` (ALLEY, 1 escena).

**Resultado SQLite para shots de seq_002:**

```json
[
  {"vb_enabled": null, "vb_applied": null, "vb_reason": null},
  {"vb_enabled": null, "vb_applied": null, "vb_reason": null},
  {"vb_enabled": null, "vb_applied": null, "vb_reason": null}
]
```

**Conclusión caso negativo:** ✅ Con feature flag `false`, ningún shot contiene `visual_bible` en su metadata. La flag aísla completamente la funcionalidad.

## 6. Fallback seguro: Visual Bible sin reglas activas

Se reseteó la Visual Bible vía `POST /api/projects/{pid}/visual-bible/reset`:
- `active_preset_id: null`
- `is_active: true`

Se generó storyboard para `seq_003` (DETECTIVE OFFICE / DAWN).

**Resultado SQLite:**

```json
{
  "enabled": true,
  "applied": false,
  "reason": "no_active_rules",
  "visual_bible_id": "e0c721da47de42b29252dba8e6392281",
  "active_preset_id": null,
  "prompt_mode": "tag_soup",
  "target_model": "SDXL",
  "base_prompt": "...",
  "warnings": []
}
```

**Conclusión fallback:** ✅ Al no haber reglas activas (preset nulo), el sistema no aplica enriquecimiento, registra `reason="no_active_rules"`, y la generación del storyboard continúa sin errores.

## 7. Resumen de validaciones

| # | Prueba | Resultado |
|---|---|---|
| 1 | Feature flag off → no modificación | ✅ `vb_audit` ausente en metadata |
| 2 | VB con preset activo → enrichment aplicado | ✅ `enriched_prompt` con tags noir |
| 3 | VB sin preset activo → fallback | ✅ `applied=false, reason="no_active_rules"` |
| 4 | `base_prompt` preservado en metadata | ✅ Presente y completo |
| 5 | `enriched_prompt` correcto | ✅ Contiene base + tags |
| 6 | `negative_prompt` del preset aplicado | ✅ `bright, colorful, high key, ...` |
| 7 | `applied_tags` completo | ✅ 11 tags en array |
| 8 | Warning por prompt largo | ✅ `enriched_prompt_length_exceeds_recommended_sdxl_attention_zone` |
| 9 | Generación no se rompe sin VB | ✅ Storyboard generado sin errores |
| 10 | metadatos previos preservados | ✅ `validation_result`, `shot_plan`, `positive_prompt`, etc intactos |

## 8. Incidencias

1. **DB path duplicado:** El runtime usa `SQLAlchemy` con `DATABASE_URL` del legacy config (`src/config.py`) que resuelve a `/opt/SERVICIOS_CINE/ailinkcinema_s2.db` cuando no hay `DATABASE_URL` en `os.environ`. El `.env` define `DATABASE_URL` para Pydantic Settings pero no se exporta al proceso. Esto es un hallazgo pre-existente (no introducido por FASE 2B).

2. **Prompt largo:** Todos los shots enriquecidos disparan el warning `enriched_prompt_length_exceeds_recommended_sdxl_attention_zone` (>350 chars). Esto es esperado para prompts de storyboard detallados. No hay truncamiento activo.

## 9. Veredicto

**GO** ✅ — FASE 2B.1 smoke test superado.

La integración Visual Bible → Storyboard funciona correctamente:
- Feature flag aísla la funcionalidad cuando está `false`
- Con flag `true` y preset activo, el enriquecimiento se aplica y queda auditado en `metadata_json.visual_bible`
- Sin preset activo, cae suavemente con `reason="no_active_rules"`
- Todos los campos del contrato `metadata_json.visual_bible` están presentes y correctos
- La generación de storyboard no se interrumpe en ningún escenario
