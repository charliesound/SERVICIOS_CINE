# CID Local Media Agent — Scanner CLI Safe Baseline v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.SAFE.BASELINE.V1`

## Objective

This phase implements the first minimal safe local scanner baseline for the future `cid-media-agent scan` command.

The implementation lives in `scripts/cid_media_agent_scan.py`.

It scans a local input root, classifies candidate placeholder files by extension and simple folder/name heuristics, and writes scanner-safe outputs only under a local output root.

## Scope

The scanner baseline supports:

- `--input-root`;
- `--output-root`;
- `--project-id`;
- `--project-name`;
- `--privacy-mode`;
- `--path-policy`;
- `--dry-run`;
- `--json`;
- `--strict-local-only`.

It writes only to:

- `00_project/`;
- `01_media_catalog/`;
- `99_logs/`.

## No-goals

This phase does not use ffmpeg, does not use ffprobe, does not transcode media, does not extract audio, does not generate proxies, does not sync media, does not perform waveform analysis, does not transcribe, does not translate, does not generate subtitles, does not create DaVinci timelines, does not call CID SaaS, does not call Stripe, does not call AI Jobs, does not write database rows, does not create migrations, does not touch Docker, does not touch frontend, and does not touch credits or ledger.

## Privacy

The scanner must not copy, modify, rename, delete, transcode, proxy, extract, upload, or process original media.

It creates only metadata/catalog/report outputs in a client-controlled output folder.

## Acceptance criteria

This phase is accepted when the scanner works against synthetic fixtures, creates only scanner-safe output folders, supports dry-run and JSON output, refuses unsafe input/output overlap, avoids full local path leakage by default, requires human review for ambiguous assets, and all previous Local Media Agent contract tests still pass.
