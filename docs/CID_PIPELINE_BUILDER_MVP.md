# CID Pipeline Builder MVP

CID Pipeline Builder convierte una intención creativa en un pipeline audiovisual ejecutable.

## Alcance MVP

- Generación simulada de pipelines.
- Validación estructural.
- Presets iniciales.
- Jobs simulados.
- Legal Gate básico.
- Preparación futura para ComfyUI.

## Fuera de alcance MVP

- Ejecución real en ComfyUI.
- Generación autónoma perfecta de workflows.
- Clonación de voz sin consentimiento.
- Reparación automática avanzada.

## Arquitectura

CID Frontend → Planner Agent → Pipeline Builder → Workflow Knowledge Base → Workflow Validator → Execution Adapter → Job Queue → Assets.

## Endpoints previstos

- POST /api/pipelines/generate
- POST /api/pipelines/validate
- POST /api/pipelines/execute
- GET /api/pipelines/jobs
- GET /api/pipelines/jobs/{job_id}
- GET /api/pipelines/presets

## Servicios previstos

- pipeline_builder_service.py
- workflow_validator_service.py
- workflow_knowledge_service.py
- legal_gate_service.py
- comfyui_adapter.py

## Seguridad

- Autenticación obligatoria.
- organization_id obligatorio.
- project_id opcional pero recomendado.
- Feature flags.
- No secretos en logs.
- ComfyUI nunca expuesto públicamente.

## Criterios de cierre

- Documentación creada.
- Sin cambios funcionales.
- Diff limpio y revisable.
- Ningún archivo .db staged.
