# AILink Script-to-Production Breakdown — Demo Readiness

**Phase:** AILINK.CID.SCRIPT_TO_PRODUCTION_BREAKDOWN.DEMO.READINESS.PHASE5
**Version:** 1.0
**Date:** 2026-06-13
**Status:** Documental / Test-only

---

## 1. Propósito

Este documento prepara la presentación segura de la demo funcional de Script-to-Production Breakdown a productores independientes.

Objetivos:
- Explicar qué se enseña en la demo.
- Explicar qué no se promete.
- Conectar guion, desglose, viabilidad y presupuesto preliminar.
- Preparar mensaje seguro de beta/controlada.
- Definir claims permitidos y prohibidos.
- Establecer criterios de aceptación para la demo.

---

## 2. Estado actual de la demo

- Prototipo funcional local (CLI Python).
- Proyecto Demo Bruma (guion ficticio controlado).
- Genera 3 formatos de salida: JSON, Markdown, Excel `.xlsx`.
- Excel generado con stdlib (`zipfile` + `xml.etree`), sin openpyxl.
- No usa IA real. No simula IA.
- No procesa guiones reales.
- Parser determinista con marcadores controlados.
- Validado manualmente en fase E2E (fase 4.2).

### Datos de la demo

| Dato | Valor |
|------|-------|
| Escenas | 8 |
| Personajes | 5 |
| Localizaciones | 5 |
| Riesgos | 10 |
| Categorías de presupuesto | 18 |
| IDs de aislamiento | organization_id, tenant_id, project_id, film_id |

---

## 3. Flujo de demo de 5 minutos

| Min | Acción | Qué se ve |
|-----|--------|-----------|
| 0:00 | Abrir explicación del problema | Diapositiva o pantalla en blanco |
| 0:45 | Enseñar guion ficticio | Archivo de texto `proyecto_demo_bruma_script.txt` |
| 1:30 | Ejecutar o mostrar salida generada | Terminal con comandos ejecutados |
| 2:15 | Enseñar Markdown en pantalla | `breakdown.md` abierto en editor |
| 3:00 | Enseñar Excel editable | `script_breakdown_demo_bruma.xlsx` abierto en LibreOffice/Excel |
| 3:45 | Explicar aislamiento productora/película | Sección Metadata del Markdown |
| 4:30 | Cerrar con próximos pasos | Mensaje de límites y beta futura |

---

## 4. Guion verbal de demo

### Frases preparadas

- "Esto es una demo controlada con un guion ficticio."
- "No es un presupuesto definitivo."
- "Sirve para acelerar el primer análisis del productor."
- "Todo requiere revisión humana."
- "El valor está en conectar guion, producción y finanzas."

### Apertura

> "Hoy les muestro una herramienta que toma un guion y genera un primer desglose de producción: escenas, personajes, localizaciones, riesgos y un presupuesto preliminar revisable. Esto es una demo controlada con un guion ficticio."

### Cierre

> "Esto es un punto de partida, no un producto final. Sirve para que el productor tenga una primera visión estructurada antes de sentarse con su equipo. Todo requiere revisión humana."

---

## 5. Qué enseñar

| Sección | Qué se muestra |
|---------|----------------|
| Resumen del proyecto | Título, tipo, género, duración, semanas, moneda |
| Escenas | 8 escenas con localización, INT/EXT, Día/Noche, personajes |
| Personajes | 5 personajes con rol, escenas, edad, complejidad |
| Localizaciones | 5 localizaciones con tipo, permisos, complejidad |
| Riesgos | 10 riesgos con impacto, probabilidad, mitigación |
| Viabilidad | 11 indicadores con semáforos y justificación |
| Presupuesto preliminar | 18 categorías con 3 escenarios (baja/media/alta) |
| Recomendaciones | 10 recomendaciones concretas |
| Revisión humana | 7 notas de revisión pendiente |
| Metadata/aislamiento | organization_id, tenant_id, project_id, film_id |

---

## 6. Qué NO enseñar todavía

| Elemento | Razón |
|----------|-------|
| Guiones reales | Solo guion ficticio controlado |
| Presupuesto definitivo | Solo preliminar revisable |
| PDF | No generado en esta fase |
| Integración con SaaS real | No implementada |
| Integración con Production Finance Control real | Futura |
| Integración con Sync Dialogue real | Independiente |
| IA real | Parser determinista |
| OCR | No implementado |
| RAG multimodal | No implementado |
| Plan de rodaje automático final | No implementado |

---

## 7. Claims permitidos

- "primer desglose orientativo"
- "presupuesto preliminar revisable"
- "apoyo al productor"
- "detección temprana de riesgos"
- "demo local controlada"
- "requiere revisión humana"

---

## 8. Claims prohibidos

- "presupuesto exacto"
- "sustituye al productor"
- "sustituye al director de producción"
- "garantiza viabilidad"
- "producto final"
- "producto disponible"
- "IA real ya integrada"
- "procesa cualquier guion real"
- "integración SaaS ya disponible"

