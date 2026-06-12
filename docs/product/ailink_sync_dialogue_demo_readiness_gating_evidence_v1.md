# AILink Sync Dialogue — Demo Readiness Gating Evidence v1

## 1. Objetivo

Este documento define el paquete mínimo de evidencias internas necesario para aplicar la matriz PASS, LIMITED PASS o FAIL antes de enseñar una demo de AILink Sync Dialogue.

Esta fase es documental y de evidencias. No implementa código, no ejecuta demo, no modifica scanner, no modifica matching, no modifica exports, no modifica reportes, no crea UI real, no crea backend, no crea frontend, no crea instalador, no crea n8n, no crea CRM, no toca PostgreSQL real, no toca Docker, no toca runtime, no toca configuración y no modifica CID SaaS.

## 2. Relación con fases previas

Esta fase depende de:

- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.PHASE7
- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.GATING.AUDIT.PHASE7.1

Phase7 definió qué se puede enseñar, qué es beta, qué no se debe prometer y cómo estructurar una demo comercial de 5 a 7 minutos.

Phase7.1 convirtió esa preparación en gates verificables y una matriz de decisión PASS, LIMITED PASS o FAIL.

Esta fase define qué evidencias mínimas deben existir antes de aplicar esos gates.

## 3. Principio de evidencia

Una evidencia no es una promesa.

Una evidencia debe ser concreta, revisable, localizable, comprensible, no sensible, coherente con el mensaje beta y coherente con el enfoque local-first.

Las evidencias no deben contener material audiovisual de cliente, datos personales reales, rutas privadas sensibles, credenciales, tokens, correos reales, nombres de clientes, promesas comerciales no implementadas ni referencias que confundan AILink Sync Dialogue con CID SaaS.

Control explícito de contenido prohibido:

- Material audiovisual de cliente.
- Datos personales reales.
- Credenciales.
- Tokens.
- Promesas comerciales no implementadas.
- Referencias que confundan AILink Sync Dialogue con CID SaaS.

## 4. Paquete mínimo de evidencias

El paquete recomendado debe incluir:

- Evidencia de privacidad.
- Evidencia de ejecución.
- Evidencia de outputs.
- Evidencia de reporte HTML.
- Evidencia de mensaje comercial.
- Evidencia de límites.
- Evidencia de preguntas y respuestas.
- Evidencia de decisión final.

Esta fase no crea esa carpeta ni esos archivos. Solo define qué deberían contener.

## 5. Evidencias críticas

### EV-PRIVACY-001 — Declaración de material seguro

Debe confirmar que el material usado no pertenece a un cliente, no pertenece a terceros sin autorización, no contiene datos personales, es de prueba, propio o fixture controlado y puede enseñarse sin riesgo.

Gate relacionado: GATE-PRIVACY-001.

Si esta evidencia no existe, la demo debe clasificarse como FAIL.

### EV-PRIVACY-002 — Confirmación local-first

Debe confirmar que la demo no sube material audiovisual sensible, no depende de servicios externos para explicar el valor actual, no presenta procesamiento cloud como capacidad actual y mantiene el mensaje local-first.

Gate relacionado: GATE-PRIVACY-002.

Si esta evidencia no existe, la demo debe clasificarse como FAIL.

### EV-TECH-001 — Registro de ejecución repetible

Debe confirmar que el flujo de demo se ejecutó sin error, generó los outputs esperados y no dependió de GPU, n8n, Docker ni CID SaaS.

Gate relacionado: GATE-TECH-001.

Si esta evidencia no existe, la demo debe clasificarse como FAIL o LIMITED PASS, según el público.

### EV-OUTPUT-001 — Lista de outputs generados

Debe incluir, si están disponibles:

- Resultado JSON.
- CSV de media.
- CSV de sugerencias de matching.
- Reporte HTML.
- Resumen de conteos.
- Observaciones de limitación.

Gate relacionado: GATE-TECH-002.

Si esta evidencia no existe, la demo no debe enseñarse externamente.

### EV-REPORT-001 — Captura o revisión del reporte HTML

Debe confirmar que el reporte HTML es legible, que se reconocen vídeos, audios, matches o ausencia de matches, resumen, confidence y reasons cuando existan, y que no aparecen datos sensibles.

Gate relacionado: GATE-UX-001.

## 6. Evidencias comerciales

### EV-COMM-001 — Mensaje de apertura

Debe explicar problema, propuesta, enfoque local-first, estado beta y alcance real.

No debe decir que la herramienta es un sincronizador final.

Gate relacionado: GATE-COMM-001.

### EV-COMM-002 — Lista de funciones no prometidas

Debe recordar que no deben venderse como actuales:

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

