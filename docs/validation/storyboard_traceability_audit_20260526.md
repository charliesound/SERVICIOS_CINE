# Auditoría de Trazabilidad del Storyboard (Prompt → Workflow → Modelo → Asset → Versión)
**Fecha:** 2026-05-26  
**Rol:** Principal Product Architect + Backend Traceability Architect (AILinkCinema/CID)

---

## 1. Estado Actual de la Trazabilidad (Genealogía Existente)

Tras auditar los modelos de base de datos (`StoryboardShot`, `MediaAsset`, `ProjectJob`, `JobHistory`), la lógica de encolamiento (`JobScheduler`) y persistencia de assets (`JobTrackingService`), se determinó qué nivel de reconstrucción y rastreo de linaje visual es posible realizar hoy en día para cada plano (shot) del storyboard:

| Dimensión de Trazabilidad | Estado Actual | Método de Reconstrucción |
| :--- | :--- | :--- |
| **Guion de Origen** | **Parcial** | Se asocia indirectamente a través del `project_id` y el texto de la escena (`scene_heading` / `narrative_text`). No hay un fragmento inmutable del guion original enlazado al instante de la creación. |
| **Secuencia / Escena** | **Completo** | Persistido mediante `sequence_id`, `sequence_order` y `scene_number` en el modelo `StoryboardShot`. |
| **Prompt (Original / Enriquecido)** | **Completo** | Persistido en `narrative_text` (enriquecido) y en metadatos del shot (`metadata_json.prompt_safe_description_en` y `metadata_json.display_description_es`). |
| **Workflow ComfyUI** | **Completo** | Almacenado en `metadata_json` de `MediaAsset` mediante `workflow_key`, `workflow_profile` y `workflow_fallback_report`. |
| **Modelo / Checkpoint / Parámetros** | **Parcial** | El `model_family` (ej. SDXL) se guarda en los metadatos del shot. Sin embargo, el archivo checkpoint específico (`ckpt_name`), la semilla (`seed`), los pasos (`steps`), el sampler y los LoRAs aplicados **no se guardan de forma unificada en el StoryboardShot** (solo quedan en el JSON de ejecución crudo de ComfyUI en los metadatos de `MediaAsset`). |
| **Render Job** | **Completo** | Persistido mediante `generation_job_id` y `render_job_id` (en los metadatos del shot), enlazado directamente a `project_jobs`. |
| **Asset Final Producción** | **Completo** | Relacionado mediante `StoryboardShot.asset_id` -> `MediaAsset.id`. |
| **Versión del Plano** | **Completo** | Columna `version` en `StoryboardShot` (incrementa de forma secuencial). |

---

## 2. Huecos Críticos Identificados (Gaps)

### A. Pérdida de Trazabilidad en Reparación de Assets (`storyboard_asset_repair_service.py`)
El servicio de reparación (`repair_storyboard_shot_asset_links`) busca y reasocia heurísticamente imágenes a los planos cuando se pierden enlaces. Si un asset se vincula por aproximación (ej. buscando el ID de shot dentro del nombre del archivo en disco), **no se registra que fue un enlace heurístico / reparado**. Esto contamina el linaje de auditoría estricto.

### B. Ocultamiento de Historial de Versiones en la UI
Cuando un plano se regenera, el sistema crea un nuevo registro `StoryboardShot` incrementando `version` y marca el registro anterior como `is_active = False`. No obstante, el frontend (`StoryboardBuilderPage.tsx`) **solo solicita los planos activos** (`is_active = True`), haciendo invisibles las versiones antiguas para el usuario. No se pueden comparar prompts ni imágenes de versiones anteriores desde la UX.

### C. Parámetros de Generación Críticos No Estructurados
El sampler, steps, CFG y la semilla (seed) reales aplicados en el nodo KSampler de ComfyUI **no se mapean de vuelta** en una estructura legible en `StoryboardShot`. Quedan enterrados en el dump crudo de metadatos de salida (`outputs`) del scheduler.

### D. Exposición de Rutas Físicas del Servidor
El backend continúa retornando `canonical_path` y `storage_path` absolutos del servidor (p. ej., `/opt/SERVICIOS_CINE/...`) dentro del JSON de metadatos del asset. Esto es un riesgo de seguridad de filtración de infraestructura.

---

## 3. Diseño de la Estructura Mínima de Trazabilidad (`StoryboardTraceRecord`)

Proponemos un esquema unificado de trazabilidad para exponer a auditorías e interfaces de usuario:

