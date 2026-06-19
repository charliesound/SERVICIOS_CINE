# CID Local Media Agent - Second Controlled Scenario Execution Readiness Gate v1

Phase: CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.EXECUTION.READINESS.GATE.V1

This readiness gate defines the final readiness requirements for a later second controlled scenario execution gate. It does not run the CLI and does not authorize execution.

Required upstream phases:
- CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.EXECUTION.AUTHORIZATION.QA.GATE.V1
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

Readiness objective:
- prepare a later execution gate
- require explicit human authorization evidence before any CLI command is run
- require a bounded second controlled scenario
- require synthetic non-sensitive local files only
- require local Linux-only folder only
- require dry-run-only CLI preflight
- preserve sanitized output expectations
- preserve abort conditions
- preserve repository evidence restrictions

Second controlled scenario candidate requirements:
- candidate folder is defined outside the repository
- candidate folder is local Linux-only
- candidate folder is synthetic
- candidate folder is non-sensitive
- candidate folder contains no client material
- candidate folder contains no personal data
- candidate folder is not a mounted Windows path
- candidate folder is not cloud-synced
- candidate folder is not a network share
- candidate folder contains multiple nested subfolders
- candidate folder contains at least two accepted media extensions
- candidate folder contains at least one ignored extension
- candidate folder contains at least one rejected extension
- candidate folder does not require symlink following
- candidate folder is small enough for bounded dry-run preflight

Required explicit limits for later execution gate:
- maximum file count must be declared
- maximum total size must be declared
- maximum scan depth must be declared
- accepted extensions must be declared
- symlink following must remain disabled
- output format must remain sanitized

Allowed later command shape:
- CLI preflight only
- dry-run behavior only
- explicit input folder
- optional explicit output folder only when synthetic and local Linux-only
- explicit accepted extensions
- explicit maximum file count
- explicit maximum total size
- explicit maximum scan depth
- symlink following disabled
- sanitized format only

Expected sanitized output fields:
- status
- sanitized_input_folder_label
- sanitized_output_folder_label
- media_file_count
- total_selected_media_size_bucket
- maximum_detected_scan_depth
- accepted_extension_counts
- ignored_extension_counts
- rejected_extension_counts
- failed_check_identifiers
- remediation_items
- exit_code

Expected sanitized output restrictions:
- no private path
- no machine name
- no user name
- no folder name
- no file name
- no project name
- no client name
- no raw evidence payload
- no stack trace

Abort conditions:
- abort if explicit human authorization is missing
- abort if candidate folder is missing
- abort if candidate folder is not local Linux-only
- abort if candidate folder contains real client media
- abort if candidate folder contains sensitive media
- abort if candidate folder contains personal data
- abort if candidate folder is a mounted Windows path
- abort if candidate folder is cloud-synced
- abort if candidate folder is a network share
- abort if symlink following would be required
- abort if limits are not declared
- abort if accepted extensions are not declared
- abort if scanner integration is required
- abort if ffprobe or ffmpeg is required
- abort if media probing or decoding is required
- abort if report generation is required
- abort if output would expose private paths, machine names, user names, folder names, file names, project names, client names, or raw evidence

Repository evidence policy:
- human authorization evidence remains outside the repository
- candidate folder path remains outside the repository
- real command output remains outside the repository unless represented only as sanitized summary fields
- no private path, machine name, user name, project name, client name, folder name, file name, or raw evidence payload may be copied into this repository

Execution boundary:
- This readiness gate does not authorize execution.
- This readiness gate does not run the CLI.
- A later execution gate must still be created.
- A separate controlled execution phase must still be explicitly authorized before any CLI command is run.
- This readiness gate does not create, modify, scan, probe, decode, transcribe, translate, sync, export, or upload media.

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
- second controlled scenario execution gate only, without running the CLI.
