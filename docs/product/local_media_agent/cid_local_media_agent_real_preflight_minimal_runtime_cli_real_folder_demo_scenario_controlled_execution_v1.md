# CID Local Media Agent - Controlled Execution v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.CONTROLLED.EXECUTION.V1`

## Authorization

Authorized by `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.EXECUTION.AUTHORIZATION.GATE.V1`.

Authorization result: `LOCAL_MEDIA_AGENT_DEMO_SCENARIO_EXECUTION_AUTHORIZATION_GATE_PASS_READY_FOR_CONTROLLED_SYNTHETIC_SCANNER_EXECUTION`.

Authorized HEAD: `b5a3bd23ee3851684cfc219fefb29dd0ae94a555`.

## Fixture

Synthetic fixture root: `/tmp/cid_local_media_agent_synthetic_demo_001`.

Input root: `/tmp/cid_local_media_agent_synthetic_demo_001/input`.

Output root: `/tmp/cid_local_media_agent_synthetic_demo_001/output`.

The fixture was recreated after WSL closure because `/tmp` is temporary.

The fixture contained seven synthetic placeholder files:

- `camera/A001_SC001_TK001.mov`
- `camera/A001_SC001_TK002.mp4`
- `sound/A001_SC001_TK001.wav`
- `proxies/A001_SC001_TK001_PROXY.mp4`
- `non_media/notes.txt`
- `non_media/installer.exe`
- `UNKNOWN/UNKNOWN_ASSET.txt`

## Executed Command

Only this authorized command was executed:

```bash
python scripts/cid_media_agent_scan.py --input-root /tmp/cid_local_media_agent_synthetic_demo_001/input --output-root /tmp/cid_local_media_agent_synthetic_demo_001/output --json
```

## Runtime Result

- `exit_code`: `1`
- `status`: `completed_with_warnings`
- `privacy_mode`: `local_only`
- `candidate_media_count`: `5`
- `files_seen`: `5`
- `human_review_required_count`: `1`
- `warnings_count`: `1`
- `warnings`: `unknown synthetic placeholder`
- `accepted_extension_counts`: `.mov=1`, `.mp4=2`, `.wav=1`
- `rejected_extension_counts`: `.exe=1`, `.txt=2`
- `ignored_extension_counts`: `{}`
- `ffprobe_preflight.requested`: `false`
- `ffprobe_preflight.status`: `skipped`

The exit code `1` is expected because the fixture intentionally includes one unknown asset requiring human review.

## Persisted Outputs

- `00_project/project_manifest.json`
- `00_project/processing_status.json`
- `00_project/privacy_report.md`
- `00_project/human_review_index.md`
- `01_media_catalog/media_catalog.json`
- `01_media_catalog/media_catalog.csv`
- `01_media_catalog/media_catalog.md`
- `01_media_catalog/scan_warnings.json`
- `01_media_catalog/manual_media_review.csv`
- `99_logs/processing_log.md`
- `99_logs/errors.json`
- `99_logs/warnings.json`
- `99_logs/privacy_events.json`

## Persisted JSON Facts

`processing_status.json` persisted `status = completed_with_warnings`, `candidate_media_count = 5`, `human_review_required_count = 1`, `accepted_extension_counts = {".mov": 1, ".mp4": 2, ".wav": 1}`, `rejected_extension_counts = {".exe": 1, ".txt": 2}`, `ignored_extension_counts = {}`, `ffprobe_preflight.requested = false`, and `ffprobe_preflight.status = skipped`.

`scan_warnings.json` persisted `warnings = ["unknown synthetic placeholder"]`.

`99_logs/warnings.json` persisted `warnings = ["unknown synthetic placeholder"]`.

`99_logs/errors.json` persisted `errors = []`.

`99_logs/privacy_events.json` persisted `event = local_only_scan_completed` and `original_media_left_client_system = false`.

## Documented Deltas

- `warnings_count` appears in stdout summary but is not persisted as a JSON field.
- `synthetic_project` appears in stdout summary but is not persisted in inspected JSON outputs.
- Future contract directories were not created by the current scanner: `02_audio_sync`, `03_transcription`, `04_subtitles`, `05_reports`, `06_exports`.
- `privacy_events.json` is not empty; it correctly records local-only completion.

## Privacy Result

Privacy token check passed.

No forbidden tokens were found in persisted outputs: `/mnt/`, Windows drive paths, UNC paths, `DESKTOP-`, `harliesound`, or `SERVICIOS_CINE`.

The approved `/tmp/cid_local_media_agent_synthetic_demo_001` root was not present in persisted outputs during the final privacy check.

## Non-Goals Preserved

This phase did not authorize or perform real client media scanning, public/client-facing demo, ffprobe execution, ffmpeg execution, audio/video synchronization, transcription, subtitle generation, DaVinci Resolve export, SaaS upload, database writes, network calls, frontend/backend SaaS changes, Docker or Alembic changes, Stripe, AI Jobs, credits, or ledger changes.

## Git Boundary

Runtime outputs stayed outside Git under `/tmp`.

Repository remained clean after execution and verification.

No `/tmp` scanner output was committed.

## Result

`LOCAL_MEDIA_AGENT_CONTROLLED_SYNTHETIC_SCANNER_EXECUTION_PASS_WITH_DOCUMENTED_DELTAS_READY_FOR_QA_GATE`

## Next Recommended Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.CONTROLLED.EXECUTION.QA.GATE.V1`