```json
{
  "shot_id": "shot_uuid_12345",
  "project_id": "project_uuid_67890",
  "organization_id": "org_uuid_abcde",
  "created_at": "2026-05-26T10:00:00Z",
  "created_by_user": {
    "user_id": "user_uuid_999",
    "name": "Alex Director"
  },
  "prompt_trace": {
    "original_narrative": "El personaje saca una linterna y apunta al pasillo oscuro.",
    "positive_prompt_enriched": "extreme close-up on hand holding a metal flashlight, volumetric light beam cutting through a dark hotel hallway, hand-drawn storyboard style, monochrome",
    "negative_prompt_enriched": "color, photo, photo-realistic, smooth skin, low quality"
  },
  "workflow_trace": {
    "workflow_key": "still_storyboard_frame",
    "workflow_profile": "realistic_review",
    "workflow_profile_executed": "storyboard_safe_fallback",
    "fallback_applied": true,
    "fallback_reason": "Missing custom node WAS_Suite in target instance"
  },
  "model_trace": {
    "checkpoint": "sd_xl_base_1.0.safetensors",
    "model_family": "SDXL",
    "loras": [
      { "name": "storyboard_style_lora.safetensors", "weight": 0.85 }
    ],
    "sampler": "euler_ancestral",
    "scheduler": "normal",
    "steps": 30,
    "cfg": 7.0,
    "seed": 29810398201
  },
  "asset_trace": {
    "media_asset_id": "asset_uuid_9988",
    "file_name": "still_node_09_01.png",
    "file_size": 248109,
    "mime_type": "image/png",
    "thumbnail_url": "/api/projects/67890/storyboard/shots/shot_uuid_12345/thumbnail",
    "image_url": "/api/projects/67890/storyboard/shots/shot_uuid_12345/image",
    "association_method": "direct_metadata_link"
  },
  "version_trace": {
    "current_version": 2,
    "total_versions": 2,
    "history": [
      {
        "version": 1,
        "shot_id": "shot_uuid_old_111",
        "created_at": "2026-05-26T09:30:00Z",
        "prompt": "El personaje corre por el pasillo."
      }
    ]
  }
}
```

---

## 4. Propuesta de Endpoints (Backend REST API)

1. **`GET /api/projects/{project_id}/storyboard/shots/{shot_id}/trace`**
   - **Propósito:** Retorna el `StoryboardTraceRecord` unificado para un plano específico.
   - **Aislamiento:** Tenant-safe (valida `organization_id`).

2. **`GET /api/projects/{project_id}/storyboard/trace`**
   - **Propósito:** Retorna el reporte de auditoría agregada de trazabilidad para todo el proyecto (porcentaje de fallbacks de workflow, listado de checkpoints utilizados y recuento de versiones).

3. **`GET /api/projects/{project_id}/storyboard/assets/{asset_id}/trace`**
   - **Propósito:** Trazabilidad inversa. Permite auditar qué plano de guion, qué versión y qué usuario generaron este asset de imagen física.

4. **`POST /api/projects/{project_id}/storyboard/shots/{shot_id}/trace/snapshot`**
   - **Propósito:** Congelar el estado de trazabilidad y prompts de un plano para revisiones de producción inmutables.

---

## 5. Propuesta UX (Interfaces en Storyboard Builder)

### A. Panel "Trazabilidad" en `ShotCard`
Se integrará una pestaña o collapsible dentro de cada tarjeta de plano:
- **Resumen Técnico:** Exposición clara del modelo/checkpoint, semilla (seed) y si se aplicó fallback de workflow (alerta visual en ámbar si hubo fallback).
- **Acciones Rápidas:**
  - Botón **"Copiar Prompt"**: Copia el prompt enriquecido final en el portapapeles.
  - Botón **"Ver Ficha de Trazabilidad"**: Abre un modal modal con el JSON completo del `StoryboardTraceRecord` formateado.

### B. Comparador e Historial de Versiones
Si el plano tiene `version > 1`:
- Se muestra un indicador `"v{version} (Ver historial)"`.
- Al hacer clic, abre una vista comparativa (carrusel o side-by-side) de la versión actual frente a las anteriores inactivas (`is_active = False`), mostrando su miniatura, fecha y el prompt original para permitir un **Rollback** manual a una versión previa.

---

## 6. Roadmap para FASE STORYBOARD.TRACE.2 (Ejecución)

* **Fase 1: Implementación de Esquemas y Modelo Trace (Backend)**
  - Unificar la extracción de parámetros de ComfyUI (seed, checkpoint, sampler) durante la persistencia de assets.
  - Construir el servicio `StoryboardTraceService` para consolidar el objeto `StoryboardTraceRecord`.
* **Fase 2: Implementación de Endpoints**
  - Programar los endpoints de auditoría y asegurar la exclusión de rutas absolutas físicas (`canonical_path`).
* **Fase 3: Integración de Panel de Trazabilidad en UI (Frontend)**
  - Añadir pestaña "Trazabilidad" en `ShotCard.tsx`.
* **Fase 4: Comparador de Versiones e Historial**
  - Implementar consulta de versiones inactivas en la API y vista comparativa con botón de Rollback en la UI.

---

## 7. Dictamen de Implementación: GO

La información de trazabilidad técnica (workflows, prompts, jobs) ya se registra en gran medida en las bases de datos de `MediaAsset` y `ProjectJob` por el scheduler y el tracker de jobs. La implementación de la fase **STORYBOARD.TRACE.2** es de bajo riesgo y de alto impacto comercial, al unificar estos datos dispersos en una estructura consumible por auditoría e interfaces visuales de cara a la demo comercial.
