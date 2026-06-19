# CID Local Media Agent - Second Controlled Scenario Execution Gate v1

Phase: CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.EXECUTION.GATE.V1

This execution gate defines the final decision conditions for a later separately authorized second controlled scenario execution phase. It does not run the CLI and does not record an execution result.

Required upstream phases:
- CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.EXECUTION.READINESS.GATE.V1
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

Gate objective:
- define final go or hold conditions for a later controlled execution phase
- require explicit human authorization evidence before any CLI command is run
- require a bounded synthetic second scenario
- require local Linux-only non-sensitive files
- require dry-run-only CLI preflight
- preserve sanitized output requirements
- preserve abort conditions
- prevent any expansion into scanner, probing, decoding, reporting, transcription, sync, edit decision output, or SaaS work

Gate possible decisions:
- GATE_HOLD if explicit human authorization is missing
- GATE_HOLD if candidate folder evidence is incomplete
- GATE_ABORT if any forbidden storage, media, privacy, path, or tooling condition is detected
- GATE_READY_FOR_SEPARATE_CONTROLLED_EXECUTION_PHASE only when every gate condition is satisfied

Mandatory decision evidence:
- explicit human authorization exists outside the repository
- authorization names this execution gate phase
- authorization names the second controlled scenario
- authorization confirms synthetic non-sensitive files only
- authorization confirms local Linux-only folder only
- authorization confirms no real client media
- authorization confirms no personal data
- authorization confirms no mounted Windows paths
- authorization confirms no cloud-synced folders
- authorization confirms no network shares
- authorization confirms no scanner integration
- authorization confirms no ffprobe or ffmpeg
- authorization confirms no media probing
- authorization confirms no media decoding
- authorization confirms no report generation
- authorization confirms dry-run-only CLI preflight

Candidate folder gate conditions:
- candidate folder exists outside the repository
- candidate folder is local Linux-only
- candidate folder is synthetic
- candidate folder is non-sensitive
- candidate folder contains no real client media
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

Mandatory limits for the later controlled execution phase:
- maximum file count is explicitly declared
- maximum total size is explicitly declared
- maximum scan depth is explicitly declared
- accepted extensions are explicitly declared
- symlink following remains disabled
- sanitized output format is explicitly declared

Allowed command shape for the later controlled execution phase:
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

Allowed sanitized output fields:
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

Forbidden output:
- private path
- machine name
- user name
- folder name
- file name
- project name
- client name
- raw evidence payload
- stack trace
- media metadata beyond preflight summary
- scanner output
- probing output
- decoding output
- report output

Abort conditions:
- abort if explicit human authorization is missing
- abort if authorization does not name this phase
- abort if authorization does not name the second controlled scenario
- abort if candidate folder is missing
- abort if candidate folder evidence is incomplete
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
- abort if transcription, translation, subtitles, sync, edit decision output, export, upload, desktop app, installer, licensing, SaaS, backend, frontend, database, Docker, Alembic, Stripe, AI Jobs, credits, or ledger work is required
- abort if output would expose private paths, machine names, user names, folder names, file names, project names, client names, or raw evidence

Repository evidence policy:
- human authorization evidence remains outside the repository
- candidate folder path remains outside the repository
- real command output remains outside the repository unless represented only as sanitized summary fields
- no private path, machine name, user name, project name, client name, folder name, file name, or raw evidence payload may be copied into this repository

Execution boundary:
- This execution gate does not run the CLI.
- This execution gate does not record an execution result.
- This execution gate does not authorize immediate execution in this phase.
- A separate controlled execution phase must still be explicitly authorized before any CLI command is run.
- This execution gate does not create, modify, scan, probe, decode, transcribe, translate, sync, export, or upload media.

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
- second controlled scenario controlled execution phase only, and only if explicit human authorization evidence exists outside the repository.
