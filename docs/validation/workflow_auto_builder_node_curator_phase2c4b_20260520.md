# Fase 2C.4B — Workflow Auto Builder + Node Curator Defensivo

**Fecha:** 2026-05-20  
**Base estable:** `ffe7a19`  
**Tag base:** `cid-dev-stable-visual-bible-media-asset-final-phase2c3-20260520`

## 1. Objetivo

Implementar una base defensiva para seleccionar workflows ComfyUI segun nodos realmente disponibles, sin instalar nodos nuevos y sin romper el flujo validado en Phase 2C.3.

## 2. Auditoria Node Curator

| Instancia | Puerto | Conteo nodos |
|-----------|--------|--------------|
| image | 8188 | 3664 |
| video | 8189 | 2573 |
| dubbing | 8190 | 1915 |
| restoration | 8191 | 1915 |
| 3d | 8192 | 654 |

Decision mantenida:

- **No instalar nodos nuevos todavia**
- Mantener fuera de `custom_nodes/` en 8188:
  - `comfyui-lora-manager`
  - `comfyui-enhancement-utils`
  - `comfyui_image_metadata_extension`
  - `comfyui-deploy`

## 3. Implementacion

### 3.1 Profiles implementados

- `smoke_light`
- `storyboard_safe`
- `storyboard_fast` (degrada a `storyboard_safe`)
- `production_quality` (degrada a `storyboard_safe` por ahora)

### 3.2 Selector defensivo

Fallback chain soportada:

- `production_quality -> storyboard_fast -> storyboard_safe -> smoke_light`
- `storyboard_fast -> storyboard_safe -> smoke_light`
- `storyboard_safe -> smoke_light`
- `smoke_light -> error controlado`

Razones de fallback implementadas:

- `profile_not_implemented`
- `missing_nodes`
- `capability_check_unavailable`
- `template_not_found`

### 3.3 Plantillas JSON

Archivos creados:

- `data/workflows/comfyui/smoke_light.json`
- `data/workflows/comfyui/storyboard_safe.json`

Ambas usan solo nodos core:

- `CheckpointLoaderSimple`
- `CLIPTextEncode`
- `EmptyLatentImage`
- `KSampler`
- `VAEDecode`
- `SaveImage`

### 3.4 Capabilities reales

Nuevo servicio:

- `src/services/comfyui_node_capability_service.py`

Capacidades soportadas:

- lectura de `/api/object_info`
- snapshot defensivo de nodos disponibles
- conteo total de nodos
- validacion de class types requeridos por workflow
- deteccion de `missing_nodes`

### 3.5 Metadata preservada y extendida

Metadata nueva propagada hacia `media_assets.metadata_json`:

```json
"workflow_profile": {
  "requested": "storyboard_safe",
  "executed": "storyboard_safe"
}
```

```json
"workflow_fallback_report": {
  "requested_profile": "storyboard_safe",
  "executed_profile": "storyboard_safe",
  "fallback_applied": false,
  "reason": "none",
  "missing_nodes": [],
  "missing_models": []
}
```

Campos adicionales observados en asset final:

- `workflow_key=still_storyboard_frame`
- `available_node_count=3664`

Visual Bible se mantuvo intacta:

```json
"visual_bible": {
  "enabled": true,
  "applied": false,
  "visual_bible_id": "6a33e3f0cf294842a5bde9e14207768e",
  "visual_bible_preset": null,
  "source": "render_job_metadata"
}
```

## 4. Validacion local

### 4.1 Compile

Ejecutado:

```bash
python -m py_compile \
  src/schemas/comfyui_workflow_schema.py \
  src/services/comfyui_node_capability_service.py \
  src/services/comfyui_workflow_selector_service.py \
  src/services/workflow_builder.py \
  src/services/job_scheduler.py \
  src/services/job_tracking_service.py \
  src/services/storyboard_service.py
```

Resultado: **OK**

### 4.2 Suite focalizada

Ejecutado:

```bash
PYTHONPATH=src python -m pytest tests/unit -q -k "workflow or comfyui or visual_bible or storyboard or render"
```

Resultado: **15 passed**

### 4.3 Suite completa unit

