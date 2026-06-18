# CID Local Media Agent — Synthetic End-to-End Local Demo Report Visible Report Template Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.TEMPLATE.CONTRACT.V1`

## Objective

This phase defines the future template structure for the first stakeholder-readable synthetic visible report of CID Local Media Agent.

The purpose is to specify the layout, sections, wording rules, data bindings, visible disclaimers, and blocked claims before any report artifact, renderer, generator, loader, runtime, scanner change, ffprobe execution, ffmpeg execution, SaaS integration, installer behavior, licensing behavior, or real media processing is created.

This phase is documentation/test-only.

It defines a template contract.

It does not create a report artifact.

It does not create HTML.

It does not create PDF.

It does not create DOCX.

It does not create XLSX.

It does not create a Markdown report.

It does not create a renderer.

It does not create a generator.

It does not create a fixture loader.

It does not create runtime code.

It does not modify scanner runtime.

It does not modify SaaS runtime.

It does not execute external binaries.

It does not process client media.

## Baseline

Current stable HEAD before this phase:

`08f5c4c`

Previous QA gate:

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.CONTRACT.QA.GATE.V1`

Previous QA gate result:

`PASS_SYNTHETIC_VISIBLE_REPORT_CONTRACT_READY_FOR_TEMPLATE_CONTRACT`

Visible report contract:

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.CONTRACT.V1`

Validated fixture:

`tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json`

Standalone product blueprint:

`CID.LOCAL_MEDIA_AGENT.STANDALONE.PRODUCT.BLUEPRINT.V1`

## Template status

Template status:

`SYNTHETIC_VISIBLE_REPORT_TEMPLATE_CONTRACT_ONLY`

This status means the phase defines the structure of a future report but does not generate one.

The future report artifact remains blocked.

The future renderer remains blocked.

The future generator remains blocked.

The future loader remains blocked.

Runtime behavior remains blocked.

## Future template output family

The contract may later support these output families, but this phase does not create them:

- Markdown report
- HTML report
- PDF report
- DOCX report
- XLSX summary
- console preview
- internal QA snapshot

Only the contract exists in this phase.

## Template language

The template must be Spanish-first.

Technical identifiers may remain in English when they are fixture identifiers, warning codes, or internal status labels.

The report must be readable by non-engineering stakeholders.

The main body must use production-facing language:

- montaje
- ayudante de montaje
- DIT
- sonido
- subtítulos
- revisión humana
- organización de material
- cola de revisión
- candidatos de sincronía
- privacidad local
- inventario sintético
- informe de demostración

## Template layout

A future report generated from this template must use this exact top-level layout:

1. `Portada`
2. `Resumen ejecutivo`
3. `Aviso de privacidad local`
4. `Inventario sintético del proyecto`
5. `Resumen por departamentos`
6. `Candidatos de sincronía`
7. `Alertas y cola de revisión humana`
8. `Organización sugerida de carpetas`
9. `Qué demuestra esta demo`
10. `Qué no demuestra todavía`
11. `Siguientes pasos de producto`
12. `Apéndice técnico de validación sintética`

The order is mandatory.

## Section template — Portada

The cover section must include these visible fields:

- `Producto`: `CID Local Media Agent`
- `Ecosistema`: `CID — Cinematic Intelligence Direction`
- `Tipo de informe`: `Synthetic End-to-End Local Demo Report`
- `Fixture`: `SYNTHETIC_LOCAL_DEMO_001`
- `Versión fixture`: `v1`
- `Privacidad`: `synthetic_safe_labels_only`
- `Estado`: `Datos sintéticos de demostración`
- `Uso`: `No usar como informe técnico final`

The cover must not include:

- client name
- project title
- production title
- private path
- raw filename
- person name
- real location
- dialogue excerpt
- transcription excerpt
- script excerpt

## Section template — Resumen ejecutivo

The executive summary must be short and producer-readable.

Required wording:

`Este informe muestra, con datos sintéticos, cómo CID Local Media Agent podría organizar un proyecto local para revisión de montaje, DIT, sonido y subtítulos sin subir vídeo ni audio.`

Required fixture counts:

- `10 elementos sintéticos`
- `4 elementos tipo vídeo`
- `3 elementos tipo audio`
- `1 imagen fija`
- `1 documento de producción`
- `1 elemento ignorado/no soportado`
- `6 grupos candidatos de sincronía`
- `10 elementos requieren revisión humana`

