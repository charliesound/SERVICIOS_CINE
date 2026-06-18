# CID Local Media Agent — Scanner CLI Test Fixtures Baseline v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.TEST.FIXTURES.BASELINE.V1`

## Objective

This phase creates the first safe synthetic fixture baseline for the future `cid-media-agent scan` command.

The fixtures are local, deterministic, tiny, synthetic, and non-playable.

This phase does not implement the scanner, does not call ffmpeg, does not call ffprobe, does not process media, does not extract audio, does not transcribe, does not translate, does not create subtitles, does not create DaVinci timelines, does not call CID SaaS, does not touch database models, does not create Alembic migrations, does not touch Docker, does not touch frontend, does not touch Stripe, does not touch AI Jobs, and does not touch credits or ledger.

## Fixture root

`tests/fixtures/local_media_agent/scanner_cli/`

## Created fixture families

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

## Privacy

Fixtures contain no real media, no playable media, no copied camera originals, no copied sound originals, no real transcripts, no real subtitles, no real logs, no real project names, no real client names, no real personal data, and no real local absolute paths.

## Placeholder policy

Files with media-like extensions are placeholders only.

They are not playable video, not playable audio, not camera originals, not sound originals, not proxies, and not extracted from real productions.

## Acceptance criteria

This baseline is accepted when the fixture root exists, fixture families exist, placeholder files are tiny, fixture contents are synthetic, expected outputs are synthetic, no forbidden real content is present, no real absolute user paths are committed, and previous Local Media Agent contracts still pass.
