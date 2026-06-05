# CID Roles, Permissions and Modules Matrix v1

Version: 1.0
Status: SPEC (documental, no implementation)
Date: 2026-06-05
Owners: CID Architecture / CID Product
Scope: AILinkCinema CID SaaS product (authenticated app, plan-gated, multitenancy-aware).
Companion docs:
- `docs/architecture/cid_saas_model_contract_v1.md` (modelo SaaS, 22 roles, 31 permisos, planes, créditos).
- `docs/architecture/backend_gating_contract_v1.md` (cierre P0/P1, 8 patrones de router, 8 P2 manual review).
- `docs/architecture/sound_ingest_field_recorders_spec_v1.md` (modulo `sound_ingest`).
- `docs/architecture/cid_backend_gating_policy_v1.md` (politica general de gating).
- `docs/product/cid_project_access_model_v1.md` (modelo funcional de acceso por proyecto, ramas, estados).

## 1. Resumen ejecutivo

Esta matriz baja el contrato SaaS a reglas operativas. No sustituye al backend gating; lo complementa. La division de responsabilidades es:

- **Backend gating** responde a la pregunta: ¿puede acceder al endpoint? Lo enforza en cada ruta via `Depends(require_write_permission)`, `Depends(validate_project_access)`, `Depends(require_module_access)`. Es codigo, es la ultima linea.
- **Matriz de roles/permisos/modulos** responde a las preguntas: ¿que puede hacer dentro del proyecto?, ¿que modulos ve?, ¿que acciones ejecuta?, ¿que limites concretos le aplican?. Es contrato, es esta matriz, es la forma del producto.

El frontend debe ocultar o bloquear acciones segun esta matriz. Si el backend rechaza una accion que el frontend muestra, hay un bug de frontend. Si el frontend muestra una accion que el backend rechazaria, hay un bug de matriz.

Regla de oro: **una accion, un permiso, un modulo, un plan, un rol, un estado**. Toda decision de UI o de API se descompone en estos seis elementos y se valida contra la matriz antes de ejecutarse.

## 2. Principios

- **Organizacion como tenant.** Toda decision de acceso parte de `organization_id`. El backend gating ya lo enforza; la matriz documenta que los roles de organizacion (`organization_owner`, `organization_admin`, `billing_admin`) actuan sobre la organizacion completa, no sobre un proyecto.
- **Proyecto como boundary de trabajo.** Los 22 roles de proyecto actuan dentro de un `project_id`. Un usuario con rol `director` en el proyecto A y `productor` en el proyecto B tiene permisos distintos en cada uno.
- **Rol audiovisual no siempre equivale a rol tecnico.** `direccion_fotografia` es un rol de produccion con alta capacidad creativa pero sin acceso a `billing.manage` ni a `credits.purchase`. `organization_admin` es un rol tecnico del SaaS que rara vez coincide con un rol creativo.
- **Permiso tecnico granular.** Los 31 permisos base son atomicos, en notacion `domain.action`. Cualquier UI o endpoint nuevo debe reutilizar un permiso existente o proponer uno nuevo versionado en este documento.
- **Multiples roles por usuario.** Un usuario puede tener varios `project_role` en el mismo proyecto y en distintos proyectos. Los permisos efectivos son la union, no la interseccion.
- **Permisos efectivos = interseccion de seis dimensiones.** Los permisos reales que un usuario tiene en un instante son la interseccion de:
  - **plan**: el plan contratado (`starter`, `pro`, `studio`, `premium`, `enterprise`) define modulos disponibles.
  - **modulo activo**: el `module_key` debe estar habilitado en el plan (`incluido`, `limitado`, `add-on` activo).
  - **rol del usuario**: el `role_key` que tiene asignado en el proyecto define permisos por defecto.
  - **permisos explicitos**: grants adicionales o restricciones concedidas por un admin.
  - **estado del proyecto**: `pre_produccion`, `produccion`, `postproduccion`, `delivery`, `archivado` cambia disponibilidad.
  - **creditos disponibles**: si la accion requiere IA, debe haber saldo de creditos suficiente.

## 3. Roles canonicos

Los 22 roles del contrato SaaS (seccion 5 de `cid_saas_model_contract_v1.md`) se describen aqui con siete campos cada uno: descripcion, responsabilidad real, modulos principales, permisos read, permisos write/generate/export, restricciones, notas SaaS. Los `role_key` estan en snake_case en backend y en capitalizacion natural en UI.

Convenciones:
- `(*)` = el rol es tipicamente tambien `org_role=admin` u `org_role=owner`.
- `(ext)` = rol externo a la organizacion; permisos limitados por defecto.
- Permisos listados usan la notacion canonica `domain.action`.

### 3.1 Productor (`productor`, `(*)`)

- **Descripcion**: responsable de viabilidad, presupuesto, financiacion, entrega. Decide sobre el proyecto. Es el cargo de produccion con maxima autoridad creativa-administrativa a nivel de proyecto.
- **Responsabilidad real**: aprueba el presupuesto, cierra la financiacion, aprueba el plan de rodaje, firma el delivery, representa al proyecto ante cliente y distribucion. Es el unico que puede publicar entregables a cliente.
- **Modulos principales**: `project_memory`, `budget`, `funding`, `producer_pitch`, `delivery`, `distribution_pack`, `client_feedback` (en modo aprobacion).
- **Permisos read**: `project.read`, `script.read`, `storyboard.read`, `concept_art.read`, `character_bible.read`, `budget.read`, `funding.read`, `sound.read`, `delivery.read`, `distribution.read`, `credits.read`, `client_feedback.read`, `audit.read`.
- **Permisos write/generate/export**: `project.write`, `project.admin`, `budget.write`, `funding.write`, `pitch.generate`, `delivery.publish`, `distribution.write`, `export.generate`, `ai.run`, `ai.approve`, `credits.purchase`, `user.invite`, `user.remove`.
- **Restricciones**: no edita arte visual directamente (delega en `direccion_arte`); no edita montaje (delega en `montaje`); no edita color (delega en `color`).
- **Notas SaaS**: suele coincidir con `org_role=admin` o `owner`. Ve todos los modulos que su plan habilita. Ve creditos, billing, auditoria. Es el unico `project_role` que puede aprobar un `ai_action_requested` por encima del plan default.

### 3.2 Productor ejecutivo (`productor_ejecutivo`, `(*)`)

- **Descripcion**: supervisa multiples proyectos, alineacion estrategica y financiera. Tiene lectura global y escritura en presupuesto/financiacion.
- **Responsabilidad real**: ve el estado de todos los proyectos de la organizacion; aprueba presupuestos grandes; supervisa la financiacion y la entrega; no ejecuta operaciones de produccion.
- **Modulos principales**: `project_memory`, `budget`, `funding`, `producer_pitch`, `distribution_pack` (lectura).
- **Permisos read**: todos los de lectura listados en productor, mas `audit.read` (lectura).
- **Permisos write/generate/export**: `budget.write`, `funding.write`, `export.generate`, `ai.approve` (no `ai.run` directo).
- **Restricciones**: no ejecuta IA pesada; no edita storyboard ni concept art; no modifica delivery final (solo sugiere).
- **Notas SaaS**: tipicamente `org_role=admin`. No necesariamente tiene `credits.purchase`. Ve dashboard de organizacion, no de proyecto.

### 3.3 Jefe de produccion (`jefe_produccion`)

- **Descripcion**: ejecuta el plan de produccion dia a dia, coordina equipos en set, controla shooting plan y shotlist.
- **Responsabilidad real**: arma el calendario de rodaje, reparte recursos, asegura que el plan se cumpla, controla costes reales vs estimados.
- **Modulos principales**: `shooting_plan`, `shotlist`, `budget`, `project_memory`.
- **Permisos read**: `project.read`, `script.read`, `budget.read`, `funding.read`, `shotlist.read`, `shooting_plan.read`, `sound.read`.
- **Permisos write/generate/export**: `shooting_plan.write`, `shotlist.write`, `budget.write` (solo lineas de coste, no totales finales), `ai.run` (solo modulos de planificacion), `export.generate`.
- **Restricciones**: no edita guion; no aprueba pitch; no entrega a cliente.
- **Notas SaaS**: rol muy operativo, casi siempre `org_role=member`. No ve `billing.manage`.

### 3.4 Director (`director`, `(*)`)

- **Descripcion**: responsable creativo principal. Aprueba tratamiento visual, narrativo y montaje.
- **Responsabilidad real**: define el lenguaje visual y narrativo, aprueba storyboards, concept art, biblia de personaje, y montaje final. Aprueba entregas a cliente.
- **Modulos principales**: `script_analysis`, `storyboard_ai`, `concept_art`, `character_bible`, `shooting_plan`, `client_feedback`.
- **Permisos read**: `project.read`, `script.read`, `storyboard.read`, `concept_art.read`, `character_bible.read`, `sound.read`, `client_feedback.read`.
- **Permisos write/generate/export**: `script.write`, `storyboard.generate`, `concept_art.generate`, `character_bible.write`, `ai.run`, `ai.approve`, `client_feedback.write` (comentarios), `export.generate`.
- **Restricciones**: no edita presupuesto; no gestiona financiacion; no firma delivery tecnico (delega en `delivery`).
- **Notas SaaS**: tipicamente `org_role=member` o `org_role=admin`. Ve creditos solo si el plan lo permite. No ve `billing.manage`.

### 3.5 Ayudante de direccion (`ayudante_direccion`)

