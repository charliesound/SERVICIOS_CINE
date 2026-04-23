# Sprint 5 Locking Specification: Review, Approval & Delivery

## 1. Objetivo del Sprint
Implementar el bucle de validación profesional y el sistema de entrega final, permitiendo el feedback trazable, la toma de decisiones formal (Aprobación/Rechazo) y la gestión de activos terminados (Deliverables).

## 2. Alcance Exacto
### Entra:
- **Jerarquía de Revisión:** Relación funcional `Asset/AssemblyCut -> Review -> ApprovalDecision -> Deliverable`.
- **Review Dashboard:** Gestión de todas las revisiones activas y estados de aprobación por escena.
- **Collaboration Area:** Sistema de comentarios asociados a piezas específicas para feedback técnico y creativo.
- **Approval Decision Loop:** Acción de aprobar (marca el activo como listo para entrega) o rechazar (reinicia el estado del Shot/Asset a "Revision Needed").
- **Delivery Manager:** Listado de todos los archivos aprobados listos para exportar o enviar al cliente.

### No Entra:
- **Frame-by-Frame Annotations:** No hay herramientas de dibujo sobre el vídeo en esta versión.
- **Multi-Client Real-time Feedback:** No hay sistema de chat en vivo ni concurrencia de revisores externos masivos.
- **Cloud Delivery Engine:** No hay envío directo a YouTube/Vimeo/Plataformas de streaming.

## 3. Vistas Finales
1.  **Reviews Overview:** Lista de control de calidad del proyecto. Muestra qué escenas están pendientes de revisión y cuáles han sido aprobadas/rechazadas.
2.  **Review Detail / Collaboration Hub:** Vista del activo en grande con el historial de comentarios y los botones de decisión formal.
3.  **Delivery Overview:** Directorio "limpio" que contiene solo las versiones aprobadas finales.
4.  **Deliverable Detail:** Ficha técnica del activo final con metadatos de aprobación (Quién aprobó, cuándo, y qué versión es).

## 4. Acciones del Usuario por Vista
- **Reviews Overview:** Priorizar revisiones, filtrar por estado "Urgent" o "Pending".
- **Review Detail:** Reproducir vídeo/imagen, añadir nota de feedback, pulsar botón de "Approve" o "Request Changes".
- **Delivery Overview:** Descargar archivos finales, generar enlaces de compartición externos (V2).
- **Deliverable Detail:** Consultar el historial de decisiones que llevó a este activo final.

## 5. Nivel de Control (MVP)
- **Feedback:** Comentarios de texto plano vinculados al objeto de revisión.
- **Decisión:** Un rechazo desbloquea automáticamente la edición del Shot original para permitir una nueva iteración visual (S3).
- **Entrega:** La aprobación automática genera una entrada en el *Delivery Manager*.

## 6. Datos Demo Obligatorios
- **Review History:** Al menos 3 comentarios de revisión en *The Robot's Journey* (ej: "Ajustar iluminación en plano medio", "Aprobado para montaje").
- **Approved Deliverables:** Al menos 2 activos listos para entrega final.

## 7. Estados Vacíos / Placeholders
- **Empty Review View:** "Clean board. No pending reviews for the current production phase."
- **Markup Tools Placeholder:** Iconos deshabilitados de "Pen/Circle" (Visual markup coming soon).
- **Export Presets Placeholder:** Menú deshabilitado de "ProRes / DNxHR / H265" (Coming soon).

## 8. Percepción del Producto
- **Trazabilidad de Decisiones:** El equipo sabe *por qué* se cambió un plano.
- **Control de Calidad:** Nada sale del pipeline sin haber sido formalmente aprobado.
- **Profesionalidad:** La fase de entrega se siente como el cierre de un proceso industrial serio.

## 9. Criterios de Terminado (DoD)
- [ ] El modelo de datos soporta `Review`, `Comment` y `ApprovalDecision`.
- [ ] Un activo rechazado actualiza correctamente el estado del Shot original.
- [ ] El `Delivery Overview` solo muestra archivos que han pasado el flujo de aprobación.
- [ ] La búsqueda en el portal de cliente permite filtrar por "Aprobado".
- [ ] Demo Interna: "Abrir una revisión, dejar un comentario, rechazarla, ver el cambio de estado en el Shot, volver a aprobarla y encontrarla en el área de Delivery".

## 10. Decisiones Congeladas
1.  **State Uniqueness:** Un activo solo puede tener un estado de revisión activo a la vez.
2.  **Audit Trail:** Todas las decisiones de aprobación se guardan permanentemente y no son editables.
3.  **Deliverable Isolation:** Una vez que un activo entra en el área de Delivery, se considera "Locked" (Inmutable).
