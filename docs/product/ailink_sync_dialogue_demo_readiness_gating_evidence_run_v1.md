# AILink Sync Dialogue — Demo Readiness Gating Evidence Run v1

## 1. Objetivo

Este documento registra una ejecución interna controlada de evidencias para AILink Sync Dialogue.

La finalidad es aplicar de forma práctica los criterios definidos en:

- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.PHASE7
- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.GATING.AUDIT.PHASE7.1
- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.GATING.EVIDENCE.PHASE7.2

Esta fase es documental y de registro de evidencias. No implementa código, no modifica scanner, no modifica matching, no modifica exports, no modifica reportes, no crea UI real, no crea backend, no crea frontend, no crea instalador, no crea n8n, no crea CRM, no toca PostgreSQL real, no toca Docker, no toca runtime, no toca configuración y no modifica CID SaaS.

## 2. Alcance de la ejecución

La evidencia se ejecutó de forma local y controlada usando una carpeta temporal fuera del repo:

- /tmp/ailink_sync_dialogue_evidence_run_phase7_3

La ejecución no dejó archivos nuevos dentro del repo.

La ejecución usó scripts existentes:

- scripts/demo/create_sync_dialogue_metadata_demo.py
- scripts/demo/run_sync_dialogue_demo_e2e.py

No se usó material audiovisual de cliente.

No se usaron datos personales reales.

No se usó GPU.

No se usó n8n.

No se usó Docker.

No se usó CID SaaS.

## 3. Estado de repositorio antes y después

HEAD estable usado:

- baa6f0c
- tag: ailink-dev-stable-sync-dialogue-demo-gating-evidence-phase7-2-20260612

Resultado posterior:

- git status quedó limpio.
- No se generaron archivos versionables dentro del repo.
- Los outputs quedaron en /tmp.

## 4. Evidencia EV-TECH-001 — Ejecución metadata demo

Comando ejecutado:

- scripts/demo/create_sync_dialogue_metadata_demo.py con --output-dir y --force.

Resultado observado:

- AILink Sync Dialogue metadata demo created.
- Video count: 3.
- Audio count: 4.
- Match suggestions count: 5.
- High confidence count: 2.
- Report HTML generado.

Outputs observados:

- scan_result.json.
- media_files.csv.
- match_suggestions.csv.
- report.html.

Tamaños observados:

- scan_result.json: 5767 bytes.
- media_files.csv: 823 bytes.
- match_suggestions.csv: 858 bytes.
- report.html: 4375 bytes.
- total: 11823 bytes.

Conclusión:

- EV-TECH-001 pasa para metadata demo controlada.
- EV-OUTPUT-001 pasa para metadata demo controlada.
- EV-REPORT-001 pasa como evidencia de existencia de reporte HTML.

## 5. Evidencia EV-TECH-001 — Ejecución e2e demo

Comando ejecutado:

- scripts/demo/run_sync_dialogue_demo_e2e.py con --work-dir y --force.

Resultado observado:

- total files: 7.
- video count: 3.
- audio count: 3.
- unsupported count: 1.
- match suggestions count: 0.
- output json path generado.
- output csv path generado.
- output matches path generado.
- output html path generado.
- AILink Sync Dialogue demo completed.

Nota importante:

- match suggestions puede ser 0 porque el fixture usa dummy files sin metadata real.

Conclusión:

- EV-TECH-001 pasa para demo e2e local.
- EV-OUTPUT-001 pasa porque genera JSON, CSV y HTML.
- El resultado de 0 matches no es fallo en este fixture; debe explicarse como limitación esperada.

## 6. Evidencia EV-OUTPUT-001 — Outputs generados

Outputs metadata demo:

- /tmp/ailink_sync_dialogue_evidence_run_phase7_3/metadata_demo/scan_result.json
- /tmp/ailink_sync_dialogue_evidence_run_phase7_3/metadata_demo/media_files.csv
- /tmp/ailink_sync_dialogue_evidence_run_phase7_3/metadata_demo/match_suggestions.csv
- /tmp/ailink_sync_dialogue_evidence_run_phase7_3/metadata_demo/report.html

Outputs e2e demo:

- /tmp/ailink_sync_dialogue_evidence_run_phase7_3/e2e_demo/output/scan_result.json
- /tmp/ailink_sync_dialogue_evidence_run_phase7_3/e2e_demo/output/media_files.csv
- /tmp/ailink_sync_dialogue_evidence_run_phase7_3/e2e_demo/output/match_suggestions.csv
- /tmp/ailink_sync_dialogue_evidence_run_phase7_3/e2e_demo/output/report.html

Conclusión:

- EV-OUTPUT-001 pasa.

## 7. Evidencia EV-REPORT-001 — Reporte HTML

Inspección metadata demo:

- scan_result_keys: match_suggestions, media_files, root_path, summary.
- media_rows: 7.
- match_rows: 5.
- html_contains_AILink: True.
- html_contains_client_forbidden_word: False.
- html_contains_personal_forbidden_word: False.