- **Descripcion**: apoya al director, lleva la agenda, distribuye llamadas, prepara el plan diario de rodaje.
- **Responsabilidad real**: convierte el plan del director en un operativo para el equipo de rodaje; lleva la continuidad logistica.
- **Modulos principales**: `script_analysis`, `shooting_plan`, `shotlist`.
- **Permisos read**: `project.read`, `script.read`, `shotlist.read`, `shooting_plan.read`.
- **Permisos write/generate/export**: `shooting_plan.write`, `shotlist.write`, `ai.run` (solo modulos de planificacion).
- **Restricciones**: no aprueba; no edita storyboard final; no edita presupuesto.
- **Notas SaaS**: `org_role=member`. Sin acceso a billing, creditos, admin.

### 3.6 Script/continuidad (`script_continuidad`)

- **Descripcion**: garantiza raccord y consistencia entre planos. Documenta la continuidad visual y narrativa.
- **Responsabilidad real**: anota cada plano con detalles de raccord (vestuario, posicionamiento, objetos), valida la coherencia entre escenas.
- **Modulos principales**: `script_analysis`, `character_bible`, `shotlist`, `project_memory`.
- **Permisos read**: `project.read`, `script.read`, `character_bible.read`, `shotlist.read`, `concept_art.read`.
- **Permisos write/generate/export**: `script.write` (anotaciones de continuidad), `character_bible.write` (entradas de raccord), `shotlist.write` (notas), `ai.run` (solo modulos de analisis).
- **Restricciones**: no edita storyboard final; no aprueba nada.
- **Notas SaaS**: `org_role=member`. Sin acceso a billing, admin, delivery.

### 3.7 Direccion de fotografia (`direccion_fotografia`)

- **Descripcion**: define el look, lente, luz. Dirige camara y aprueba el plan fotografico.
- **Responsabilidad real**: planifica la iluminacion, el movimento de camara, la consistencia visual entre escenas. Trabaja con camara y gaffer.
- **Modulos principales**: `concept_art`, `storyboard_ai`, `shooting_plan`, `shotlist`, `shotlist_camera` (submodulo).
- **Permisos read**: `project.read`, `script.read`, `concept_art.read`, `storyboard.read`, `shotlist.read`.
- **Permisos write/generate/export**: `concept_art.generate`, `storyboard.generate`, `shooting_plan.write` (solo bloque fotografico), `shotlist.write` (solo entradas de camara), `ai.run`, `export.generate`.
- **Restricciones**: no edita guion narrativo; no edita presupuesto total.
- **Notas SaaS**: `org_role=member` tipicamente. Sin acceso a billing.

### 3.8 Camara (`camara`)

- **Descripcion**: opera camara. No decide plano, ejecuta el plan fotografico definido por la direccion de fotografia.
- **Responsabilidad real**: enfoca, mueve, opera el equipo. Reporta al director de fotografia.
- **Modulos principales**: `shotlist`, `shotlist_camera` (submodulo).
- **Permisos read**: `project.read`, `shotlist.read`, `shooting_plan.read`.
- **Permisos write/generate/export**: `shotlist.write` (solo notas tecnicas de camara).
- **Restricciones**: no ejecuta IA; no edita nada creativo.
- **Notas SaaS**: `org_role=member`. Sin acceso a creditos, billing, admin.

### 3.9 DIT/Data wrangler (`dit_data_wrangler`)

- **Descripcion**: ingesta, organiza y respalda material en set. Es el guardian de los datos durante el rodaje.
- **Responsabilidad real**: descarga tarjetas, respalda en multiples destinos, cataloga el material, reporta al director de fotografia.
- **Modulos principales**: `shotlist`, `integrations_n8n` (submodulo de backup), `project_memory`.
- **Permisos read**: `project.read`, `shotlist.read`, `sound.read`, `delivery.read`.
- **Permisos write/generate/export**: `asset.write` (subida de material), `shotlist.write` (catalogo), `export.generate` (manifests y reports), `ai.run` (solo catalogacion automatica).
- **Restricciones**: no edita guion ni storyboard; no aprueba nada creativo.
- **Notas SaaS**: `org_role=member`. Acceso a integraciones limitado por plan.

### 3.10 Sonido directo (`sonido_directo`)

- **Descripcion**: captura audio en set. Es autoridad sobre la calidad sonora original.
- **Responsabilidad real**: microfonea, registra, monitorea, reporta al director. Es el dueno de la calidad del audio original.
- **Modulos principales**: `sound_ingest`, `shooting_plan`, `shotlist`.
- **Permisos read**: `project.read`, `script.read` (para identificar replicas), `shotlist.read`, `sound.read`.
- **Permisos write/generate/export**: `asset.write` (subida de audio), `sound.ingest`, `ai.run` (solo modulos de audio: `sound.process`), `shotlist.write` (entradas de sonido).
- **Restricciones**: no edita visual; no aprueba; no edita presupuesto.
- **Notas SaaS**: `org_role=member`. Acceso al modulo `sound_ingest` segun plan (ver matriz modulo x plan).

### 3.11 Arte (`direccion_arte`)

- **Descripcion**: define y ejecuta el diseno de produccion. Es la cabeza del departamento de arte.
- **Responsabilidad real**: define la estetica de decorados, vestuario, atrezzo, maquillaje. Trabaja con `concept_art` y `character_bible`.
- **Modulos principales**: `concept_art`, `character_bible`, `shotlist`.
- **Permisos read**: `project.read`, `script.read`, `storyboard.read`, `concept_art.read`, `character_bible.read`.
- **Permisos write/generate/export**: `concept_art.generate`, `character_bible.write`, `shotlist.write` (entradas de arte), `ai.run`, `export.generate`.
- **Restricciones**: no edita guion; no edita presupuesto; no aprueba pitch financiero.
- **Notas SaaS**: `org_role=member`. Ve creditos solo si el plan lo permite.

### 3.12 Vestuario (`vestuario`)

- **Descripcion**: diseno y ejecucion de vestuario.
- **Responsabilidad real**: diseña el vestuario por personaje, escena y epoca; coordina con arte y con el elenco.
- **Modulos principales**: `character_bible`, `concept_art`.
- **Permisos read**: `project.read`, `script.read`, `character_bible.read`, `concept_art.read`.
- **Permisos write/generate/export**: `character_bible.write` (entradas de vestuario), `concept_art.generate`, `ai.run`.
- **Restricciones**: no edita presupuesto; no aprueba.
- **Notas SaaS**: `org_role=member`. Sin acceso a billing, admin.

### 3.13 Maquillaje/peluqueria (`maquillaje_peluqueria`)

- **Descripcion**: diseno y ejecucion de maquillaje y peluqueria.
- **Responsabilidad real**: disena el look fisico de los personajes por escena, ejecuta en set.
- **Modulos principales**: `character_bible`, `concept_art`.
- **Permisos read**: `project.read`, `script.read`, `character_bible.read`, `concept_art.read`.
- **Permisos write/generate/export**: `character_bible.write` (entradas de maquillaje/peluqueria), `concept_art.generate`, `ai.run`.
- **Restricciones**: no edita presupuesto; no aprueba.
- **Notas SaaS**: `org_role=member`. Sin acceso a billing, admin.

### 3.14 Casting (`casting`)

- **Descripcion**: seleccion de elenco.
- **Responsabilidad real**: evalua candidatos, mantiene la base de actores, propone elenco, coordina pruebas.
- **Modulos principales**: `character_bible`, `producer_pitch`.
- **Permisos read**: `project.read`, `script.read`, `character_bible.read`, `concept_art.read`.
- **Permisos write/generate/export**: `character_bible.write` (entradas de casting), `ai.run` (solo modulos de matching y pruebas).
- **Restricciones**: no edita storyboard; no edita presupuesto.
- **Notas SaaS**: `org_role=member`. Maneja datos personales de candidatos: aplica retencion legal y GDPR/avPD.

### 3.15 Montaje (`montaje`)

- **Descripcion**: edicion narrativa. Es el responsable del corte final.
- **Responsabilidad real**: organiza el material, propone el corte, integra musica y efectos temporales, entrega al director para aprobacion.
- **Modulos principales**: `script_analysis`, `shotlist`, `project_memory`.
- **Permisos read**: `project.read`, `script.read`, `storyboard.read`, `shotlist.read`, `sound.read`, `client_feedback.read`.
- **Permisos write/generate/export**: `script.write` (entradas de edicion), `shotlist.write` (entradas de EDL), `ai.run` (solo modulos de edicion), `export.generate` (EDL, AAF, cortes previos).
- **Restricciones**: no edita presupuesto; no aprueba delivery final (lo hace `director` o `delivery`).
- **Notas SaaS**: `org_role=member`. Sin acceso a billing.

### 3.16 Postproduccion de sonido (`postproduccion_sonido`)

- **Descripcion**: diseno sonoro, mezcla, edicion de dialogo, Foley.
- **Responsabilidad real**: toma el audio original entregado por `sonido_directo` y lo termina: limpia, anade ambiente, Foley, musica, mezcla final.
- **Modulos principales**: `sound_ingest`, `project_memory`.
- **Permisos read**: `project.read`, `script.read`, `sound.read`, `shotlist.read`.
- **Permisos write/generate/export**: `asset.write` (subida de material sonoro), `sound.ingest`, `sound.process` (con IA), `ai.run` (modulos de audio), `export.generate` (mezcla, stems, M+E).
- **Restricciones**: no edita visual; no aprueba delivery al cliente.
- **Notas SaaS**: `org_role=member`. Acceso al modulo `sound_ingest` segun plan.

