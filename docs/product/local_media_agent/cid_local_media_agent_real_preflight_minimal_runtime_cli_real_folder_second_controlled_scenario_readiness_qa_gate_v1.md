# CID Local Media Agent - Second Controlled Scenario Readiness QA Gate v1

Phase: CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.READINESS.QA.GATE.V1

This QA gate validates the second controlled scenario readiness contract without authorizing execution.

Required upstream phases:
- CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.READINESS.CONTRACT.V1
- CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.POST.CONTROLLED.EXECUTION.BOUNDARY.QA.GATE.V1
- CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.POST.CONTROLLED.EXECUTION.BOUNDARY.CONTRACT.V1
- CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DRY_RUN.CONTROLLED.EXECUTION.QA.GATE.V1
- CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DRY_RUN.CONTROLLED.EXECUTION.V1

Required previous controlled result:
- status=PREFLIGHT_PASS
- exit_code=0
- media_file_count=2
- accepted_extension_counts=.mov:1,.wav:1
- maximum_detected_scan_depth=3
- total_selected_media_size_bucket=LE_100MB

Required readiness shape:
- Linux-only synthetic folder.
- Non-sensitive local files only.
- No real client media.
- No personal data.
- Multiple nested subfolders.
- At least two accepted media extensions.
- At least one ignored extension.
- At least one rejected extension.
- Explicit maximum file count limit.
- Explicit maximum total size limit.
- Explicit maximum scan depth limit.
- Symlink following disabled.
- Sanitized labels only.
- Sanitized summary fields only.
- Human authorization evidence remains outside the repository.
- Execution output remains outside the repository unless represented as sanitized summary fields.

Required QA validation chain:
- second controlled scenario readiness contract test passes
- post controlled execution boundary QA gate test passes
- post controlled execution boundary contract test passes
- controlled execution QA gate test passes
- controlled execution record test passes
- dry-run execution gate test passes
- dry-run readiness gate test passes
- real folder authorization QA gate test passes
- real folder authorization contract test passes
- WSL repository secrets guard passes
- PostgreSQL-only regression guard passes

Execution boundary:
- This QA gate does not authorize execution.
- A later phase must provide separate human authorization evidence.
- A later phase must define explicit candidate folder restrictions.
- A later phase must define expected sanitized outcome.
- A later phase must define abort conditions.
- A later phase must complete QA validation before any command is run.

Hard non-goals:
- real client media
- sensitive media
- personal data processing
- mounted Windows paths
- cloud-synced folders
- network shares
- scanner integration
- ffprobe or ffmpeg
- media probing
- media decoding
- report generation
- transcription
- translation
- subtitles
- sync
- edit decision output
- upload
- desktop app
- installer
- licensing
- SaaS integration
- backend changes
- frontend changes
- database changes
- Docker changes
- Alembic changes
- Stripe changes
- AI Jobs changes
- credits
- ledger changes

Allowed next step:
- second controlled scenario execution authorization contract only, without running the CLI.
