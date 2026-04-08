# SESION 08: OpenCode - Workflows V1

## Rol
Senior Backend Engineer + AI Workflow Specialist

## Ruta de Trabajo
`D:\SERVICIOS_CINE\src`

## Objetivo
Implementar sistema de auto-creacion de workflows desde intenciones.

## Workflows Base V1

### STILL
- still_text_to_image_pro
- still_img2img_cinematic
- still_inpaint_production
- still_storyboard_frame
- still_character_consistency
- still_upscale_master

### VIDEO
- video_text_to_video_base
- video_image_to_video_base
- video_first_last_frame
- video_refine_upscale

### DUBBING
- dubbing_tts_es_es
- dubbing_voice_clone_single
- dubbing_multi_character_dialog
- dubbing_translate_stt_tts

### LAB
- lab_probe_nodes
- lab_auto_assemble_test

## Archivos a Crear/Verificar

### 1. services/workflow_registry.py (ya existe)
Verificar que incluye:
- TaskCategory enum
- WorkflowNode dataclass
- WorkflowTemplate dataclass
- WorkflowRegistry singleton
- get_workflow(), get_catalog(), get_workflows_by_category()

### 2. services/workflow_planner.py (ya existe)
Verificar que incluye:
- IntentAnalysis dataclass
- WorkflowPlanner singleton
- analyze_intent() con reglas de decision

### 3. services/workflow_builder.py (ya existe)
Verificar que incluye:
- WorkflowBuilder singleton
- build_workflow()
- build_from_intent()

### 4. services/workflow_validator.py (ya existe)
Verificar que incluye:
- ValidationError, ValidationResult dataclasses
- WorkflowValidator singleton
- validate(), validate_inputs()

### 5. services/workflow_preset_service.py (ya existe)
Verificar que incluye:
- Preset dataclass
- WorkflowPresetService singleton
- create_preset(), get_preset(), list_presets()

### 6. routes/workflow_routes.py (ya existe)
Verificar endpoints:
- GET /api/workflows/catalog
- POST /api/workflows/plan
- POST /api/workflows/build
- POST /api/workflows/validate
- GET /api/workflows/presets
- POST /api/workflows/presets

## Reglas de Decision del Planner
- si hay source_image y no hay mask -> img2img
- si hay mask -> inpaint
- si menciona storyboard -> still_storyboard_frame
- si menciona personaje -> still_character_consistency
- si video con source_image -> video_image_to_video_base
- si video sin source_image -> video_text_to_video_base
- si dubbing con audio_ref -> voice_clone_single
- si dubbing con texto -> tts_es_es

## Smoke Test
```bash
# Ver catalogo
curl http://localhost:8000/api/workflows/catalog

# Planificar workflow
curl -X POST http://localhost:8000/api/workflows/plan \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "genera una imagen cinematica de un robot",
    "context": {}
  }'
```

## Response Example
```json
{
  "task_type": "still",
  "backend": "still",
  "detected_workflow": "still_text_to_image_pro",
  "confidence": 0.85,
  "reasoning": "Tarea clasificada como: still. Workflow seleccionado: Text to Image Pro.",
  "missing_inputs": [],
  "suggested_params": {}
}
```