### 3.17 VFX (`vfx`)

- **Descripcion**: efectos visuales, composicion, simulaciones.
- **Responsabilidad real**: planifica y ejecuta los planos con elementos digitales, integra con el material rodado.
- **Modulos principales**: `storyboard_ai`, `concept_art`, `shotlist`.
- **Permisos read**: `project.read`, `script.read`, `storyboard.read`, `concept_art.read`, `shotlist.read`.
- **Permisos write/generate/export**: `storyboard.generate` (previz), `concept_art.generate`, `shotlist.write` (entradas VFX), `ai.run` (modulos de imagen/video), `export.generate` (renders intermedios).
- **Restricciones**: no edita guion narrativo; no edita presupuesto total.
- **Notas SaaS**: `org_role=member`. Consumo alto de creditos y almacenamiento; verifica cuota del plan.

### 3.18 Color (`color`)

- **Descripcion**: etalonaje y direccion de color.
- **Responsabilidad real**: define la paleta, aplica look por escena, entrega el master coloreado.
- **Modulos principales**: `shotlist`, `export.generate`.
- **Permisos read**: `project.read`, `script.read`, `shotlist.read`, `storyboard.read`, `concept_art.read`.
- **Permisos write/generate/export**: `shotlist.write` (entradas de color), `ai.run` (modulos de LUT y color matching), `export.generate` (master coloreado).
- **Restricciones**: no edita guion; no aprueba delivery al cliente (lo hace `director` o `delivery`).
- **Notas SaaS**: `org_role=member`. Acceso a `advanced_exports` segun plan.

### 3.19 Delivery (`delivery`)

- **Descripcion**: entrega tecnica: masters, QC, deliverables por plataforma.
- **Responsabilidad real**: prepara el master final, valida QC, genera los deliverables para cada plataforma (broadcast, streaming, festivales), los entrega.
- **Modulos principales**: `delivery`, `distribution_pack`.
- **Permisos read**: `project.read`, `shotlist.read`, `client_feedback.read`, `delivery.read`.
- **Permisos write/generate/export**: `delivery.export`, `delivery.publish`, `distribution.write`, `export.generate`.
- **Restricciones**: no edita produccion; no edita contenido creativo.
- **Notas SaaS**: `org_role=member`. Acceso al modulo `delivery` y `advanced_exports` segun plan.

### 3.20 Distribucion/ventas (`distribucion_ventas`)

- **Descripcion**: comercializacion, festivales, ventas internacionales, agentes.
- **Responsabilidad real**: representa el proyecto en mercados, festivales, agentes de venta. Genera materiales comerciales.
- **Modulos principales**: `producer_pitch`, `distribution_pack`, `funding`.
- **Permisos read**: `project.read` (lectura), `funding.read`, `client_feedback.read`.
- **Permisos write/generate/export**: `pitch.generate`, `distribution.write`, `export.generate` (materiales comerciales), `delivery.publish` (en mercados).
- **Restricciones**: no edita contenido creativo; no ve costos internos detallados (solo agregados).
- **Notas SaaS**: `org_role=member`. Maneja datos comerciales sensibles; aplica retencion legal.

### 3.21 Cliente externo/revisor (`cliente_externo`, `(ext)`)

- **Descripcion**: marca o cliente final. Solo revisa y aprueba.
- **Responsabilidad real**: ve los entregables que el productor le muestra, deja feedback, aprueba o pide cambios.
- **Modulos principales**: `client_feedback`, `producer_pitch` (preview), `delivery` (preview).
- **Permisos read**: `project.read` (solo donde invitado), `client_feedback.read`, `delivery.read` (solo preview).
- **Permisos write/generate/export**: `client_feedback.write`, `ai.approve` (aprobar/rechazar propuestas de IA, no `ai.run`).
- **Restricciones**: no edita nada; no ve creditos; no ve billing; no ve costos internos; no ve admin.
- **Notas SaaS**: pertenece a la organizacion cliente del proyecto, no a la productora. Acceso acotado a los proyectos donde esta invitado. Auditable como externo.

### 3.22 Revisor invitado (`revisor_invitado`, `(ext)`)

- **Descripcion**: consultor,评委 externo, actor top invitado, director invitado. Acceso a un solo proyecto, acotado temporalmente.
- **Responsabilidad real**: ve lo que el productor o el director le muestra, deja feedback opcional.
- **Modulos principales**: el subconjunto que el productor determine al invitar.
- **Permisos read**: `project.read` (un solo proyecto), `client_feedback.read`.
- **Permisos write/generate/export**: `client_feedback.write` (opcional, decidido al invitar).
- **Restricciones**: sin acceso a creditos, billing, admin, otros proyectos; tipicamente con `expires_at`.
- **Notas SaaS**: `org_role=external`. Si se le invita a un segundo proyecto, se crea una membresia nueva con un `access_grant` por proyecto; nunca acumula permisos entre proyectos.

## 4. Permisos base

31 permisos en notacion `domain.action`, agrupados por dominio. La agrupacion es solo documental: el permiso es atomico y se enforza individualmente.

### 4.1 Organizacion y billing

- `organization.manage`: configurar la organizacion (logos, dominios, SSO basico).
- `billing.read`: ver suscripcion, facturas, historial de pagos.
- `billing.manage`: cambiar plan, gestionar metodo de pago, descargar facturas.
- `user.invite`: invitar miembros a la organizacion o al proyecto.
- `user.remove`: quitar miembros de la organizacion o del proyecto.
- `audit.read`: consultar el log de auditoria de la organizacion o del proyecto.

### 4.2 Proyecto y equipos

- `project.read`: ver metadatos y assets de un proyecto.
- `project.write`: editar metadatos del proyecto (nombre, tipo, estado, lead).
- `project.admin`: archivar, eliminar, transferir propiedad, cambiar configuracion de proyecto.
- `asset.read`: ver y descargar assets (imagenes, videos, audios, PDFs).
- `asset.write`: subir, eliminar, etiquetar assets.

### 4.3 Guion y narrativa

- `script.read`: ver guion y analisis.
- `script.write`: editar guion (incluye anotaciones de continuidad).

### 4.4 Storyboard y concept art

- `storyboard.read`: ver hojas de storyboard.
- `storyboard.generate`: crear y renderizar hojas de storyboard (con IA).

### 4.5 Biblia de personaje

- `character_bible.read`: ver biblia de personaje.
- `character_bible.write`: editar entradas de biblia (incluye vestuario, maquillaje, casting, raccord).

### 4.6 Sonido

- `sound.read`: escuchar y descargar material sonoro.
- `sound.ingest`: subir y procesar material sonoro (incluye IA de transcripcion y etiquetado).

### 4.7 Presupuesto y financiacion

- `budget.read`: ver presupuesto.
- `budget.write`: editar presupuesto (lineas, totales, categorias).
- `funding.read`: ver dossieres de financiacion y materiales de pitch.
- `funding.write`: editar dossieres de financiacion y materiales de pitch.

### 4.8 Delivery y distribucion

- `delivery.read`: ver paquetes de delivery y masters.
- `delivery.export`: generar deliverables tecnicos (EDL, AAF, ProRes, DNxHR, IMF).
- `delivery.publish`: publicar entregable a cliente o plataforma externa.
- `distribution.read`: ver materiales de distribucion y ventas.
- `distribution.write`: editar y publicar materiales de distribucion y ventas.

### 4.9 IA, creditos y feedback

- `ai.run`: permiso paraguas para ejecutar cualquier job de IA. Se evalua junto al permiso especifico del modulo (`storyboard.generate` + `ai.run`).
- `ai.approve`: aprobar o rechazar un resultado de IA o un plan de uso de IA. No ejecuta.
- `credits.read`: ver saldo y consumo de creditos.
- `credits.manage`: comprar paquete de creditos adicional; asignar pool a proyecto.
- `client_feedback.read`: ver feedback del cliente externo.
- `client_feedback.write`: dejar feedback, aprobar o rechazar entregables en modo cliente.

### 4.10 Notas de aplicacion

- `ai.run` siempre se evalua junto al permiso especifico. `storyboard.generate` sin `ai.run` falla; `ai.run` sin permiso especifico no inicia ningun job.
- `ai.approve` lo tienen Productor, Director y Cliente externo. Productor Ejecutivo solo en modo aprobacion, no ejecucion.
- `billing.manage`, `credits.manage`, `user.invite`, `user.remove`, `audit.read` son permisos de organizacion. Solo `org_role=owner`, `admin`, `billing` los tienen.
- `client_feedback.read` y `client_feedback.write` aplican solo a usuarios externos o a miembros con rol `cliente_externo` o `revisor_invitado`. Un Director puede leer feedback (lo tiene via `client_feedback.read` por su rol), pero un Productor no escribe feedback (lo hace el cliente).
- Permisos no listados aqui no existen. Si una accion nueva lo requiere, se anade al contrato y se versiona en este documento antes de implementarse.

## 5. Matriz rol x permiso

Compacta, 22 filas por 12 columnas agrupadas. Codigos: `R` = read, `W` = write, `G` = generate/IA, `E` = export, `A` = admin, `C` = condicionado, `N` = no permitido.

