# CID Mixed Module Ownership Audit

## Objetivo

Auditar las tres superficies de ruta que quedaron deliberadamente sin enforcement modular en Sprint 3, documentar ownership real por endpoint y producir recomendaciones de enforcement para Commit 5.

## Contexto

- Sprint 3 aplicó `require_module_access()` a 11 route files de 5 módulos vendibles.
- Tres routers se dejaron fuera por ser superficies compartidas entre varios módulos:
  - `src/routes/presentation_routes.py`
  - `src/routes/delivery_routes.py`
  - `src/routes/cid_script_to_prompt_routes.py`
- Este documento audita ownership, consumidores y riesgos de cada endpoint.

---

## 1. presentation_routes.py

**Archivo**: `src/routes/presentation_routes.py` (313 lines)
**Prefijo**: `/api/projects/{project_id}/presentation`
**Módulo en modules.yml**: `pitch_deck` — route_prefixes incluye `/api/projects/*/presentation`
**Router tag**: `"presentation"`
**Auth**: `routes.auth_routes.get_tenant_context` en todos los endpoints
**Servicios que importa**:
- `presentation_service` — construye filmstrip desde storyboard shots + media assets + comments (read-only aggregator)
- `pdf_service` — renderiza PDF del filmstrip
- `delivery_service.create_project_file_deliverable` — persiste PDF como deliverable (solo en `POST .../persist`)

### Matriz endpoint → módulo propietario → consumidores

| Endpoint | Propietario | Consumidores | Auth | Notas |
|---|---|---|---|---|
| `GET /{pid}/presentation/filmstrip` | **pitch_deck** | pitch_deck UI | Sí | Agrega shots + assets + comments del proyecto |
| `GET /{pid}/presentation/filmstrip.html` | **pitch_deck** | pitch_deck UI | Sí | Vista previa HTML del filmstrip |
| `GET /{pid}/presentation/export/pdf` | **pitch_deck** | pitch_deck UI | Sí | Descarga PDF |
| `POST /{pid}/presentation/export/pdf/persist` | **pitch_deck** + entrega a `delivery_distribution` | pitch_deck UI, delivery | Sí | Genera PDF y lo persiste como deliverable |
| `GET /{pid}/presentation/assets/{aid}/preview` | **pitch_deck** | pitch_deck UI | Sí | Preview de asset del filmstrip |
| `GET /{pid}/presentation/assets/{aid}/thumbnail` | **pitch_deck** | pitch_deck UI | Sí | Thumbnail de imagen con PIL |
| `POST /{pid}/presentation/export-pdf` | **pitch_deck** | pitch_deck UI | Sí | Endpoint legacy, redirige a GET |

### Dependencias cruzadas reales

- `presentation_service.build_filmstrip()` lee de modelos: `Project`, `StoryboardShot`, `MediaAsset`, `StorageSource`, `Review`, `ReviewComment` — todo **lectura**, no escritura
- `delivery_service.create_project_file_deliverable()` solo se llama en el endpoint `POST .../persist` para guardar el PDF como deliverable. Esto es un **output** hacia delivery, no un conflicto de ownership

### GO/NO-GO

**GO → pitch_deck**. El router es propiedad claramente de pitch_deck. El prefix está correctamente declarado en modules.yml. La única interacción cross-module es escribir un deliverable (output), no depender de otro módulo para funcionar.

### Recomendación Commit 5

Aplicar `require_module_access("pitch_deck")` a nivel de router (como ya hace `producer_pitch_routes.py`). El endpoint `POST .../persist` seguirá funcionando porque el enforcement es por plan del usuario, no por módulo destino del deliverable.

---

## 2. delivery_routes.py

**Archivo**: `src/routes/delivery_routes.py` (232 lines)
**Prefijo**: `/api/delivery`
**Módulo en modules.yml**: `delivery_distribution` — route_prefixes incluye `/api/delivery`
**Router tag**: `"delivery"`
**Auth**: `dependencies.tenant_context.get_tenant_context` en todos los endpoints
**Servicios que importa**:
- `delivery_service` — CRUD de deliverables + descarga
- `export_service` — exportación ZIP de proyecto
- `plan_limits_service` — verificación de límites de plan

### Matriz endpoint → módulo propietario → consumidores

