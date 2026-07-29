# CID Local Media Agent - Read Only Folder Scanner Implementation Gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.IMPLEMENTATION.GATE.V1`

## Expected closure result

`LOCAL_MEDIA_AGENT_READ_ONLY_FOLDER_SCANNER_IMPLEMENTATION_GATE_V1_CLOSED`

## Starting state

`LOCAL_MEDIA_AGENT_READ_ONLY_FOLDER_SCANNER_READINESS_GATE_V1_CLOSED`

## Previous phase

`CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.READINESS.GATE.V1`

## Next allowed phase

`CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.QA.GATE.V1`

## Scope

This phase implements only the isolated Python API for a local read-only folder scanner.

This phase is limited to exactly three files:

- `docs/product/local_media_agent/cid_local_media_agent_read_only_folder_scanner_implementation_gate_v1.md`
- `scripts/local_media_agent/read_only_folder_scanner.py`
- `tests/unit/test_cid_local_media_agent_read_only_folder_scanner_implementation_gate_v1.py`

This phase does not create a public CLI.

This phase does not create `cid scan`.

This phase does not create `cid_cli.py`.

This phase does not modify `pyproject.toml`.

This phase does not create package entrypoints.

This phase does not create installed commands.

This phase does not touch backend, frontend, DB, SaaS, Docker, Alembic, Stripe, auth, AI Jobs, or ledger.

## Implemented API

The implementation module is:

`scripts/local_media_agent/read_only_folder_scanner.py`

The public API is:

- `scan_read_only_folder(input_root)`
- `manifest_to_json(manifest)`
- `emit_manifest_json(manifest, stream)`

The API is stdlib-only, isolated, and testable without argparse or installed entrypoints.

## Runtime contract implemented

The scanner accepts only one local Linux absolute folder path.

The scanner rejects relative paths, missing folders, individual files, symlink roots, URL-like paths, Windows drive paths, UNC paths, `/mnt` paths, `wsl.localhost` paths, `/opt/SERVICIOS_CINE`, and every descendant of `/opt/SERVICIOS_CINE`.

The scanner is strictly read-only.

The scanner performs controlled recursion only.

The scanner never follows symlinks.

The scanner uses only one superficial filesystem metadata read per traversed entry through `path.lstat()`.

The scanner classifies traversed entries with `stat.S_ISLNK(st_mode)`, `stat.S_ISDIR(st_mode)`, and `stat.S_ISREG(st_mode)`.

The scanner does not use `child.is_symlink()`, `child.is_dir()`, or `child.is_file()` during traversal.

The scanner does not open file contents.

The scanner does not read bytes.

The scanner does not compute content hashes.

The scanner does not use MIME detection.

The scanner does not use magic-byte inspection.

The scanner does not use ffprobe, ffmpeg, subprocess, shell execution, network, database, or SaaS.

The scanner does not write artifacts.

The optional JSON emission writes only to an injected stream.

## Fixed V1 limits

- `max_files = 5000`
- `max_depth = 8`
- `max_errors = 100`

When `files_seen` reaches exactly `max_files`, traversal stops in a controlled way, `MAX_FILES_REACHED` is added, `truncated=true` is returned, and the status is `READ_ONLY_FOLDER_SCAN_TRUNCATED`.

When more than `max_files` files exist, `files_seen` never exceeds `max_files`.

When `max_errors` is reached, traversal stops in a controlled way and `truncated=true` is returned.

When an entry would be at depth greater than `max_depth`, it is rejected before metadata is obtained and a sanitized warning is recorded.

## Manifest contract

The manifest contains:

- `schema_version`
- `status`
- `input_label`
- `privacy`
- `scanner_summary`
- `extension_summary`
- `warnings`
- `errors`

The fixed `schema_version` is `cid.local_media_agent.read_only_folder_scanner.v1`.

The fixed `input_label` is `SANITIZED_LOCAL_FOLDER_INPUT`.

The manifest does not expose input paths, absolute paths, relative paths, filenames, folder names, hostnames, usernames, machine names, symlink targets, or raw exception text.

`scanner_summary` includes:

- `files_seen`
- `directories_seen`
- `media_candidates`
- `non_media_files`
- `symlinks_rejected`
- `total_bytes`
- `truncated`

The implementation preserves this invariant:

`media_candidates + non_media_files = files_seen`

## Classification contract

Media classification uses only the V1 extension allowlist.

Extension comparison is case-insensitive.

Files without extensions and files outside the allowlist count as `non_media_files`.

No content inspection, MIME detection, magic-byte inspection, ffprobe, ffmpeg, or external tool is used.

## Acceptance criteria

This implementation gate is accepted only when:

- the implementation module exists;
- the implementation gate document exists;
- the implementation gate test exists;
- only the three authorized files are changed;
- the API returns sanitized JSON-compatible dictionaries;
- validation rejects unsafe roots fail-closed;
- recursion, depth, symlink, counters, limits, classification, privacy, and serialization behavior are covered by tests;
- no CLI, entrypoint, packaging, SaaS, DB, backend, frontend, or media-tool integration is introduced;
- the next allowed phase is exactly `CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.QA.GATE.V1`.
