# CID Local Media Agent - Read Only Folder Scanner Readiness Gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.READINESS.GATE.V1`

## Expected closure result

`LOCAL_MEDIA_AGENT_READ_ONLY_FOLDER_SCANNER_READINESS_GATE_V1_CLOSED`

## Scope

This phase is documentation-only and test-only.

This phase creates the readiness contract for a future local read-only folder scanner.

This phase does not implement scanner runtime.

This phase does not create CLI commands.

This phase does not modify package entrypoints.

This phase does not execute scans.

This phase does not open or read audiovisual file contents.

This phase does not create runtime scripts.

This phase is limited to exactly two files:

- `docs/product/local_media_agent/cid_local_media_agent_read_only_folder_scanner_readiness_gate_v1.md`
- `tests/unit/test_cid_local_media_agent_read_only_folder_scanner_readiness_gate_v1.py`

## Future scanner input contract

The future scanner input root must be one local Linux absolute folder path.

The future scanner input root must already exist.

The future scanner must reject an individual file as the input root.

The future scanner must reject a symlink as the input root.

The future scanner must reject URL-like inputs.

The future scanner must reject Windows drive paths.

The future scanner must reject UNC paths.

The future scanner must reject `/mnt` paths.

The future scanner must reject `wsl.localhost` paths.

The future scanner must reject `/opt/SERVICIOS_CINE` as the input root.

The future scanner must reject every descendant of `/opt/SERVICIOS_CINE` as the input root.

The future scanner must fail closed when input validation is ambiguous.

## Future scanner operating contract

The future scanner must be strictly read-only.

The future scanner may perform controlled recursive traversal only.

The future scanner must not follow symlinks.

The future scanner must reject symlink entries encountered during traversal and count them in `symlinks_rejected`.

The future scanner may collect only superficial metadata based on `stat`.

The future scanner must not open file contents.

The future scanner must not read media bytes.

The future scanner must not compute content hashes.

The future scanner must not execute `ffprobe`.

The future scanner must not execute `ffmpeg`.

The future scanner must not use subprocess.

The future scanner must not use shell execution.

The future scanner must not use network access.

The future scanner must not use a database.

The future scanner must not use SaaS.

The future scanner must not transcribe audio.

The future scanner must not generate subtitles.

The future scanner must not copy, move, rename, delete, overwrite, transcode, proxy, or modify any original material.

The future first implementation must not write artifacts to disk.

The future first implementation must emit a sanitized JSON manifest to stdout.

The future manifest must not contain absolute paths.

The future manifest must not contain real filenames.

The future manifest must not contain private folder names.

The future manifest must not contain hostnames, usernames, machine names, credentials, tokens, or raw environment values.

The future scanner must terminate in a controlled way when a configured limit is reached.

## Initial limits

The future first implementation must use these fixed initial limits:

- `max_files = 5000`
- `max_depth = 8`
- `max_errors = 100`

When `max_files` is reached, the future scanner must stop traversal, set `truncated=true`, and return a controlled status.

When `max_depth` is reached, the future scanner must not descend further, must record a sanitized warning, and must continue only where safe.

When `max_errors` is reached, the future scanner must stop traversal, set `truncated=true`, and return a controlled status.

## Depth semantics

The future scanner must assign `depth = 0` to the validated input root folder.

The future scanner must assign `depth = 1` to direct descendants of the validated input root folder.

Each deeper descendant must increment depth by one relative to its parent.

The future scanner must not descend into entries whose depth would exceed `max_depth`.

The future scanner must record a sanitized warning when traversal is stopped by `max_depth`.

The future scanner must never use a path string from the input root as the reported depth label.

## Directory counting semantics

The future `directories_seen` value must include the validated input root folder.

The future `directories_seen` value must include only real directories actually visited.

The future `directories_seen` value must not include symlinks rejected during root validation or traversal.

The future `directories_seen` value must not include entries that are not directories.

The future `directories_seen` value must not include directories skipped because descending into them would exceed `max_depth`.

## Byte counting semantics

The future `total_bytes` value must sum only `st_size` from regular files processed successfully.

The future `total_bytes` value must not include directory sizes.

