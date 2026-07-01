# CID Local Media Agent — Controlled Local Demo Runner Operator Runbook Gate V1

## Gate identity

- `PHASE_ID`: `CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.INSTALLED.CONTROLLED.LOCAL.DEMO.RUNNER.OPERATOR.RUNBOOK.GATE.V1`
- `EXPECTED_RESULT`: `LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_OPERATOR_RUNBOOK_GATE_V1_CLOSED`
- `SCOPE_STATUS`: `DOCUMENTATION_AND_QA_ONLY`
- `RUNBOOK_STATUS`: `INTERNAL_OPERATOR_RUNBOOK_DEFINED`
- `DEMO_STATUS`: `DEMO_TECNICA_LOCAL_CONTROLADA_ONLY`
- `PRODUCT_STATUS`: `NOT_PRODUCT_FINAL`
- `COMMERCIAL_STATUS`: `INTERNAL_OPERATOR_RUNBOOK_NOT_PUBLIC_DEMO_SCRIPT`

This gate converts the controlled demo narrative into an internal operator runbook. The runbook is a procedural guide for executing the current controlled local demo without improvisation, hype, or accidental product claims. It does not add capability. It does not change runtime behavior. It does not make the demo suitable for customers, public launch, paid use, installer distribution, or real production media.

## Stable baseline to be preserved

- Expected starting commit: `c98fde139a28b464c2225f7bbea90b46aafd4117`.
- Expected starting tag: `cid-dev-stable-local-media-agent-controlled-local-demo-runner-demo-narrative-gate-v1-20260630`.
- Previous closed result: `LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_DEMO_NARRATIVE_GATE_V1_CLOSED`.
- Installed export command: `cid-local-media-agent-visible-report-write-enabled-export`.
- Installed controlled demo runner: `cid-local-media-agent-controlled-local-demo-runner`.
- Controlled artifact name: `controlled_visible_report.controlled.txt`.
- Controlled artifact SHA256: `277bca892ae1591c3dec5c36935a0fc0489d31ed0796c3e3703f8c63b3ec3c6f`.
- Controlled artifact byte count: `167`.

These values are evidence anchors for the controlled demo only. They are not evidence of real media scanning, real metadata extraction, sync, transcription, subtitle generation, DaVinci Resolve export, licensing, SaaS integration, installer readiness, or production deployment.

## Scope boundaries

### Allowed in this gate

- Documentation for a reproducible internal operator runbook.
- QA tests that verify the runbook exists, is bounded, and contains the required operational sequence.
- Pre-demo checklist, live execution sequence, evidence capture checklist, failure handling, cleanup discipline, and closeout wording.
- Conservative instructions for showing `--help`, `--result-json`, and `--result-json --keep-output`.

### Forbidden in this gate

- No implementation changes.
- No `pyproject.toml` change.
- No runtime change.
- No command entrypoint change.
- No scanner implementation.
- No real `ffprobe` execution.
- No real `FFmpeg` execution.
- No media-file analysis.
- No material real.
- No cliente real.
- No demo pública.
- No SaaS integration.
- No database access.
- No installer.
- No backend change.
- No frontend change.
- No network dependency.
- No writing inside the repository during the runner demo.
- No overwrite behavior.
- No production readiness claim.

## Operator principle

The operator must run the demo exactly as a controlled technical demonstration:

> Ejecutamos una cadena local controlada para demostrar reproducibilidad, evidencia JSON, hash/bytes estables y limpieza temporal. No estamos demostrando todavía análisis real de carpetas de rodaje ni funcionalidad final de producto.

The operator must not invent missing features, must not reinterpret a failure as success, and must not promise future features as if they already exist. If a command, hash, byte count, cleanup check, or guard fails, the runbook instruction is: **STOP_DO_NOT_IMPROVISE**.

## Pre-demo checklist

Before any spoken demo or screen recording, the operator must verify:

- `WORKTREE_CLEAN_BEFORE_DEMO`: the repository is clean before the demo.
- `WSL_REPO_CONTEXT_CONFIRMED`: execution happens in `/opt/SERVICIOS_CINE` under WSL Ubuntu.
- `.venv` is activated.
- `HEAD` and `origin/main` are on the expected controlled baseline for the current phase.
- Target tag for the next closure is absent locally and remotely.
- The installed export command is available.
- The installed controlled demo runner is available.
- No client media is present in the demo input path.
- No real camera, sound, subtitle, EDL, XML, AAF, or DaVinci Resolve project file is used.
- No SaaS, database, network, backend, frontend, installer, Stripe, credits, ledger, or AI Jobs service is part of the demo.
- The operator has the allowed phrases and forbidden claims visible before speaking.

