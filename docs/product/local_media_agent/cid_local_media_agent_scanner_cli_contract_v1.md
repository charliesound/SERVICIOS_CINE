# CID Local Media Agent — Scanner CLI Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.CONTRACT.V1`

## Objective

This document defines the command-line contract for the future local media scanner used by **CID Local Media Agent**, the local execution layer of **CID Editing Intelligence**.

The scanner CLI will inspect a client-selected local media folder or disk, classify candidate media files, extract safe file metadata, prepare a local media catalog, and write scanner outputs into the local output layout defined by the Local Output Contract.

This phase is documentation/test-only.

It does not implement scanner code, filesystem walking, ffprobe calls, ffmpeg calls, media probing, metadata extraction, hashing, waveform analysis, sync, transcription, translation, subtitle generation, DaVinci export, licensing, iLok/PACE, installer logic, SaaS integration, database models, Alembic migrations, backend routes, frontend code, Docker configuration, workers, AI Jobs, credits, ledger, or real media processing.

## SaaS isolation rule

The scanner CLI contract is local-only and must remain isolated from CID SaaS.

It must not touch CID SaaS runtime, backend routes, database models, Alembic migrations, Docker configuration, frontend code, Stripe/payment code, AI Jobs runtime, credits, ledger, workers, production configuration, or integration code.

Future SaaS integration requires a separate explicit phase.

## Privacy rule

Original media never leaves the client system.

The scanner must read from the client-selected input root and write generated outputs only under the client-controlled output root.

The scanner must not upload, copy, move, rename, delete, rewrite, transcode, proxy, extract audio from, or modify original camera media, original sound media, video files, audio files, or proxies.

The scanner may record local metadata and safe references according to the path policy.

Full local paths, transcripts, subtitles, summaries, logs, or metadata may only leave the local system with explicit client authorization in a future connected mode.

## Command name

The future scanner command should be:

`cid-media-agent scan`

The command belongs to the local app/CLI, not to the CID SaaS backend.

## Required arguments

The scanner CLI must require:

- `--input-root`
- `--output-root`

`--input-root` points to the client-controlled folder, disk, RAID, SSD, or NAS path that should be scanned.

`--output-root` points to the client-controlled local folder where generated CID outputs will be written.

The scanner must refuse to run if `--input-root` and `--output-root` resolve to the same path.

## Optional arguments

The scanner CLI may support:

- `--project-id`
- `--project-name`
- `--privacy-mode`
- `--path-policy`
- `--include-extension`
- `--exclude-dir`
- `--max-files`
- `--dry-run`
- `--json`
- `--no-ffprobe`
- `--write-manifest`
- `--strict-local-only`

Allowed `--privacy-mode` values:

- `local_only`
- `connected_metadata_allowed_future`

The default must be `local_only`.

Allowed `--path-policy` values:

- `local_absolute_path`
- `local_relative_path`
- `sanitized_path`
- `hashed_path`
- `redacted_path`

The default connected/reportable policy must prefer `sanitized_path`, `hashed_path`, or `redacted_path`.

## Supported candidate file types

The scanner contract must support detecting candidate files with extensions such as:

- `.mov`
- `.mp4`
- `.mxf`
- `.wav`
- `.bwf`
- `.aif`
- `.aiff`
- `.flac`
- `.xml`
- `.ale`
- `.edl`
- `.srt`
- `.vtt`
- `.json`
- `.csv`
- `.txt`

Detection does not mean processing.

The scanner may classify files as:

- `camera_original`
- `production_sound`
- `proxy`
- `sidecar_metadata`
- `subtitle`
- `report`
- `unknown`

## Preflight checks

Before scanning, the CLI must validate:

- current process is running locally;
- `--input-root` exists;
- `--input-root` is readable;
- `--output-root` can be created or is writable;
- `--input-root` is not equal to `--output-root`;

Plain-language checks:

- --input-root exists;
- --input-root is readable;
- --output-root can be created or is writable;
- --input-root is not equal to `--output-root`;
- output root does not point inside a protected system location;
- privacy mode is explicit or defaults to `local_only`;
- path policy is valid;
- local output layout can be created safely;
- no SaaS integration is required;
- no original media copy is requested.