Ejecutado:

```bash
PYTHONPATH=src python -m pytest tests/unit -q
```

Resultado:

- `527 passed`
- `8 failed`

Los 8 fallos quedaron concentrados en:

- `tests/unit/test_project_visual_bible_service.py`

Fallo observado:

- `sqlite3.OperationalError: no such table: projects`

Esto apunta a un problema del fixture SQLite de esa suite, no al nuevo flujo de workflow selector.

## 5. Smoke real

### 5.1 Infra validada

- Backend Docker reconstruido con el codigo nuevo
- ComfyUI WSL 8188 accesible
- `/api/object_info` devuelve **3664** class types

### 5.2 Ejecucion real

Usuario usado:

- `smoke@test.com`

Proyecto usado:

- `947a8b441dd34717a9e2e8e43e00d143`

Storyboard:

- modo `SINGLE_SCENE`

Render job:

- `eb6b230e`
- `status=succeeded`
- `workflow_key=still_storyboard_frame`

Asset final:

- `storyboard_947a8b44_001_301f2d58_00001_.png`

Metadata final observada en `media_assets.metadata_json`:

```json
"workflow_profile": {
  "requested": "storyboard_safe",
  "executed": "storyboard_safe"
}
```

```json
"workflow_fallback_report": {
  "requested_profile": "storyboard_safe",
  "executed_profile": "storyboard_safe",
  "fallback_applied": false,
  "reason": "none",
  "missing_nodes": [],
  "missing_models": []
}
```

```json
"workflow_key": "still_storyboard_frame"
```

```json
"available_node_count": 3664
```

Resultado del smoke:

- render completado
- `media_asset` creado
- Visual Bible preservada
- workflow metadata presente
- sin `unknown node type` en el path del render exitoso

## 6. Riesgos abiertos

1. **Full unit suite no esta verde**: 8 fallos por fixture SQLite en `test_project_visual_bible_service.py`.
2. **TypeError ajeno en log de ComfyUI**: aparece un error de `zsq_prompt` (`VAELoader.vae_list() missing 1 required positional argument: 's'`) durante startup/discovery, aunque el prompt de render ejecuta correctamente.
3. **`production_quality` y `storyboard_fast` aun no tienen plantilla propia**: hoy degradan defensivamente a `storyboard_safe`.
4. **Instalacion segura de nodos avanzada pendiente**: no se instalan nuevos nodos en esta fase.
5. **Impact / IPAdapter / ControlNet avanzado pendiente**.
6. **Docker ComfyUI sigue pendiente**: esta fase sigue validando contra WSL 8188.

## 7. Decision

### Resultado: **GO PARCIAL**

Se cumple:

- builder carga plantillas
- selector valida nodos y hace fallback
- `still_storyboard_frame` sigue funcionando
- smoke real crea `media_asset`
- metadata Visual Bible sigue intacta
- metadata `workflow_profile` y `workflow_fallback_report` llega al asset final

No se declara GO total porque:

- la suite completa `tests/unit` no queda totalmente verde
- el log de ComfyUI sigue mostrando un TypeError ajeno de otro custom node no usado por el render exitoso

## 8. Proximo paso recomendado

1. Corregir o aislar el fixture SQLite de `test_project_visual_bible_service.py`.
2. Curar el nodo `zsq_prompt` o excluirlo si no es necesario en 8188.
3. Implementar plantillas reales para `storyboard_fast` y `production_quality` cuando exista una base estable de nodos permitidos.

## 9. Hardening after GO PARCIAL

### 9.1 Causa de los 8 fallos

Los 8 fallos de `tests/unit/test_project_visual_bible_service.py` no venian de logica productiva. La causa era una fixture rota:

- el test abria una SQLite temporal
- consultaba e insertaba en `projects`
- pero nunca creaba la tabla `projects`

Ademas, intentar `Base.metadata.create_all()` completo en ese contexto introducia dependencias no resueltas a tablas externas (`matcher_jobs`) por imports parciales del metadata global.

### 9.2 Fix aplicado

Se corrigio solo el setup del test, sin tocar servicios productivos:

- la fixture ahora usa un archivo SQLite aislado por test (`tmp_path`)
- crea explicitamente solo las tablas necesarias:
  - `Project.__table__`
  - `ProjectVisualBible.__table__`

Esto mantiene el test autocontenido y evita depender de una DB real o de metadata global incompleta.

### 9.3 Resultado tests final

Ejecutado:

```bash
PYTHONPATH=src python -m pytest tests/unit/test_project_visual_bible_service.py -q
```

Resultado: **8 passed**

Ejecutado:

```bash
PYTHONPATH=src python -m pytest tests/unit/test_visual_bible_workflow_metadata.py -q
```

Resultado: **2 passed**

Ejecutado:

```bash
PYTHONPATH=src python -m pytest tests/unit -q -k "workflow or comfyui or visual_bible or storyboard or render"
```

Resultado: **16 passed**

Ejecutado:

```bash
PYTHONPATH=src python -m pytest tests/unit -q
```

Resultado final: **536 passed**

### 9.4 Analisis de `visual_bible.applied=false`

El smoke 2C.4B original no fue una regresion del Workflow Auto Builder.

Hallazgo:

- el proyecto usado en ese smoke tenia `active_preset_id=null`
- `storyboard_service._apply_visual_bible_enrichment_to_shot_prompt()` marca:
  - `enabled=true`
  - `applied=false`
  - `reason=no_active_rules`

Por tanto, el `applied=false` observado en el asset del primer smoke 2C.4B corresponde al caso esperado **A**:

- Visual Bible presente
- sin preset activo
- sin reglas aplicables

No fue causado por `workflow_profile` ni por `workflow_fallback_report`.

### 9.5 Verificacion con `noir_classic`

Se repitio una comprobacion activando `active_preset_id=noir_classic` en el proyecto smoke.

Resultado observado en el `render:still` mas reciente (`a926bf99`) dentro de `project_jobs.result_data.metadata`:

```json
{
  "visual_bible_enabled": true,
  "visual_bible_applied": true,
  "visual_bible_preset": "noir_classic",
  "visual_bible_id": "6a33e3f0cf294842a5bde9e14207768e",
  "workflow_profile_requested": "storyboard_safe",
  "workflow_profile_executed": "storyboard_safe",
  "workflow_fallback_report": {
    "fallback_applied": false,
    "reason": "none",
    "missing_nodes": [],
    "missing_models": []
  },
  "workflow_key": "still_storyboard_frame",
  "available_node_count": 3664
}
```

Esto confirma que:

- `workflow_profile` no sobreescribe Visual Bible
- `workflow_fallback_report` no rompe Visual Bible
- cuando el preset esta realmente activo, el job metadata conserva `visual_bible_applied=true`

El render asociado seguia en `running` al cerrar esta validacion, por lo que no se documento todavia un segundo `media_asset` final con `applied=true`; sin embargo, la propagacion previa al asset queda confirmada a nivel de `project_jobs.result_data`.

### 9.6 Test de coexistencia agregado

Se reforzo `tests/unit/test_visual_bible_workflow_metadata.py` para cubrir el caso:

- Visual Bible `applied=true`
- fallback de workflow presente
- workflow metadata coexistiendo sin sobrescribir `visual_bible`

### 9.7 zsq_prompt auditado

Error observado en el log de ComfyUI 8188:

```text
File "/home/harliesound/ai/ComfyUI_instances/ComfyUI-image/custom_nodes/zsq_prompt/nodes/zsq_loader.py", line 767
TypeError: VAELoader.vae_list() missing 1 required positional argument: 's'
```

Estado:

- aparece durante startup/discovery
- no fue necesario para `still_storyboard_frame`
- no bloqueo el smoke real exitoso
- queda como riesgo no bloqueante

### 9.8 Decision final tras hardening

### Resultado: **GO**

Se cumple ahora:

- `tests/unit` completo en verde
- fixture rota corregida
- `workflow_profile` intacto
- fallback intacto
- smoke real previo de 2C.4B sigue valido
- `visual_bible.applied=false` explicado como comportamiento esperado cuando no hay preset activo
- verificacion adicional muestra `visual_bible_applied=true` en metadata del render job cuando `noir_classic` se activa
