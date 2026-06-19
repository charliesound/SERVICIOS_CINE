# CID Local Media Agent — Real Folder Dry Run Execution Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DRY_RUN.EXECUTION.GATE.V1`

## Objective

This phase defines the conservative execution gate for a future controlled real-folder dry-run.

This phase is docs/test-only.

It does not execute the CLI. It does not run against a real folder. It does not authorize immediate execution. It does not authorize real client media, sensitive media, personal data processing, mounted Windows paths, `/mnt/` paths, /mnt/ paths, Windows drive paths, cloud-synced folders, network shares, scanner integration, ffprobe, ffmpeg, media probing, media decoding, report generation, transcription, translation, subtitles, NLE export, upload, packaging, desktop app, installer, licensing, SaaS, backend, frontend, database, Docker, Alembic, Stripe, AI Jobs, credits, or ledger work.

This gate alone does not execute the command.

## Current clean stable prerequisite

Latest clean stable prerequisite:

`cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-dry-run-readiness-gate-v1-20260619`

Expected prerequisite commit:

`38401c4b7b79c3b1b14bc3bb8cbb53a89edfca16`

## Required prerequisite chain

1. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.AUTHORIZATION.CONTRACT.V1`
2. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.AUTHORIZATION.QA.GATE.V1`
3. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DRY_RUN.READINESS.GATE.V1`
4. `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.DRY_RUN.EXECUTION.GATE.V1`

## Execution gate decision states

Allowed states:

- `EXECUTION_GATE_PASS`
- `EXECUTION_GATE_FAIL`
- `EXECUTION_GATE_BLOCKED`

## Required human execution authorization record

Required fields before any later command is run:

- `authorized_by_human`
- `authorization_timestamp`
- `authorized_phase`
- `execution_candidate_folder_class`
- `execution_candidate_folder_is_local_linux_only`
- `execution_candidate_folder_is_synthetic_or_non_sensitive`
- `execution_candidate_folder_contains_real_client_media`
- `execution_candidate_folder_contains_sensitive_media`
- `execution_candidate_folder_contains_personal_data`
- `execution_candidate_folder_is_not_repo_root`
- `execution_candidate_folder_is_not_home_root`
- `execution_candidate_folder_is_not_entire_disk`
- `execution_candidate_folder_is_not_mounted_windows_path`
- `execution_candidate_folder_is_not_under_mnt`
- `execution_candidate_folder_is_not_cloud_synced`
- `execution_candidate_folder_is_not_network_share`
- `execution_candidate_expected_file_count_range`
- `execution_candidate_expected_total_size_range`
- `execution_candidate_allowed_extensions`
- `execution_candidate_input_snapshot_confirmed`
- `execution_candidate_output_folder_empty_or_nonexistent`
- `execution_candidate_no_media_decoding`
- `execution_candidate_no_report_generation`
- `execution_candidate_no_scanner_integration`
- `execution_candidate_no_ffprobe_or_ffmpeg`
- `execution_candidate_no_network_access`
- `execution_candidate_expected_exit_codes`
- `execution_candidate_stop_conditions`
- `execution_candidate_rollback_plan`

This execution gate does not store raw private paths in Git.

## Eligible execution candidate class

A later execution candidate may be considered only if all of the following are true:

- local Linux folder visible inside WSL
- intentionally selected by the human operator
- synthetic or non-sensitive
- contains no real client media
- contains no sensitive media
- contains no personal data
- not the repository root
- not a home directory root
- not the entire disk
- not a mounted Windows path
- not under `/mnt/`
- not a /mnt/ path
- not a Windows drive path
- not a cloud-synced directory
- not a network share
- not a backup folder
- not a database folder
- small, bounded number of files
- snapshotted before execution

## Only allowed command template for a later manual execution

Allowed command shape:

`python scripts/cid_local_media_agent_real_preflight_cli.py --input-folder <AUTHORIZED_LOCAL_LINUX_SYNTHETIC_OR_NON_SENSITIVE_FOLDER> --output-folder <AUTHORIZED_LOCAL_LINUX_EMPTY_OUTPUT_FOLDER> --max-file-count 25 --max-total-size-bytes 104857600 --max-scan-depth 3 --accepted-extension .mp4 --accepted-extension .mov --accepted-extension .wav --accepted-extension .mxf --format json --no-follow-symlinks`

The later command must not use raw private paths in committed files, shell globs, broad directories, mounted Windows paths, `/mnt/` paths, network paths, or cloud-synced paths.

## Allowed behavior for later execution only

Allowed behavior is limited to:

- minimal CLI preflight invocation
- local filesystem metadata checks only
- accepted extension counting
- ignored extension counting
- rejected extension counting
- bounded file count validation
- bounded size bucket validation
- bounded scan depth validation
- sanitized stdout
- sanitized stderr
- deterministic exit code mapping

## Required sanitized output fields

A later execution must produce only these sanitized fields:

- `status`
- `sanitized_input_folder_label`
- `sanitized_output_folder_label`
- `media_file_count`
- `total_selected_media_size_bucket`
- `maximum_detected_scan_depth`
- `accepted_extension_counts`
- `ignored_extension_counts`
- `rejected_extension_counts`
- `failed_check_identifiers`
- `remediation_items`
- `exit_code`

The output must not contain raw private paths, raw filenames, client names, project names, personal data, stack traces, media content, generated reports, transcripts, subtitles, timeline files, or upload references.

## Required stop conditions

Abort if any condition is true:

- repository is dirty outside the intended execution evidence area
- WSL/repository guard fails
- PostgreSQL-only regression guard fails
- candidate folder is under `/mnt/`
- candidate folder is a /mnt/ path
- candidate folder is a mounted Windows path
- candidate folder is a Windows drive path
- candidate folder contains real client media
- candidate folder contains sensitive media
- candidate folder contains personal data
- output policy would write reports
- command would invoke scanner integration
- command would invoke ffprobe
- command would invoke ffmpeg
- command would decode media
- command would probe media bytes
- command would call a network service

## Required test matrix before closing this phase

The following matrix must remain green:

- real folder dry-run execution gate
- real folder dry-run readiness gate
- real folder authorization QA gate
- real folder authorization contract
- smoke/demo readiness gate
- smoke/demo QA gate
- smoke/demo implementation
- smoke/demo contract
- CLI QA gate
- CLI implementation
- CLI contract
- minimal runtime QA gate
- minimal runtime implementation
- minimal runtime contract
- WSL/repository guard
- PostgreSQL-only regression guard

## Repository safety requirements

Before closing this phase:

- this execution gate document must exist
- this execution gate test must exist
- the real folder dry-run readiness gate document must exist
- the real folder dry-run readiness gate test must exist
- the latest real folder dry-run readiness gate stable tag must exist
- the latest real folder dry-run readiness gate stable tag must point to the expected commit
- protected files must not be staged
- `.env` must not be staged
- database files must not be staged
- backup files must not be staged
- WSL/repository guard must pass
- PostgreSQL-only regression guard must pass

## Acceptance criteria

Accepted only if this document and test exist, the phase is docs/test-only, no CLI execution is authorized, the stable prerequisite tag is verified, the prerequisite chain is documented, human execution authorization fields are documented, eligible candidate restrictions are documented, the allowed command template is documented, allowed behavior is minimal and sanitized, output expectations are documented, stop conditions are documented, previous tests still pass, and repository guards still pass.