Muestras de media:

- scene01_take01.mov.
- scene01_take02.mov.
- scene02_take01.mxf.
- scene01_take01.wav.
- scene01_take02.wav.

Muestras de confianza:

- high.
- medium.
- high.
- medium.
- low.

Conclusión:

- EV-REPORT-001 pasa para demo controlada.
- El HTML contiene marca AILink.
- No se detectaron palabras evidentes de cliente o datos personales en el HTML.

## 8. Evidencia EV-PRIVACY-001 — Material seguro

La ejecución se hizo con:

- metadata demo controlada.
- fixture e2e dummy.
- rutas temporales bajo /tmp.
- nombres ficticios como scene01_take01.mov y scene01_take01.wav.

No hay indicio de material de cliente.

No hay indicio de datos personales reales.

Conclusión:

- EV-PRIVACY-001 pasa para esta ejecución interna.

## 9. Evidencia EV-PRIVACY-002 — Local-first

La evidencia se generó localmente.

No se observó dependencia de servicios externos.

No se observó dependencia de cloud.

No se observó dependencia de Docker.

No se observó dependencia de n8n.

No se observó dependencia de PostgreSQL real.

Conclusión:

- EV-PRIVACY-002 pasa para esta ejecución interna.

## 10. Seguridad de grep

Se ejecutó una búsqueda de marcadores sensibles sobre los outputs temporales.

Patrones buscados:

- password.
- secret.
- token.
- credential.
- cliente real.
- client name.
- emails comunes.
- rutas Windows.
- /mnt/c.
- /home/harliesound.

Resultados observados:

- shared_name_tokens aparece en scan_result.json, report.html y match_suggestions.csv.
- shared_name_tokens es una razón técnica de matching.
- No es un token secreto.
- No es una credencial.
- No es un dato sensible.

Conclusión:

- No se detectaron secretos evidentes.
- El hallazgo shared_name_tokens se clasifica como falso positivo técnico aceptado.

## 11. Matriz de decisión aplicada

### GATE-PRIVACY-001

Resultado: PASS.

Razón:

- No se usó material de cliente.
- Se usó demo controlada y fixture dummy.

### GATE-PRIVACY-002

Resultado: PASS.

Razón:

- La ejecución fue local-first.
- No hubo dependencia cloud.

### GATE-TECH-001

Resultado: PASS.

Razón:

- Metadata demo ejecutó correctamente.
- E2E demo ejecutó correctamente.

### GATE-TECH-002

Resultado: PASS.

Razón:

- Se generaron JSON, CSV y HTML.

### GATE-COMM-001

Resultado: LIMITED PASS.

Razón:

- Esta ejecución técnica no valida todavía el discurso oral.
- El documento Phase7 sí advierte que no debe venderse como sincronizador final.

### GATE-COMM-002

Resultado: LIMITED PASS.

Razón:

- Esta ejecución no promete funciones futuras.
- Falta todavía una revisión del guion final antes de terceros.

### GATE-COMM-003

Resultado: LIMITED PASS.

Razón:

- El mensaje beta está definido en documentos previos.
- Falta aplicarlo en una demo grabada o ensayada.

## 12. Decisión final de esta evidence run

Resultado:

- LIMITED PASS.

Justificación:

- Los gates técnicos y de privacidad pasan.
- La demo local genera outputs reales.
- La metadata demo muestra matches y reporte legible.
- La e2e demo funciona con dummy fixture.
- Falta todavía validar guion, discurso comercial y preguntas/respuestas en una demo ensayada.

Público permitido:

- Interno.
- Persona de confianza muy cercana.

Público no recomendado todavía:

- Escuelas de cine.
- Productoras externas.
- Leads fríos.
- LinkedIn público como demo final.

## 13. Riesgos pendientes

Riesgos pendientes:

- El e2e dummy genera 0 match suggestions.
- El usuario externo podría interpretar la herramienta como sincronizador final.
- Falta una demo ensayada de 5 a 7 minutos.
- Falta decidir qué captura o vídeo enseñar.
- Falta revisar el reporte desde la mirada de un montador no técnico.
- Falta una plantilla de feedback real.

## 14. Siguiente acción recomendada

La siguiente acción recomendada es:

- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.SCRIPT.REFINEMENT.PHASE7.3

Objetivo:

- Preparar el guion real de demo de 5 a 7 minutos usando estas evidencias.
- Dejar claro que el estado actual es LIMITED PASS.
- evitar vender sincronización automática final.
- Preparar explicación de por qué e2e dummy puede tener 0 matches.
- Preparar transición hacia feedback de una persona de confianza.

## 15. Resumen ejecutivo

La evidence run confirma que AILink Sync Dialogue puede generar outputs locales controlados.

La parte técnica y de privacidad pasa para una demo interna.

La decisión responsable es LIMITED PASS, no PASS público.

El siguiente paso no debe ser añadir funcionalidad; debe ser refinar el guion de demo y ensayar el mensaje.
