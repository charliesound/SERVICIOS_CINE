# AILink Script-to-Production Breakdown - Demo Visual QA

**Phase:** AILINK.CID.SCRIPT_TO_PRODUCTION_BREAKDOWN.DEMO.VISUAL.QA.PHASE5.1
**Version:** 1.0
**Date:** 2026-06-13
**Status:** Documental / Test-only

---

## 1. Propósito

Este documento define una revisión visual y comercial de la demo funcional de Script-to-Production Breakdown antes de enseñarla a productores.

Objetivos:

- Evaluar si la demo se entiende visualmente.
- Comprobar si el Excel es útil para enseñar a productores.
- Detectar necesidades de pulido visual antes de una presentación real.
- No modificar código en esta fase.
- Mantener la separación entre demo local controlada y producto final.

---

## 2. Estado actual

- Demo basada en Proyecto Demo Bruma.
- Salidas funcionales: JSON, Markdown y Excel `.xlsx` editable.
- Excel generado con stdlib, sin openpyxl.
- Demo local controlada.
- No procesa guiones reales.
- No usa IA real.
- El Excel contiene 10 hojas: Resumen, Escenas, Personajes, Localizaciones, Riesgos, Viabilidad, Presupuesto, Recomendaciones, Revisión humana y Metadata.
- La demo mantiene aislamiento mediante organization_id, tenant_id, project_id y film_id.
- La demo no genera PDF/HTML/CSV.

---

## 3. Criterios visuales generales

La revisión debe valorar si una persona productora no técnica entiende la demo sin explicación excesiva.

Checklist visual general:

- Claridad para productor no técnico.
- Legibilidad en pantalla.
- Orden lógico de hojas.
- Lenguaje comprensible.
- Advertencias visibles.
- Separación entre demo y producto final.
- Presupuesto claramente preliminar.
- Revisión humana visible.
- Metadata/aislamiento presente sin dominar la presentación.
- Flujo narrativo claro: guion -> producción -> finanzas.

---

## 4. Criterios por hoja Excel

### 4.1 Resumen

| Criterio | Descripción |
|---|---|
| Qué debe comunicar | Qué proyecto se está analizando, qué tipo de demo es y cuál es la lectura inicial. |
| Qué debe verse primero | Proyecto Demo Bruma, tipo de obra, duración, moneda, viabilidad global y advertencia de demo. |
| Posibles problemas visuales | Que parezca una ficha técnica final o que oculte que no es presupuesto definitivo. |
| PASS | El productor entiende el contexto en menos de 20 segundos y ve que es demo controlada. |
| LIMITED PASS | Se entiende, pero necesita una portada o explicación inicial más clara. |
| FAIL | El productor no entiende qué está mirando o cree que es un producto final. |

### 4.2 Escenas

| Criterio | Descripción |
|---|---|
| Qué debe comunicar | El guion se descompone en escenas accionables para producción. |
| Qué debe verse primero | Número de escena, localización, INT/EXT, día/noche, personajes y complejidad. |
| Posibles problemas visuales | Columnas largas, texto demasiado denso o falta de agrupación por localización. |
| PASS | Las 8 escenas se leen con claridad y muestran el salto de guion a desglose. |
| LIMITED PASS | La información está completa, pero necesita ajuste de ancho de columnas. |
| FAIL | La hoja resulta ilegible o no se entiende la relación con el guion. |

### 4.3 Personajes

| Criterio | Descripción |
|---|---|
| Qué debe comunicar | Qué personajes impactan producción, reparto y complejidad. |
| Qué debe verse primero | Nombre, rol, escenas, edad y complejidad. |
| Posibles problemas visuales | Roles poco destacados o escenas difíciles de leer. |
| PASS | Los 5 personajes se entienden y se identifica quién pesa más en producción. |
| LIMITED PASS | Funciona, pero convendría ordenar por presencia o complejidad. |
| FAIL | No ayuda a entender reparto ni carga de producción. |

### 4.4 Localizaciones

| Criterio | Descripción |
|---|---|
| Qué debe comunicar | Qué espacios exige el proyecto y qué permisos o complejidades generan. |
| Qué debe verse primero | Nombre de localización, tipo, INT/EXT, escenas, permisos y complejidad. |
| Posibles problemas visuales | Metadata de permisos poco visible o nombres largos. |
| PASS | Las 5 localizaciones se entienden y permiten detectar necesidades de permisos. |
| LIMITED PASS | Se entiende, pero necesita agrupación o color por permiso/complejidad. |
| FAIL | El productor no detecta localizaciones críticas. |

