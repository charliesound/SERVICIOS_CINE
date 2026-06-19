# CID Local Media Agent — Real Preflight Minimal Runtime CLI QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.QA.GATE.V1`

## Objective

This phase audits the minimal CLI wrapper created for the real preflight minimal runtime.

This phase is a QA gate.

It does not add CLI features. It does not widen CLI scope. It does not modify the runtime. It does not modify scanner behavior. It does not generate reports. It does not process media content. It does not add packaging, installer, desktop, licensing, SaaS, backend, frontend, database, billing, upload, or cloud behavior.

The only purpose of this phase is to verify that the current CLI remains inside the approved minimal runtime CLI contract.

## CLI under audit

The CLI file under audit is:

`scripts/cid_local_media_agent_real_preflight_cli.py`

## Runtime under audit

The runtime called by the CLI is:

`scripts/cid_local_media_agent_real_preflight.py`

The CLI must call the approved runtime boundary and must not duplicate traversal logic outside the runtime.

## Governing contract

The governing CLI contract is:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.CONTRACT.V1`

The implementation phase under audit is:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.IMPLEMENTATION.V1`

## Required QA decision states

This QA gate may produce only these conceptual decisions:

- `QA_PASS`
- `QA_FAIL`
- `QA_BLOCKED`

`QA_PASS` means the current CLI remains inside the approved minimal preflight boundary.

`QA_FAIL` means one or more expected checks failed and must be corrected before continuing.

`QA_BLOCKED` means the CLI appears to cross a privacy, media-processing, integration, repository, dependency, or scope boundary.

## Required CLI behavior

The CLI must:

- accept only approved arguments;
- call `run_real_preflight_check`;
- return deterministic exit codes;
- emit sanitized JSON by default;
- emit sanitized text only when requested;
- never print private paths;
- never print raw filenames;
- never print stack traces by default;
- never write inside selected input or output folders;
- never call scanner modules;
- never call media tools;
- never call remote APIs;
- never connect to SaaS, databases, billing, upload, or cloud services.

## Approved CLI arguments

The CLI may accept only:

- `--input-folder`;
- `--output-folder`;
- `--max-file-count`;
- `--max-total-size-bytes`;
- `--max-scan-depth`;
- `--accepted-extension`;
- `--no-follow-symlinks`;
- `--format`.

## Approved output formats

The CLI may output only:

- `json`;
- `text`.

JSON must be the default output format.

Both output formats must be sanitized.

## Required exit code mapping

The CLI must preserve this mapping:

- `PREFLIGHT_PASS` -> exit code `0`;
- `PREFLIGHT_FAIL` -> exit code `2`;
- `PREFLIGHT_BLOCKED` -> exit code `3`;
- invalid CLI usage -> exit code `64`;
- unexpected internal error before sanitized output can be produced -> exit code `70`.

## Required JSON payload fields

The CLI JSON output may include only:

- `status`;
- `sanitized_input_folder_label`;
- `sanitized_output_folder_label`;
- `media_file_count`;
- `total_selected_media_size_bucket`;
- `maximum_detected_scan_depth`;
- `accepted_extension_counts`;
- `ignored_extension_counts`;
- `rejected_extension_counts`;
- `failed_check_identifiers`;
- `remediation_items`;
- `exit_code`.

## Prohibited output content

The CLI output must not include:

- full private paths;
- raw filenames;
- client names;
- project names;
- absolute paths;
- relative source paths;
- environment variables;
- user account names;
- hostnames;
- media hashes;
- media content;
- stream metadata;
- codec metadata;
- timecode metadata;
- embedded metadata;
- transcript text;
- subtitle text;
- waveform data;
- frame data;
- thumbnail data.

## Source boundary

The CLI source must not import or invoke:

- scanner modules;
- synthetic visible report modules;
- media probing wrappers;
- transcription modules;
- translation modules;
- sync modules;
- subtitle modules;
- NLE export modules;
- SaaS modules;
- database modules;
- billing modules;
- licensing modules;
- upload modules;
- network clients;
- subprocess execution.

## No-write boundary

The CLI must not create, modify, or delete files in:

- the selected input folder;
- the selected output folder.

The CLI must not create:

- reports;
- manifests;
- indexes;
- caches;
- thumbnails;
- waveform data;
- transcripts;
- subtitles;
- sidecars;
- NLE export files;
- temporary files inside selected folders.

## Operations still blocked

This QA gate does not authorize:

- media decoding;
- stream probing;
- codec probing;
- container probing;
- real file probing tools;
- media conversion tools;
- frame extraction;
- thumbnail generation;
- waveform generation;
- audio analysis;
- speech recognition;
- transcription;
- translation;
- subtitle generation;
- sync analysis;
- clap detection;
- timecode extraction;
- scanner integration;
- report generation;
- synthetic visible report integration;
- DaVinci Resolve integration;
- Avid integration;
- NLE export;
- EDL generation;
- XML generation;
- AAF generation;
- OTIO generation;
- timeline generation;
- upload;
- cloud transfer;
- desktop packaging;
- installer creation;
- licensing activation;
- SaaS integration;
- backend changes;
- frontend changes;
- database changes;
- billing changes.

## Acceptance criteria

This phase is accepted only if:

- the CLI QA gate document exists;
- the CLI implementation file exists;
- the CLI implementation test exists;
- the CLI contract test exists;
- the runtime file exists;
- the CLI accepts only approved arguments;
- the CLI import boundary is verified;
- blocked operation terms are absent from CLI source;
- JSON output is sanitized;
- text output is sanitized;
- private paths are never printed;
- raw filenames are never printed;
- exit code mapping is verified;
- invalid usage returns sanitized exit code `64`;
- internal errors return sanitized exit code `70`;
- selected input and output folders are not modified by the CLI;
- previous CLI implementation tests still pass;
- previous CLI contract tests still pass;
- previous runtime QA tests still pass;
- repository guards still pass.
