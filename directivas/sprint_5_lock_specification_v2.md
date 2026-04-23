# Contrato Funcional Bloqueado: Sprint 5 (Review, Approval & Delivery)

## 1. Objetivo del Sprint
Cerrar el ciclo de vida del activo audiovisual permitiendo el feedback trazable entre productor y cliente, la toma de decisiones formal y la consolidación de entregables finales.

## 2. Alcance Exacto
### Entra:
- **Modelo de datos:** `Review`, `Comment` (texto plano), `ApprovalStatus` (Pending / Needs Changes / Approved), `Deliverable`.
- **Lógica de Estado:** 
    - `Approved`: Bloquea el activo y lo envía al área de Delivery.
    - `Needs Changes`: Desbloquea la edición/re-render en el Visual Pipeline (S3/S4).
- **Trazabilidad:** Historial de comentarios vinculado a la versión específica del activo.
- **Seguridad Básica:** Distinción visual entre vista de Productor (Owner) y vista de Cliente (Invited).

### No Entra:
- **Anotaciones Visuales:** Dibujo sobre frames o marcas de tiempo (Timecode markers).
- **Colaboración Real-time:** Chat en vivo o presencia múltiple simultánea.
- **Transcoding:** Generación de formatos de exportación (ProRes, etc.) en el servidor (solo gestión de assets en S3).
- **Notificaciones Externas:** Envío de emails o integraciones con Slack/WhatsApp.

## 3. Vistas Finales
1.  **Reviews Overview:** Panel de control con listado de escenas/clips pendientes de validación.
2.  **Review Detail:** Espacio de reproducción de media con feed de comentarios lateral y botones de decisión (Approve/Reject).
3.  **Delivery Overview:** Repositorio "Master-Only" con los activos aprobados y listos para descarga.
4.  **Deliverable Detail:** Ficha técnica individual del activo final con su rastro de aprobación (Quién, Cuándo, Versión).

## 4. Acciones del Usuario por Vista
- **Reviews Overview:** 
    - Filtrar por estado.
    - Identificar rápidamente prioridades de revisión.
- **Review Detail:** 
    - Reproducir media (Player básico).
    - Escribir comentario técnico/creativo.
    - Cambiar estado formal del activo mediante botones de acción.
- **Delivery Overview:** 
    - Buscar activos por metadatos de producción.
    - Descarga directa de archivos aprobados.
- **Deliverable Detail:** 
    - Consultar el histórico de decisiones que llevó a este activo.

## 5. Datos Demo Obligatorios (Seed Data)
- **Proyecto "The Robot's Journey":**
    - 1 Revisión activa con feedback crítico (ej: "Ajustar contraste en fondo").
    - 1 Activo en estado "Approved" visible en el área de Delivery.
    - 1 Activo en estado "Needs Changes" con historial de comentarios previo.

## 6. Placeholders Permitidos (Coming Soon)
- Botones de exportación avanzada (ProRes, DNxHR) deshabilitados.
- Herramienta de "Markup / Pen" con icono deshabilitado.
- Opción de "Add Team Member" deshabilitada.

## 7. Criterios de Terminado (DoD)
- [ ] La relación funcional `Asset -> Review -> ApprovalDecision -> Deliverable` es operativa.
- [ ] Un cambio a "Approved" bloquea la edición del activo original (Read-Only).
- [ ] Los comentarios se registran con timestamp y autor (Productor/Cliente).
- [ ] El área de Delivery es accesible y solo muestra versiones maestras aprobadas.

## 8. Exclusiones
- No se permiten versiones "borrador" en el área de Delivery.
- No hay edición de guion ni de montaje (S2/S4) desde el área de Review.

## 9. Decisiones Congeladas
- El feedback es únicamente a nivel de Clip/Master (no por frame).
- El área de Delivery es el nodo final del pipeline del MVP; no hay integración con plataformas de streaming externas.