### 4.5 Riesgos

| Criterio | Descripción |
|---|---|
| Qué debe comunicar | Riesgos tempranos, impacto, probabilidad y mitigación. |
| Qué debe verse primero | Riesgo, impacto, probabilidad y mitigación. |
| Posibles problemas visuales | Demasiado texto por fila o falta de jerarquía visual. |
| PASS | Los 10 riesgos se leen y ayudan a priorizar conversación de producción. |
| LIMITED PASS | La hoja funciona, pero necesita colores o orden por impacto. |
| FAIL | Los riesgos parecen genéricos o no accionables. |

### 4.6 Viabilidad

| Criterio | Descripción |
|---|---|
| Qué debe comunicar | Lectura orientativa de viabilidad, semáforos y recomendaciones. |
| Qué debe verse primero | Viabilidad global, semáforo y principales indicadores. |
| Posibles problemas visuales | Semáforos poco claros, falta de leyenda o exceso de indicadores. |
| PASS | Se entiende que la viabilidad es orientativa y requiere revisión humana. |
| LIMITED PASS | Funciona, pero necesita leyenda visual o colores más evidentes. |
| FAIL | El productor cree que la herramienta garantiza viabilidad. |

### 4.7 Presupuesto

| Criterio | Descripción |
|---|---|
| Qué debe comunicar | Presupuesto preliminar revisable por categorías y escenarios. |
| Qué debe verse primero | Categoría, baja, media, alta, confianza y total. |
| Posibles problemas visuales | Que parezca presupuesto exacto, fiscal u oficial. |
| PASS | Se entiende que es presupuesto preliminar, editable y no presupuesto definitivo. |
| LIMITED PASS | Los números funcionan, pero conviene separar por bloques o añadir notas. |
| FAIL | El productor interpreta que es un presupuesto exacto. |

### 4.8 Recomendaciones

| Criterio | Descripción |
|---|---|
| Qué debe comunicar | Próximas acciones útiles para producción. |
| Qué debe verse primero | Lista numerada de recomendaciones concretas. |
| Posibles problemas visuales | Recomendaciones demasiado largas o poco priorizadas. |
| PASS | Las recomendaciones son claras y accionables. |
| LIMITED PASS | Son útiles, pero necesitan prioridad o agrupación. |
| FAIL | Parecen genéricas y no conectan con el proyecto. |

### 4.9 Revisión humana

| Criterio | Descripción |
|---|---|
| Qué debe comunicar | Todo resultado requiere validación humana. |
| Qué debe verse primero | Notas de revisión humana y límites de la demo. |
| Posibles problemas visuales | Que quede escondida al final o parezca secundaria. |
| PASS | La revisión humana es visible y refuerza el mensaje seguro. |
| LIMITED PASS | Existe, pero debería destacarse más. |
| FAIL | El productor no ve que la demo requiere revisión humana. |

### 4.10 Metadata

| Criterio | Descripción |
|---|---|
| Qué debe comunicar | Aislamiento productora/película y trazabilidad técnica. |
| Qué debe verse primero | organization_id, tenant_id, project_id y film_id. |
| Posibles problemas visuales | Demasiado técnico para una demo comercial. |
| PASS | Los IDs se entienden como garantía de separación de datos. |
| LIMITED PASS | Está correcto, pero requiere explicación verbal. |
| FAIL | Confunde al productor o distrae del valor comercial. |

---

## 5. Revisión del Markdown

El Markdown debe ser útil para enseñar en pantalla y para explicar la demo sin abrir todavía el Excel.

Debe cumplir:

- Secciones claras.
- Advertencia visible de demo ficticia.
- Explicación explícita de que no es presupuesto definitivo.
- Presencia clara de revisión humana.
- Lectura comprensible para productor no técnico.
- Mención de Proyecto Demo Bruma.
- Separación entre desglose, riesgos, viabilidad y presupuesto preliminar.

Resultado esperado del Markdown:

- PASS: se puede enseñar en pantalla como narrativa de la demo.
- LIMITED PASS: funciona, pero necesita mejor jerarquía visual.
- FAIL: no comunica límites o genera una promesa incorrecta.