Grupos:
- **Org**: `organization.manage`, `billing.read`, `billing.manage`, `user.invite`, `user.remove`, `audit.read`.
- **Project**: `project.read`, `project.write`, `project.admin`.
- **Asset**: `asset.read`, `asset.write`.
- **Script**: `script.read`, `script.write`.
- **Story**: `storyboard.read`, `storyboard.generate`.
- **Bible**: `character_bible.read`, `character_bible.write`.
- **Sound**: `sound.read`, `sound.ingest`.
- **Budget**: `budget.read`, `budget.write`, `funding.read`, `funding.write`.
- **Delivery**: `delivery.read`, `delivery.export`, `delivery.publish`, `distribution.read`, `distribution.write`.
- **AI**: `ai.run`, `ai.approve`.
- **Credits**: `credits.read`, `credits.manage`.
- **Feedback**: `client_feedback.read`, `client_feedback.write`.

| Rol | Org | Project | Asset | Script | Story | Bible | Sound | Budget | Delivery | AI | Credits | Feedback |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `productor` | W,A | R,W,A | R,W | R,W | R,G | R,W | R,W | R,W | R,E,A | G,A | R,W | R |
| `productor_ejecutivo` | R,C | R | R | R | R | R | R | R,W (budget+funding W) | R | A (no G) | R | R |
| `jefe_produccion` | N | R,W | R,W | R | R | R | R | R,W (costes) | R | G (planif) | N | R |
| `director` | N | R,W | R,W | R,W | R,G | R,W | R | R | R | G,A | R (C) | R,W |
| `ayudante_direccion` | N | R,W | R,W | R | R | R | R | R | R | G (planif) | N | R |
| `script_continuidad` | N | R,W | R,W | R,W (anot) | R | R,W (raccord) | R | R | R | G (analisis) | N | R |
| `direccion_fotografia` | N | R,W | R,W | R | R,G | R | R | R | R | G | N | R |
| `camara` | N | R,W | R,W | R | R | R | R | R | R | N | N | R |
| `dit_data_wrangler` | N | R,W | R,W | R | R | R | R | R | R | G (catalog) | N | R |
| `sonido_directo` | N | R,W | R,W | R (replicas) | R | R | R,W | R | R | G (audio only) | N | R |
| `direccion_arte` | N | R,W | R,W | R | R | R,W | R | R | R | G | R (C) | R |
| `vestuario` | N | R,W | R,W | R | R | R,W | R | R | R | G | N | R |
| `maquillaje_peluqueria` | N | R,W | R,W | R | R | R,W | R | R | R | G | N | R |
| `casting` | N | R,W | R,W | R | R | R,W | R | R | R | G (matching) | N | R |
| `montaje` | N | R,W | R,W | R,W (EDL) | R | R | R | R | R | G (edit) | N | R |
| `postproduccion_sonido` | N | R,W | R,W | R | R | R | R,W | R | R | G (audio) | N | R |
| `vfx` | N | R,W | R,W | R | R,G | R | R | R | R | G | N | R |
| `color` | N | R,W | R,W | R | R | R | R | R | R | G (LUT) | N | R |
| `delivery` | N | R,W | R,W | R | R | R | R | R | R,E,A | N | N | R |
| `distribucion_ventas` | N | R (C) | R | R | R | R | R | R (C, agregados) | R,W (publish) | A (no G) | N | R |
| `cliente_externo` (ext) | N | R (C, invitado) | R (preview) | N | R (preview) | N | N | N | R (preview) | A (no G) | N | R,W |
| `revisor_invitado` (ext) | N | R (1 proyecto) | R (preview) | N | R (preview) | N | N | N | R (preview) | N | N | R,W (opcional) |

**Notas:**

- `C` = condicionado: el permiso aplica solo bajo condiciones (plan que habilita el modulo, proyecto donde esta invitado, organizacion que lo adquirio como add-on, cuota no agotada).
- `R (C)` para `distribucion_ventas` significa que el rol ve solo informacion agregada, no costos internos detallados.
- `A` en columna AI para `cliente_externo` significa que puede `ai.approve` (aprobar/rechazar) pero no `ai.run`.
- `productor` y `director` tienen `A` en AI porque pueden aprobar planes de uso de IA y rechazar resultados.
- Roles tecnicos y administrativos especiales se tratan en la seccion 7.

## 6. Matriz rol x modulo

Compacta, 22 filas por 19 columnas. Codigos:
- `F` = full (read + write + generate + export, con `project.admin` si aplica).
- `C` = contribute (read + write, sin `project.admin`).
- `R` = read (lectura del modulo).
- `V` = review (read + `client_feedback.write` para aprobacion).
- `P` = plan-dependent (lectura por defecto; escritura/g.generate solo si el plan habilita el modulo y el usuario tiene cuota).
- `N` = none (no ve el modulo, no aparece en la navegacion).

Modulos (19):

1. `script_analysis`
2. `project_memory`
3. `storyboard_ai`
4. `concept_art`
5. `character_bible`
6. `budget`
7. `shooting_plan`
8. `shotlist`
9. `funding`
10. `producer_pitch`
11. `delivery`
12. `distribution_pack`
13. `sound_ingest`
14. `client_feedback`
15. `crm_sales`
16. `ai_pipeline_builder`
17. `integrations_n8n`
18. `advanced_exports`
19. `admin_analytics`

| Rol \ Modulo | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `productor` | F | F | F | C | C | F | C | C | F | F | F | F | C | V | C | P | P | P | P |
| `productor_ejecutivo` | R | R | R | R | R | F | R | R | F | F | R | R | R | R | R | N | N | N | P |
| `jefe_produccion` | R | C | N | N | N | C | C | C | R | R | R | R | N | R | N | P | N | N | N |
| `director` | F | C | F | F | F | R | C | C | C | C | C | C | C | V | N | P | N | N | N |
| `ayudante_direccion` | C | C | N | N | N | R | C | C | N | R | N | N | N | R | N | N | N | N | N |
| `script_continuidad` | F | C | N | R | C | N | R | C | N | N | N | N | N | R | N | N | N | N | N |
| `direccion_fotografia` | R | C | F | C | R | R | C | C | N | R | N | N | N | R | N | N | N | C | N |
| `camara` | R | C | N | N | N | N | R | C | N | N | N | N | N | R | N | N | N | N | N |
| `dit_data_wrangler` | R | C | N | N | N | N | R | C | N | N | R | R | N | R | N | P | P | N | N |
| `sonido_directo` | R | C | N | N | N | N | R | C | N | N | N | N | F | R | N | N | N | N | N |
| `direccion_arte` | R | C | C | F | F | R | R | C | N | R | N | N | N | R | N | N | N | N | N |
| `vestuario` | R | C | N | C | F | N | N | R | N | N | N | N | N | R | N | N | N | N | N |
| `maquillaje_peluqueria` | R | C | N | C | F | N | N | R | N | N | N | N | N | R | N | N | N | N | N |
| `casting` | R | C | N | R | F | N | N | R | N | C | N | N | N | R | N | N | N | N | N |
| `montaje` | C | C | R | R | R | N | R | C | N | N | N | N | R | R | N | N | N | N | N |
| `postproduccion_sonido` | R | C | N | N | N | N | R | R | N | N | N | N | F | R | N | N | N | C | N |
| `vfx` | R | C | F | C | R | N | R | C | N | N | N | N | N | R | N | N | N | C | N |
| `color` | R | C | R | R | R | N | R | C | N | N | N | N | N | R | N | N | N | F | N |
| `delivery` | N | R | N | N | N | N | N | R | N | R | F | F | N | R | N | N | N | F | N |
| `distribucion_ventas` | R | R | N | N | N | R (C) | N | N | R | F | R | F | N | R | F | N | N | N | N |
| `cliente_externo` (ext) | N | R | R (preview) | N | N | N | N | N | N | R (preview) | R (preview) | N | N | V | N | N | N | N | N |
| `revisor_invitado` (ext) | N | R | R (preview) | N | N | N | N | N | N | R (preview) | R (preview) | N | N | V (opc) | N | N | N | N | N |

**Notas:**

- `F` incluye export si el rol lo tiene; en `producer_pitch` el `F` significa generar pitch + exportar; en `delivery` significa exportar + publicar.
- `P` (plan-dependent) aplica a `ai_pipeline_builder`, `integrations_n8n`, `advanced_exports`, `admin_analytics`: el rol Productor y Director pueden usarlos si su plan los incluye como `incluido` o `add-on` activo; en caso contrario, el modulo no aparece en su navegacion.
- `R (preview)` para cliente externo: lectura en modo preview, no puede descargar el original sin autorizacion; el Productor controla que se muestra.
- Modulos `crm_sales`, `ai_pipeline_builder`, `integrations_n8n`, `advanced_exports`, `admin_analytics` no aparecen (`N`) para la mayoria de roles creativos; son modulos administrativos o de pipeline reservados a Productor, Director (parcial), DIT (integraciones), Delivery (advanced_exports), Distribucion (crm_sales), y admin tecnicos.
- El modulo `sound_ingest` es `F` para `sonido_directo` y `postproduccion_sonido`, `C` para `productor` y `director` (pueden revisar ingestion), `N` para el resto de roles creativos que no son de sonido.

## 7. Roles especiales

Ademas de los 22 roles de proyecto, CID modela 8 roles especiales. Estos se asignan a nivel de organizacion o son cuentas de servicio; no son roles de proyecto.

### 7.1 `organization_owner`

