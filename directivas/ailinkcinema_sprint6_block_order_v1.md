# AILinkCinema: Orden de Bloqueo de Sprint 6 y Corrección de Sprint 5

## 1. Orden de Bloqueo
Se declara formalmente el **BLOQUEO de Sprint 6 (Producer Area & Funding)**. Queda prohibida cualquier implementación técnica o de diseño relacionada con esta fase hasta que el Sprint 5 sea validado técnica y funcionalmente.

## 2. Prioridad Inmediata
La única prioridad operativa es la **CORRECCIÓN MANDATORIA DE SPRINT 5**. El producto no puede avanzar hacia métricas ejecutivas (S6) sin antes resolver el ciclo de vida del activo (S5).

## 3. Contrato Funcional Obligatorio (Sprint 5)
El sistema debe implementar los siguientes hitos de forma inmediata:
*   **Rutas de API:** `/api/reviews` y `/api/delivery` (Esquemas de Review y Deliverable).
*   **Reviews Overview:** Panel de control de piezas pendientes de validación.
*   **Review Detail:** Vista con player de media, feed de comentarios y botones de estado (Pending / Approved / Needs Changes).
*   **Delivery Overview:** Directorio master automático que filtre solo activos aprobados.
*   **Trazabilidad:** Persistencia de comentarios vinculados a versiones específicas de `Asset` o `AssemblyCut`.

## 4. Bloques Congelados Temporalmente
Quedan congelados hasta nuevo aviso:
*   **Sprint 6 Completo:** Dashboard ejecutivo, CRM, Matching de Financiación.
*   **Colaboración Compleja:** Invitaciones a equipos externos, chat persistente.
*   **Export Engine Avanzado:** Transcodificación a formatos profesionales.

## 5. Criterio de Desbloqueo de Sprint 6
El Sprint 6 se desbloqueará únicamente cuando se realice una demo interna exitosa donde:
1.  Un activo se visualice en el área de **Review**.
2.  Un usuario emita un **Comment** y pulse **Approve**.
3.  El activo aparezca instantáneamente en el área de **Delivery** como un entregable válido.

## 6. Criterio de “Gobernanza Restablecida”
La gobernanza se considerará restablecida cuando el **[ROADMAP.md](file:///SERVICIOS_CINE/docs/ROADMAP.md)** técnico refleje el estado real de la deuda técnica de Sprint 5 y el equipo de desarrollo (OpenCode) presente los nuevos esquemas de datos correspondientes a la capa de negocios.