---

## 9. Preguntas esperables de productores

### ¿Puede analizar mi guion real?
> "Actualmente no. Esta demo solo funciona con un guion ficticio controlado. La lectura de guiones reales está en nuestra hoja de ruta, siempre bajo autorización y con revisión humana."

### ¿Esto sustituye a un director de producción?
> "No. Es una herramienta de apoyo que acelera el primer análisis. La decisión final siempre es del equipo de producción."

### ¿El presupuesto es fiable?
> "Es un presupuesto preliminar revisable. Sirve como punto de partida para la conversación con el equipo financiero. No es definitivo."

### ¿Se puede exportar a Excel?
> "Sí. Genera un archivo `.xlsx` editable con 10 hojas: resumen, escenas, personajes, localizaciones, riesgos, viabilidad, presupuesto, recomendaciones, revisión humana y metadata."

### ¿Se puede conectar con facturas y gastos reales?
> "No todavía. Estamos desarrollando Production Finance Control para comparar previsto vs real. Esta demo es el primer paso."

### ¿Se puede usar por varias películas de una productora?
> "Sí. El sistema está diseñado para aislamiento multi-película. Cada proyecto tiene su propio espacio con organization_id, tenant_id, project_id y film_id."

### ¿Se mezclan los datos entre proyectos?
> "No. Cada película tiene sus propios datos. No se cruzan datos entre películas ni entre productoras."

### ¿Qué pasa con la confidencialidad del guion?
> "Esta demo no procesa guiones reales. Cuando se implemente la lectura de guiones, se trabajará bajo NDA y con procesamiento local."

### ¿Cuándo estaría disponible para beta?
> "Estamos en fase de preparación. La beta privada estará disponible pronto para productores que quieran probar la herramienta."

### ¿Qué coste tendría?
> "La beta será gratuita para productores seleccionados. El modelo de precios final se definirá tras la fase de beta."

---

## 10. Aislamiento productora/película

- Una productora puede tener varias películas.
- Cada película/proyecto tiene su propio espacio.
- No se mezclan datos entre películas.
- No se cruzan datos entre productoras.

### IDs de aislamiento

| ID | Propósito | Valor demo |
|----|-----------|------------|
| organization_id | Identifica la productora | ORG-DEMO-001 |
| tenant_id | Identifica el tenant/espacio | TENANT-DEMO-001 |
| project_id | Identifica el proyecto | PROJECT-DEMO-001 |
| film_id | Identifica la película | FILM-DEMO-001 |

---

## 11. Conexión con Production Finance Control

- Esta demo genera presupuesto preliminar (3 escenarios: baja/media/alta).
- Production Finance Control futuro comparará previsto vs real.
- No hay integración real todavía.
- El Excel actual es demo y revisable.

---

## 12. Conexión con CID

- Esto encaja con **CID Script Intelligence** (lectura y desglose de guiones).
- **CID Production Intelligence** (planificación y viabilidad).
- **CID Production Finance Control** (presupuesto previsto vs real).
- No es el SaaS completo todavía.

---

## 13. Checklist antes de enseñar

- [ ] Repo limpio (`git status --short` vacío).
- [ ] Ejecutar demo en `/tmp` (no en el repo).
- [ ] No usar guion real.
- [ ] Confirmar que solo hay JSON, Markdown y XLSX en la salida.
- [ ] Confirmar que no hay PDF/HTML/CSV.
- [ ] Abrir Excel antes para verificar que se abre correctamente.
- [ ] Tener mensaje de límites preparado.
- [ ] Pedir feedback concreto al productor.

---

## 14. Criterios de PASS/LIMITED PASS/FAIL

| Criterio | PASS | LIMITED PASS | FAIL |
|----------|------|--------------|------|
| Ejecución | Genera salidas correctas | Genera salidas con warnings | No genera salidas |
| Excel | Se entiende, 10 hojas claras | Funcional pero necesita pulido visual | No se abre o confunde |
| Mensaje | Seguro, sin prometer de más | Mayormente seguro, algunos claims ambiguos | Promete demasiado |
| Formatos | Solo JSON/MD/XLSX | JSON/MD/XLSX + algún formato extra no autorizado | PDF/HTML/CSV generados |

---

## 15. Próximos pasos tras la demo

1. Pulido visual de Excel (colores de semáforo, bordes, anchos automáticos).
2. Script de demo comercial (guion verbal completo).
3. Landing futura para presentación pública.
4. Beta privada con productores seleccionados.
5. Conexión futura con Production Finance Control.
6. Más adelante: lectura de guiones reales bajo autorización y NDA.

---

## 16. No-goals

- No código runtime.
- No runtime.
- No Excel nuevo generado en esta fase.
- No PDF.
- No HTML.
- No CSV.
- No IA real.
- No guiones reales.
- No integración real con SaaS.
- No integración real con Production Finance Control.
- No integración real con Sync Dialogue.