- **Scope**: organizacion completa.
- **Quien lo tiene**: el usuario que creo la organizacion o a quien el owner anterior transfirio la propiedad.
- **Permisos**: todos los de `organization_admin` mas `organization.manage`, `billing.manage`, capacidad de transferir ownership, capacidad de eliminar la organizacion (con periodo de gracia).
- **Restricciones**: no hay mas de uno por organizacion. Si el owner abandona, la organizacion queda en estado `ownerless` y un admin puede ascender a otro o el sistema bloquea operaciones criticas hasta que se resuelva.
- **SaaS**: equivalente a `org_role=owner`.

### 7.2 `organization_admin`

- **Scope**: organizacion completa.
- **Quien lo tiene**: usuarios designados por el owner.
- **Permisos**: `organization.manage`, `billing.manage`, `user.invite`, `user.remove`, `user.invite` a cualquier proyecto, `audit.read` completo, `credits.manage`.
- **Restricciones**: no puede transferir la organizacion a otro usuario. No puede eliminar la organizacion.
- **SaaS**: equivalente a `org_role=admin`. Puede coincidir con `project_role=productor` o cualquier otro.

### 7.3 `project_admin`

- **Scope**: un proyecto concreto.
- **Quien lo tiene**: cualquier usuario con `project_role=productor` o `project_admin` flag.
- **Permisos**: todos los de `productor` mas `project.admin` (archivar, eliminar, transferir propiedad del proyecto).
- **Restricciones**: la transferencia de propiedad del proyecto es exclusiva del `project_admin` actual; un `organization_admin` no puede forzar una transferencia.
- **SaaS**: se modela como un flag sobre el `project_role` o como un `project_role` explicito. Implementacion: unico rol con `project.admin`.

### 7.4 `billing_admin`

- **Scope**: organizacion, solo modulo billing.
- **Quien lo tiene**: usuarios con `org_role=billing` o designados por owner/admin.
- **Permisos**: `billing.read`, `billing.manage`, `credits.read`, `credits.manage`. Ve invoices y descarga facturas.
- **Restricciones**: no ve produccion (no tiene `project.read` por defecto); no edita contenido creativo; no ve log de auditoria de proyectos.
- **SaaS**: equivalente a `org_role=billing`. Pensado para perfiles financieros/financieros de la productora que no son productores.

### 7.5 `external_reviewer`

- **Scope**: un proyecto puntual, con `expires_at`.
- **Quien lo tiene**: usuarios invitados desde fuera de la organizacion.
- **Permisos**: `project.read` (un solo proyecto), `client_feedback.read`, `client_feedback.write` (opcional), `ai.approve` (opcional).
- **Restricciones**: no ve costos, billing, admin, otros proyectos, creditos. Acceso temporal por defecto (7-30 dias).
- **SaaS**: union de `cliente_externo` y `revisor_invitado` cuando la distincion no es relevante. Implementacion: misma estructura, scope reducido.

### 7.6 `global_admin`

- **Scope**: plataforma completa, no es un usuario normal.
- **Quien lo tiene**: staff CID con flag `is_global_admin=true`.
- **Permisos**: `admin.platform` (unico permiso exclusivo), acceso a cualquier organizacion solo bajo `support_session=true` con justificacion obligatoria, `audit.read` cross-organization.
- **Restricciones**: no puede asignarse `credits.manage` ni `billing.manage` a si mismo. Toda sesion de soporte queda registrada con scope explicito. No puede ver inputs de IA del cliente sin autorizacion del cliente.
- **SaaS**: rol de staff, no asignable a clientes. Su uso esta regulado por la politica de soporte de CID.

### 7.7 `service_account`

- **Scope**: organizacion, no es un usuario humano.
- **Quien lo tiene**: lo crea un `organization_admin` para automatizaciones (CI, scripts, integraciones).
- **Permisos**: configurables por el admin al crear la cuenta. Tipicamente: `project.read`, `script.read`, `storyboard.read`, `asset.read`. Nunca `billing.manage`, `credits.manage`, `user.invite`.
- **Restricciones**: no puede autenticarse via OAuth de usuario; usa API key con rotacion. Toda accion queda registrada con `actor_type=service_account`. No puede ser owner de la organizacion.
- **SaaS**: para integraciones n8n, ComfyUI server-side, sincronizaciones con Drive/Frame.io. Limite de cuentas por plan.

### 7.8 `ai_worker`

- **Scope**: plataforma, no es un usuario de cliente.
- **Quien lo tiene**: lo asigna el sistema (ComfyUI, Ollama, motor de transcripcion, generador de embeddings).
- **Permisos**: ninguno en el sentido humano; es un actor tecnico de los jobs de IA. Aparece en `ai_job.actor_type=ai_worker`.
- **Restricciones**: nunca tiene `permission_key` propio. Sus acciones se enforzan via el `permission_key_used` del job (`storyboard.generate`, `sound.process`, etc.) y via la `organization_id` del job.
- **SaaS**: rol interno, no aparece en el panel de miembros. Existe solo para trazabilidad y para distinguir acciones humanas de automaticas en auditoria.

## 8. Reglas de permisos efectivos

Los permisos que un usuario tiene en un instante se calculan como la interseccion de seis dimensiones. La pseudologica se aplica en el orden indicado: si alguna dimension rechaza, la accion se rechaza.

```
effective_permissions(
  user, project, action
) = plan_modules(plan)
  ∩ module_active(plan, action.module_key)
  ∩ role_permissions(user.role_in_project)
  ∩ explicit_grants(user, project, action)
  ∩ project_state(project, action)
  ∩ credit_state(organization, action)
```

Reglas por dimension:

- **plan_modules(plan)**: el plan del usuario en su organizacion debe incluir el modulo de la accion. Si el modulo es `N` (no incluido) en su plan, la accion se rechaza aunque el rol la permita.
- **module_active(plan, action.module_key)**: el modulo debe estar activo (no suspendido, no expirado, no en gracia de downgrade). Si la organizacion hizo downgrade, los modulos超出 quedan en `graced` durante 30 dias; pasado ese tiempo, `module_active=false` y la accion se rechaza.
- **role_permissions(user.role_in_project)**: el `project_role` del usuario en el proyecto debe incluir el `permission_key` de la accion. Si no, se rechaza con `403 Forbidden`.
- **explicit_grants(user, project, action)**: si un admin concedio o denego explicitamente un permiso a este usuario en este proyecto, ese grant tiene precedencia sobre el permiso por defecto del rol. Grants son por usuario-proyecto, no por organizacion.
- **project_state(project, action)**: el estado del proyecto debe permitir la accion. `archivado` rechaza todo salvo `project.read` para auditores. `delivery` rechaza `script.write` y `storyboard.generate` (la produccion esta cerrada). `pre_produccion` permite planificacion; rechaza `delivery.publish`.
- **credit_state(organization, action)**: si la accion requiere IA (`ai.run` implicito), el saldo de la organizacion debe ser `>= credit_estimate`. Si no, se rechaza con `402 Payment Required`.

### 8.1 Casos de la pseudologica

- **Modulo no incluido por plan**: el plan Starter no incluye `sound_ingest`. Un Productor con plan Starter intenta hacer `sound.ingest`. `plan_modules(plan) = {}` para `sound_ingest`; `module_active = false`. Resultado: `403` con mensaje "El modulo Sound Ingest no esta incluido en tu plan Starter. Puedes activarlo como add-on o subir a Pro."
- **Rol sin permiso aunque el plan lo incluya**: el plan Pro incluye `budget.write`. Un Director intenta editar presupuesto. `role_permissions(director) = { budget.read, ... }`; `budget.write` no esta. Resultado: `403` con mensaje "Esta accion requiere el rol Productor o Jefe de Produccion."
- **Usuario externo con acceso limitado**: un `cliente_externo` intenta descargar el master coloreado. `role_permissions(cliente_externo) = { project.read, client_feedback.read/write, ai.approve }`; `delivery.export` no esta. Resultado: `403` con mensaje "Como cliente externo, solo puedes revisar y dejar feedback, no descargar masters."
- **Creditos agotados**: Productor en plan Pro intenta generar 5 hojas de storyboard (5 x 30 = 150 creditos). Saldo actual 80. `credit_state = 80 < 150`. Resultado: `402` con CTA a comprar paquete o subir plan.
- **Proyecto archivado**: un Director intenta generar storyboard en proyecto archivado. `project_state(archivado, storyboard.generate) = false`. Resultado: `403` con mensaje "El proyecto esta archivado. Para reactivarlo, contacta al administrador de la organizacion."
- **Override de admin**: un `organization_admin` usa `admin_override` para forzar la generacion de un storyboard en un proyecto archivado (caso excepcional de recuperacion). El sistema registra `admin_override_used` con motivo obligatorio, ejecuta la accion, mantiene el resultado accesible solo al admin y al productor. No es transparente al Director.
- **Enterprise custom permission**: una organizacion Enterprise con un acuerdo a medida tiene un permiso `legal.review.write` que no esta en la lista canonica. Se trata como override de organizacion; el backend gating lo reconoce por estar en la `organization.custom_permissions`. Documentado en este contrato v2 cuando se estabilice.

### 8.2 Orden de evaluacion

El backend evalua en este orden para minimizar trabajo y dar mensajes claros:

