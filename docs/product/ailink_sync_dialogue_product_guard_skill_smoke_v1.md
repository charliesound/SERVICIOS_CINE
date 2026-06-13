# AILink Sync Dialogue Product Guard Skill Smoke v1

Fase: `AILINK.PRODUCT.SYNC_DIALOGUE.CODEX.SKILL.PRODUCT_GUARD.SMOKE.PHASE4.1`
Fecha: 2026-06-13
Tipo: smoke documental y test-only

Skill probada: `ailink-sync-dialogue-product-guard`.
Último HEAD estable conocido: `fb7bb2c`.
Último tag estable conocido: `ailink-cid-dev-stable-sync-dialogue-product-guard-skill-phase4-20260613`.
Etiqueta de seguridad: No runtime changes.
Estado de publicación: No production public release.
Regla de comunicación: No promises of unimplemented features.

## 1. Propósito del smoke test

Este smoke test valida el uso documental de la skill
`ailink-sync-dialogue-product-guard`. No modifica la skill, no crea nuevas
skills y no modifica `.agents/skills`.

El objetivo es comprobar que la skill ayuda a preparar fases futuras de AILink
Sync Dialogue sin tocar runtime y sin mezclar su alcance con CID SaaS, CRM,
pagos, landing pública, VPS productivo o CID backend runtime.

## 2. Qué skill se está probando

La skill probada es `.agents/skills/ailink-sync-dialogue-product-guard/SKILL.md`.

La prueba verifica que la skill protege AILink Sync Dialogue como herramienta
independiente, local-first y en estado beta/demo controlada.

## 3. Último HEAD/tag estable

- HEAD estable: `fb7bb2c`.
- Tag estable: `ailink-cid-dev-stable-sync-dialogue-product-guard-skill-phase4-20260613`.

Este punto estable identifica la fase en la que la skill fue aprobada antes de
este smoke documental.

## 4. Escenario de prueba

Escenario: preparar una futura fase de AILink Sync Dialogue sin tocar runtime.

La fase futura hipotética podría definir mejoras documentales, demo controlada,
reportes, scanner, matching, exports o tests. El smoke comprueba que la skill
exige autorización explícita de fase antes de permitir cualquier trabajo.

Esta fase no edita backend runtime, frontend runtime, Docker, Alembic, `.env`,
modelos, DB, pagos, configuración ni scripts operativos.

## 5. Qué debe permitir la skill

La skill puede permitir, siempre que la fase lo autorice explícitamente:

- documentación de Sync Dialogue;
- demo controlada;
- reportes;
- scanner;
- matching;
- exports;
- tests.

Permitir esas áreas no equivale a autorización general de runtime ni a una
promesa comercial nueva.

## 6. Qué debe bloquear o advertir

La skill debe bloquear o advertir ante:

- mezclar Sync Dialogue con CID SaaS;
- prometer sincronización automática final;
- prometer edición automática final;
- prometer integración real con DaVinci/Avid/Premiere si no está implementada;
- prometer cloud;
- subir material audiovisual real;
- mezclar con CRM, pagos, landing pública, VPS productivo o CID backend runtime.

Regla corta: no cloud, no subir material audiovisual real y no convertir beta en
producto final.

## 7. Claims permitidos, claims prohibidos y guardrails operativos

Claims permitidos:

- AILink Sync Dialogue sigue siendo herramienta independiente.
- AILink Sync Dialogue es local-first.
- Estado actual: beta/demo controlada.
- Puede preparar evidencias, demo controlada y reportes si la fase lo autoriza.
- Un agente escribe, otro audita.

Claims comerciales prohibidos:

- No prometer sincronización automática final.
- No prometer edición automática final.
- No prometer integración real con DaVinci, Avid o Premiere si no está
  implementada.
- No prometer cloud.
- No presentar Sync Dialogue como prueba de madurez de CID SaaS.

Guardrails operativos:

- No production public release.
- No promises of unimplemented features.
- No runtime changes.
- No cloud.
- No subir material audiovisual real.
- No mezclar con CID SaaS, CRM, pagos, landing pública, VPS productivo o CID
  backend runtime.

## 8. Señales de uso correcto

La skill se ha usado correctamente si:

- la fase declara no-goals explícitos;
- la fase mantiene AILink Sync Dialogue separado de CID SaaS;
- la fase declara No runtime changes;
- la fase evita CRM, pagos, landing pública, VPS productivo y CID backend
  runtime;
- la fase mantiene privacidad y no subir material audiovisual real;
- la fase mantiene claims prudentes y verificables;
- la fase recuerda que un agente escribe, otro audita.

## 9. Señales de fallo

La skill falla o debe detener la fase si:

- se propone tocar runtime sin autorización explícita;
- se mezcla Sync Dialogue con CID SaaS;
- se promete sincronización automática final o edición automática final;
- se promete cloud;
- se promete integración real con DaVinci/Avid/Premiere no implementada;
- se intenta subir material audiovisual real;
- se mezcla con CRM, pagos, landing pública, VPS productivo o CID backend
  runtime;
- se modifica la skill o `.agents/skills` durante este smoke.

## 10. Resultado esperado del smoke test

Resultado esperado: la fase queda estrictamente documental/test-only y confirma
que `ailink-sync-dialogue-product-guard` sirve para controlar alcance, claims,
privacidad y separación de producto antes de abrir una fase real de Sync
Dialogue.

Esta fase no modifica la skill; solo valida su uso documental.

## 11. Próximas fases recomendadas

Si el smoke test pasa, las próximas fases recomendadas son:

1. `AILINK.SYNC_DIALOGUE.DEMO.EVIDENCE.BASELINE.1`: preparar evidencias de demo
   controlada sin material sensible.
2. `AILINK.SYNC_DIALOGUE.REPORTS.CONTRACT.1`: revisar contratos de reportes y
   exports sin prometer edición final.
3. `AILINK.SYNC_DIALOGUE.SCANNER.MATCHING.QA.1`: auditar scanner y matching con
   fixtures seguros.
4. `AILINK.SYNC_DIALOGUE.PUBLIC.CLAIMS.REVIEW.1`: revisar claims públicos con
   auditoría independiente antes de publicación.

## 12. Criterios de aceptación

- Documento creado en `docs/product/ailink_sync_dialogue_product_guard_skill_smoke_v1.md`.
- Test creado en `tests/unit/test_ailink_sync_dialogue_product_guard_skill_smoke.py`.
- La fase declara que no crea nuevas skills.
- La fase declara que no modifica `.agents/skills`.
- La fase queda estrictamente documental/test-only.
- No hay staging, commit, tag ni push.
- No runtime changes.
