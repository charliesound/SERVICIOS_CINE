# AILinkCinema: Master Operating Document (MOD) V1

> Nota historica: este MOD mantiene la vision de producto V1, pero no sustituye al estado operativo real del codigo. Para despliegue y readiness usar `docs/PRODUCTION_CANDIDATE_STATUS.md`.

## 1. Resumen Ejecutivo
AILinkCinema no es una herramienta de IA generativa; es un **Orquestador Industrial del Pipeline Audiovisual**. Su objetivo es permitir que una productora gestione un proyecto desde el guion hasta el primer montaje con trazabilidad total, control de costes y asistencia visual mediante IA, sin sacrificar el control profesional.

## 2. Definición del Producto
**¿Qué es AILinkCinema?**
Una plataforma B2B de infraestructura para cine y publicidad que conecta el flujo creativo (guion) con la ejecución técnica (render/IA) y la supervisión financiera (Producer Area).

## 3. Promesa Central
> "Del guion al primer montaje, con trazabilidad completa."

## 4. El Problema que Resuelve
1.  **Caos de Pipeline:** Fraccionamiento entre herramientas de escritura, generación y montaje.
2.  **Opacidad de Costes:** Imposibilidad de saber cuánto cuesta "realmente" cada iteración visual.
3.  **Falta de Trazabilidad:** Pérdida de la conexión entre el guion original y los activos generados.
4.  **Barrera Técnica:** Productores que no saben usar nodos de IA pero necesitan sus resultados.

## 5. Primer Paquete Vendible (Core Orchestrator)
El MVP se centra en el **Orquestador de Infraestructura**. No vendemos "vídeo bonito", vendemos "capacidad de ejecución industrial".
- **Modelo:** Suscripción por capacidad (Prioridad y Concurrencia).
- **Valor:** Acceso a infraestructura optimizada con interfaz premium audiovisual.

## 6. Módulos Incluidos (V1)
- **CID Core:** Gestión de usuarios, planes y seguridad.
- **CID Ingesta:** Análisis de intención y carga de contexto (Base).
- **CID Visual Pipeline:** Orquestación de renders (Still, Video, Audio) en múltiples backends.
- **CID Queue & Scheduler:** Gestión de concurrencia y prioridades por plan.
- **CID Producer Dashboard:** Visión ejecutiva de actividad y créditos.
- **CID Client Portal:** Compartición de resultados con clientes externos para feedback rápido.

## 7. Exclusiones Críticas (Fuera de V1)
- Generación de largometraje completo en un clic.
- Crowdfunding real (solo gestión de "Funding Leads").
- Pasarelas de pago integradas (billing manual/offline).
- Doblaje/Localización avanzado.

## 8. Recorrido Demoable Principal
1.  **Dashboard Home:** Visión de "MITO Studio" con métricas de uso.
2.  **Script to Scene:** El productor sube un guion (o intención) y el sistema sugiere un Workflow.
3.  **Live Progress:** Visualización de la cola y el render en tiempo real.
4.  **Client Review:** Envío del resultado al portal externo para aprobación del cliente.

## 9. Cliente Objetivo Prioritario
- **Productoras Independientes:** Que necesitan agilidad sin equipo técnico masivo.
- **Agencias de Contenido/VFX:** Que buscan optimizar costes de previsualización.

## 10. Valor Específico para el Productor
- **Control Financiero:** Ver créditos consumidos por escena.
- **Velocidad de Venta:** Generar visuales rápidos para "pitchar" proyectos.
- **SSoT (Single Source of Truth):** Todo el proyecto centralizado.

## 11. Roadmap de Sprints 1–6
- **Sprint 1 (VALIDADO):** Build Foundation. Infraestructura, seguridad y UI Premium.
- **Sprint 2:** Narrative Ingestion. Proyectos, escenas y personajes estructurados.
- **Sprint 3:** Visual Engine V1. Renders síncronos y asíncronos con previsualización.
- **Sprint 4:** Traceability & Pipeline. Conexión Guion-Activo-Coste.
- **Sprint 5:** Review & Collaboration. Sistema de feedback y portal de cliente avanzado.
- **Sprint 6:** Producer Area & Funding Matching. Dashboard ejecutivo y módulo de leads de financiación.

## 12. Definiciones de Calidad
- **Foundation Build:** Código escalable, tipos estrictos y UI consistente (MITO Design).
- **Internal Demo:** Funcionalidad completa probada por el equipo.
- **External Demo:** Estabilidad para mostrar a clientes sin errores de UX.
- **Sale-Ready:** Documentación, pricing y materiales comerciales alineados con la build.

## 13. Criterios de Corte (MVP Rule)
1.  Si no ayuda a la trazabilidad o a la venta del piloto, se pospone.
2.  Si requiere integración compleja de pagos de terceros, se pospone.
3.  Si es IA generativa "pura" sin contexto de pipeline cinematográfico, se elimina.