1. `get_tenant_context` (ya autenticado, `organization_id` resuelto).
2. `validate_project_access` (proyecto existe, pertenece al tenant; `404` si no).
3. `require_module_access(module_key)` (plan incluye el modulo, no suspendido; `403` si no).
4. `require_write_permission` (si la accion es mutante) o `require_read_permission` (si es read).
5. Evaluacion del `permission_key` especifico contra los permisos efectivos del usuario.
6. Evaluacion de `project_state` para la accion concreta.
7. Evaluacion de `credit_state` si la accion es IA.
8. Reserva de creditos, ejecucion, cargo o rollback.

Si cualquier paso falla, los siguientes no se ejecutan. El frontend recibe el primer error y muestra el mensaje correspondiente.

## 9. Acciones criticas

Catalogo de las 13 acciones mas relevantes del producto. Para cada accion: permiso, modulo, write, creditos, rol tipico.

| # | Accion | Permiso requerido | Modulo requerido | Write | Creditos | Rol tipico permitido |
|---|---|---|---|---|---|---|
| 1 | Crear proyecto | `project.write` + `project.admin` | `project_memory` | si | 0 | `organization_admin`, `organization_owner` |
| 2 | Invitar usuario al proyecto | `user.invite` | n/a (organizacion) | si | 0 | `organization_admin`, `project_admin`, `productor` (en su proyecto) |
| 3 | Subir guion | `script.write` + `asset.write` | `script_analysis` | si | 0 | `director`, `script_continuidad`, `productor` |
| 4 | Analizar guion con IA | `ai.run` + `script.read` | `script_analysis` | si | 20-100 | `director`, `productor`, `script_continuidad`, `productor_ejecutivo` |
| 5 | Generar hoja de storyboard | `storyboard.generate` + `ai.run` | `storyboard_ai` | si | 30-60 | `director`, `direccion_fotografia`, `direccion_arte`, `vfx`, `productor` |
| 6 | Render ComfyUI | `storyboard.generate` + `concept_art.generate` + `ai.run` | `storyboard_ai`, `concept_art` | si | 30-90 | `director`, `direccion_fotografia`, `direccion_arte`, `vfx` |
| 7 | Ingerir sonido | `sound.ingest` + `asset.write` + `ai.run` | `sound_ingest` | si | 15-25/h | `sonido_directo`, `postproduccion_sonido` |
| 8 | Generar dossier financiacion | `funding.write` + `pitch.generate` + `ai.run` | `funding`, `producer_pitch` | si | 80 | `productor`, `productor_ejecutivo`, `distribucion_ventas` |
| 9 | Exportar delivery | `delivery.export` + `export.generate` | `delivery` | si | 20 | `delivery`, `color`, `montaje`, `vfx` |
| 10 | Ver feedback cliente | `client_feedback.read` | `client_feedback` | no | 0 | `productor`, `director`, `cliente_externo`, `revisor_invitado` |
| 11 | Gestionar billing | `billing.manage` | n/a (organizacion) | si | 0 | `organization_owner`, `organization_admin`, `billing_admin` |
| 12 | Cambiar plan | `billing.manage` + `organization.manage` | n/a (organizacion) | si | 0 | `organization_owner`, `organization_admin` |
| 13 | Ver auditoria | `audit.read` | n/a (organizacion o proyecto) | no | 0 | `organization_owner`, `organization_admin`, `project_admin`, `global_admin` |

**Notas:**

- `Write` indica si la accion muta estado. Una accion con `Write=no` puede leerse pero no modificarse; un Productor puede ver auditoria pero no editarla.
- `Creditos` es la estimacion por unidad. Acciones que generan multiples unidades (varias hojas de storyboard) multiplican el coste.
- `Rol tipico permitido` no es exhaustivo: la columna `Permiso requerido` es la verdad. Si un rol no listado tiene el permiso, puede ejecutar la accion (salvo restricciones de plan o modulo).
- Las acciones 1, 2, 11, 12 son de organizacion: no se evalua `project_state`; se evalua `organization_state` (suspendida, deleted).
- Las acciones 3-10 son de proyecto: se evalua `project_state`.
- La accion 13 es transversal: aplica a nivel organizacion o nivel proyecto segun el contexto del usuario.

## 10. Relacion con backend gating

Esta matriz trabaja en coordinacion con el contrato de backend gating cerrado (`docs/architecture/backend_gating_contract_v1.md`). La division es:

- **Matriz de roles/permisos/modulos** (este documento) define la forma del producto: que roles existen, que permisos tienen, que modulos ven. Es contrato, no codigo.
- **Backend gating** (ya cerrado) enforza la forma en el backend: cada endpoint declara que dependencias de gating usa. Es codigo.

### 10.1 Correspondencia con dependencias existentes

| Dependencia actual (backend gating v1) | Que enforza | Que define esta matriz |
|---|---|---|
| `get_tenant_context` (de `dependencies/tenant_context`) | Resuelve `TenantContext` con `organization_id`, `user_id`, `plan`, `role`. Devuelve `401` si no hay token. | Los 8 roles especiales de la seccion 7 y el `org_role` (owner/admin/member/billing) son visibles en el `TenantContext`. |
| `validate_project_access` (de `dependencies/tenant_context`) | Resuelve el `Project` por path `project_id` y verifica ownership por `organization_id`. `404` si no se encuentra. | Los 22 roles de proyecto (seccion 3) son visibles al validar acceso; la matriz rol x modulo (seccion 6) decide que modulos se ofrecen en el proyecto. |
| `require_write_permission` (de `dependencies/tenant_context`) | Encadena sobre `require_organization` y aplica `can_write_project(tenant)`. `403` si no permite escritura. | La matriz rol x permiso (seccion 5) define quien tiene `project.write` y derivados. |
| `require_module_access(module_key)` (de `dependencies/module_access`) | Verifica que el plan del tenant habilita el modulo. `403` si no esta habilitado. | La matriz modulo x plan del contrato SaaS (seccion 8 de `cid_saas_model_contract_v1.md`) es la fuente de verdad de que modulos estan habilitados. |
| (futuro) `require_permission(permission_key)` | Resolvera contra los 31 permisos base y el rol del usuario en el proyecto. `403` si no tiene. | Esta matriz (seccion 4) define los 31 permisos. La seccion 8 define la pseudologica de evaluacion. |
| (futuro) `require_credit(action_credit_estimate)` | Verifica saldo, reserva, ejecuta, cobra o rollbackea. `402` si saldo insuficiente. | Seccion 9 del contrato SaaS (modelo de creditos) y seccion 8.1 (casos) de este documento. |

### 10.2 Reglas de coherencia

- Toda accion permitida por la matriz debe ser ejecutable por el backend gating. Si la matriz dice "puede", el gating tiene que poder enforzar "si" con un `permission_key` registrado.
- Toda accion denegada por la matriz debe ser rechazada por el backend gating con el codigo HTTP canonico (`403`, `402`, `429`, `423`, `451`).
- El frontend consume `/api/capabilities` (futuro) para saber que mostrar; no hardcodea la matriz. La fuente de verdad es este documento + el modelo SaaS + el backend gating.
- Cambios en esta matriz sin cambios en el gating son incompletos (el backend no sabra enforzar permisos nuevos). Cambios en el gating sin cambios en la matriz son invisibles para el cliente. Ambos se versionan juntos (v1, v2, etc.).
- Toda adicion de `permission_key` nuevo requiere: alta en seccion 4, actualizacion de la matriz en seccion 5, asignacion a roles en seccion 3, y un `P0` o `P1` de gating en el router correspondiente (patron 8 de `backend_gating_contract_v1.md`).

### 10.3 Endpoints que seran afectados proximamente

Los siguientes endpoints del backend seran ampliados en fases futuras para consumir los 31 permisos base y la matriz rol x modulo:

- `POST /api/projects` (crear proyecto) -> `require_permission("project.write") + require_permission("project.admin")`.
- `POST /api/projects/{id}/script` (subir guion) -> `require_permission("script.write") + require_module_access("script_analysis")`.
- `POST /api/projects/{id}/storyboard/sheet` (generar storyboard) -> `require_permission("storyboard.generate") + require_module_access("storyboard_ai") + require_credit(30)`.
- `POST /api/projects/{id}/sound/ingest` (ingerir sonido) -> `require_permission("sound.ingest") + require_module_access("sound_ingest") + require_credit(15)`.
- `POST /api/projects/{id}/delivery/export` (exportar delivery) -> `require_permission("delivery.export") + require_module_access("delivery") + require_credit(20)`.
- `POST /api/billing/change-plan` (cambiar plan) -> `require_permission("billing.manage")` (sin project_id).
- `GET /api/audit` (ver auditoria) -> `require_permission("audit.read")`.

Estos endpoints se mantendran en la capa de `routes/` y se iran modificando de forma incremental en las fases `CID.SAAS.ROLES.PERMISSIONS.BACKEND.ENFORCEMENT.1` y siguientes. Hasta entonces, el gating cerrado v1 sigue siendo la fuente de verdad operativa.

## 11. Relacion con frontend

El frontend consume `/api/capabilities` (futuro) para saber que mostrar. La matriz de este documento define la forma esperada de esa respuesta. Hasta que `/api/capabilities` exista, el frontend consume los endpoints ya existentes y replica la logica de esta matriz localmente, con la advertencia de que cualquier cambio en la matriz requiere actualizar el frontend.

### 11.1 Sidebar por modulos disponibles

El sidebar principal se construye a partir de los `module_key` que:

1. El plan del usuario habilita (`plan_modules(plan)`).
2. El rol del usuario en el proyecto activo permite (`role_permissions x module_active`).
3. El estado del proyecto permite (`project_state` distinto de `archivado` para escritura; `archivado` solo muestra `project.read` y `audit.read`).