| Endpoint | Propietario | Consumidores | Auth | Notas |
|---|---|---|---|---|
| `GET /projects/{pid}/deliverables` | **delivery_distribution** (superficie) | pitch_deck, funding_grants, postproduction | Sí | Lista deliverables de cualquier módulo |
| `GET /deliverables/{did}` | **delivery_distribution** (superficie) | pitch_deck, funding_grants, postproduction | Sí | Detalle de deliverable individual |
| `GET /reviews/{rid}/deliverable` | **delivery_distribution** (superficie) | review workflow | Sí | Busca deliverable por review |
| `POST /projects/{pid}/deliverables` | **delivery_distribution** (superficie) | External API consumers, testing | Sí + write | Crea deliverable genérico |
| `PATCH /deliverables/{did}` | **delivery_distribution** (superficie) | delivery UI, testing | Sí + write | Actualiza estado |
| `GET /deliverables/{did}/download` | **delivery_distribution** (superficie) | pitch_deck, funding_grants, postproduction | Sí | Descarga archivo físico |
| `POST /projects/{pid}/export` | **core / export** | Todos los módulos | Sí + write | Export ZIP del proyecto |

### Dependencias cruzadas reales

`delivery_service.create_project_file_deliverable()` es llamado desde 3 rutas de módulos distintos:

| Origen | Módulo | Línea |
|---|---|---|
| `presentation_routes.py` | pitch_deck | 167 |
| `funding_routes.py` | funding_grants | 414 |
| `editorial_routes.py` | postproduction | 544, 617, 707 |

El router `delivery_routes.py` es la **superficie de consulta/descarga** para deliverables creados por otros módulos. Si se enforce `delivery_distribution` a nivel de router, un usuario con `funding_grants` pero sin `delivery_distribution` no podría listar ni descargar sus propios dossiers.

### GO/NO-GO

**NO-GO** para enforcement directo a nivel de router. `delivery_routes.py` es una superficie compartida que sirve a múltiples módulos. No se puede cerrar sin un modelo de ownership por deliverable (ej. inspeccionar `format_type` o `source_review_id` para determinar qué módulo originó el deliverable y verificar acceso a ese módulo).

### Recomendación Commit 5

No aplicar `require_module_access()` en este commit. En su lugar:
1. Documentar que `delivery_routes.py` requiere un modelo de enforcement granular (por deliverable, no por router).
2. Proponer un diseño futuro: middleware que inspeccione `deliverable.format_type` o `source_review_id` para determinar el módulo propietario y verificar acceso.
3. Mientras tanto, mantener el control por `require_write_permission` y el scoping por organización.

---

## 3. cid_script_to_prompt_routes.py

**Archivo**: `src/routes/cid_script_to_prompt_routes.py` (169 lines)
**Prefijo**: `/api/cid/script-to-prompt`
**Módulo en modules.yml**: **NO LISTADO** en ningún module.route_prefixes
**Router tag**: `"cid-script-to-prompt"`
**Auth**: Solo `POST /analyze-full` usa `get_tenant_context`; los demás endpoints son **stateless y sin auth**
**Servicios que importa** (9 servicios):
- `cid_script_scene_parser_service` — parsea texto de guion en escenas/planos
- `cid_script_to_prompt_pipeline_service` — orquesta pipeline completo
- `cinematic_intent_service` — construye intención cinematográfica
- `continuity_memory_service` — memoria de continuidad entre escenas
- `director_lens_service` — perfiles de lente de director
- `directorial_intent_service` — intención direccional
- `montage_intelligence_service` — inteligencia de montaje
- `prompt_construction_service` — construye prompts
- `semantic_prompt_validation_service` — valida prompts semánticamente

### Matriz endpoint → módulo propietario → consumidores

