# CID Project Command Center — Arquitectura funcional por ramas

**Documento:** `docs/product/cid_project_command_center_branches_v1.md`
**Versión:** 1.0
**Fecha:** 2026-06-02
**Tags:** `CID`, `product-architecture`, `branches`, `RBAC-functional`, `permission-pyramid`

---

## Índice

1. [Objeto y contexto](#1-objeto-y-contexto)
2. [Ramas funcionales de producción cinematográfica](#2-ramas-funcionales-de-producción-cinematográfica)
3. [Roles y responsabilidades](#3-roles-y-responsabilidades)
4. [Arquitectura piramidal de acceso y responsabilidad](#4-arquitectura-piramidal-de-acceso-y-responsabilidad)
5. [Matriz de permisos funcionales](#5-matriz-de-permisos-funcionales)
6. [Reglas de visibilidad del Command Center](#6-reglas-de-visibilidad-del-command-center)
7. [Rama 1: Producción y Financiación](#7-rama-1-producción-y-financiación)
8. [Rama 2: Creativo y Rodaje](#8-rama-2-creativo-y-rodaje)
9. [Rama 3: Postproducción, Entrega y Comercialización](#9-rama-3-postproducción-entrega-y-comercialización)
10. [Mapa de módulos actuales por rama](#10-mapa-de-módulos-actuales-por-rama)
11. [Flujo de trabajo entre ramas](#11-flujo-de-trabajo-entre-ramas)
12. [Flujo de proyecto por fases](#12-flujo-de-proyecto-por-fases)
13. [Command Center — Tarjetas de estado por rama](#13-command-center--tarjetas-de-estado-por-rama)
14. [Ejemplos de experiencia por rol](#14-ejemplos-de-experiencia-por-rol)
15. [Indicadores y métricas por rama](#15-indicadores-y-métricas-por-rama)
16. [Implicaciones para el producto](#16-implicaciones-para-el-producto)
17. [Futuras extensiones](#17-futuras-extensiones)
18. [NO IMPLEMENTAR TODAVÍA](#18-no-implementar-todavía)
19. [Próxima fase](#19-próxima-fase)

---

## 1. Objeto y contexto

CID debe evolucionar de un conjunto de módulos independientes a un **Project Command Center** organizado por las ramas funcionales de una producción cinematográfica real. Este documento define la arquitectura funcional que debe guiar la reorganización del producto.

**Principios rectores:**
- Cada módulo pertenece a una rama funcional.
- Cada rol tiene acceso prioritario a su rama y acceso restringido a las demás.
- El Productor y Productor Ejecutivo tienen visión global.
- El Command Center no es un dashboard único para todos, sino una experiencia adaptada por rol.
- No se diseñan mecanismos técnicos (RBAC, backend, endpoints) — solo arquitectura funcional y de producto.

---

## 2. Ramas funcionales de producción cinematográfica

CID se organiza en tres ramas que cubren el ciclo de vida completo de una producción:

| Rama | Etiqueta | Ciclo |
|---|---|---|
| Rama 1 | **Producción y Financiación** | Desarrollo financiero — búsqueda de ayudas, presupuesto, plan financiero, contratación, dossier, captación de inversores |
| Rama 2 | **Creativo y Rodaje** | Preproducción creativa y rodaje — análisis de guion, desglose, storyboard, arte, concepto, plan de rodaje, partes |
| Rama 3 | **Postproducción, Entrega y Comercialización** | Postproducción, entregas, distribución, ventas, CRM, festivales, explotación comercial |

Estas ramas no son estancas: hay dependencias funcionales entre ellas. El Command Center debe reflejar esas dependencias sin mezclar responsabilidades.

---

## 3. Roles y responsabilidades

CID reconoce los siguientes roles funcionales, ordenados por nivel jerárquico:

### Nivel 1 — Dirección del proyecto
| Rol | Descripción |
|---|---|
| **Productor** | Responsable último del proyecto. Visión global completa. |
| **Productor Ejecutivo** | Supervisión financiera y estratégica. Acceso total salvo decisiones internas del equipo creativo. |

### Nivel 2 — Jefatura de departamento
| Rol | Rama principal | Descripción |
|---|---|---|
| **Jefe de Producción** | Producción y Financiación | Ejecución del plan de producción, presupuesto, contratación, órdenes de cambio. |
| **Director** | Creativo y Rodaje | Dirección creativa, visión artística, supervisión de guion, rodaje, montaje. |
| **Post Supervisor** | Postproducción | Coordinación de postproducción, entregas, QC. |

### Nivel 3 — Especialistas
| Rol | Rama principal | Descripción |
|---|---|---|
| **Guionista** | Creativo y Rodaje | Desarrollo de guion, versiones, análisis. |
| **Script Supervisor** | Creativo y Rodaje | Continuidad, raccord, partes de cámara. |
| **Ayudante de Dirección** | Creativo y Rodaje | Plan de rodaje, partes, llamadas. |
| **Montador / Editor** | Postproducción | Montaje, assembly cut, FCPXML. |
| **Editor de Sonido** | Postproducción | Postproducción de sonido. |
| **Distribuidor** | Comercialización | Estrategia de distribución, venta territorial. |
| **Agente de Ventas** | Comercialización | Negociación con plataformas, ventas internacionales. |

---

## 4. Arquitectura piramidal de acceso y responsabilidad

CID NO debe organizarse como un dashboard donde todos los usuarios ven todas las áreas. Debe diseñarse como una **arquitectura piramidal de permisos y responsabilidades** inspirada en una producción cinematográfica real.

### Principios

1. **El Productor y Productor Ejecutivo tienen visión global del proyecto.** Pueden ver cualquier rama, cualquier módulo, cualquier indicador. Su dashboard es el único completo.

2. **El acceso desciende por responsabilidad, no por curiosidad.** Cada usuario ve lo que necesita para ejecutar su trabajo, no todo lo que existe.

3. **Cada departamento debe ver principalmente su rama funcional.** Un montador no necesita ver el presupuesto; un jefe de producción no necesita ver el raccord.

4. **Los módulos sensibles no son visibles para todos.** Financiación, contratos, presupuestos detallados, ayudas, ventas, CRM e información comercial son módulos protegidos.

5. **Dirección puede acceder a las áreas creativas y de rodaje,** pero no necesariamente a toda la información financiera ni a los detalles contractuales.

6. **Script puede acceder a continuidad, raccord, partes y planificación relacionada,** pero no a financiación ni comercialización.

7. **Postproducción puede acceder a materiales, montaje, sonido, VFX, QC y delivery,** pero no a ayudas ni contratos salvo autorización expresa del productor.

8. **Distribución y ventas pueden acceder a materiales comerciales y estrategia de explotación,** pero no a información financiera interna salvo permisos específicos del productor.

9. **El sistema debe permitir futuras políticas RBAC,** aunque no se diseñe todavía la implementación técnica. La arquitectura funcional actual debe ser compatible con un modelo RBAC futuro.

---

## 5. Matriz de permisos funcionales

| Rol | Prod. y Financiación | Creativo y Rodaje | Postproducción | Entrega | Comercialización |
|---|---|---|---|---|---|
| **Productor** | Completo | Completo | Completo | Completo | Completo |
| **Productor Ejecutivo** | Completo | Solo lectura | Solo lectura | Solo lectura | Completo |
| **Jefe de Producción** | Completo | Parcial (planificación) | Sin acceso | Parcial (costes) | Sin acceso |
| **Director** | Solo lectura (presupuesto) | Completo | Completo | Parcial (versión final) | Sin acceso |
| **Guionista** | Sin acceso | Completo (guion) | Sin acceso | Sin acceso | Sin acceso |
| **Script Supervisor** | Sin acceso | Completo (continuidad) | Sin acceso | Sin acceso | Sin acceso |
| **Ayudante de Dirección** | Sin acceso | Completo (rodaje) | Sin acceso | Sin acceso | Sin acceso |
| **Montador / Editor** | Sin acceso | Parcial (referencias) | Completo | Parcial (entregables) | Sin acceso |
| **Editor de Sonido** | Sin acceso | Sin acceso | Parcial (sonido) | Sin acceso | Sin acceso |
| **Post Supervisor** | Sin acceso | Sin acceso | Completo | Completo | Sin acceso |
| **Distribuidor** | Sin acceso | Sin acceso | Sin acceso | Completo | Completo |
| **Agente de Ventas** | Sin acceso | Sin acceso | Sin acceso | Parcial (materiales) | Completo |

**Legenda:**
- **Completo**: Acceso total a la rama (lectura, escritura, creación, eliminación).
- **Parcial**: Acceso solo a submódulos específicos dentro de la rama.
- **Solo lectura**: Puede consultar pero no modificar.
- **Sin acceso**: La rama no está visible en su Command Center.

---

## 6. Reglas de visibilidad del Command Center

1. **El Productor ve el estado global.** Su dashboard es el único que muestra indicadores de las tres ramas simultáneamente.

2. **Cada rol ve por defecto su rama principal.** Al entrar en CID, el usuario aterriza en el dashboard de su rama, no en el dashboard global.

3. **Las ramas secundarias aparecen solo cuando exista dependencia funcional.** Un director puede ver postproducción cuando el montaje comienza. Un jefe de producción puede ver rodaje cuando necesita planificar costes.

4. **Las tarjetas del dashboard deben poder ocultarse por rol.** No todos los widgets son relevantes para todos los roles.

5. **Ninguna funcionalidad debe asumirse visible para todos los usuarios.** Por defecto, un módulo es privado de su rama; el productor debe conceder acceso explícito.

6. **Las transiciones entre ramas deben estar gobernadas por eventos del proyecto.** Por ejemplo: cuando el guion está bloqueado, se habilita el desglose y el storyboard; cuando el rodaje termina, se habilita postproducción.

### Reglas UX adicionales

7. **Cada usuario ve primero su rama principal.** El dashboard de inicio se determina por el rol, no por preferencia.

8. **Mostrar tareas accionables, no botones decorativos.** Cada tarjeta del dashboard debe tener una acción real asociada. Si no hay acción posible, no mostrar el botón.

9. **Evitar dashboards vacíos.** Si una rama no tiene datos, mostrar un estado vacío informativo con la primera acción sugerida, no un grid de widgets sin contenido.

10. **Evitar módulos sin flujo operativo real.** No incluir un módulo en el Command Center hasta que tenga al menos un flujo mínimo definido (entrada → acción → salida).

11. **Las tarjetas del dashboard deben priorizar información accionable sobre información decorativa.** Mostrar siempre: estado actual, siguiente acción, riesgo si existe.

12. **El Command Center no es un escaparate de funcionalidades. Es una herramienta de trabajo.** Cada elemento debe responder a una necesidad real de la producción.

---

## 7. Rama 1: Producción y Financiación

### Propósito
Gestión del negocio de la producción: financiación, presupuesto, ayudas, inversores, contratación, plan financiero, y control de costes.

### Módulos actuales asociados
- **Budget Estimator** (`/projects/:projectId/budget`) — Estimación de presupuesto con partidas, confianza baja/media/alta, exportación.
- **Project Funding** (`/projects/:projectId/funding`) — Oportunidades de financiación (RAG matching + ayudas públicas + financiación privada).
- **Producer Pitch Pack** (`/projects/:projectId/producer-pitch`) — Dossier de productor con logline, sinopsis, presupuesto, financiación, storyboard.
- **Project Members** (`/projects/:projectId/members`) — Gestión del equipo con roles y permisos.
- **Change Requests** (`/projects/:projectId/change-requests`) — Órdenes de cambio y gobernanza de modificaciones.
- **Project Dashboard** (`/projects/:projectId/dashboard`) — Panel de control con fase Priority (budget, funding, producer pack).

### Módulos planeados / futuros
- **Funding Intelligence** — Taxonomía de ayudas, calculadora de incentivos fiscales, simulador de cash flow.
- **Tax Rebate Calculator** — Cálculo de deducciones fiscales por territorio (España, Canarias, Navarra, etc.).
- **Coproduction Portal** — Gestión de acuerdos de coproducción, splits, territorios.
- **Insurance & Bonds** — Seguros de producción, avales, completion bond.
- **Contratos** — Gestión de contratos con talento, proveedores, distribuidores.
- **Sales Agent Module** — Integración con datos de ventas y agentes.
- **Cashflow / Tesorería** — Gestión de tesorería: cobros, pagos, previsiones, gap de liquidez, alertas de descubierto.
- **Cierre Financiero** — Seguimiento del cierre financiero: hitos de desembolso, condiciones suspensivas, documentación.
- **Cost Reports** — Informes de coste por departamento, partida y periodo; desviaciones sobre presupuesto; proyecciones a cierre.
- **Business Plan** — Plan de negocio con proyecciones financieras, análisis de viabilidad, escenarios de explotación.
- **CRM Institucional** — Gestión de relaciones institucionales (organismos de ayuda, televisiones, plataformas, coproductores).
- **Comercialización Temprana** — Estrategia comercial desde desarrollo: positioning, target, ventanas, territorios.

### Usuarios objetivo
Productor, Productor Ejecutivo, Jefe de Producción.

---

## 8. Rama 2: Creativo y Rodaje

### Propósito
Desarrollo creativo y ejecución del rodaje: guion, análisis, desglose, storyboard, arte, concepto, planificación de rodaje, partes de cámara.

### Módulos actuales asociados
- **Script Analysis Pro** (`/projects/:projectId/script-analysis`) — Análisis avanzado de guion con extracción de personajes, localizaciones, estructura.
- **Breakdown** (`/projects/:projectId/breakdown`) — Desglose técnico por escenas y departamentos.
- **Storyboard Builder** (`/projects/:projectId/storyboard-builder`) — Creación de storyboard con IA, 4 pestañas (analizar, secuencias, personajes, planos).
- **Concept Art** (tab en ProjectDetailPage) — Generación de arte conceptual y key visual.
- **Pipeline Builder** (`/cid/pipeline-builder`) — Pipeline generativo multi-modo (storyboard, imagen, vídeo, doblaje).
- **Character Bible** (panel en StoryboardBuilder) — Definiciones visuales de personajes.
- **Character Breakdown** (panel en StoryboardBuilder) — Apariciones de personajes por secuencia.
- **Director Feedback Panel** (panel en StoryboardBuilder) — Retroalimentación del director sobre planos.
- **Director Visual Reference Panel** (panel en StoryboardBuilder) — Tablero de referencias visuales del director.
- **Cinematic Intelligence** (parámetro en generación de storyboard) — Lente de director e inteligencia de montaje.

### Módulos planeados / futuros
- **Shooting Plan** — Plan de rodaje con desglose por jornadas.
- **Shot List** — Lista de planos por escena.
- **Call Sheet Generator** — Generación automática de orden de rodaje.
- **Daily Reports** — Partes de producción diarios.
- **Continuity / Raccord** — Herramienta de continuidad para Script Supervisor.
- **Scene Scheduling** — Planificación de escenas por localización, personajes, disponibilidad.
- **Director's Notebook** — Notas del director por escena/plano.
- **Visual Bible** — Biblia visual del proyecto: paleta cromática, referencias estéticas, dirección de arte, moodboards.
- **Casting Manager** — Gestión de casting por personaje, propuestas, audiciones, químicas, decisiones.
- **Location Manager** — Gestión de localizaciones: scouting, referencias, permisos, disponibilidad, costes.
- **Transporte y Alojamiento** — Gestión de transporte y alojamiento del equipo: rutas, vehículos, hoteles, dietas, coordinación logística.

### Usuarios objetivo
Director, Guionista, Script Supervisor, Ayudante de Dirección.

---

## 9. Rama 3: Postproducción, Entrega y Comercialización

### Propósito
Cierre de la producción: montaje, sonido, VFX, QC, entregas, distribución, ventas, CRM, festivales, explotación.

### Módulos actuales asociados
- **Editorial Assembly** (`/projects/:projectId/editorial`) — Montaje editorial con takes, sync, assembly cut, exportación FCPXML/DaVinci.
- **Reviews Overview** (`/projects/:projectId/reviews`) — Pipeline de revisión y aprobación.
- **Review Detail** (`/projects/:projectId/reviews/:reviewId`) — Revisión individual con comentarios y flujo de aprobación.
- **Delivery Overview** (`/projects/:projectId/delivery`) — Gestión de entregables finales.
- **Deliverable Detail** (`/projects/:projectId/delivery/:deliverableId`) — Detalle de entregable individual.
- **Distribution Pack** (`/projects/:projectId/distribution`) — Paquetes de distribución por tipo (distribuidor, agente de ventas, festival, cine, plataforma).
- **Commercial CRM** (`/projects/:projectId/crm`) — Pipeline de ventas con oportunidades y tareas.

### Módulos planeados / futuros
- **Sound Post** — Edición de sonido, diálogos, ADR, Foley, mezcla.
- **Music / Score** — Gestión de banda sonora, composición, licencias, supervisión musical.
- **Sound Restoration** — Restauración de sonido, limpieza de diálogos, reposición, conformado de pistas.
- **VFX Management** — Seguimiento de planos VFX, versiones, aprobaciones, proveedores.
- **Conform / QC** — Conformado, control de calidad, informes, informes de materiales.
- **Color Grading** — Gestión de etalonaje: LUTs, referencias, versiones, aprobación de color.
- **DCP / OV / Closed Captions** — Generación de DCP, versión original, subtítulos, closed captions.
- **Broadcast & OTT Delivery** — Entregas para televisión y plataformas: especificaciones, formats, metadatos, cumplimiento técnico.
- **Festival Strategy** — Planificación de festivales, deadlines, requisitos de copia, premiere strategy.
- **Sales CRM avanzado** — Seguimiento de ventas por territorio, reporting.
- **Exploitation Dashboard** — Ingresos por ventana (cine, TV, plataforma, físico).

### Usuarios objetivo
Montador, Editor de Sonido, Post Supervisor, Distribuidor, Agente de Ventas.

---

## 10. Mapa de módulos actuales por rama

### Rama 1: Producción y Financiación (8 módulos)
| Módulo | Tipo | Estado |
|---|---|---|
| Budget Estimator | Página | Completo |
| Project Funding | Página | Completo |
| Producer Pitch Pack | Página | Completo |
| Project Members | Página | Completo |
| Change Requests | Página | Completo |
| Project Dashboard (fase Priority) | Página | Completo |
| Producer Studio Hub | Página | Completo |
| Commercial CRM (*) | Página | Completo |

(*) CRM comparte funcionalidad con Rama 3; el acceso debe controlarse por rol.

### Rama 2: Creativo y Rodaje (10 módulos)
| Módulo | Tipo | Estado |
|---|---|---|
| Script Analysis Pro | Página | Completo |
| Breakdown | Página | Completo |
| Storyboard Builder | Página | Completo |
| Pipeline Builder | Página | Completo |
| Concept Art | Componente (tab) | Parcial |
| Character Bible | Componente (panel) | Parcial |
| Character Breakdown | Componente (panel) | Parcial |
| Director Feedback Panel | Componente (panel) | Completo |
| Director Visual Reference Panel | Componente (panel) | Completo |
| Cinematic Intelligence | Parámetro (backend) | Placeholder |

### Rama 3: Postproducción, Entrega y Comercialización (7 módulos)
| Módulo | Tipo | Estado |
|---|---|---|
| Editorial Assembly | Página | Completo |
| Reviews Overview | Página | Parcial |
| Review Detail | Página | Parcial |
| Delivery Overview | Página | Parcial |
| Deliverable Detail | Página | Placeholder |
| Distribution Pack | Página | Completo |
| Commercial CRM | Página | Completo |

### Módulos transversales (visibles según rol)
| Módulo | Rama primaria | Visible también para |
|---|---|---|
| Project Dashboard | Productor (global) | Jefe de Producción (parcial), Director (solo lectura) |
| Project Members | Producción | Todos (solo lectura) |
| Change Requests | Producción | Todos (según módulo afectado) |
| Documents | Transversal | Según permiso del documento |
| Reports | Transversal | Según tipo de reporte |

---

## 11. Flujo de trabajo entre ramas

### Dependencias funcionales

```
RAMA 1 (Producción)
  │
  ├── Presupuesto → alimenta a Rama 2 (plan de rodaje) y Rama 3 (costes de post)
  ├── Financiación → determina alcance de Rama 2 y Rama 3
  └── Dossier → consume de Rama 2 (storyboard, análisis) y Rama 3 (materiales)
  
RAMA 2 (Creativo y Rodaje)
  │
  ├── Guion bloqueado → habilita desglose y storyboard
  ├── Storyboard → alimenta a Rama 1 (dossier) y Rama 3 (montaje)
  └── Partes de rodaje → alimentan a Rama 1 (costes) y Rama 3 (material)

RAMA 3 (Postproducción, Entrega, Comercialización)
  │
  ├── Assembly cut → alimenta a Rama 1 (versión para inversores)
  ├── Entregables → base para comercialización
  └── CRM → retroalimenta a Rama 1 (proyección de ingresos)
```

### Eventos de transición entre ramas

| Evento | Transición | Efecto en Command Center |
|---|---|---|
| Guion bloqueado | Rama 2 → Rama 1 | El dossier de productor puede empezar a generarse |
| Rodaje completado | Rama 2 → Rama 3 | La rama Postproducción se activa en el dashboard del director |
| Primer corte completado | Rama 3 → Rama 1 | La versión para inversores está disponible |
| Entrega completada | Rama 3 → Comercialización | El CRM y distribución se activan completamente |
| Hito de financiación | Rama 1 → Rama 2 | El presupuesto realimenta el plan de rodaje |

---

## 12. Flujo de proyecto por fases

El ciclo de vida completo de una producción cinematográfica en CID se organiza en las siguientes fases. Cada fase tiene responsables, entregables y módulos CID asociados.

### Fase 1: Idea
| Atributo | Descripción |
|---|---|
| **Responsables** | Productor, Director, Guionista |
| **Entregables** | Logline, sinopsis, tratamiento, nota de intención |
| **Módulos CID** | Proyecto nuevo, Script Analysis Pro (básico) |
| **Ramas involucradas** | Rama 2 (creación de concepto) |

### Fase 2: Desarrollo
| Atributo | Descripción |
|---|---|
| **Responsables** | Guionista, Director, Productor |
| **Entregables** | Guion literario, análisis de guion, desglose preliminar, perfiles de personaje |
| **Módulos CID** | Script Analysis Pro, Breakdown, Character Bible, Character Breakdown |
| **Ramas involucradas** | Rama 2 (Creativo) |

### Fase 3: Financiación
| Atributo | Descripción |
|---|---|
| **Responsables** | Productor, Productor Ejecutivo |
| **Entregables** | Presupuesto, plan de financiación, dossier de productor, solicitudes de ayuda, tax rebate, acuerdos de coproducción |
| **Módulos CID** | Budget Estimator, Project Funding, Producer Pitch Pack, Funding Intelligence |
| **Ramas involucradas** | Rama 1 (Producción y Financiación) |

### Fase 4: Preproducción
| Atributo | Descripción |
|---|---|
| **Responsables** | Director, Ayudante de Dirección, Jefe de Producción, Script Supervisor |
| **Entregables** | Storyboard, plan de rodaje, desglose técnico completo, casting, localizaciones, bible visual, órdenes de cambio |
| **Módulos CID** | Storyboard Builder, Breakdown, Pipeline Builder, Concept Art, Director Visual Reference, Character Bible |
| **Ramas involucradas** | Rama 2 (Creativo y Rodaje) |

### Fase 5: Rodaje
| Atributo | Descripción |
|---|---|
| **Responsables** | Director, Ayudante de Dirección, Script Supervisor, Jefe de Producción |
| **Entregables** | Partes de cámara, partes de sonido, raccord, continuidad, informes diarios |
| **Módulos CID** | Project Members, Change Requests, (futuro: Call Sheet, Daily Reports, Continuity) |
| **Ramas involucradas** | Rama 2 (Creativo y Rodaje), Rama 1 (control de costes) |

### Fase 6: Postproducción
| Atributo | Descripción |
|---|---|
| **Responsables** | Montador, Post Supervisor, Editor de Sonido, Director |
| **Entregables** | Assembly cut, montaje fino, mezcla de sonido, VFX, color, conformado, QC |
| **Módulos CID** | Editorial Assembly, Reviews, (futuro: Sound Post, VFX Management, Color Grading, Conform/QC) |
| **Ramas involucradas** | Rama 3 (Postproducción) |

### Fase 7: Entrega
| Atributo | Descripción |
|---|---|
| **Responsables** | Post Supervisor, Productor |
| **Entregables** | DCP, OV, M&E, closed captions, broadcast master, OTT package, metadatos |
| **Módulos CID** | Delivery Overview, Deliverable Detail, (futuro: DCP Generation, Broadcast & OTT Delivery) |
| **Ramas involucradas** | Rama 3 (Entrega) |

### Fase 8: Comercialización
| Atributo | Descripción |
|---|---|
| **Responsables** | Distribuidor, Agente de Ventas, Productor |
| **Entregables** | Paquetes de distribución, materiales promocionales, CRM de ventas, estrategia de festivales, plan de explotación |
| **Módulos CID** | Distribution Pack, Commercial CRM, (futuro: Festival Strategy, Exploitation Dashboard) |
| **Ramas involucradas** | Rama 3 (Comercialización), Rama 1 (proyección de ingresos) |

---

## 13. Command Center — Tarjetas de estado por rama

La pantalla principal de CID para cada rol muestra tarjetas de estado. El Productor ve las tres tarjetas simultáneamente. Los demás roles ven principalmente su rama.

### Tarjeta: Producción y Financiación (Rama 1)

```
┌──────────────────────────────────────────────┐
│  PRODUCCIÓN & FINANCIACIÓN        [●] Ámbar  │
├──────────────────────────────────────────────┤
│  Financiación cerrada   65%  ███████░░░░░░░  │
│  Gap pendiente          €240K                │
│  Ayudas activas         3 de 5               │
│  Presupuesto ejecutado  42%  ████░░░░░░░░░░  │
├──────────────────────────────────────────────┤
│  ⚠️  Riesgo: Ayuda ICAA sin resolver          │
│  ▶ Siguiente acción: Revisar solicitudes     │
│  📊 Progreso: Financiación ▸▸▸ Presupuesto   │
│  🔗 Ir a: Financiación · Presupuesto · Ayudas│
└──────────────────────────────────────────────┘
```

### Tarjeta: Creativo y Rodaje (Rama 2)

```
┌──────────────────────────────────────────────┐
│  CREATIVO & RODAJE                [●] Verde   │
├──────────────────────────────────────────────┤
│  Guion analizado      v3      ████████████░  │
│  Storyboard           78%     ████████░░░░░  │
│  Desglose completado  100%    ██████████████  │
│  Plan de rodaje       No iniciado             │
├──────────────────────────────────────────────┤
│  ⚠️  Riesgo: Plan de rodaje no generado       │
│  ▶ Siguiente acción: Generar plan de rodaje  │
│  📊 Progreso: Guion ▸▸ Storyboard ▸▸ Rodaje  │
│  🔗 Ir a: Guion · Storyboard · Desglose      │
└──────────────────────────────────────────────┘
```

### Tarjeta: Postproducción y Comercialización (Rama 3)

```
┌──────────────────────────────────────────────┐
│  POSTPRODUCCIÓN & COMERCIALIZACIÓN  [●] Rojo  │
├──────────────────────────────────────────────┤
│  Montaje             Corte 1 pendiente        │
│  Sonido              No iniciado              │
│  Delivery            0 de 12 entregables      │
│  Ventas              4 oportunidades activas  │
├──────────────────────────────────────────────┤
│  ⚠️  Riesgo: Retraso en montaje               │
│  ▶ Siguiente acción: Revisar material         │
│  📊 Progreso: Montaje ▸▸ Sonido ▸▸ Delivery   │
│  🔗 Ir a: Montaje · Delivery · CRM           │
└──────────────────────────────────────────────┘
```

### Reglas de las tarjetas
- Cada tarjeta muestra un semáforo de estado general (Verde/Ámbar/Rojo).
- Las barras de progreso son relativas a los hitos definidos para cada rama.
- Los riesgos se muestran solo cuando existen alertas activas.
- "Siguiente acción" es la tarea de mayor prioridad pendiente en la rama.
- "Accesos rápidos" (🔗) son enlaces directos a los módulos principales de la rama para navegación inmediata.
- El Productor ve las tres tarjetas en una fila de tres columnas.
- Los roles no productor ven su tarjeta principal en grande y las otras colapsadas.

---

## 14. Ejemplos de experiencia por rol

### Productor

Al entrar en CID, el Productor ve:

1. **Dashboard global** con tres columnas (una por rama) mostrando:
   - Rama 1: Estado de financiación (conseguido vs objetivo), presupuesto (ejecutado vs plan), alertas de cambio.
   - Rama 2: Progreso de guion (versión, análisis completado), storyboard (planos generados vs planificados).
   - Rama 3: Estado de montaje (takes sincronizadas, corte generado), entregas pendientes, pipeline de ventas.
2. **Barra superior** con acceso directo a cualquier módulo de cualquier rama.
3. **Widget de riesgos**: alertas consolidadas de todas las ramas (presupuesto excedido, guion no bloqueado, entregas en riesgo).
4. **Acciones rápidas**: crear proyecto, añadir miembro, generar dossier, revisar finanzas.

### Director

Al entrar en CID, el Director ve:

1. **Dashboard de Rama 2** con:
   - Estado del guion (versión actual, análisis completado, personajes extraídos).
   - Progreso del storyboard (secuencias completadas, planos generados, feedback pendiente).
   - Enlace a referencias visuales y panel de feedback.
2. **Acceso a Rama 3** solo después de que el rodaje esté completo (montaje, revisiones).
3. **Sección de dirección**: notas por escena, vision board, lente de dirección.
4. **No ve**: presupuesto detallado, financiación, contratos, CRM, distribución.

### Ayudante de Dirección

Al entrar en CID, el Ayudante de Dirección ve:

1. **Dashboard de Rama 2 (subsección rodaje)** con:
   - Plan de rodaje (si implementado).
   - Desglose por jornada.
   - Lista de planos pendientes.
2. **Acceso a miembros del equipo** para coordinar llamadas.
3. **No ve**: storyboard completo, guion en desarrollo, presupuesto, financiación, postproducción, CRM.

### Script Supervisor

Al entrar en CID, el Script Supervisor ve:

1. **Dashboard de continuidad** con:
   - Raccord por escena/plano.
   - Partes de cámara.
   - Notas de continuidad.
2. **Acceso al guion** en modo consulta (versión bloqueada).
3. **No ve**: presupuesto, financiación, contratos, postproducción, distribución, CRM.

### Montador / Editor

Al entrar en CID, el Montador ve:

1. **Dashboard de Rama 3 (subsección montaje)** con:
   - Editorial Assembly: takes, sync, assembly cut.
   - FCPXML / DaVinci export.
   - Revisiones pendientes.
2. **Acceso a referencias del director** (storyboard, notas) en modo consulta.
3. **No ve**: presupuesto, financiación, ayudas, contratos, CRM, distribución.

### Distribuidor

Al entrar en CID, el Distribuidor ve:

1. **Dashboard de Comercialización** con:
   - Distribution Pack (generar/exportar por tipo).
   - CRM de ventas (oportunidades, pipeline, tareas).
   - Entregables disponibles para distribución.
2. **Acceso a materiales**: storyboard seleccionado, dossier de productor (versión comercial), metadatos técnicos.
3. **No ve**: presupuesto interno, financiación, ayudas, contratos, guion completo, montaje en curso.

---

## 15. Indicadores y métricas por rama

### Rama 1 — Producción y Financiación
| Indicador | Descripción |
|---|---|
| Presupuesto total vs ejecutado | Porcentaje de presupuesto consumido |
| Financiación conseguida | Fondos asegurados vs objetivo total |
| Gap de tesorería | Diferencia entre cobros y pagos previstos |
| Cierre financiero | Porcentaje de hitos de desembolso cumplidos |
| Ayudas solicitadas | Número de solicitudes enviadas, pendientes, concedidas |
| Cost reports | Coste real vs presupuestado por partida y departamento |
| Número de inversores | Inversores captados vs objetivo |
| Coste por departamento | Desviación por área |
| ROI estimado | Retorno proyectado sobre inversión total |

### Rama 2 — Creativo y Rodaje
| Indicador | Descripción |
|---|---|
| Progreso de guion | Versión actual, análisis completado, escenas validadas |
| Storyboard completado | Planos generados vs planificados |
| Días de rodaje | Días ejecutados vs planificados |
| Desglose completado | Escenas desglosadas vs totales |
| Transporte y alojamiento | Reservas confirmadas vs necesidades del plan de rodaje |
| Personajes definidos | Personajes con bible visual completada |

### Rama 3 — Postproducción, Entrega y Comercialización
| Indicador | Descripción |
|---|---|
| Takes sincronizadas | Porcentaje de material sincronizado |
| Assembly cut | Corte generado vs versiones pendientes |
| Revisiones pendientes | Número de assets pendientes de aprobación |
| Entregables completados | Deliverables generados vs requeridos |
| Oportunidades en CRM | Pipeline activo por etapa |
| Paquetes de distribución | Paquetes generados por tipo |

### Indicadores globales (Productor)
| Indicador | Fuente |
|---|---|
| Health score del proyecto | Algoritmo combinado de las tres ramas |
| Alertas críticas | Riesgos consolidados (presupuesto, plazo, calidad) |
| Próximos hitos | Eventos de transición entre ramas |
| Estado general por rama | Semáforo por rama (verde/ámbar/rojo) |

---

## 16. Implicaciones para el producto

### Navegación
- La barra de navegación principal debe mostrar las tres ramas, pero solo las accesibles para el rol actual.
- El dashboard de inicio debe ser específico por rol, no el mismo para todos.
- El breadcrumb debe indicar la rama actual y el módulo.

### Onboarding
- Al asignar un rol por primera vez, CID debe mostrar un tour guiado de la rama correspondiente.
- El Productor debe recibir un tour completo de las tres ramas.
- Cada rol debe ver una explicación de qué ramas tiene visibles y por qué.

### UX de permisos
- Los módulos no accesibles no deben aparecer en la navegación ni en búsquedas.
- Si un usuario intenta acceder por URL directa a un módulo sin permiso, debe ver una pantalla de "acceso restringido" con opción de solicitar permiso al Productor.
- El Productor debe poder gestionar permisos excepcionales desde un panel central.

### Dashboard por rama
- Rama 1 dashboard: widgets de financiación, presupuesto, ayudas, equipo.
- Rama 2 dashboard: widgets de guion, storyboard, desglose, personajes.
- Rama 3 dashboard: widgets de montaje, revisiones, entregas, CRM.
- Productor dashboard: todos los anteriores en formato resumido + health score global.

### Estados y transiciones
- Los módulos deben mostrar su estado actual en relación con la rama (bloqueado, listo, en progreso, completado).
- Las dependencias entre ramas deben ser visibles: "El storyboard no puede comenzar hasta que el guion esté analizado".
- Los eventos de transición deben generar notificaciones a los roles afectados.

---

## 17. Futuras extensiones

### Nuevos módulos por rama
| Rama | Módulo futuro | Prioridad estimada |
|---|---|---|
| Producción | Funding Intelligence | Alta |
| Producción | Tax Rebate Calculator | Alta |
| Producción | Coproduction Portal | Alta |
| Producción | Cashflow / Tesorería | Alta |
| Producción | Cierre Financiero | Alta |
| Producción | Cost Reports | Alta |
| Producción | Business Plan | Alta |
| Producción | CRM Institucional | Alta |
| Producción | Comercialización Temprana | Alta |
| Producción | Insurance & Bonds | Media |
| Producción | Sales Agent Module | Media |
| Producción | Contratos | Media |
| Creativo | Shooting Plan | Alta |
| Creativo | Call Sheet Generator | Alta |
| Creativo | Daily Reports | Alta |
| Creativo | Continuity / Raccord | Alta |
| Creativo | Visual Bible | Alta |
| Creativo | Casting Manager | Alta |
| Creativo | Location Manager | Alta |
| Creativo | Transporte y Alojamiento | Alta |
| Creativo | Director's Notebook | Media |
| Postproducción | Sound Post | Alta |
| Postproducción | Music / Score | Alta |
| Postproducción | Sound Restoration | Alta |
| Postproducción | VFX Management | Alta |
| Postproducción | Color Grading | Alta |
| Postproducción | Conform / QC | Media |
| Postproducción | DCP / OV / Closed Captions | Media |
| Comercialización | Broadcast & OTT Delivery | Alta |
| Comercialización | Festival Strategy | Alta |
| Comercialización | Sales CRM avanzado | Alta |
| Comercialización | Exploitation Dashboard | Media |

### Evolución de la matriz de permisos
- En futuras versiones, la matriz de permisos debe ser configurable por proyecto.
- El Productor debe poder crear roles personalizados con permisos específicos.
- Los permisos deben poder concederse a nivel de módulo, no solo de rama.
- Debe ser posible conceder acceso temporal a una rama (ej. "el Director puede ver postproducción durante 2 semanas").
- Los permisos deben auditarse: quién accedió a qué módulo y cuándo.

### Integración con planes de suscripción
- Los módulos de Rama 1 pueden requerir plan Producer o superior.
- Los módulos de Rama 2 pueden estar disponibles desde plan Creator.
- Los módulos de Rama 3 pueden requerir plan Studio o Enterprise para funcionalidades avanzadas (CRM, distribución).

---

## 18. NO IMPLEMENTAR TODAVÍA

El presente documento es exclusivamente de **arquitectura funcional y de producto**. Los siguientes elementos NO deben implementarse en esta fase:

- **RBAC real** — No diseñar ni implementar sistema de control de acceso basado en roles. La matriz de permisos es conceptual.
- **Backend** — No crear endpoints, servicios, ni lógica de autorización en el servidor.
- **Frontend** — No crear páginas, componentes, rutas, ni lógica de visibilidad en el cliente.
- **Base de datos** — No crear tablas, esquemas, migraciones, ni modelos de permisos.
- **Automatizaciones** — No crear flujos automáticos de transición entre ramas.
- **Sistema de notificaciones** — No implementar alertas ni eventos reales.
- **Métricas en tiempo real** — No conectar indicadores a datos reales.
- **Command Center UI** — No maquetar ni implementar las tarjetas de estado como interfaz funcional.

Todo lo anterior son **decisiones de producto diferidas** que deben validarse primero con este modelo funcional antes de cualquier implementación técnica.

---

## 19. Próxima fase

### CID.PRODUCT.ARCHITECTURE.DATA.MODEL.1

Revisión del presente documento por:

- **Completitud**: ¿cubre todas las áreas de una producción real?
- **Coherencia**: ¿los módulos actuales están bien ubicados en sus ramas?
- **Permisos**: ¿la matriz refleja correctamente la realidad de una producción?
- **Flujo**: ¿las transiciones entre ramas tienen sentido?
- **UX**: ¿las reglas de visibilidad son implementables sin backend?

La revisión debe producir una versión 1.1 con correcciones y validaciones del equipo de producto.

---

## Historial de revisiones

| Fecha | Versión | Cambios |
|---|---|---|
| 2026-06-02 | 1.0 | Creación inicial del documento con arquitectura de 3 ramas, matriz de permisos, reglas de visibilidad, ejemplos por rol y mapa de módulos actuales. |
| 2026-06-02 | 1.1 | Añadidas secciones: Flujo de proyecto por fases (12), Command Center tarjetas (13), NO IMPLEMENTAR TODAVÍA (18), Próxima fase (19). Añadidos módulos faltantes en las tres ramas. Ampliadas reglas UX (6). Renumeración de secciones. |
| 2026-06-03 | 1.2 | Revisión contra 11 criterios. Corregida próxima fase a DATA.MODEL.1. Añadidos accesos rápidos a tarjetas. Añadidos cashflow/tesorería, cierre financiero, cost reports, transporte/alojamiento. |