Modulos no disponibles: no aparecen. No se muestra enlace, tab ni breadcrumb. Si el usuario conoce la URL y la escribe, ve la pantalla de "acceso restringido" (ver 11.3).

Cliente externo y revisor invitado: solo ven `project_memory` (lectura), `client_feedback` (lectura + feedback), `producer_pitch` (preview), `delivery` (preview), y `storyboard_ai`/`concept_art` (preview). No ven `budget`, `funding`, `sound_ingest`, `crm_sales`, `admin_analytics`, `integrations_n8n`.

### 11.2 Botones por permisos

Cada accion de UI se asocia a un `permission_key`. El boton se renderiza solo si el usuario tiene ese permiso en el contexto actual (proyecto + estado). Si no, no se renderiza (preferible) o se renderiza deshabilitado (con tooltip explicativo).

Ejemplos:

- "Generar storyboard" -> requiere `storyboard.generate` + `ai.run`. Si el usuario no tiene storyboard.generate, el boton no aparece. Si tiene pero el plan no incluye `storyboard_ai`, el boton aparece deshabilitado con tooltip de upgrade.
- "Aprobar" en feedback -> requiere `client_feedback.write` o `ai.approve`. Si el usuario es cliente externo, aparece. Si es un Director, aparece con semantica de aprobacion interna. Si es un Productor, no aparece (su aprobacion se hace via `delivery.publish`).
- "Comprar creditos" -> requiere `credits.manage`. Solo aparece para `organization_admin`, `organization_owner`, `billing_admin`. Si el Productor del proyecto intenta, el boton no esta.
- "Cambiar plan" -> requiere `billing.manage` + `organization.manage`. Solo aparece para owner y admin de organizacion.

### 11.3 Disabled states y mensajes de upgrade

Cuando un boton aparece pero no esta habilitado, el tooltip explica el motivo y la accion a tomar. Formato canonico: "Esta accion requiere [rol/permiso/modulo]." + CTA contextual.

Ejemplos de mensajes (mismos que la seccion 13 del contrato SaaS):

- "El modulo Sound Ingest no esta incluido en tu plan Starter. Puedes activarlo como add-on por 149 €/mes o subir a Pro."
- "Esta accion cuesta unos 30 creditos. Tu saldo actual es 12. Compra un paquete de 100 creditos (29 €) o sube a Pro para 10.000 creditos/mes."
- "Has llegado al limite de 100 hojas de storyboard de tu plan Pro este mes. El contador se reinicia el dia 1."
- "El proyecto esta archivado. Para reactivarlo, contacta al administrador de tu organizacion."

### 11.4 Modo cliente externo / revisor invitado

Cuando el actor activo es `cliente_externo` o `revisor_invitado`, la UI aplica un modo especial:

- **No se muestran**: saldos de creditos, botones de billing, configuracion, admin, costos, miembros del proyecto con emails, timestamps de ultimo acceso.
- **Se muestra solo**: preview de entregables, su propio feedback, opciones de aprobar/rechazar, comentarios. El preview puede ser video, audio, PDF, imagen; nunca el master original.
- **Navegacion**: sidebar reducido a `Projecto`, `Feedback`, `Pitch` (preview), `Delivery` (preview).
- **Marca visual**: banda superior con "Vista de cliente externo" y opcion de cambiar al modo Productor si el usuario pertenece a la organizacion y tiene rol dual.
- **Acciones**: solo `feedback.write`, `ai.approve` (si fue concedido al invitar). Ninguna escritura sobre el contenido.

### 11.5 Dashboard por rol

Cada rol aterriza en su dashboard principal. Esto es la seccion 11 de `cid_project_access_model_v1.md` traducida a la terminologia SaaS.

| Rol | Dashboard | Widgets principales |
|---|---|---|
| `productor` | Projecto (global) | Estado de proyectos, presupuesto, financiacion, equipo, riesgos, calendario. |
| `productor_ejecutivo` | Organizacion (multi-proyecto) | KPIs cross-proyecto, financiacion consolidada, alertas estrategicas. |
| `jefe_produccion` | Produccion (proyecto) | Plan de rodaje, shotlist, costes reales vs estimados, equipo en set. |
| `director` | Creativo (proyecto) | Storyboard, concept art, biblia, montaje, feedback del cliente. |
| `ayudante_direccion` | Rodaje (proyecto) | Plan diario, llamadas, agenda, equipo en set. |
| `script_continuidad` | Continuidad (proyecto) | Script anotado, raccord, hoja de continuidad. |
| `direccion_fotografia` | Fotografia (proyecto) | Plan fotografico, storyboard, concept art, LUTs. |
| `camara` | Operativa (proyecto) | Shotlist del dia, plano asignado, notas. |
| `dit_data_wrangler` | Datos (proyecto) | Catalogo de material, backups, status de ingesta. |
| `sonido_directo` | Sonido (proyecto) | Audio ingestado, calidad, monitoreo, catalogacion. |
| `direccion_arte` | Arte (proyecto) | Concept art, biblia, decorados, atrezzo. |
| `vestuario` | Vestuario (proyecto) | Biblia de personaje (entradas vestuario), pruebas. |
| `maquillaje_peluqueria` | Maky/pel (proyecto) | Biblia de personaje (entradas), pruebas. |
| `casting` | Casting (proyecto) | Biblia de personaje (entradas), base de actores, pruebas. |
| `montaje` | Edicion (proyecto) | Material disponible, EDL, cortes previos, notas. |
| `postproduccion_sonido` | Post-sonido (proyecto) | Audio ingestado, mezcla, stems, M+E. |
| `vfx` | VFX (proyecto) | Previz, planos VFX, renders intermedios, integracion. |
| `color` | Color (proyecto) | LUTs, master coloreado, variantes. |
| `delivery` | Delivery (proyecto) | Masters, QC, deliverables por plataforma, clientes. |
| `distribucion_ventas` | Comercializacion (multi-proyecto) | Festivales, agentes, ventas, materiales comerciales. |
| `cliente_externo` (ext) | Cliente (proyecto) | Entregables en preview, feedback, aprobaciones. |
| `revisor_invitado` (ext) | Revisor (proyecto) | Material que el productor decidio mostrar. |

## 12. Auditoria

Esta matriz genera los siguientes eventos de auditoria. Se anexan a los 28 del contrato SaaS (seccion 15 de `cid_saas_model_contract_v1.md`); no los sustituyen. La union de los dos conjuntos forma el catalogo completo de eventos auditables de CID.

| Evento | Cuando se registra | Campos clave |
|---|---|---|
| `permission_granted` | Un admin concede un permiso explicito a un usuario en un proyecto. | `actor_id`, `target_user_id`, `permission_key`, `project_id`, `expires_at`, `reason`. |
| `permission_revoked` | Un admin revoca un permiso explicito. | `actor_id`, `target_user_id`, `permission_key`, `project_id`, `reason`. |
| `role_assigned` | Se asigna un `project_role` a un usuario en un proyecto. | `actor_id`, `target_user_id`, `role_key`, `project_id`, `source` (manual/import/invitation). |
| `role_removed` | Se quita un `project_role` de un usuario. | `actor_id`, `target_user_id`, `role_key`, `project_id`, `reason`. |
| `permission_denied` | El backend gating rechaza una accion por falta de permiso. | `actor_id`, `permission_key`, `endpoint`, `project_id`, `reason` (rol sin permiso, plan sin modulo, etc.). |
| `module_blocked` | El backend gating rechaza por modulo no disponible en el plan. | `actor_id`, `module_key`, `plan_key`, `project_id`, `reason` (no incluido, add-off expirado, grace). |
| `ai_action_requested` | Un usuario lanza un job de IA. | `actor_id`, `module_key`, `permission_key`, `project_id`, `credit_estimate`, `action_type`. |
| `export_requested` | Un usuario solicita un export (EDL, AAF, PDF, paquete). | `actor_id`, `format`, `project_id`, `size_estimate`. |
| `billing_action_attempted` | Un usuario intenta una accion de billing (cambiar plan, comprar creditos, anadir metodo de pago). | `actor_id`, `action_type`, `result` (success/denied), `reason` si denied. |

**Reglas:**

- Los eventos se escriben con `event_id` (UUID), `occurred_at` y `actor_id` (o `system` o `ai_worker`).
- Append-only. Las correcciones se hacen con un evento `audit_event_corrected` que referencia al anterior, no sobreescribiendo.
- Datos personales en eventos (`client_feedback` con texto, `casting` con datos de actores) se seudonimizan tras el periodo legal; el `user_id` se mantiene.
- Eventos de `permission_denied` se monitorean para detectar fugas (un cliente externo intentando acceder a `billing.manage` es senal de bug de UI o de matriz).
- Eventos de `ai_action_requested` se cruzan con `ai_job_started` del contrato SaaS para verificar que toda peticion termino en un job o fue rechazada.

## 13. Casos limite

8 casos limite que la matriz y el backend deben resolver de forma consistente.

### 13.1 Usuario con dos roles

Ana es `director` y `montaje` en el mismo proyecto. Permisos efectivos: union de ambos. UI: dashboard combina vista de director y de montaje; no se duplican widgets. Permisos redundantes no se penalizan; `script.write` aparece una sola vez. Si se le quita `montaje`, sus permisos de `montaje` desaparecen; los de `director` se mantienen.

### 13.2 Productora externa invitada