Required limitation:

`No se ha analizado material real.`

## Section template — Aviso de privacidad local

The privacy section must include this block:

`CID Local Media Agent está diseñado como producto local-first. En esta demo sintética no se sube vídeo ni audio, no se analizan rutas privadas, no se muestran nombres reales y no se procesa material de cliente.`

Required checklist:

- `Vídeo/audio subido: No`
- `Material real analizado: No`
- `Rutas privadas incluidas: No`
- `Nombres reales incluidos: No`
- `Contenido de guion incluido: No`
- `Diálogo incluido: No`
- `Transcripción incluida: No`
- `Ejecución ffprobe/ffmpeg: No`
- `Revisión humana: Sí`

## Section template — Inventario sintético del proyecto

The inventory section must display a grouped table or list.

Required columns:

- `Etiqueta segura`
- `Tipo`
- `Duración orientativa`
- `Pista técnica`
- `Grupo de sincronía`
- `Estado de revisión`
- `Revisión recomendada`

Allowed item categories:

- `video`
- `audio`
- `still_image`
- `production_document`
- `ignored_non_media`

The inventory must group items in this order:

1. video-like items
2. audio-like items
3. still-image-like items
4. document-like items
5. ignored or unsupported items

The inventory must use safe display labels only.

## Section template — Resumen por departamentos

The department section must include these review groups:

- `Montaje`
- `Ayudante de montaje`
- `DIT / media management`
- `Sonido`
- `Subtítulos / localización`
- `Producción`
- `Ignorar o archivar`

The section must explain practical impact for each group.

Allowed language:

- `Revisar antes de ingesta`
- `Revisar candidatos de sincronía`
- `Comprobar metadatos sintéticos`
- `Preparar cola de revisión humana`
- `Valorar archivo o descarte`

Blocked language:

- `Validado automáticamente`
- `Sincronizado automáticamente`
- `Transcrito automáticamente`
- `Traducido automáticamente`
- `Preparado para entrega final`
- `Aprobado legalmente`
- `Certificado para emisión`

## Section template — Candidatos de sincronía

The sync section must present sync groups as candidates only.

Required labels:

- `Grupo candidato`
- `Elementos asociados`
- `Motivo de revisión`
- `Riesgo técnico`
- `Acción humana recomendada`

Allowed wording:

- `candidato de sincronía`
- `posible doble sistema`
- `revisión humana necesaria`
- `timecode no disponible en metadatos sintéticos`
- `posible discrepancia de frame rate`
- `posible discrepancia de sample rate`

Blocked wording:

- `sincronizado`
- `bloqueado`
- `conformado`
- `listo para montaje sin revisión`
- `waveform sync complete`
- `timecode sync complete`
- `clap sync complete`

## Section template — Alertas y cola de revisión humana

The warning section must group warnings by practical impact.

Required warning codes:

- `MISSING_TIMECODE`
- `POSSIBLE_DOUBLE_SYSTEM_SOUND`
- `FRAME_RATE_MISMATCH`
- `SAMPLE_RATE_MISMATCH`
- `NEEDS_HUMAN_REVIEW`
- `READY_FOR_EDITOR_REVIEW`
- `READY_FOR_DIT_REVIEW`
- `READY_FOR_SOUND_REVIEW`
- `READY_FOR_SUBTITLE_REVIEW`
- `UNSUPPORTED_CONTAINER_HINT`

Required groups:

- `Montaje / organización`
- `DIT / gestión de media`
- `Sonido / sincronía`
- `Subtítulos / localización`
- `Archivo / descarte`

Each warning group must include a human action.

## Section template — Organización sugerida de carpetas

The folder section must show:

- `01_VIDEO`
- `02_AUDIO`
- `03_STILLS`
- `04_DOCUMENTS`
- `05_REPORTS`
- `06_REVIEW_NEEDED`
- `07_EXPORTS_FOR_EDIT`

Mandatory note:

`Esta organización es una sugerencia de informe. No implica que se hayan movido, copiado o renombrado archivos.`

Blocked claims:

- files moved
- files copied
- files renamed
- folder structure created on disk
- ingest completed

## Section template — Qué demuestra esta demo

Allowed claims:

