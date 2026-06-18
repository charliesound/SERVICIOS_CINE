# CID Local Media Agent — Scanner CLI Path Policy Privacy Edge Cases v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.PATH_POLICY.PRIVACY.EDGE_CASES.V1`

## Objective

This phase hardens path-policy and privacy edge cases for the current safe baseline scanner before any future ffprobe or technical metadata phase.

The scanner script under test is:

`scripts/cid_media_agent_scan.py`

## Scope

This phase validates that default scanner outputs do not leak full local absolute paths through:

- JSON stdout;
- `media_catalog.json`;
- `media_catalog.csv`;
- `media_catalog.md`;
- `project_manifest.json`;
- `processing_status.json`;
- `privacy_report.md`;
- `processing_log.md`;
- warnings and privacy event logs.

It also validates:

- paths with spaces;
- paths with non-ASCII characters;
- filenames that look production-like but remain synthetic;
- default `sanitized_path` behavior;
- explicit `local_relative_path`;
- explicit `hashed_path`;
- explicit `redacted_path`;
- explicit `local_absolute_path` opt-in;
- preflight errors without unnecessary absolute path exposure;
- no output creation outside `--output-root`.

## No-goals

This phase does not implement ffmpeg, does not implement ffprobe, does not probe media, does not parse technical metadata, does not hash media contents, does not process media, does not transcode, does not extract audio, does not generate proxies, does not sync media, does not perform waveform analysis, does not transcribe, does not translate, does not generate subtitles, does not create DaVinci timelines, does not call CID SaaS, does not call Stripe, does not call AI Jobs, does not write database rows, does not create migrations, does not touch Docker, does not touch frontend, and does not touch credits or ledger.

## Privacy requirements

Default path policy must avoid full local absolute path leakage.

`local_absolute_path` is allowed only as explicit opt-in.

Generated logs and reports must not include full local absolute paths by default.

Preflight errors should be useful but should avoid dumping full filesystem details unless a future explicit debug mode is defined.

## Acceptance criteria

This phase is accepted when tests confirm default path privacy, safe behavior for unusual synthetic paths, explicit behavior for each path policy, no absolute path leakage in default reports/logs/catalogs/stdout, safe preflight errors, and no writes outside `--output-root`, while all previous Local Media Agent tests continue to pass.