Minimum preflight commands:

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate
git fetch origin --tags
git status --short
git rev-parse HEAD
git rev-parse origin/main
command -v cid-local-media-agent-visible-report-write-enabled-export
command -v cid-local-media-agent-controlled-local-demo-runner
```

## Live demo execution sequence

The operator must follow this exact order. Do not skip, reorder, or merge the steps.

### Step 1 — Show discoverability with `--help`

Command:

```bash
cid-local-media-agent-controlled-local-demo-runner --help
```

Say:

> Primero enseño el punto de entrada instalado y sus opciones. Esto prueba que existe una interfaz de operador descubierta desde CLI, no una interfaz final de producto.

Evidence to capture:

- `HELP_OUTPUT_CAPTURED`.
- Visible command name.
- Visible options including `--result-json` and `--keep-output`.

Do not claim:

- product UI readiness;
- installer readiness;
- onboarding readiness;
- client training readiness.

### Step 2 — Run default safe JSON mode with `--result-json`

Command:

```bash
cid-local-media-agent-controlled-local-demo-runner --result-json
```

Say:

> Ahora ejecuto el modo seguro por defecto. La salida JSON sirve para verificación técnica: nombre de artefacto, SHA256, bytes y comportamiento de limpieza. No es una pieza comercial ni una prueba de análisis real de rodaje.

Evidence to capture:

- `RESULT_JSON_CAPTURED`.
- Artifact name: `controlled_visible_report.controlled.txt`.
- SHA256: `277bca892ae1591c3dec5c36935a0fc0489d31ed0796c3e3703f8c63b3ec3c6f`.
- Byte count: `167`.
- Default cleanup behavior: `TEMP_OUTPUT_CLEANUP_BY_DEFAULT`.

Acceptance condition:

- The JSON must contain the controlled artifact identity.
- The SHA256 must match exactly.
- The byte count must match exactly.
- The default execution must not leave uncontrolled output behind.

Failure rule:

- If JSON is malformed, if the SHA differs, if bytes differ, or if output cleanup is not clear, stop the demo and record `JSON_EVIDENCE_FAILURE_STOPPED`.

### Step 3 — Preserve temporary output explicitly with `--result-json --keep-output`

Command:

```bash
cid-local-media-agent-controlled-local-demo-runner --result-json --keep-output
```

Say:

> Ahora repito la demo preservando temporalmente la salida. Esto solo se hace con una bandera explícita de operador. Sirve para inspección interna o grabación de evidencia, no para crear un workspace de producción.

Evidence to capture:

- `KEEP_OUTPUT_JSON_CAPTURED`.
- `KEEP_OUTPUT_REQUIRES_EXPLICIT_OPERATOR_FLAG`.
- Temporary output root path, if the runner exposes it.
- Artifact identity preserved as `controlled_visible_report.controlled.txt`.
- SHA256 preserved as `277bca892ae1591c3dec5c36935a0fc0489d31ed0796c3e3703f8c63b3ec3c6f`.
- Byte count preserved as `167`.

Acceptance condition:

- Preserved output is clearly framed as temporary evidence.
- The operator must not call it a production workspace, customer deliverable, media bin, ingest folder, or project storage.

### Step 4 — Manual cleanup after preserved-output inspection

After the `--keep-output` run, the operator must remove the preserved output root once the evidence has been inspected or recorded.

Say:

> Cierro la demo limpiando la salida preservada. La disciplina de limpieza evita residuos entre ejecuciones y evita confundir evidencia temporal con producto final.

Evidence to capture:

- `CONTROLLED_KEEP_OUTPUT_CLEANUP_PASS`.
- Confirmation that the preserved output root no longer exists after manual cleanup.
- Confirmation that nothing was written inside the repository.

Failure rule:

- If cleanup cannot be confirmed, stop the demo and record `KEEP_OUTPUT_CLEANUP_FAILURE_STOPPED`.

## Evidence pack checklist

A valid operator evidence pack for this phase must include:

- `HELP_OUTPUT_CAPTURED`.
- `RESULT_JSON_CAPTURED`.
- `KEEP_OUTPUT_JSON_CAPTURED`.
- `CONTROLLED_ARTIFACT_NAME_VERIFIED`.
- `CONTROLLED_SHA256_VERIFIED`.
- `CONTROLLED_BYTE_COUNT_VERIFIED`.
- `TEMP_OUTPUT_CLEANUP_BY_DEFAULT`.
- `KEEP_OUTPUT_REQUIRES_EXPLICIT_OPERATOR_FLAG`.
- `CONTROLLED_KEEP_OUTPUT_CLEANUP_PASS`.
- `NO_REPO_WRITE_DURING_DEMO`.
- `NO_NETWORK_USED`.
- `NO_DATABASE_USED`.
- `NO_REAL_MEDIA_USED`.
- `NO_PUBLIC_DEMO_CLAIM`.
- `NO_CLIENT_READY_CLAIM`.

## Failure handling matrix

| Failure | Operator action | Allowed wording | Forbidden reaction |
|---|---|---|---|
| Command missing | Stop | `COMMAND_ENTRYPOINT_MISSING_STOPPED` | Do not reinstall or edit runtime live. |
| Help output unexpected | Stop | `HELP_OUTPUT_UNEXPECTED_STOPPED` | Do not hide the terminal or continue. |
| JSON malformed | Stop | `JSON_EVIDENCE_FAILURE_STOPPED` | Do not describe it as a partial success. |
| SHA mismatch | Stop | `CONTROLLED_SHA256_MISMATCH_STOPPED` | Do not say the artifact is equivalent. |
| Byte count mismatch | Stop | `CONTROLLED_BYTE_COUNT_MISMATCH_STOPPED` | Do not round, ignore, or reinterpret bytes. |
| Cleanup unclear | Stop | `KEEP_OUTPUT_CLEANUP_FAILURE_STOPPED` | Do not leave preserved output undocumented. |
| Worktree dirty unexpectedly | Stop | `WORKTREE_NOT_CLEAN_STOPPED` | Do not commit or stash casually. |
| Network/database activity suspected | Stop | `BOUNDARY_VIOLATION_STOPPED` | Do not continue the demo. |

The failure policy is intentionally strict. A stopped demo is a better outcome than an inflated claim.

## Approved commercial framing

For a producer, productora, school, or potential client, say:

> Esta demo no enseña todavía una herramienta lista para producción. Enseña que estamos construyendo la base local con control, trazabilidad, salida verificable y límites claros. El valor futuro será analizar carpetas reales de rodaje, metadatos, sincronización, transcripción y reportes de postproducción, pero eso entrará por fases verificadas, no por promesas.

For an internal technical reviewer, say:

> El runbook fuerza orden, evidencia y parada segura. Si la cadena controlada no reproduce hash, bytes y limpieza, no se vende como avance.

For a film school, say:

> Esta demo puede enseñar metodología: primero reproducibilidad y límites; después material real solo cuando el gate correspondiente esté cerrado.

## Forbidden product claims

The operator must not say or imply any of the following:

- `PRODUCTO_FINAL_LISTO`.
- `DEMO_PUBLICA_LISTA`.
- `CLIENTE_REAL_VALIDADO`.
- `MATERIAL_REAL_PROCESADO`.
- `SCANNER_REAL_IMPLEMENTADO`.
- `FFPROBE_REAL_EJECUTADO`.
- `FFMPEG_REAL_EJECUTADO`.
- `SINCRONIZACION_IMPLEMENTADA`.
- `TRANSCRIPCION_IMPLEMENTADA`.
- `SUBTITULOS_IMPLEMENTADOS`.
- `DAVINCI_EXPORT_IMPLEMENTADO`.
- `SAAS_INTEGRADO`.
- `DATABASE_INTEGRATED`.
- `INSTALLER_LISTO`.
- `LICENSING_LISTO`.
- `READY_FOR_PAID_CUSTOMER_USE`.
- `READY_FOR_PUBLIC_LAUNCH`.

Forbidden natural-language claims include:

- ya está listo para vender;
- producto final ya disponible;
- demo pública disponible;
- cliente real ya validado;
- material real ya procesado;
- scanner real ya implementado;
- ffprobe real ya ejecutado;
- ffmpeg real ya ejecutado;
- sincronización ya implementada;
- transcripción ya implementada;
- subtítulos ya implementados;
- DaVinci export ya implementado;
- SaaS ya integrado;
- installer ya listo;
- licensing ya listo.

## Operator closeout

End the demo with this controlled closeout:

> Cierre: la demo técnica controlada queda reproducida con evidencia de comando instalado, JSON verificable, SHA/bytes estables, limpieza por defecto y preservación temporal solo bajo bandera explícita. No se ha usado material real, no se ha ejecutado ffprobe/FFmpeg real, no se ha tocado SaaS ni base de datos y no se ha demostrado producto final. El siguiente paso debe seguir siendo incremental y verificable.

Closeout checklist:

- `OPERATOR_RUNBOOK_SEQUENCE_COMPLETED`.
- `OPERATOR_EVIDENCE_CAPTURED`.
- `OPERATOR_FAILURE_POLICY_DEFINED`.
- `OPERATOR_CLEANUP_DISCIPLINE_DEFINED`.
- `OPERATOR_NO_HYPE_BOUNDARY_DEFINED`.
- `NOT_PUBLIC_DEMO`.
- `NOT_CLIENT_READY`.
- `NOT_PRODUCT_FINAL`.

## Gate acceptance criteria

This gate can close only if:

- the runbook document exists;
- the runbook names the exact phase and close token;
- the runbook preserves the controlled artifact identity;
- the runbook contains the ordered command sequence;
- the runbook defines preflight, live execution, evidence capture, failure handling, cleanup, commercial framing, and closeout;
- QA verifies the document and boundaries;
- repo scope is limited to this document and its QA test;
- WSL guard passes;
- PostgreSQL-only regression guard passes;
- no runtime, `pyproject.toml`, scanner, ffprobe/FFmpeg, SaaS/database, installer, backend, or frontend changes are staged.
