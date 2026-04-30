# Presentation Visual Validation

## Objetivo

Convertir el smoke visual real del slice Presentation en un fixture reproducible del repo sin versionar la base de datos viva del entorno.

## Activos controlados

- Fixture de imagenes reales:
  - `data/smoke_tenant_A/project_alpha/storyboard/seqA_shot01.png`
  - `data/smoke_tenant_A/project_alpha/storyboard/seqA_shot02.png`
- Seed reproducible e idempotente:
  - `scripts/seed_presentation_visual_smoke.py`
- Test automatizado de integracion:
  - `tests/integration/test_presentation_visual_validation.py`

## Regla de persistencia

- No versionar `ailinkcinema_s2.db`
- El seed debe insertar o actualizar `media_assets` apuntando a los fixtures reales image/png
- El test debe validar JSON, HTML, asset preview, PDF sincronico, PDF persistido y bloqueo cross-tenant

## Dataset smoke esperado

- `organization_id = db4d7a5dadc9457ebaa2993a30d48201`
- `project_id = 32fb858f66ef4569a7bc12db3b5ef2fd`
- `storage_source_id = d7fac025-fa34-487d-a83a-d81ce2aadcac`
- dos assets `image/*` con metadata:
  - `sequence_id = SEQ_A`
  - `shot_order = 1` y `2`
  - `shot_type`
  - `visual_mode = storyboard`
  - `prompt_summary`

## Criterios de validacion automatizada

- filmstrip DTO `200`
- secuencia real `SEQ_A`
- HTML preview con ambas imagenes
- asset preview `image/png` `200`
- export PDF `200` con imagenes embebidas
- persist PDF `201`
- descarga persistida `200`
- tenant B bloqueado para preview, export y download persistido

## Ejecucion recomendada

```bash
python scripts/seed_presentation_visual_smoke.py
DATABASE_URL='sqlite+aiosqlite:////opt/SERVICIOS_CINE/ailinkcinema_s2.db' QUEUE_AUTO_START_SCHEDULER=0 PYTHONPATH=src python -m unittest tests.integration.test_presentation_visual_validation
```

## Nota

El fixture visual existe para endurecer el camino editorial completo del filmstrip y del PDF con thumbnails reales sin reabrir el slice Presentation.
