# Presentation PDF Export

## Estado

- `FILMSTRIP RUNTIME = CLOSED`
- `ASSET PREVIEW TENANT-SAFE = CLOSED`
- `WEASYPRINT = VIABLE`
- `PDF SYNC EXPORT = CLOSED`
- Estrategia activa: exportacion PDF sincrona MVP dentro del backend API actual
- `PRESENTATION SLICE = FEATURE FREEZE`

## Decision tecnica

- Renderer elegido: `WeasyPrint`
- Motivo: ya validado en el `venv`, dependencias del sistema presentes y smoke real HTML -> PDF exitoso
- Namespace final: `GET /api/projects/{project_id}/presentation/export/pdf`
- Compatibilidad temporal: `POST /api/projects/{project_id}/presentation/export-pdf`

## Contrato operativo MVP

### Download final

- `GET /api/projects/{project_id}/presentation/export/pdf`
- Autenticado y tenant-safe desde dia 1
- Respuesta OK:
  - `Content-Type: application/pdf`
  - `Content-Disposition: attachment; filename="{project_name}_filmstrip.pdf"`
- Errores:
  - `403` tenant no autorizado
  - `404` proyecto inexistente
  - `500` fallo real del renderer o plantilla

### Legacy wrapper

- `POST /api/projects/{project_id}/presentation/export-pdf`
- Se mantiene para no romper contrato previo
- No devuelve bytes PDF
- Debe confirmar que el render sincrono ya esta disponible y apuntar al endpoint `GET`

## Checklist final de cierre

- WeasyPrint validado e instalado en el `venv`
- Endpoint final `GET /presentation/export/pdf` operativo
- Cabecera PDF valida `%PDF`
- Sin self-fetch HTTP al propio backend durante render
- Filmstrip y asset preview siguen tenant-safe
- Tenant B bloqueado para export PDF de tenant A
- Wrapper legacy `POST /presentation/export-pdf` no queda roto
- `/health` y `/ready` siguen en `200`

## Reglas de render

- No hacer self-fetch HTTP al propio backend durante la generacion PDF
- No usar URLs `/api/projects/.../presentation/assets/...` dentro del renderer PDF
- Para `image/*`, resolver `file://` local solo cuando el asset fisico haya pasado validacion tenant-safe
- Para assets no imagen o no resolubles, renderizar placeholder textual estable
- Un asset defectuoso no debe romper todo el PDF; se degrada ese bloque y el documento sigue

## Limites operativos del MVP

- Flujo sincronico, sin colas async
- Sin persistencia de deliverables PDF en esta fase
- Sin billing, reporting ni reapertura de admin/auth/export
- Plantilla HTML/CSS simple y compatible con WeasyPrint; sin JS ni recursos externos
- Layout optimizado para estabilidad antes que para complejidad visual extrema

## Deuda tecnica diferida

- Persistir PDF final en storage segregado si el producto lo exige
- Añadir smoke de imagenes reales para validar embedded thumbnails en runtime editorial
- Medir tiempos de render y limites de tamano por proyecto
- Definir politica de cache o regeneracion bajo demanda

## Criterio futuro para async

Pasar a job async solo cuando se cumpla al menos uno:

- PDFs grandes con muchas secuencias o imagenes pesadas aumentan latencia HTTP
- necesidad de persistir historial/versionado de exports
- necesidad de reintento automatico y observabilidad de jobs
- necesidad de descarga diferida desde storage segregado

Hasta entonces, el modo sincronico MVP es la opcion preferida.

## Nota de congelacion

Feature freeze explicito del slice Presentation. No se abren en este bloque persistencia historica, colas async ni cambios de contrato fuera de la compatibilidad legacy ya mantenida.
