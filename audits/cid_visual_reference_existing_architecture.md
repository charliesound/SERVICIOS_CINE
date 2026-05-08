# CID Visual Reference — Auditoría de arquitectura existente

> FASE 1 — Análisis del pipeline CID actual para integrar Director Visual Reference / Style Reference Profile.

---

## 1. Qué existe

### Schemas (src/schemas/cid_script_to_prompt_schema.py)
- `ScriptScene` — heading, int_ext, location, time_of_day, characters, props, conflict, tones
- `DirectorLensProfile` — framing_bias, camera_movement_bias, compositional_biases
- `DirectorialIntent` — mise_en_scene, blocking, camera_strategy, visual_metaphor, prompt_guidance
- `CinematicIntent` — subject, action, environment, lighting, color_palette, mood, required_elements
- `PromptSpec` — positive_prompt, negative_prompt, semantic_anchors

### Servicios
| Servicio | Archivo | Función clave |
|---|---|---|
| `cinematic_intent_service` | `cinematic_intent_service.py` | `build_intent()` — Intención cinematográfica base |
| `directorial_intent_service` | `directorial_intent_service.py` | `build_directorial_intent()` — Estrategia de dirección |
| `prompt_construction_service` | `prompt_construction_service.py` | `build_prompt_spec()` — Prompt final |
| `semantic_prompt_validation_service` | `semantic_prompt_validation_service.py` | `validate()` — Validación semántica |
| `visual_qc_service` | `visual_qc_service.py` | `evaluate_prompt()` — QA visual |
| `continuity_memory_service` | `continuity_memory_service.py` | `build_continuity_anchors()` — Memoria de continuidad |
| `montage_intelligence_service` | `montage_intelligence_service.py` | Estrategia de montaje |
| `cid_script_to_prompt_pipeline_service` | `cid_script_to_prompt_pipeline_service.py` | Orquestador |
| `storyboard_service` | `storyboard_service.py` | Generación de storyboard |

### Parámetro existente
- `allow_director_reference_names: bool` ya existe en `run_script_to_prompt_pipeline()` y se pasa a `build_prompt_spec()`, pero **se descarta** en `prompt_construction_service.py:117`.
- No existe subida de imágenes, ni análisis de referencia visual, ni perfil de estilo.

### Assets / imágenes
- `src_frontend/public/landing-media/` — imágenes V3 y V4
- No hay sistema de asset management con metadata de estilo visual.

### ComfyUI
- `src/comfyui_workflows/imported_templates/flux_cine_2.template.json`
- No hay soporte para IPAdapter, CLIPVision ni image-to-prompt en la generación actual.

---

## 2. Qué falta

| Capacidad | Estado |
|---|---|
| Subir imagen de referencia visual | No existe |
| Analizar imagen y extraer perfil de estilo | No existe |
| Almacenar StyleReferenceProfile por proyecto | No existe |
| Enriquecer prompt con guía de referencia visual | No existe |
| Pasar referencia visual a storyboard_service | No existe |
| ComfyUI IPAdapter/ControlNet reference | No existe (solo FLUX template) |
| Frontend para subir/analizar referencia | No existe |

---

## 3. Dónde integrar sin duplicar

### Punto 1: Post `cinematic_intent` / Pre `prompt_construction`
El `StyleReferenceProfile` debe aplicarse **entre** la construcción de `CinematicIntent` y la construcción de `PromptSpec`. Esto permite que la referencia visual modifique el prompt sin contaminar la intención cinematográfica base.

**Archivo a modificar:** `cid_script_to_prompt_pipeline_service.py`
**Insertar:** Después de `build_intent()`, antes de `build_prompt_spec()`

### Punto 2: En `DirectorialIntent`
`DirectorialIntent` ya contiene `prompt_guidance`. Es el lugar natural para añadir:
- `visual_reference_id: str | None`
- `visual_reference_guidance: str | None`

**Archivo a modificar:** `src/schemas/cid_script_to_prompt_schema.py`

### Punto 3: En `PromptConstructionService._build_positive_prompt()`
Añadir una sección `"VISUAL REFERENCE GUIDANCE"` con la paleta, luz, atmósfera, textura extraídas.

### Punto 4: En `storyboard_service._build_cinematic_storyboard_shot()`
Pasar `visual_reference_profile_id` a través del pipeline hasta el shot metadata.

---

## 4. Endpoints recomendados

| Método | Ruta | Propósito |
|---|---|---|
| `POST` | `/api/cid/visual-reference/analyze` | Analizar imagen y devolver `StyleReferenceProfile` |
| `POST` | `/api/cid/visual-reference/apply-to-scene` | Aplicar perfil a una escena y devolver prompt enriquecido |
| `POST` | `/api/cid/visual-reference/apply-to-storyboard` | Aplicar perfil a storyboard |
| `GET` | `/api/cid/visual-reference/profiles/{project_id}` | Listar perfiles de un proyecto |

---

## 5. Modelos/schemas necesarios

- `DirectorVisualReferenceRequest` — Input de la API (imagen + propósito + parámetros)
- `StyleReferenceProfile` — Output del análisis de imagen
- `VisualReferenceAnalysisResult` — Resultado completo del análisis

---

## 6. Riesgos de duplicación

| Riesgo | Mitigación |
|---|---|
| Duplicar funcionalidad de `directorial_intent_service` | El perfil visual es *complementario* a la dirección: el lens profile define *cómo dirigir*, el visual reference define *cómo se ve* |
| Crear otro schema monolítico | Separar claramente: request → analysis → profile. Cada modelo tiene responsabilidad única. |
| Añadir más parámetros al pipeline ya cargado | `visual_reference_profile_id` es un string opcional. No añade carga computacional si no se usa. |
| Confundir referencia visual con assets finales | Documentar explícitamente: la referencia es guía de estilo, no activo de producción. |

---

## 7. Conclusión

La arquitectura CID existente tiene los puntos de integración claros:
- `DirectorialIntent` → extender con `visual_reference_guidance`
- `PromptConstructionService._build_positive_prompt()` → añadir sección VISUAL REFERENCE GUIDANCE
- `cid_script_to_prompt_pipeline_service.run_script_to_prompt_pipeline()` → añadir `visual_reference_profile_id` opcional
- `storyboard_service._build_cinematic_storyboard_shot()` → pasar referencia a metadata_json

No hay riesgo de duplicación significativo si se respeta la separación: perfil visual ≠ dirección artística literaria.