Gate relacionado: GATE-COMM-002.

Si esta evidencia no existe, la demo debe clasificarse como LIMITED PASS como máximo.

### EV-COMM-003 — Mensaje beta

Debe explicar qué ya funciona, qué está en validación, qué feedback se busca, qué tipo de tester interesa y qué no se garantiza todavía.

Gate relacionado: GATE-COMM-003.

## 7. Evidencias operativas

### EV-OPS-001 — Guion o escaleta de 5 a 7 minutos

Debe incluir problema, propuesta, demo técnica, lectura de reporte, límites e invitación a feedback.

Gate relacionado: GATE-OPS-001.

### EV-OPS-002 — Preguntas y respuestas preparadas

Debe cubrir sincronización, timecode, material sin timecode, privacidad, compatibilidad con material profesional, export a NLE, transcripción, precio beta y datos guardados.

Gate relacionado: GATE-OPS-002.

### EV-FEEDBACK-001 — Mecanismo de feedback

Puede ser nota manual, documento interno, hoja de seguimiento, formulario futuro o email de respuesta.

Debe recoger si el reporte ayuda, qué no se entiende, qué salida necesitan, qué formatos usan y qué les haría pagar una beta.

## 8. Evidencia de decisión final

Antes de enseñar, debe registrarse una decisión:

- PASS
- LIMITED PASS
- FAIL

La decisión debe incluir fecha de revisión, persona que revisa, resultado, gates críticos revisados, gates altos revisados, riesgos pendientes, público permitido y siguiente acción.

## 9. Plantilla de decisión

Plantilla recomendada:

AILink Sync Dialogue demo gating decision.

Campos mínimos:

- Fecha.
- Revisor.
- Versión o referencia.
- Material usado.
- Resultado: PASS / LIMITED PASS / FAIL.
- Gates críticos: GATE-PRIVACY-001, GATE-PRIVACY-002, GATE-TECH-001, GATE-TECH-002, GATE-COMM-001, GATE-COMM-002, GATE-COMM-003.
- Gates altos: GATE-UX-001, GATE-OPS-001, GATE-OPS-002.
- Riesgos pendientes.
- Público permitido.
- Decisión.
- Siguiente acción.

## 10. Interpretación de resultados

### PASS

Puede enseñarse a una persona de confianza o tester semiprivado.

Requisitos:

- Evidencias críticas presentes.
- Gates críticos superados.
- Mensaje beta claro.
- Límites explicados.
- Feedback preparado.

### LIMITED PASS

Puede enseñarse solo internamente o a una persona muy cercana.

Casos típicos:

- Los gates críticos pasan.
- Falta alguna evidencia alta.
- El reporte necesita explicación.
- El guion no está suficientemente cerrado.
- Las preguntas y respuestas no están completas.

### FAIL

No debe enseñarse.

Casos típicos:

- Falta evidencia de privacidad.
- Hay material de cliente.
- Hay datos personales.
- No se ejecutó el flujo.
- No hay outputs revisables.
- Se confunde con CID SaaS.
- Se vende como sincronizador final.
- Se prometen funciones futuras como actuales.

## 11. Evidencias que no conviene crear todavía

No conviene crear todavía evidencias de integración real con NLE, instalador, CRM, n8n, SaaS multiusuario, procesamiento cloud, transcripción robusta, waveform matching u OCR de claqueta.

Esas evidencias serían engañosas si se presentan como actuales.

## 12. Orden recomendado

Orden recomendado:

1. Revisar este documento.
2. Ejecutar una demo interna controlada en otra fase.
3. Reunir evidencias críticas.
4. Reunir evidencias comerciales.
5. Reunir evidencias operativas.
6. Aplicar la plantilla de decisión.
7. Clasificar PASS, LIMITED PASS o FAIL.
8. Decidir si se enseña o se corrige antes.
9. Registrar feedback después de la demo.

## 13. Próximas fases

Fases posibles después de esta:

- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.GATING.EVIDENCE.RUN.PHASE7.3
- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.SCRIPT.REFINEMENT.PHASE7.3
- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.SAFE_SAMPLE.PHASE7.3
- AILINK.PRODUCT.SYNC_DIALOGUE.REPORT.PDF.CONTRACT.PHASE8

La recomendación inmediata es preparar primero una ejecución interna de evidencias antes de crear más funcionalidades.

## 14. Resumen ejecutivo

Esta fase define el paquete mínimo de evidencias para decidir si la demo se enseña.

El objetivo no es vender más, sino reducir riesgo.

AILink Sync Dialogue debe demostrar claridad, orden y preparación para montaje, manteniendo límites honestos y privacidad.
