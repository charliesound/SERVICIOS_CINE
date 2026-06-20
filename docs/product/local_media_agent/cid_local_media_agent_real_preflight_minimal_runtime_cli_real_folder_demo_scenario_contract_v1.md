# CID Local Media Agent — Real Folder Demo Scenario Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.CONTRACT.V1`

## Objective

Define the controlled local synthetic demo scenario. This phase is docs/test-only. It does not create folders, does not create files, does not execute the scanner, and does not use real client material.

## Required prior readiness gate

`LOCAL_MEDIA_AGENT_DEMO_READINESS_GATE_PASS_CONTROLLED_LOCAL_SYNTHETIC_ONLY`

## Contract result

`LOCAL_MEDIA_AGENT_DEMO_SCENARIO_CONTRACT_PASS_SYNTHETIC_LOCAL_ONLY`

## Demo scenario

Scenario name: `CID_LOCAL_MEDIA_AGENT_SYNTHETIC_DEMO_001`

Allowed root: `/tmp/cid_local_media_agent_synthetic_demo_001/`

Allowed input: `/tmp/cid_local_media_agent_synthetic_demo_001/input/`

Allowed output: `/tmp/cid_local_media_agent_synthetic_demo_001/output/`

Forbidden paths: Windows paths, `/mnt/`, network paths, cloud sync folders, and real production folders.

## Synthetic input shape

- `camera/A001_SC001_TK001.mov`
- `camera/A001_SC001_TK002.mp4`
- `sound/A001_SC001_TK001.wav`
- `proxies/A001_SC001_TK001_PROXY.mp4`
- `non_media/notes.txt`
- `non_media/installer.exe`
- `UNKNOWN/UNKNOWN_ASSET.txt`

All files must be text placeholders containing exactly: `synthetic placeholder only`.

No real audio, video, image, transcript, subtitle, metadata extraction, client material, or shoot material is allowed.

## Expected command

`python scripts/cid_media_agent_scan.py --input-root /tmp/cid_local_media_agent_synthetic_demo_001/input --output-root /tmp/cid_local_media_agent_synthetic_demo_001/output --json`

No `--ffprobe-preflight` flag is allowed.

## Expected result

- `exit_code=1`
- `status=completed_with_warnings`
- `candidate_media_count=5`
- `warnings_count=1`
- `human_review_required_count=1`
- `warnings=["unknown synthetic placeholder"]`
- `ffprobe_preflight.requested=false`
- `ffprobe_preflight.status=skipped`
- `accepted_extension_counts={".mov":1,".mp4":2,".wav":1}`
- `rejected_extension_counts={".exe":1,".txt":2}`
- `ignored_extension_counts={}`

## Expected outputs

- `00_project/processing_status.json`
- `01_media_catalog/media_catalog.json`
- `02_audio_sync/README.txt`
- `03_transcription/README.txt`
- `04_subtitles/README.txt`
- `05_reports/README.txt`
- `06_exports/README.txt`

Media catalog must include accepted media plus `UNKNOWN_ASSET.txt` for human review.

Media catalog must not include `notes.txt` or `installer.exe`.

## Privacy checks required later

Later validation must verify no absolute input path leak, no absolute output path leak, no Windows path leak, no `/mnt/` leak, no real client names, no real production names, and no host absolute paths in media catalog or processing status.

## Abort conditions

Later execution must abort if repo is not clean, HEAD is not approved lineage, root is outside `/tmp/cid_local_media_agent_synthetic_demo_001/`, real media is detected, real client material is detected, Windows or `/mnt/` paths are detected, scanner exits with code `2`, required JSON fields are missing, output folders differ, scanner writes outside output root, semantic counts differ, or privacy checks fail.

## Explicit no-goals

This contract does not authorize public demo, client-facing demo, sales demo, production-ready claim, clean classification PASS claim, real client material, media probing, media decoding, ffmpeg execution, ffprobe execution beyond skipped default availability state, transcription, translation, subtitles, sync, NLE export, SaaS calls, database writes, network calls, or report-expansion scope.

## Runtime boundary

This contract changes no runtime files and does not authorize scanner, report, or CLI behavior changes.

## Protected scope still blocked

This contract does not authorize SaaS backend/frontend, database, Docker, Alembic, Stripe, AI Jobs, credits, ledger, frontend, backend, or media-processing implementation.

## Required validation chain

demo scenario contract test, demo readiness gate, bounded implementation QA gate, bounded implementation test, scanner safe baseline, scanner execution hardening, scanner CLI contract, wider real preflight contracts, py_compile, git diff --check, guard_wsl_repo.sh, and guard_no_sqlite_regressions.sh must pass.

## Recommended next phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DEMO.SCENARIO.CREATE.FIXTURE.V1`

That next phase may create the synthetic fixture only if this contract is closed and tagged.

## Contract result

`PASS`

The controlled local synthetic demo scenario is contract-defined. The demo itself is not yet created. The scanner is not yet executed for this demo scenario. No real client-material demo is authorized.