- `La estructura del informe es comprensible.`
- `Los datos sintéticos permiten explicar el valor del producto.`
- `La cola de revisión humana se puede presentar por departamentos.`
- `La promesa local-first se puede comunicar de forma clara.`
- `El reporte futuro puede ayudar a montaje, DIT, sonido, subtítulos y producción.`

The section must not claim runtime capability.

## Section template — Qué no demuestra todavía

Required limitations:

- real media scanning
- real metadata extraction
- ffprobe integration
- ffmpeg integration
- waveform synchronization
- timecode synchronization
- clap synchronization
- transcription
- speaker detection
- language detection
- subtitle translation
- DaVinci export
- Avid export
- Premiere export
- installer behavior
- license activation
- customer deployment
- SaaS synchronization

## Section template — Siguientes pasos de producto

Allowed next steps:

1. QA del contrato de template
2. contrato de renderer sintético
3. contrato de loader local sintético
4. implementación controlada de generador visible
5. revisión humana del reporte generado
6. preparación de demo local-only
7. plan de packaging comercial

This section must say:

`Estos pasos son planificación; no son capacidades implementadas en esta fase.`

## Section template — Apéndice técnico de validación sintética

The appendix must include:

- fixture path
- schema version
- fixture id
- fixture version
- item count
- category distribution
- warning coverage
- department review coverage
- privacy assertions
- validation rules
- known limitations
- next gated phase

The appendix must be visually separated from the main producer-facing body.

## Data binding contract

A future renderer or generator must bind only these data sources:

- validated fixture JSON fields
- contract-approved static text
- contract-approved derived counts
- contract-approved warning groups
- contract-approved department groups
- contract-approved disclaimers

It must not bind:

- raw paths
- raw filenames
- real media metadata
- dialogue text
- transcript text
- client names
- person names
- real locations
- credentials
- secrets
- cloud URLs

## Fixture-derived fields

The future template may bind these fixture fields:

- `fixture_id`
- `fixture_version`
- `privacy_level`
- `fixture_kind`
- `items`
- `project_summary`
- `suggested_folders`
- `privacy_assertions`
- `validation_rules`
- `next_recommended_phase`

The future template may bind these item fields:

- `safe_item_id`
- `safe_display_label`
- `category`
- `duration_hint`
- `container_hint`
- `codec_hint`
- `sync_candidate_group`
- `warning_codes`
- `recommended_department_review`
- `report_notes`

The future template must not display:

- private local path
- raw filename
- original filename
- absolute path
- card name
- real production name
- real location name
- real person name

## Human review contract

The template must show human review as mandatory.

Human review labels:

- `Pendiente de revisión humana`
- `Revisar antes de usar en demo pública`
- `Revisar antes de cualquier claim técnico`
- `Revisión de montaje requerida`
- `Revisión DIT requerida`
- `Revisión de sonido requerida`
- `Revisión de subtítulos requerida`

No section may say that the tool replaces human judgment.

## Commercial demo contract

The template may support a controlled commercial demo for trusted contacts only after a later human review gate.

Allowed commercial message:

`CID Local Media Agent ayuda a ordenar y explicar material local para revisión de postproducción, manteniendo el material del cliente en local por defecto.`

Blocked commercial message:

`CID Local Media Agent ya sincroniza, transcribe, traduce y exporta material real de forma automática.`

## Accessibility and readability

The future template should be readable on:

- laptop screen
- projector
- shared PDF preview
- printed one-page summary
- producer-facing review call

The future report should use:

- short paragraphs
- clear headings
- practical labels
- visible disclaimers
- no dense engineering blocks in the main body
- appendix for technical validation

## Contract decision

Contract decision:

`SYNTHETIC_VISIBLE_REPORT_TEMPLATE_CONTRACT_READY_FOR_QA`

This decision allows only the next documentation/test-only template contract QA gate.

It keeps report artifact creation blocked.

It keeps HTML/PDF/DOCX/XLSX creation blocked.

It keeps renderer implementation blocked.

It keeps generator implementation blocked.

It keeps loader implementation blocked.

It keeps runtime changes blocked.

It keeps scanner runtime changes blocked.

It keeps SaaS integration blocked.

It keeps external binary execution blocked.

It keeps real media processing blocked.

## Next recommended phase

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.TEMPLATE.CONTRACT.QA.GATE.V1`