La Productora X (organizacion distinta) es invitada a un proyecto de la Productora Y como `direccion_arte` externo. Ana, de la Productora X, ve solo el proyecto donde esta invitada; no ve otros proyectos de la Productora Y. Si la Productora Y le concede `client_feedback.read` adicional, lo tiene solo en ese proyecto. Si intenta acceder por URL a otro proyecto, recibe `404` (no existe) o `403` (no tiene acceso); el gating nunca expone la existencia del otro proyecto.

### 13.3 Cliente que solo revisa

El cliente externo Carlos esta invitado a 3 proyectos. En cada uno tiene `client_feedback.read` + `client_feedback.write` + `ai.approve` (este ultimo opcional). No ve `billing`, no ve `credits`, no ve `admin`. Si se le quita la invitacion a un proyecto, su acceso a ese proyecto se revoca inmediatamente; los otros dos proyectos no se ven afectados.

### 13.4 Director sin permiso de billing

Maria es `director` en un proyecto. Intenta acceder a `/billing/change-plan`. El frontend no le muestra el boton (no tiene `billing.manage` en la matriz). Si escribe la URL, el backend devuelve `403` con `permission_denied`. El evento se registra; si la accion se repite, soporte recibe una alerta de intento sospechoso.

### 13.5 Sonidista con sound_ingest pero sin budget

Pablo es `sonido_directo` en un proyecto. Su plan es Pro con `sound_ingest` como add-on. Puede usar `sound.ingest` y `sound.process` (con IA, cobrando creditos). No puede ver `budget.read` segun la matriz (`sonido_directo` tiene `R` en Budget condicional, no por defecto). Si intenta acceder, el frontend no muestra el modulo `budget` en su sidebar; si escribe la URL, recibe `403`.

### 13.6 Montador con lectura de script/storyboard pero sin financiacion

Lucia es `montaje` en un proyecto. Ve `script.read`, `storyboard.read` (necesario para editar con contexto narrativo y visual). No ve `funding.read` (la matriz da `R` a `montaje` en Budget condicional, no en Funding). Su dashboard no muestra la pestana de Financiacion. Si quiere entender el contexto de distribucion, debe pedirselo al `productor` o al `distribucion_ventas`.

### 13.7 Admin global soporte tecnico

Carlos es `global_admin` de CID staff. Atiende un ticket de la Productora Y. Inicia una `support_session` con justificacion obligatoria: "Investigar fallo de export en proyecto P-1234". Durante la sesion, ve el proyecto y puede ejecutar acciones readonly (`project.read`, `audit.read`, `asset.read`). No puede `billing.manage` ni `credits.manage`. La sesion queda registrada con `actor_id=global_admin`, `support_session_id`, `justification`, `scope`. Al cerrar la sesion, los grants temporales se revocan.

### 13.8 Proyecto archivado

El Proyecto P-1234 pasa a estado `archivado` (decision del `productor` o del admin). Efectos:

- Todos los roles de proyecto pierden permisos de escritura: `script.write`, `storyboard.generate`, `sound.ingest`, `budget.write`, etc., devuelven `403`.
- Los permisos de lectura se mantienen: `project.read`, `audit.read`, `script.read`, `storyboard.read` siguen disponibles para los miembros que los tenian.
- `cliente_externo` y `revisor_invitado` pierden acceso (los proyectos archivados no son visibles para externos).
- `delivery.export` y `delivery.publish` siguen disponibles para el equipo de delivery durante el periodo de gracia (30 dias) por si se necesita regenerar un master.
- El modulo `project_memory` sigue en modo read-only, accesible para `audit.read`.

Para reactivar, el `project_admin` debe usar `project.admin` con una accion explicita de "Reactivar proyecto". El sistema registra `project_state_changed` en auditoria.

## 14. Fases siguientes

Plan de implementacion, en orden. Cada fase tiene su propio spec, su propia implementacion backend/frontend y su propio cierre de validacion.

1. **CID.SAAS.ROLES.PERMISSIONS.SCHEMA.1**: persistir los 22 roles de proyecto, los 8 roles especiales y los 31 permisos base. Tablas `role`, `permission`, `role_permission`, `project_member`, `organization_member`, `explicit_grant`. Endpoints CRUD admin con gating existente.
2. **CID.SAAS.ROLES.PERMISSIONS.SEED.1**: seed inicial con los 22 roles, los 31 permisos y la matriz rol x permiso por defecto. Versionado en el catalogo; cualquier cambio requiere nueva fase.
3. **CID.SAAS.ROLES.PERMISSIONS.BACKEND.ENFORCEMENT.1**: introducir `require_permission(permission_key)` en `src/dependencies/`. Migrar routers existentes gradualmente. Anadir `require_credit` para acciones de IA. Cada router migrado tiene su test contract (mismo patron que `backend_gating_contract_v1.md`).
4. **CID.SAAS.ROLES.PERMISSIONS.FRONTEND.VISIBILITY.1**: introducir `/api/capabilities` (endpoint que devuelve la matriz efectiva para un usuario en un proyecto). Frontend consume y aplica visibilidad (sidebar, botones, disabled states, mensajes).
5. **CID.SAAS.ROLES.PERMISSIONS.TESTS.1**: suite de tests que valida la coherencia entre la matriz documental (este archivo), el seed (fase 2) y el enforcement (fase 3). Verifica que toda `permission_key` usada por un endpoint esta en la lista canonica y que toda `permission_key` de la lista esta cubierta por al menos un test.

Fases de soporte (no bloqueantes, planificables en paralelo):

- **CID.SAAS.ROLES.PERMISSIONS.AUDIT.1**: persistencia de los 9 eventos de la seccion 12.
- **CID.SAAS.EXTERNAL.REVIEWERS.UI.1**: UI especializada para `cliente_externo` y `revisor_invitado` (modo preview, sidebar reducido, marca visual de externo).
- **CID.SAAS.ORG.OWNERSHIP.TRANSFER.1`: flujo de transferencia de ownership de organizacion.
- **CID.SAAS.PROJECT.STATE.MACHINE.1`: implementar la maquina de estados del proyecto (`pre_produccion`, `produccion`, `postproduccion`, `delivery`, `archivado`) con transiciones validadas por `project_state` de la seccion 8.
- **CID.SAAS.SERVICE.ACCOUNTS.1`: cuentas de servicio para integraciones n8n, ComfyUI server-side, sincronizaciones.

## 15. Criterio GO

Esta matriz v1 se considera **GO** para guiar las fases de implementacion cuando se cumplen todos los puntos siguientes:

1. Los 22 roles de proyecto (seccion 3) estan definidos con los 7 campos cada uno (descripcion, responsabilidad, modulos, permisos read, permisos write/generate/export, restricciones, notas SaaS).
2. Los 31 permisos base (seccion 4) estan definidos en notacion `domain.action`, agrupados por dominio, con notas de aplicacion.
3. La matriz rol x permiso (seccion 5) es completa para los 22 roles contra los 12 grupos de permisos, con codigos `R`, `W`, `G`, `E`, `A`, `C`, `N` y notas aclaratorias.
4. La matriz rol x modulo (seccion 6) es completa para los 22 roles contra los 19 modulos, con codigos `F`, `C`, `R`, `V`, `P`, `N` y notas aclaratorias.
5. Los 8 roles especiales (seccion 7) estan definidos con scope, permisos, restricciones y notas SaaS.
6. La pseudologica de permisos efectivos (seccion 8) esta definida como interseccion de 6 dimensiones, con casos resueltos y orden de evaluacion.
7. Las 13 acciones criticas (seccion 9) estan mapeadas con permiso, modulo, write, creditos y rol tipico.
8. La relacion con el backend gating cerrado (seccion 10) es explicita, con tabla de correspondencia, reglas de coherencia y endpoints futuros identificados.
9. La relacion con frontend (seccion 11) es explicita: sidebar, botones, disabled states, mensajes, modo externo, dashboards por rol.
10. Los 9 eventos de auditoria (seccion 12) estan definidos, sin contradecir los 28 del contrato SaaS.
11. Los 8 casos limite (seccion 13) estan resueltos con la solucion esperada.
12. El roadmap (seccion 14) enumera las fases en orden, con su prefijo CID.SAAS.* y su objetivo.
13. El documento es internamente consistente: ningun permiso de la seccion 4 rompe un rol de la seccion 3; ninguna cuota de la seccion 6 rompe un limite del contrato SaaS; ningun evento de la seccion 12 rompe una accion de la seccion 9; ningun caso limite de la seccion 13 rompe la pseudologica de la seccion 8.
14. El documento no contradice `cid_saas_model_contract_v1.md` ni `backend_gating_contract_v1.md`. Los 22 roles, los 31 permisos y los 19 modulos son consistentes con los documentos companeros.

Cuando todos estos puntos se cumplen, la matriz sirve como base contractual para:

- Disenar la primera iteracion del schema de roles/permisos (`CID.SAAS.ROLES.PERMISSIONS.SCHEMA.1`).
- Disenar el seed inicial (`CID.SAAS.ROLES.PERMISSIONS.SEED.1`).
- Disenar la API de capabilities para el frontend (`CID.SAAS.ROLES.PERMISSIONS.FRONTEND.VISIBILITY.1`).
- Iniciar la migracion gradual de routers al `require_permission` canonico.

La matriz no implementa nada. Es un GO de diseno, suficiente para que las fases 1-5 del roadmap arranquen con un modelo de roles/permisos/modulos estable, sin tener que revisarlo en cada sprint.
