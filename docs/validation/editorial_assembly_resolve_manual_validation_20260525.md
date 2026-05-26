# EDITORIAL.2D - Validacion manual DaVinci Resolve

**Fecha:** 2026-05-25  
**Workspace:** `/opt/SERVICIOS_CINE`  
**Estado:** GO VALIDADO MANUALMENTE EN RESOLVE 20

## Objetivo

Documentar la importacion manual en DaVinci Resolve del FCPXML generado por EDITORIAL.2C desde el fixture real `production_real_20260428`.

Nota: la validacion real reportada fue ejecutada en DaVinci Resolve 20, no en Resolve 21.

## Artefacto Importado

- FCPXML: `docs/validation/editorial_assembly_resolve_smoke_20260525/CID_Editorial_Resolve_Smoke_assembly.fcpxml`
- Manifest origen: `docs/validation/editorial_assembly_resolve_smoke_20260525/manifest.json`
- Relink report origen: `docs/validation/editorial_assembly_resolve_smoke_20260525/media_relink_report.json`

## Entorno Manual

- Version de DaVinci Resolve usada: `20`
- Sistema operativo: `Windows`
- Ruta reportada de importacion: `\\wsl.localhost\Ubuntu\opt\SERVICIOS_CINE\docs\validation\editorial_assembly_resolve_smoke_20260525`
- FCPXML importado: `docs/validation/editorial_assembly_resolve_smoke_20260525/CID_Editorial_Resolve_Smoke_assembly.fcpxml`
- Metodo de importacion: importacion manual FCPXML en DaVinci Resolve

## Resultado de Importacion

- Importa sin error: si
- Crea timeline: si
- Nombre esperado de timeline/proyecto: `CID Editorial Resolve Smoke`
- Nombre timeline observado: no informado
- Numero esperado de clips visibles: `6`
- Numero observado de clips visibles: `6`
- Orden de clips observado: correcto
- Media online/offline: `0` offline reportado
- Warnings en Resolve: `0`
- Errores en Resolve: `0`

## Orden Esperado de Clips

El orden esperado segun `manifest.json` y `neutral_timeline.json` es:

1. `S1_SH1_TK1`
2. `S1_SH1_TK2`
3. `S1_SH2_TK1`
4. `S1_SH2_TK2`
5. `S2_SH1_TK1`
6. `S2_SH1_TK2`

## Media Esperada

- Recursos de media esperados en FCPXML: `12`
- Clips de timeline esperados en FCPXML: `6`
- Video esperado: `6` clips camera `.mov`
- Audio esperado: `6` clips sound `.wav`
- Relink report generado: `resolved_media_count=12`, `missing_media_count=0`, `offline_media_count=0`

## Comportamiento Audio Dual-System

Comportamiento esperado:

- El FCPXML usa export conservador para dual-system audio.
- Cada clip incluye referencia de video y audio externo como recurso de media.
- El adapter emite `dual_system_audio_export_partial` por clip.
- No se espera que Resolve cree Sync Clips nativos automaticamente.
- El relink y/o revision manual en Resolve puede ser necesario para confirmar sync final.

Resultado observado:

- Audio: ok
- Audio dual-system importado sin errores manuales reportados.
- No se reportaron warnings de audio en Resolve.

## Problemas Detectados

No se reportaron problemas bloqueantes.

Checklist para registrar:

- Errores de importacion FCPXML: `0`
- Timeline ausente o vacio: no
- Clips fuera de orden: no
- Media offline: `0` offline reportado
- Audio no visible o no relinkable: no reportado
- Warnings mostrados por Resolve: `0`

## Capturas

- Capturas disponibles: no indicadas
- Ruta sugerida si se agregan: `docs/validation/editorial_assembly_resolve_smoke_20260525/screenshots/`

## Evidencia Backend Disponible

La validacion automatizada previa de EDITORIAL.2C genero:

- FCPXML no vacio: `4528` bytes
- Validacion XML interna: `valid=true`, `errors=[]`, `asset_count=12`, `clip_count=6`, `fps=24.0`
- Timeline neutral: `2` secuencias, `6` clips, `2352` frames totales
- Relink report: `12` recursos resueltos, `0` missing, `0` offline

## GO / NO-GO

**GO para avanzar.**

Rationale:

- DaVinci Resolve 20 en Windows importa el FCPXML sin error.
- Se crea timeline.
- Se observan `6` clips visibles.
- El orden de clips es correcto.
- Se reporta `0` media offline.
- Audio reportado como ok.
- Se reportan `0` warnings y `0` errores.

Riesgo residual:

- La validacion manual se ejecuto en Resolve 20, no en Resolve 21. Se recomienda repetir una pasada final en Resolve 21 si la compatibilidad exacta con esa version es requisito de cierre comercial.
- No se registraron capturas en este reporte.