---

## 6. Revisión del Excel

El Excel debe funcionar como artefacto editable de demo, no como presupuesto oficial.

Debe cumplir:

- Debe abrirse.
- Debe tener 10 hojas.
- Debe mostrar el resumen de forma clara.
- Debe permitir editar datos.
- Debe tener presupuesto con valores numéricos.
- Debe contener metadata/aislamiento.
- No debe parecer una hoja fiscal oficial.
- No debe parecer presupuesto definitivo.
- No debe insinuar que procesa cualquier guion real.
- No debe insinuar IA real integrada.

---

## 7. Revisión comercial

Preguntas de evaluación:

- ¿Un productor entiende el valor en menos de 2 minutos?
- ¿Se entiende que parte de un guion?
- ¿Se entiende el salto guion -> producción -> finanzas?
- ¿Se entiende que es demo local controlada?
- ¿Se entiende que requiere revisión humana?
- ¿Se entiende que Proyecto Demo Bruma es ficticio?
- ¿Se entiende que la lectura financiera es preliminar y revisable?

Respuesta esperada:

- PASS: el productor entiende el valor y los límites.
- LIMITED PASS: el productor entiende la mecánica, pero necesita guía verbal fuerte.
- FAIL: el productor interpreta que ya es producto disponible o producto final.

---

## 8. Señales de riesgo visual

Riesgos a vigilar durante la revisión:

- Demasiadas hojas sin explicación.
- Columnas demasiado largas.
- Presupuesto confuso.
- Metadata demasiado técnica.
- Falta de advertencia.
- Semáforos poco claros.
- Productor puede creer que es presupuesto exacto.
- Productor puede creer que procesa guiones reales ya.
- Productor puede creer que usa IA real integrada.
- Productor puede creer que el producto está disponible.

---

## 9. Checklist manual de QA

Checklist antes de marcar resultado:

- [ ] Generar demo en `/tmp`.
- [ ] Confirmar repo limpio antes y después.
- [ ] Confirmar solo JSON, Markdown y XLSX.
- [ ] Confirmar no PDF/HTML/CSV.
- [ ] Abrir Markdown.
- [ ] Abrir Excel.
- [ ] Revisar hoja Resumen.
- [ ] Revisar hoja Escenas.
- [ ] Revisar hoja Personajes.
- [ ] Revisar hoja Localizaciones.
- [ ] Revisar hoja Riesgos.
- [ ] Revisar hoja Viabilidad.
- [ ] Revisar hoja Presupuesto.
- [ ] Revisar hoja Recomendaciones.
- [ ] Revisar hoja Revisión humana.
- [ ] Revisar hoja Metadata.
- [ ] Comprobar advertencias.
- [ ] Comprobar aislamiento mediante organization_id, tenant_id, project_id y film_id.
- [ ] Registrar incidencias visuales.

---

## 10. Resultado esperado

| Resultado | Criterio |
|---|---|
| PASS | Excel y Markdown se entienden y pueden enseñarse. |
| LIMITED PASS | Técnicamente funciona, pero necesita pulido visual antes de enseñar. |
| FAIL | Confunde, promete demasiado, o no se abre correctamente. |

---

## 11. Recomendaciones si LIMITED PASS

- Mejorar hoja Resumen.
- Añadir portada o explicación inicial.
- Simplificar columnas.
- Mejorar nombres de hojas.
- Destacar advertencia.
- Separar presupuesto por bloques.
- Mejorar semáforos.
- Añadir leyenda.
- Preparar guion verbal de acompañamiento.

---

## 12. Recomendaciones si PASS

- Preparar guion comercial.
- Preparar demo de 3-5 minutos.
- Preparar preguntas/respuestas.
- Preparar versión para persona de confianza.
- No enseñar aún con guiones reales.
- Mantener el mensaje de demo local controlada.

---

## 13. No-goals

- No modificar código.
- No modificar Excel export.
- No modificar CLI.
- No generar artefactos permanentes.
- No PDF.
- No HTML.
- No CSV.
- No IA real.
- No guiones reales.
- No runtime SaaS.
- No backend SaaS.
- No DB, Docker, Alembic, `.env`, modelos SQLAlchemy, migraciones, pagos ni billing runtime.
