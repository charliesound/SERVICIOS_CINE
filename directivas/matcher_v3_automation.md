# MATCHER FINANCIERO ENRIQUECIDO DOCUMENTALMENTE V3 / AUTOMATION

## Objetivo
- Automatizar el enriquecimiento de matches financieros mediante RAG documental y actualización automática de oportunidad y checklist.
- Mantener compatibilidad con matcher clásico y v2 (rag_enriched).
- Introducir processing asíncrono y estados de trabajo para trazabilidad y manejo de errores.
- Añadir puntos de confianza para auto-aplicación y human-in-the-loop para casos borderline.
- No introducir UI nueva ni romper flujos existentes de proyecto, documento, financiación o presupuesto.

## Tablas afectadas
- `matcher_jobs` (nueva tabla para trabajos de matching asíncrono)
- `project_funding_matches` (añadir referencia opcional a `matcher_jobs` y campos de trazabilidad)
- `project_documents` (desencadena jobs al actualizarse)
- `funding_calls` y `funding_requirements` (desencadenan jobs al actualizarse)
- `opportunity_trackings` (se actualizan automáticamente basado en resultados del matcher)
- `requirement_checklist_items` (se actualizan automáticamente basado en evidencia del matcher)

## Pipeline de eventos
1. Un documento se importa o actualiza en `project_document_service`.
2. Se verifica que el proyecto tenga catálogo de funding disponible (funding_calls con status open).
3. Se calcula un `input_hash` basado en:
   - Lista de (document_id, checksum) para todos los ProjectDocument del proyecto con visibility_scope=PROJECT y upload_status=COMPLETED.
   - El `ingested_at` o versión más reciente de los FundingCall relevantes para la organización.
   - La `evaluation_version` del matcher v3 (configurable o fija).
4. Si no existe un `matcher_jobs` reciente con el mismo `input_hash` y `trigger_type=document_updated` (o similar) y status=completed, se encola un nuevo `matcher_jobs` con status=pending.
5. Similarmente, cuando se actualiza un `funding_call` o `funding_requirement`, se encolan jobs para los proyectos afectados (en esta fase, para todos los proyectos de la organización que tengan documentos).
6. Un worker de cola (reutilizando `queue_service`) toma el job, marca su status como processing, ejecuta el pipeline de enriquecimiento (similar al matcher v2 pero persistiendo estado intermedio), actualiza `project_funding_matches` con los resultados y el job_id, y marca el job como completed o failed.
7. Tras un match exitoso, el worker actualiza automáticamente:
   - `requirement_checklist_items`: marca como `is_fulfilled=true` y `auto_detected=true` los requisitos que tengan evidencia suficiente.
   - `opportunity_trackings`: actualiza el status basado en reglas de negocio (ej: si todos los requirements están is_fulfilled=True, pasar a "ready").
8. Se implementan puntos de confianza para auto-aplicación de acciones recomendadas y human-in-the-loop para casos borderline.

## Riesgos de concurrencia
- Condiciones de carrera al crear múltiples jobs para el mismo input_hash: mitigado por la comprobación de idempotencia antes de encolar.
- Actualizaciones simultáneas de `project_funding_matches` desde diferentes jobs: mitigado por usar transacciones y/o por que el job más reciente sobrescribirá (se puede decidir mantener solo el más reciente o el de mayor score).
- Lecturas inconsistentes durante el cálculo del hash: mitigado por tomar una snapshot de los IDs y checksums dentro de una transacción corta al calcular el hash.

## Estrategia idempotente por input_hash
- Se define un `input_hash` como hash SHA-256 de la concatenación ordenada de:
   - project_id
   - organization_id
   - Lista ordenada de (document_id, checksum) para documentos relevantes.
   - Lista ordenada de (funding_call_id, funding_call.ingested_at) para funding calls relevantes (o bien una versión global del catálogo si se prefiere).
   - evaluation_version (string configurável, ej: "v3.0").
- Antes de encolar un nuevo job, se busca en `matcher_jobs` un job con el mismo `project_id`, `trigger_type` (o sin trigger_type si se prefiere global), y el mismo `input_hash`, cuyo status sea completed o skipped. Si existe, se salta el encolado (o se puede decidir actualizar su timestamp si se quiere renew).
- En caso de trigger manual, se puede forzar el recomputo ignorando el hash.

## Estados del job
- pending: job creado, esperando ser encolado (o directamente encolado).
- queued: job en la cola, esperando ser procesado por un worker.
- processing: worker activo, calculando el match.
- completed: match exitoso, resultados persistidos en `project_funding_matches` y actualizaciones de checklist/oportunidad realizadas.
- failed: error en el cálculo, error_message poblado.
- skipped: job no se procesó porque existía un job completado con el mismo input_hash (se puede usar para evitar trabajo duplicado).

## Criterios de cierre de Slice 0/1/2
Slice 0 (modelo de jobs + persistencia):
   - Tabla `matcher_jobs` creada con los campos mínimos.
   - `project_funding_matches` tiene una columna opcional `matcher_job_id` (FK a matcher_jobs).
   - Migración Alembic creada y aplicada.
   - Servicios de funding actualizados para aceptar el nuevo campo (si se añade).
   - Pruebas unitarias del modelo pasan.

Slice 1 (trigger por documento):
   - En `project_document_service`, tras import o actualización exitoso de ProjectDocument (y tras chunking completado), se calcula el input_hash y se encola un matcher_job si aplica.
   - El encolado no bloquea el request HTTP.
   - Se registra un log estructurado con el outcome (enqueued, skipped, error).
   - Pruebas de integración verifican que un documento nuevo lleva a un job encolado.

Slice 2 (trigger por funding call):
   - En `funding_ingestion_service`, tras actualización de FundingCall o FundingRequirement, se encolan matcher_jobs para los proyectos de la organización que tengan documentos (o bien para todos los proyectos de la organización, limitándose a aquellos con al menos un documento).
   - Se evita encolar jobs duplicados por el mismo input_hash.
   - Pruebas de integraciones verifican que una actualización de funding call lleva a jobs encolados para los proyectos afectados.

IMPLEMENTACIÓN COMPLETA
    - Todas las slices han sido implementadas según lo especificado.
    - El matcher_jobs table está creado con los campos requeridos.
    - El project_funding_matches tiene la columna matcher_job_id como FK.
    - Los triggers en project_document_service y funding_ingestion_service están funcionando.
    - El worker de matcher está procesando jobs de la cola.
    - Los API endpoints están registrados y funcionando.
    - Se han añadido pruebas de integración para verificar el flujo completo.