A failed preflight must not create partial scanner outputs unless a safe local error log is explicitly allowed.

## Output folders used by scan

The scanner may write only to these local output areas:

- `00_project/`
- `01_media_catalog/`
- `99_logs/`

The scanner must not write to sync, transcript, subtitle, editorial, DaVinci, or temp folders unless a future phase explicitly authorizes that behavior.

## Required scan outputs

A successful scan must create or update:

- `00_project/project_manifest.json`
- `00_project/processing_status.json`
- `00_project/privacy_report.md`
- `01_media_catalog/media_catalog.json`
- `01_media_catalog/media_catalog.csv`
- `01_media_catalog/media_catalog.md`
- `01_media_catalog/scan_warnings.json`
- `01_media_catalog/manual_media_review.csv`
- `99_logs/processing_log.md`
- `99_logs/errors.json`
- `99_logs/warnings.json`
- `99_logs/privacy_events.json`

If ffprobe support is enabled in a future phase, the scanner may also create:

- `01_media_catalog/ffprobe_summary.json`

This contract does not implement ffprobe.

## Media catalog requirements

The scanner must represent each discovered file as a media catalog entry.

Each entry must include conceptual fields aligned with the Media Project Data Contract:

- `asset_id`
- `media_type`
- `source_kind`
- `path`
- `path_policy`
- `file_name`
- `extension`
- `file_size_bytes`
- `created_at`
- `modified_at`
- `technical_metadata`
- `privacy`
- `warnings`
- `human_review_required`

For this contract phase, these are conceptual fields only.

## Classification rules

The scanner may classify files using safe local heuristics:

- extension;
- parent folder name;
- filename pattern;
- sidecar presence;
- known camera or sound folder names;
- file size;
- optional future ffprobe metadata.

The scanner must mark uncertain classification as `unknown` or `human_review_required`.

It must not pretend that filename-based classification is final.

## Dry-run behavior

When `--dry-run` is used, the scanner must not write the full output package.

It may print or return a planned action summary.

If `--json` is also used, it should return machine-readable planned actions.

Dry-run must not modify original media or output folders except for safe ephemeral console output.

## JSON output behavior

When `--json` is used, the command should return a machine-readable summary containing:

- `status`
- `project_id`
- `input_root_policy`
- `output_root`
- `privacy_mode`
- `files_seen`
- `candidate_media_count`
- `warnings_count`
- `human_review_required_count`
- `created_outputs`
- `exit_code`

The JSON output must not include full local paths unless explicitly allowed by path policy.

## Exit codes

Recommended exit codes:

- `0`: scan completed successfully;
- `1`: scan completed with warnings or human review required;
- `2`: argument or preflight error;
- `3`: privacy or safety violation;
- `4`: unexpected scanner error.

Exit code `0` must not mean that all media is production-ready. It only means the scan command completed successfully.

## Human review

The scanner must support human review from the first version.

It must produce or reserve:

- `00_project/human_review_index.md`
- `01_media_catalog/manual_media_review.csv`

Human review must be required when:

- media type is unknown;
- source kind is ambiguous;
- path policy cannot be safely applied;
- possible duplicate assets exist;
- file metadata is missing or suspicious;
- camera/sound/proxy classification is uncertain.

## Forbidden behavior

The scanner CLI must not:

- copy original video files;
- copy original audio files;
- copy proxies;
- modify original media;
- rename original media;
- delete original media;
- transcode media;
- extract audio;
- generate proxies;
- transcribe audio;
- translate subtitles;
- create DaVinci timelines;
- upload files;
- call CID SaaS;
- call Stripe;
- call AI Jobs;
- write database rows;
- create migrations;
- touch Docker;
- touch frontend;
- change production configuration.

## Acceptance criteria

This phase is accepted when:

- the scanner CLI command contract is documented;
- required and optional arguments are documented;
- preflight checks are documented;
- supported candidate file types are documented;
- local-only privacy is preserved;
- output folders are limited to scanner-safe areas;
- required scanner outputs are documented;
- dry-run and JSON behaviors are documented;
- exit codes are documented;
- human review is required for uncertain results;
- forbidden behavior protects original media and CID SaaS.
