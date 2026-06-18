# CID Local Media Agent — Scanner CLI Execution Hardening v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SCANNER.CLI.EXECUTION.HARDENING.V1`

## Objective

This phase hardens the real command-line execution behavior of the current safe baseline scanner.

The scanner script under test is:

`scripts/cid_media_agent_scan.py`

The purpose is to verify that the scanner behaves correctly when executed as a real terminal command, not only when imported as a Python module.

## Scope

This phase validates:

- subprocess execution;
- required CLI arguments;
- argparse failures;
- real process exit codes;
- `--json` machine-readable output;
- `--dry-run` behavior;
- preflight failure behavior;
- input/output overlap refusal;
- output-inside-input refusal;
- default path privacy;
- scanner-safe output folders only;
- no forbidden runtime imports;
- no accidental SaaS or database coupling;
- no ffmpeg or ffprobe coupling.

## No-goals

This phase does not implement ffmpeg, does not implement ffprobe, does not probe media, does not parse technical metadata, does not hash file contents, does not process media, does not transcode, does not extract audio, does not generate proxies, does not sync media, does not perform waveform analysis, does not transcribe, does not translate, does not generate subtitles, does not create DaVinci timelines, does not call CID SaaS, does not call Stripe, does not call AI Jobs, does not write database rows, does not create migrations, does not touch Docker, does not touch frontend, and does not touch credits or ledger.

## Privacy requirements

The CLI must not copy, modify, rename, delete, transcode, proxy, extract, upload, or process original media.

By default, `--json` output and generated catalogs must not leak full local absolute paths.

The scanner must continue to write only under the client-controlled `--output-root`.

## Expected execution behavior

A successful scan over synthetic fixture input should exit with code `0`.

A scan that requires human review may exit with code `1`.

Argument errors and preflight errors must exit with code `2`.

Dry-run must not create the full output package.

JSON output must be parseable JSON.

Default non-JSON output may remain human-readable.

## Acceptance criteria

This phase is accepted when subprocess tests confirm required argument handling, real exit codes, JSON behavior, dry-run behavior, preflight refusal, path privacy, safe output folders, and forbidden import protection while all previous Local Media Agent tests continue to pass.
