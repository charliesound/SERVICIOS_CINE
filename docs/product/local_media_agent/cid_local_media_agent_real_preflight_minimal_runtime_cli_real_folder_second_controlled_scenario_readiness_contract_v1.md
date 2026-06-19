# CID Local Media Agent - Second Controlled Scenario Readiness Contract v1

Phase: CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.READINESS.CONTRACT.V1

This contract defines readiness requirements for a second controlled real-folder scenario without authorizing execution.

The second controlled scenario remains synthetic, non-sensitive, Linux-only, local-only, and dry-run-only. It is intended to prepare a more demanding preflight shape after the first controlled execution was completed and bounded.

Required upstream phases:
- CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DRY_RUN.CONTROLLED.EXECUTION.V1
- CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DRY_RUN.CONTROLLED.EXECUTION.QA.GATE.V1
- CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.POST.CONTROLLED.EXECUTION.BOUNDARY.CONTRACT.V1
- CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.POST.CONTROLLED.EXECUTION.BOUNDARY.QA.GATE.V1

Previous controlled result preserved:
- status=PREFLIGHT_PASS
- exit_code=0
- media_file_count=2
- accepted_extension_counts=.mov:1,.wav:1
- maximum_detected_scan_depth=3
- total_selected_media_size_bucket=LE_100MB

Second scenario readiness shape:
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

Allowed command shape, when later separately authorized:
- CLI dry-run invocation only.
- Input folder must be local Linux-only synthetic and non-sensitive.
- Output folder, if provided, must be local Linux-only synthetic and non-sensitive.
- Accepted extensions must be explicitly declared.
- Maximum scan depth must be explicitly declared.
- Symlink following must remain disabled.

This contract does not authorize execution. A later execution phase must provide separate human authorization evidence, explicit candidate folder restrictions, expected sanitized outcome, abort conditions, and QA validation before any command is run.

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
- QA gate validating this readiness contract only.
