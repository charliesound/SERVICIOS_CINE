# AILink Sync Dialogue — Demo Readiness Gating Audit v1

## 1. Objetivo

Este documento convierte la preparación de demo de AILink Sync Dialogue en una lista de gates verificables.

La finalidad es impedir que se enseñe una demo si falta algo crítico de seguridad, privacidad, estabilidad, claridad comercial o honestidad sobre las capacidades actuales.

Esta fase es documental y de auditoría. No implementa código, no modifica scanner, no modifica matching, no modifica exports, no modifica reportes, no crea UI real, no crea backend, no crea frontend, no crea instalador, no crea n8n, no crea CRM, no toca PostgreSQL real, no toca Docker, no toca runtime, no toca configuración y no modifica CID SaaS.

## 2. Relación con Demo Readiness Phase7

La fase anterior, AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.PHASE7, definió:

- Qué se puede enseñar ya.
- Qué debe presentarse como beta.
- Qué no se debe prometer.
- Estructura de demo comercial de 5 a 7 minutos.
- Checklists técnico y comercial.
- Preguntas esperables.
- Respuestas seguras.
- Huecos actuales.
- Criterios para enseñar o no enseñar.

Esta fase añade un sistema de gating: si un gate crítico falla, la demo no debe enseñarse.

## 3. Principio de gating

Un gate no es una mejora futura.

Un gate es una condición mínima para decidir si la demo se puede enseñar de forma responsable.

Los gates críticos son bloqueantes. Si uno falla, no se enseña la demo.

Los gates no críticos pueden dejarse como observaciones, siempre que no creen riesgo comercial, legal, técnico o reputacional.

## 4. Clasificación de gates

Clasificación:

- CRITICAL: bloquea la demo.
- HIGH: puede bloquear si afecta a comprensión, privacidad o confianza.
- MEDIUM: no bloquea si se explica bien.
- LOW: mejora futura sin impacto directo en la demo.

## 5. Gates críticos

### GATE-PRIVACY-001 — No usar material de cliente

La demo no puede usar material audiovisual de cliente, terceros o proyectos reales sin autorización clara.

Resultado esperado:

- Solo material de prueba.
- Solo material propio.
- Solo fixture controlado.
- Sin datos personales.
- Sin rutas sensibles visibles.

Si falla, la demo queda bloqueada.

### GATE-PRIVACY-002 — No subir material sensible

La demo debe sostener el mensaje local-first.

Resultado esperado:

- No se sube material audiovisual.
- No se requiere conexión externa para demostrar el flujo.
- No se promete procesamiento cloud en la demo actual.

Si falla, la demo queda bloqueada.

### GATE-TECH-001 — Ejecución repetible

La demo debe ejecutarse de forma repetible en el entorno controlado.

Resultado esperado:

- El runner de demo funciona.
- El fixture de demo funciona.
- Los outputs aparecen donde se esperan.
- El reporte HTML se puede abrir.
- La ejecución no depende de GPU.
- La ejecución no depende de n8n.
- La ejecución no depende de Docker.
- La ejecución no depende de CID SaaS.

Si falla, la demo queda bloqueada.

### GATE-TECH-002 — Outputs comprensibles

Los outputs deben poder explicarse sin una sesión técnica larga.

Resultado esperado:

- JSON entendible como salida estructurada.
- CSV de media entendible.
- CSV de sugerencias entendible.
- Reporte HTML legible.
- Razones de matching explicables cuando existan.
- Limitaciones visibles o explicables.

Si falla, la demo puede quedar bloqueada.

### GATE-COMM-001 — No venderlo como sincronizador final

La demo no debe presentarse como sincronizador automático definitivo.

Resultado esperado:

- Se presenta como análisis local y preparación para montaje.
- Se habla de sugerencias de matching.
- Se deja claro que hay revisión humana.
- Se evita prometer sincronización perfecta.

Si falla, la demo queda bloqueada.

### GATE-COMM-002 — No prometer funciones futuras como actuales

La demo no debe afirmar que existen funciones no implementadas.

Funciones que no deben venderse como actuales:

- Transcripción robusta.
- Matching por waveform.
- OCR de claqueta.
- Detección automática de claqueta.
- Export XML/AAF/EDL final.
- Instalador Mac/Windows.
- UI profesional final.
- SaaS multiusuario.
- Integración real con CID SaaS.
- Integración real con n8n o CRM.

Si falla, la demo queda bloqueada.

### GATE-COMM-003 — Mensaje beta claro

La demo debe presentarse como beta controlada.

Resultado esperado:

- Se explica qué ya funciona.
- Se explica qué está en validación.
- Se explica qué feedback se busca.
- Se explica qué tipo de usuario interesa para prueba.

Si falla, la demo queda bloqueada.

## 6. Gates altos

### GATE-UX-001 — Reporte legible en menos de dos minutos

El reporte debe entenderse en una lectura rápida.

Resultado esperado:

- Se reconoce qué es vídeo.
- Se reconoce qué es audio.
- Se reconocen matches o ausencia de matches.
- Se entienden confidence y reasons.
- No requiere explicar estructura interna del código.

Si falla, la demo puede enseñarse solo internamente.

### GATE-OPS-001 — Guion de demo preparado

Debe existir un guion mínimo de demo.

Resultado esperado:

- Apertura con problema.
- Propuesta clara.
- Demo técnica breve.
- Lectura de reporte.
- Límites.
- Cierre con beta y feedback.

Si falla, la demo no debe enseñarse a terceros externos.

### GATE-OPS-002 — Preguntas y respuestas preparadas

Las preguntas probables deben tener respuesta prudente.

Resultado esperado:

- Sincronización.
- Timecode.
- Material sin timecode.
- Privacidad.
- Compatibilidad con cámaras y sonido directo.
- Export a NLE.
- Transcripción.
- Precio beta.
- Datos guardados.

Si falla, la demo puede quedar limitada a revisión interna.

## 7. Gates medios

### GATE-MARKET-001 — Perfil de tester definido

La demo debe tener claro a quién se enseña.

Perfiles adecuados:

- Montadores.
- Ayudantes de montaje.
- Técnicos de postproducción.
- Escuelas de cine.
- Productoras pequeñas.
- Equipos que reciben material de rodaje desordenado.

### GATE-MARKET-002 — Feedback esperado definido

La demo debe pedir feedback concreto.

Feedback útil:

- Si el reporte ayuda.
- Si el matching es comprensible.
- Qué metadata falta.
- Qué formatos reales usan.
- Qué salida necesitan.
- Qué les haría pagar una beta.

## 8. No-go conditions

No enseñar la demo si ocurre cualquiera de estas condiciones:

- Hay material de cliente.
- Hay datos personales reales.
- Hay rutas privadas visibles.
- El flujo falla de forma intermitente.
- El reporte HTML no se abre.
- Los outputs no se entienden.
- Se confunde AILink Sync Dialogue con CID SaaS.
- Se vende como sincronizador automático final.
- Se prometen funciones futuras como actuales.
- No está claro qué feedback se pide.
- No hay explicación honesta de límites.
- La demo depende de servicios externos no necesarios.

## 9. Go conditions

La demo puede enseñarse de forma controlada si:

- Usa material seguro.
- Ejecuta end-to-end.
- Genera outputs revisables.
- El reporte HTML es legible.
- El mensaje local-first es claro.
- El mensaje beta es claro.
- Los límites están preparados.
- No se prometen funciones no implementadas.
- Hay guion de 5 a 7 minutos.
- Hay preguntas y respuestas preparadas.
- Hay mecanismo de feedback posterior.

## 10. Matriz de decisión

### Resultado PASS

La demo puede enseñarse a una persona de confianza o tester semiprivado.

Condición:

- Todos los gates críticos pasan.
- Los gates altos están resueltos o mitigados.
- Los límites se explican claramente.

### Resultado LIMITED PASS

La demo solo puede enseñarse internamente o a una persona muy cercana.

Condición:

- Todos los gates críticos pasan.
- Uno o más gates altos quedan incompletos.
- No hay riesgo de privacidad ni promesas falsas.

### Resultado FAIL

La demo no debe enseñarse.

Condición:

- Falla cualquier gate crítico.
- Hay riesgo de privacidad.
- El flujo no es repetible.
- El mensaje comercial induce a error.

## 11. Checklist de revisión antes de demo

Checklist:

- GATE-PRIVACY-001 revisado.
- GATE-PRIVACY-002 revisado.
- GATE-TECH-001 revisado.
- GATE-TECH-002 revisado.
- GATE-COMM-001 revisado.
- GATE-COMM-002 revisado.
- GATE-COMM-003 revisado.
- GATE-UX-001 revisado.
- GATE-OPS-001 revisado.
- GATE-OPS-002 revisado.
- No-go conditions revisadas.
- Go conditions revisadas.
- Matriz de decisión aplicada.

## 12. Evidencias mínimas recomendadas

Antes de enseñar, guardar evidencias internas:

- Captura del reporte HTML.
- Lista de outputs generados.
- Confirmación de que el material es seguro.
- Confirmación de que no hay datos personales.
- Confirmación de que no se usa material de cliente.
- Resumen de límites que se van a explicar.
- Guion o escaleta de demo.
- Lista de preguntas y respuestas.

Esta fase no crea esas evidencias. Solo define cuáles deben existir.

## 13. Aplicación recomendada

Orden recomendado:

1. Ejecutar demo interna.
2. Revisar gates críticos.
3. Revisar gates altos.
4. Corregir mensaje comercial si hace falta.
5. Repetir demo.
6. Clasificar resultado como PASS, LIMITED PASS o FAIL.
7. Si hay PASS, enseñar a una persona de confianza.
8. Recoger feedback.
9. Decidir siguiente fase.

## 14. Próximas fases posibles

Fases posibles:

- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.GATING.EVIDENCE.PHASE7.2
- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.SCRIPT.REFINEMENT.PHASE7.2
- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.SAFE_SAMPLE.PHASE7.2
- AILINK.PRODUCT.SYNC_DIALOGUE.REPORT.PDF.CONTRACT.PHASE8

La recomendación inmediata es no construir más funcionalidades hasta tener una demo interna clasificada con esta matriz.

## 15. Resumen ejecutivo

AILink Sync Dialogue puede avanzar hacia demo controlada, pero no debe enseñarse sin gates.

Los gates protegen privacidad, credibilidad y foco comercial.

El producto debe vender claridad, orden y preparación para montaje; no sincronización total ni automatización completa.