| Endpoint | Auth | Propietario | Consumidores | Notas |
|---|---|---|---|---|
| `POST /run` | No | **pipeline_builder** | pipeline_builder UI, storyboard_ai | Pipeline completo script → prompts |
| `POST /analyze-full` | Sí | **pipeline_builder** | pipeline_builder UI | Carga script de proyecto, analiza |
| `POST /parse` | No | **script_analysis** / **pipeline_builder** | script_analysis, pipeline_builder | Parseo puro de texto |
| `POST /intent` | No | **pipeline_builder** | pipeline_builder | Intención cinematográfica desde escena |
| `POST /prompt` | No | **pipeline_builder** | pipeline_builder, storyboard_ai | Construcción de prompt desde intent |
| `POST /validate` | No | **pipeline_builder** | pipeline_builder | Validación semántica de prompt |
| `GET /director-lenses` | No | **pipeline_builder** | pipeline_builder | Catálogo de lentes |
| `GET /director-lenses/{id}` | No | **pipeline_builder** | pipeline_builder | Detalle de lente |
| `POST /director-lenses/choose` | No | **pipeline_builder** | pipeline_builder | Selección de lente para escena |
| `POST /directorial-intent` | No | **pipeline_builder** | pipeline_builder | Intención direccional |
| `GET /montage-profiles` | No | **pipeline_builder** | pipeline_builder | Catálogo de perfiles de montaje |
| `POST /montage-intent` | No | **pipeline_builder** | pipeline_builder | Intención de montaje |
| `POST /editorial-beats` | No | **pipeline_builder** | pipeline_builder | Beats editoriales |
| `POST /shot-editorial-purpose` | No | **pipeline_builder** | pipeline_builder | Propósito editorial de plano |

### Dependencias cruzadas reales

- Pipeline consume output de `script_analysis` (texto parseado) y produce input para `storyboard_ai` (prompts)
- Es una **capa de transformación** entre análisis y generación visual
- Los servicios utilizados son todos de transformación de datos — no hay persistencia directa en este router
- El pipeline completo está orquestado por `cid_script_to_prompt_pipeline_service` que a su vez llama a parser, intent, prompt construction, validation y visual QC

### GO/NO-GO

**GO condicional → pipeline_builder** para endpoints autenticados (`/analyze-full`). Los endpoints stateless sin auth son seguros y no requieren enforcement (son utilidades de transformación). El prefix `/api/cid/script-to-prompt` debe añadirse a `route_prefixes` de `pipeline_builder` en `modules.yml`.

**Alternativa considerada**: Dividir ownership entre `script_analysis` (parse, intents básicos) y `pipeline_builder` (prompts, validación, pipeline completo). Se descarta porque el router es una sola superficie cohesiva de transformación — dividirla añadiría complejidad sin beneficio claro.

### Recomendación Commit 5

1. Añadir `/api/cid/script-to-prompt` a `route_prefixes` de `pipeline_builder` en `modules.yml`.
2. Aplicar `require_module_access("pipeline_builder")` solo al endpoint `/analyze-full` (el único con acceso a proyecto/DB).
3. Los endpoints stateless sin auth se dejan sin enforcement — son funciones de transformación puras.

---

## Resumen de GO/NO-GO

| Router | Decisión | Modelo de enforcement | Commit |
|---|---|---|---|
| `presentation_routes.py` | **GO → pitch_deck** | Router-level `Depends(require_module_access("pitch_deck"))` | Commit 5 |
| `delivery_routes.py` | **NO-GO** | Requiere modelo por deliverable (futuro) | No enforcement |
| `cid_script_to_prompt_routes.py` | **GO → pipeline_builder** | Endpoint-level solo en `/analyze-full` | Commit 5 |

---

## Plan exacto para Commit 5

1. **No tocar** `delivery_routes.py`.
2. **`presentation_routes.py`**: Añadir `from dependencies.module_access import require_module_access` e inyectar `Depends(require_module_access("pitch_deck"))` a nivel de router (línea 28).
3. **`cid_script_to_prompt_routes.py`**: Añadir `from dependencies.module_access import require_module_access` y aplicar `Depends(require_module_access("pipeline_builder"))` solo al endpoint `POST /analyze-full`.
4. **`modules.yml`**: Añadir `/api/cid/script-to-prompt` a `route_prefixes` de `pipeline_builder`.
5. Validar con:
   - `python -m compileall src`
   - `python -m pytest tests/unit/ -q`
   - `python -m pytest tests/integration/ -q`
   - `git status --short`

---

## Riesgos y restricciones

- `delivery_routes.py` queda sin enforcement — los deliverables seguirán siendo accesibles globalmente. Esto es aceptable porque el control por organización ya existe.
- `presentation_routes.py` comparte `delivery_service` — el enforcement de pitch_deck no bloquea la creación de deliverables (la llamada a `delivery_service` ocurre después del chequeo de módulo, dentro del endpoint).
- `cid_script_to_prompt_routes.py` tiene 13 endpoints stateless sin auth — son funciones de transformación que no acceden a datos de proyecto/organización. No requieren enforcement.
- Los tests legacy que usan presentation/delivery desde cuentas admin seguirán funcionando por el bypass de admin/global_admin.
