# Master Directive: Sprint 12 — Delivery & Stability

**Estado:** READY FOR CODE
**Versión:** 1.0
**Project:** AILinkCinema
**Prioridad:** Crítica (Requisito para Demo Robusta)

---

## 1. Resumen Ejecutivo
El Sprint 12 tiene como misión blindar la experiencia de usuario en el pipeline de renderizado remoto y habilitar la entrega física de activos. Tras cerrar el Sprint 11 (histórico y auditoría), el sistema es observable pero vulnerable a cortes de red y carece de un mecanismo de descarga unificada. Este bloque de trabajo asegura que un render no se "pierda" por un corte de Tailscale y que el cliente pueda llevarse el resultado final en un ZIP profesional.

## 2. Objetivo Exacto
Certificar la estabilidad operativa del pipeline ComfyUI/Tailscale y habilitar el motor de exportación asíncrona para la entrega de entregables (Delivrables) finales.

## 3. Dependencias Cerradas
- **Sprint 13.3 (DB Queue):** La persistencia de jobs en base de datos es la base del recovery.
- **Sprint 11 (History & Assets):** La UI ya sabe mostrar qué se generó, permitiendo ahora su agrupamiento en ZIP.

## 4. Alcance Incluido
- Detección de workers offline y jobs huérfanos.
- Políticas de reintento ante fallos de red (backoff).
- Motor de creación de archivos ZIP con manifiesto JSON.
- Polling optimizado en UI para seguimiento de exportación.
- Descarga segura de archivos generados.

## 5. Alcance Excluido
- Migración a PostgreSQL (se mantiene SQLite).
- Sistema de pagos/Stripe.
- Gestión de cuotas de almacenamiento avanzada.
- Nuevos nodos o workflows de ComfyUI.

---

## 6. División de Subfases

### Sprint 12.1 — Stability / Worker Resilience
*Foco: Que el sistema no mienta al usuario sobre el estado de un render.*

- **Timeout Operativo:** Definir tiempos máximos de renderizado vs tiempos de pulso (heartbeat).
- **Detección de Worker Zombie:** Al iniciar el servidor o tras X tiempo sin updates, identificar jobs en `RUNNING` que el worker ya no conoce y marcarlos como `FAILED`.
- **Fallback/Requeue Seguro:** Si un job falla por red, permitir un número limitado de auto-reintentos antes de devolver error al usuario.
- **Trazabilidad:** Registrar en `JobHistory` cada incidencia de red detectada.
- **UI Sync:** Asegurar que la UI limpia estados de "Cargando..." si el job se considera zombie.

### Sprint 12.2 — Delivery / ZIP Export
*Foco: "El botón de descarga".*

- **Motor Backend:** Servicio asíncrono que recorre los assets de un proyecto, los zipea y genera un `manifest.json` con la metadata técnica del proceso.
- **Estados de Exportación:** `collecting` -> `zipping` -> `ready` -> `downloaded`.
- **Feedback UI:** Barra de progreso real (o estados discretos claros) en la página de detalle del proyecto.
- **Manejo de Fallos:** Si falla el zipeo (ej. falta de espacio), limpiar el archivo parcial y marcar el entregable como fallido.

---

## 7. Modelo Conceptual Afectado
- **ProjectJob:** Se extiende la lógica de resultados para incluir metadatos de exportación.
- **Deliverable:** (Modelo de Sprint 5/11) Se activa el flujo de `status` para el archivo ZIP.
- **JobHistory:** Nuevos tipos de eventos registrados para "Recovery" y "Export".

## 8. Flujo Operativo Esperado
1. El usuario hace click en "Exportar Proyecto".
2. Se dispara un `ProjectJob` de tipo `export`.
3. El frontend muestra un spinner/progreso consultando el estado del job.
4. El backend agrupa assets, crea el ZIP y actualiza el `Deliverable`.
5. Una vez `completed`, el frontend ofrece el botón de "Descargar ZIP".

## 9. Criterios de Aceptación

### Fase 12.1 (Stability)
- El scheduler no mantiene jobs en `RUNNING` tras un reinicio del backend.
- Micro-cortes de Tailscale de < 10 segundos no provocan el fallo del job (uso de backoff).
- Los jobs zombie se marcan como `FAILED` con un mensaje explicativo claro.

### Fase 12.2 (Delivery)
- El ZIP contiene exactamente los assets que el usuario ve en la Review UI.
- El `manifest.json` dentro del ZIP incluye el `project_id` y `timestamp`.
- El endpoint de descarga devuelve un 403 si el usuario no es el dueño del proyecto.

## 10. Riesgos
- **Latencia Tailscale:** Un worker muy lento puede parecer zombie. Solución: Incrementar timeouts específicos para polling de ComfyUI.
- **Espacio en Disco:** Múltiples ZIPs de proyectos pesados. Solución: Implementar limpieza de archivos `.tmp` (aunque sea manual/SOP por ahora).

## 11. Smoke Tests Esperados
- **Test 1:** Lanzar render -> Matar proceso Python -> Reiniciar -> El job debe aparecer como FAILED (no colgado).
- **Test 2:** Bloquear tráfico de red (simular caída Tailscale) 5s -> El job debe seguir vivo tras restaurar red.
- **Test 3:** Exportar proyecto vacío -> El sistema debe avisar que no hay assets (o generar ZIP vacío con aviso).

## 12. Orden Recomendado de Implementación
1. **12.1 (Stability):** Primero asegurar que la base de ejecución es sólida. Sin esto, el exportador podría fallar silenciosamente.
2. **12.2 (Delivery):** Implementar el motor de ZIP y finalmente la pieza de UI.

---

## 13. Veredicto
**READY FOR CODE**

> [!IMPORTANT]
> No se debe intentar optimizar el tamaño del ZIP ni implementar streaming avanzado en este sprint. La prioridad es el flujo de éxito y la visibilidad del error.
