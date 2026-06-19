# CID Local Media Agent - Controlled Execution QA Gate v1

Phase: CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DRY_RUN.CONTROLLED.EXECUTION.QA.GATE.V1

This QA gate validates the controlled execution record without expanding runtime capabilities.
It validates that the controlled dry-run was recorded in sanitized form only.
It validates that local human authorization evidence remains outside the repository.
It validates that no private path, machine name, user name, folder name, file name, or raw evidence payload is copied into the repository.

Required upstream record:
CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DRY_RUN.CONTROLLED.EXECUTION.V1

Required sanitized result:
status=PREFLIGHT_PASS
exit_code=0
media_file_count=2
accepted_extension_counts=.mov:1,.wav:1
maximum_detected_scan_depth=3
total_selected_media_size_bucket=LE_100MB

Required QA checks:
- controlled execution record test passes
- dry-run execution gate test passes
- dry-run readiness gate test passes
- real folder authorization QA gate test passes
- real folder authorization contract test passes
- WSL repository secrets guard passes
- PostgreSQL-only regression guard passes

This QA gate does not authorize real client media, sensitive media, personal data processing, mounted Windows paths, cloud-synced folders, network shares, scanner integration, ffprobe or ffmpeg, media probing, media decoding, report generation, transcription, translation, subtitles, sync, DaVinci Resolve integration, Avid integration, EDL, XML, AAF, OTIO generation, upload, desktop app, installer, licensing, SaaS integration, backend changes, frontend changes, database changes, Docker changes, Alembic changes, Stripe changes, AI Jobs changes, credits, or ledger changes.