The future `total_bytes` value must not include symlink sizes.

The future `total_bytes` value must not include rejected entries.

The future `total_bytes` value must not include files whose `stat` call fails.

The future `total_bytes` value must not require opening file contents.

## Media classification semantics

The future media classification must be based exclusively on the fixed V1 extension allowlist.

The future media classification must compare extensions case-insensitively.

The future media classification must not inspect file contents.

The future media classification must not use MIME detection.

The future media classification must not use magic-byte inspection.

The future media classification must not use `ffprobe`.

The future media classification must not use `ffmpeg`.

Files with no extension must count as `non_media_files`.

Files with extensions outside the V1 allowlist must count as `non_media_files`.

### V1 media extension allowlist

Video extensions:

- `.mp4`
- `.mov`
- `.mxf`
- `.mkv`
- `.avi`
- `.mts`
- `.m2ts`
- `.webm`

Audio extensions:

- `.wav`
- `.bwf`
- `.aif`
- `.aiff`
- `.mp3`
- `.m4a`
- `.aac`
- `.flac`
- `.ogg`

Image extensions:

- `.jpg`
- `.jpeg`
- `.png`
- `.tif`
- `.tiff`
- `.dng`
- `.cr2`
- `.cr3`
- `.arw`
- `.nef`
- `.orf`
- `.raf`

## Future manifest contract

The future stdout JSON manifest must include these top-level fields:

- `schema_version`
- `status`
- `input_label`
- `privacy`
- `scanner_summary`
- `extension_summary`
- `warnings`
- `errors`

The future `input_label` must be a fixed sanitized label, not a real path and not a real folder name.

The future `privacy` object must prove:

- original media modified: `false`
- file contents opened: `false`
- content hashes computed: `false`
- ffprobe executed: `false`
- ffmpeg executed: `false`
- subprocess used: `false`
- network used: `false`
- database used: `false`
- SaaS used: `false`
- artifact written: `false`

The future `scanner_summary` object must define:

- `files_seen`
- `directories_seen`
- `media_candidates`
- `non_media_files`
- `symlinks_rejected`
- `total_bytes`
- `truncated`

The future `extension_summary` object must contain sanitized extension-level counts only.

The future `warnings` list must contain sanitized warning codes or messages only.

The future `errors` list must contain sanitized error codes or messages only.

## Fail-closed behavior

The future scanner must fail closed for:

- invalid input root;
- unreadable input root;
- file root instead of folder root;
- symlink root;
- unsafe path policy;
- repository path input;
- traversal limit exhaustion;
- repeated filesystem errors;
- any attempt to use forbidden runtime capabilities.

A failed result must still be sanitized.

A failed result must not include the rejected path.

A failed result must not create artifacts.

## Explicit non-authorizations

This readiness gate does not authorize:

- scanner runtime implementation;
- `cid scan` implementation;
- CLI entrypoint creation;
- packaging changes;
- `pyproject.toml` changes;
- runtime scripts;
- real scan execution;
- customer material processing;
- public demo;
- production use;
- paid pilot;
- backend work;
- frontend work;
- database work;
- SaaS integration;
- Docker changes;
- Alembic migrations;
- Stripe changes;
- authentication changes;
- AI Jobs changes;
- ledger changes;
- ffprobe or ffmpeg execution;
- subprocess, shell, or network use.

## Next allowed phase

The only next runtime phase allowed by this readiness gate is:

`CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.IMPLEMENTATION.GATE.V1`

That future implementation gate must remain minimal, isolated, reversible, read-only, stdout-only, and covered by targeted unit tests.

## Acceptance criteria

This readiness gate is accepted only when:

- the phase identity is exact;
- this document exists;
- the scope remains limited to the two authorized files;
- future input validation rules are explicit;
- future privacy and read-only boundaries are explicit;
- required future manifest fields are explicit;
- `scanner_summary` fields are explicit;
- `max_files`, `max_depth`, and `max_errors` are explicit;
- forbidden runtime operations are explicitly blocked;
- runtime, CLI, package entrypoint, and packaging authorization remains blocked;
- the next allowed phase is exactly `CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.IMPLEMENTATION.GATE.V1`.
