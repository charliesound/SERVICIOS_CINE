# Orden de Gobernanza: Bloqueo de Sprint 6 y Corrección Maestra de Sprint 5

## 1. Orden de bloqueo
Se declara el **BLOQUEO FORMAL del Sprint 6 (Producer Area & Funding)**. Queda prohibida cualquier implementación técnica o de diseño relacionada con esta fase. El producto no tiene permiso de avanzar hacia métricas ejecutivas mientras el ciclo de vida del activo audiovisual (Review & Delivery) sea inexistente o puramente decorativo.

## 2. Prioridad inmediata
La única prioridad estratégica y técnica es la **CORRECCIÓN MANDATORIA DE SPRINT 5**. El equipo debe pivotar desde el "tech-stack experimental" hacia la "capa de negocio B2B".

## 3. Contrato funcional obligatorio de Sprint 5
Para que el Sprint 5 se considere válido, el sistema debe demostrar:
*   **Vistas Reales en Frontend:** 
    *   `ReviewsOverview`: Gestión de aprobaciones pendientes.
    *   `ReviewDetail`: Player con feed de comentarios y botones de acción (Approve/Reject).
    *   `DeliveryOverview`: Catálogo automático de activos aprobados.
*   **Lógica Backend:** 
    *   Persistencia de comentarios vinculados a versiones.
    *   Cambio de estado del activo: `Pending -> Approved` bloquea el activo y lo publica en Delivery; `Pending -> Needs Changes` libera el activo para re-render.
*   **Trazabilidad:** Relación operativa `Asset -> Review -> ApprovalDecision -> Deliverable`.

## 4. Bloques congelados temporalmente
Quedan suspendidas las siguientes áreas hasta la resolución de Sprint 5:
*   Dashboard de métricas para productores.
*   Matching de financiación (Funding).
*   CRM y gestión de clientes avanzada.
*   Optimización de infraestructura ComfyUI no crítica para el flujo editorial.

## 5. Criterio de desbloqueo de Sprint 6
El Sprint 6 se desbloqueará únicamente cuando se realice una demo interna exitosa donde un activo sea:
1.  Visualizado en el portal de revisión.
2.  Comentado y formalmente aprobado.
3.  Consultado y descargado desde el directorio de entregables (Delivery).

## 6. Criterio de “gobernanza restablecida”
La gobernanza se considerará restablecida cuando el repositorio incluya `review_routes.py` y `delivery_routes.py` con lógica de negocio real, y las páginas en `src_frontend` dejen de ser placeholders funcionales para convertirse en la interfaz de cierre del pipeline audiovisual.
