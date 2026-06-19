# CID Local Media Agent - Second Controlled Scenario Execution Authorization QA Gate v1

Phase: CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.EXECUTION.AUTHORIZATION.QA.GATE.V1

This QA gate validates the second controlled scenario execution authorization contract without running the CLI and without authorizing execution.

Required upstream phases:
- CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.EXECUTION.AUTHORIZATION.CONTRACT.V1
- CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.READINESS.QA.GATE.V1
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

Required QA validation chain:
- second controlled scenario execution authorization contract test passes
- second controlled scenario readiness QA gate test passes
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

Authorization contract requirements preserved:
- human authorization evidence remains outside the repository
- authorization decision must be explicit
- authorization must name this phase
- authorization must name the second controlled scenario
- candidate folder restrictions are explicit
- allowed command shape is explicit
- expected sanitized outcome is explicit
- abort conditions are explicit
- repository evidence policy is explicit
- execution remains blocked until a later execution phase

Candidate restrictions preserved:
- candidate folder must be local Linux-only
- candidate folder must be synthetic
- candidate folder must be non-sensitive
- candidate folder must not contain client material
- candidate folder must not contain personal data
- candidate folder must not be a mounted Windows path
- candidate folder must not be cloud-synced
- candidate folder must not be a network share
- symlink following must remain disabled

Expected sanitized outcome preserved:
- status is one of PREFLIGHT_PASS, PREFLIGHT_FAIL, or PREFLIGHT_BLOCKED
- exit_code is one of 0, 2, or 3
- sanitized_input_folder_label is present
- sanitized_output_folder_label is present when output folder is provided
- media_file_count is present
- total_selected_media_size_bucket is present
- maximum_detected_scan_depth is present
- accepted_extension_counts is present
- ignored_extension_counts is present
- rejected_extension_counts is present
- failed_check_identifiers is present
- remediation_items is present
- no private path is emitted
- no machine name is emitted
- no user name is emitted
- no file name is emitted
- no raw evidence payload is emitted

Execution boundary:
- This QA gate does not authorize execution.
- This QA gate does not run the CLI.
- A later execution readiness gate must still be created.
- A later execution gate must still be created.
- A separate controlled execution phase must still be explicitly authorized before any CLI command is run.

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
- second controlled scenario execution readiness gate only, without running the CLI.
