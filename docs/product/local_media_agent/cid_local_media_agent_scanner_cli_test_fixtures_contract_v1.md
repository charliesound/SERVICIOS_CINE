# CID Local Media Agent — Scanner CLI Test Fixtures Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.TEST.FIXTURES.CONTRACT.V1`

## Objective

This document defines the contract for future safe test fixtures for the local scanner command of **CID Local Media Agent**.

The future command under test is:

`cid-media-agent scan`

This phase is documentation/test-only.

It does not implement scanner code, filesystem walking, ffprobe calls, ffmpeg calls, media probing, metadata extraction, hashing, waveform analysis, sync, transcription, translation, subtitle generation, DaVinci export, licensing, installer logic, SaaS integration, database models, Alembic migrations, backend routes, frontend code, Docker configuration, workers, AI Jobs, credits, ledger, or real media processing.

## Relationship with previous contracts

This contract depends on the existing local-only product spec, media project data contract, local output contract, and scanner CLI contract.

The fixtures must be designed to validate the scanner contract safely before any real customer disk or real media folder is used.

## Privacy rule

Fixtures must never contain real client media.

Fixtures must never contain real scripts, real production documents, real personal names, real locations, real camera cards, real sound rolls, real transcripts, real subtitles, real logs, or real project metadata.

Fixtures must use synthetic file names, synthetic folder names, tiny placeholder files, and deterministic dummy content.

Fixtures must not include copied camera originals, copied sound originals, copied video files, copied audio files, copied proxies, extracted audio, thumbnails, waveform files, transcripts, or generated subtitles.

## Fixture root

Future fixtures should live under:

`tests/fixtures/local_media_agent/scanner_cli/`

This contract phase does not create those fixtures yet unless a future phase explicitly authorizes fixture generation.

## Required fixture families

Future scanner fixtures should include these families:

- `empty_input_root`
- `simple_camera_only`
- `simple_sound_only`
- `mixed_camera_sound_proxy`
- `sidecar_metadata_only`
- `nested_project_tree`
- `ambiguous_unknown_files`
- `unsafe_input_output_overlap`
- `excluded_dirs`
- `path_policy_examples`
- `dry_run_expected_outputs`
- `json_summary_expected_outputs`

## Fixture file policy

Fixture files must be tiny placeholder files.

Allowed placeholder extensions include:

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

The placeholder extension may simulate a media file type, but the file content must not be real media.

A `.mov`, `.mp4`, `.mxf`, `.wav`, `.bwf`, `.aif`, `.aiff`, or `.flac` fixture must be a tiny dummy placeholder, not playable media and not extracted from real media.

## Allowed synthetic naming examples

Allowed synthetic names may include:

- `SC001_TK001_CAM_A_PLACEHOLDER.mov`
- `SC001_TK001_SOUND_A_PLACEHOLDER.wav`
- `SC001_TK001_PROXY_PLACEHOLDER.mp4`
- `ROLL_A001_PLACEHOLDER.mxf`
- `SOUND_ROLL_001_PLACEHOLDER.bwf`
- `metadata_placeholder.xml`
- `camera_report_placeholder.csv`
- `unknown_asset_placeholder.bin.txt`

Names must remain generic and non-identifying.

## Forbidden fixture content

Fixtures must not contain:

- real project titles;
- real client names;
- real crew names;
- real actor names;
- real location names;
- real addresses;
- real emails;
- real phone numbers;
- real GPS coordinates;
- real call sheets;
- real camera reports;
- real sound reports;
- real transcripts;
- real subtitles;
- real production notes;
- real logs;
- real DaVinci files;
- real proxy files;
- real video frames;
- real audio samples.

## Fixture output expectations

Future fixture tests may compare expected scanner outputs.

Expected outputs may include synthetic examples of:

- `media_catalog.json`
- `media_catalog.csv`
- `media_catalog.md`
- `scan_warnings.json`
- `manual_media_review.csv`
- `privacy_report.md`
- `processing_status.json`
- `processing_log.md`
- `errors.json`
- `warnings.json`
- `privacy_events.json`

Expected outputs must also be synthetic and must not contain real media metadata.

## Scanner-safe folders

Fixture validation must preserve the scanner-safe output restriction.

The scanner test fixtures may exercise output creation only for:

- `00_project/`
- `01_media_catalog/`
- `99_logs/`

Fixtures must not require scanner tests to write into:

- `02_sync/`
- `03_transcripts_original/`
- `04_subtitles_spanish/`
- `05_editorial_summary/`
- `06_davinci/`
- `90_temp/`

Those folders belong to later phases.

## Dry-run fixture behavior

Dry-run fixtures must verify that `--dry-run` does not create the full output package.

Dry-run expected output may contain only a planned action summary.

Dry-run fixtures must not require file writes except safe console or temporary test output in a controlled test directory.

## JSON fixture behavior

JSON fixtures must verify that `--json` output is machine-readable and does not leak full local paths unless explicitly allowed by path policy.

JSON expected outputs must include synthetic values for:

- `status`
- `project_id`
- `privacy_mode`
- `files_seen`
- `candidate_media_count`
- `warnings_count`
- `human_review_required_count`
- `created_outputs`
- `exit_code`

## Path policy fixture behavior

Path policy fixtures must cover:

- `local_absolute_path`
- `local_relative_path`
- `sanitized_path`
- `hashed_path`
- `redacted_path`

Connected or reportable expectations must prefer sanitized, hashed, or redacted paths.

Fixtures must never force a real absolute user path into committed expected outputs.

## Unsafe scenario fixtures

Unsafe scenario fixtures should test that the scanner refuses or warns when:

- input root equals output root;
- output root is inside input root in an unsafe way;
- input root is missing;
- input root is unreadable;
- output root is not writable;
- path policy is invalid;
- privacy mode is invalid;
- original media copy is requested;
- SaaS integration is requested.

These fixtures must remain synthetic and local.

## Human review fixture behavior

Fixtures must cover human review when:

- media type is unknown;
- source kind is ambiguous;
- possible duplicate assets exist;
- file metadata is missing;
- filename classification is uncertain;
- path policy cannot be safely applied.

Expected outputs should mark those assets as `human_review_required`.

## Forbidden behavior

Fixture phases must not:

- add real media;
- add playable media;
- add extracted audio;
- add thumbnails;
- add waveform files;
- add transcripts;
- add subtitles;
- add real logs;
- call ffprobe;
- call ffmpeg;
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

- the fixture root is documented;
- required fixture families are documented;
- placeholder file policy is documented;
- forbidden real content is documented;
- expected scanner outputs are documented;
- dry-run fixture behavior is documented;
- JSON fixture behavior is documented;
- path policy fixture behavior is documented;
- unsafe scenario fixtures are documented;
- human review fixture behavior is documented;
- forbidden behavior protects real media and CID SaaS.
