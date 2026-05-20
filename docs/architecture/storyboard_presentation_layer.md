# Storyboard Presentation Layer

## Objetivo

Generar una hoja de storyboard presentable a partir de frames existentes para produccion, direccion, pitching y cliente, sin depender de frontend ni de nuevas ejecuciones ComfyUI.

## Referencia visual

La capa genera una plancha tipo storyboard sheet con:

- vinetas numeradas
- grids 2x2, 2x3, 2x4 y 3x3
- campos tecnicos debajo de cada vineta
- estilo limpio para revision y presentacion

## Flujo

`media_assets -> storyboard_frame_service -> storyboard_layout_engine -> storyboard_export_service`

## Layouts soportados

- `grid_2x2`
- `grid_2x3`
- `grid_2x4`
- `grid_3x3`

## Presets visuales

- `clean_corporate`
- `cinematic_pitch`
- `production_sheet`
- `realistic_client_review`

## Campos por vineta

- Shot number
- Scene / scene number
- Shot size
- Camera angle
- Movement
- Description
- Dialogue
- Notes
- Status

Tambien se preserva metadata relevante por frame:

- `visual_bible`
- `workflow_profile`
- `workflow_fallback_report`
- `render_job_id`
- `media_asset_id`

## Limitaciones 2C.4C

- usa assets ya existentes; no genera nuevos renders
- `artifact_url` queda `null` por ahora
- export PDF es simple usando Pillow
- multipagina PNG se resuelve como varios archivos PNG
- no hay preview frontend en esta fase

## Siguientes pasos

1. frontend preview
2. presets visuales personalizables
3. export PDF avanzado / DOCX
4. integracion con pitch deck y presentacion comercial

## Realistic Client Review Preset

`realistic_client_review` orienta la presentacion hacia un storyboard comercial listo para revision de cliente.

Objetivo visual:

- frames realistas o semi-realistas
- composicion limpia
- accion facil de leer
- personajes consistentes
- look de pitch / review profesional

Uso recomendado:

- pitching comercial
- revision con cliente
- direction treatment
- materiales base para video promocional

Campos de hoja pensados para este preset:

- Frame #
- Scene
- Shot size
- Camera angle
- Movement
- Action / Description
- Dialogue
- Notes
- Status

Este preset no copia interfaces ni identidad visual de herramientas externas. Solo adopta el patron funcional de storyboard comercial limpio y legible.
