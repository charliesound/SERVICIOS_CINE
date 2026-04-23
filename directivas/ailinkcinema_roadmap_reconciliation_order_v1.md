# AILinkCinema: Orden de Reconciliación de Roadmap (v1)

> Nota historica: este documento conserva una prioridad estrategica anterior. No debe usarse como estado operativo actual de implementacion.
> Para el estado real del codigo y del hardening usar `docs/PRODUCTION_CANDIDATE_STATUS.md`.

## 1. Roadmap Autoritativo v1 (SSoT)
Se establece la secuencia de **Sprints 1 a 6** como la única fuente de verdad operativa. Cualquier desviación técnica de este orden se considera deuda de producto acumulada.

*   **Sprint 1:** Foundation (Build, Base UI, Auth). [COMPLETO]
*   **Sprint 2:** Narrative Ingestion (Projects, Scenes, Characters). [COMPLETO]
*   **Sprint 3:** Visual Engine V1 (Multi-Backend, Job Routing). [COMPLETO]
*   **Sprint 4 (PRIORIDAD):** Editorial Traceability & Assembly (Scene -> Clip -> AssemblyCut).
*   **Sprint 5:** Review / Approval / Delivery (Client Portal, Feedback Loop).
*   **Sprint 6:** Producer Area (Dashboard Ejecutivo, Funding Leads, Demo Flow).

## 2. Bloques Congelados Temporalmente
Quedan suspendidas las siguientes líneas de trabajo hasta que el Sprint 4 y 5 alcancen el estado "External Demo Ready":
*   **Fase 8 (OpenCode):** Dockerización avanzada y guías de despliegue on-premise no bloqueantes.
*   **Ops Avanzadas:** Monitoreo recursivo y backups automáticos masivos.
*   **Optimizaciones de Infraestructura:** Refactorización de colas o persistencia que no impacten en la funcionalidad del Sprint 4.
*   **Expansiones Post-MVP:** Doblaje, NLE avanzado o integraciones con terceros.

## 3. Prioridad Inmediata para OpenCode
El equipo de desarrollo debe pivotar inmediatamente al **Sprint 4: Editorial Traceability**.
*   **Hito 1:** Implementar el modelo de datos `Scene -> Clip -> AssemblyCut`.
*   **Hito 2:** Crear la vista `Scene Clips View` y la asociación de activos de S3 a clips.
*   **Hito 3:** Desarrollar el `Postproduction Workspace` (Player de concatenación en frontend).

## 4. Riesgo Evitado con esta Reconciliación
Se elimina el riesgo de lanzar un "Servidor de Renders Estable" pero comercialmente inútil. Esta reconciliación garantiza que el MVP v1 cumpla la promesa de **"Script to Montage"**, permitiendo que el productor ejecutivo vea el ahorro de tiempo real en la previsualización editorial.

## 5. Criterio de “Roadmap Reconciliado”
El roadmap se considera reconciliado cuando la documentación de OpenCode (`ROADMAP.md`) adopta la numeración y objetivos de los Sprints 4, 5 y 6 de Antigravity, y la primera tarea activa en la cola de desarrollo sea la **Jerarquía de Clips de la Escena 02**.
