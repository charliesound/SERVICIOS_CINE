# CID Local Media Agent — Real Preflight Minimal Runtime CLI Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.CONTRACT.V1`

## Objective

This phase defines the contract for a future CLI wrapper around the already implemented minimal real preflight runtime.

This phase is documentation/test-only.

It does not create CLI runtime code. It does not create a shell launcher. It does not modify the existing real preflight runtime. It does not modify scanner behavior. It does not generate reports. It does not process media content. It does not add packaging, installer, desktop, licensing, SaaS, backend, frontend, database, billing, upload, or cloud behavior.

The only purpose of this phase is to define how a future CLI may safely call the existing minimal runtime without widening scope.

## Current stable prerequisite

This contract depends on the already closed phase:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.QA.GATE.V1`

The current runtime under the previous QA gate is:

`scripts/cid_local_media_agent_real_preflight.py`

The future CLI must call that runtime boundary and must not bypass it.

## Future CLI target file

A later implementation phase may create this file:

`scripts/cid_local_media_agent_real_preflight_cli.py`

This current phase must not create that file.

## Future CLI test file

A later implementation phase may create this test file:

`tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli.py`

This current phase must not create that file.

## Future CLI phase

A later implementation phase, if opened, should be:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.IMPLEMENTATION.V1`

That later phase must start from a clean repository precheck and must include tests before or with implementation.

## Future CLI purpose

The future CLI may do only this:

- receive an input folder argument;
- receive an output folder argument;
- optionally receive conservative limit flags already supported by the runtime request shape;
- build a `RealPreflightRequest`;
- call `run_real_preflight_check`;
- print a sanitized result payload;
- return an exit code mapped from the result status.

## Future CLI allowed arguments

The future CLI may accept only:

- `--input-folder`;
- `--output-folder`;
- `--max-file-count`;
- `--max-total-size-bytes`;
- `--max-scan-depth`;
- `--accepted-extension`;
- `--no-follow-symlinks`;
- `--format`.

The default output format must be JSON.

The only allowed future output formats are:

- `json`;
- `text`.

The text format must remain sanitized and must not include private paths or raw filenames.

## Future CLI forbidden arguments

The future CLI must not accept arguments that imply processing or integration beyond preflight.

Forbidden future arguments include:

- media probing flags;
- media decoding flags;
- scanner flags;
- report generation flags;
- transcription flags;
- translation flags;
- subtitle flags;
- sync flags;
- waveform flags;
- thumbnail flags;
- timecode flags;
- NLE export flags;
- upload flags;
- cloud transfer flags;
- packaging flags;
- installer flags;
- licensing flags;
- SaaS flags;
- backend flags;
- frontend flags;
- database flags;
- billing flags.

## Future CLI result mapping

The future CLI must map runtime statuses to exit codes as follows:

- `PREFLIGHT_PASS` -> exit code `0`;
- `PREFLIGHT_FAIL` -> exit code `2`;
- `PREFLIGHT_BLOCKED` -> exit code `3`;
- invalid CLI usage -> exit code `64`;
- unexpected internal error before sanitized output can be produced -> exit code `70`.

The future CLI must not expose private paths or raw filenames in error output.

## Future CLI output payload

The future CLI JSON output may include only:

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

## Future CLI output must not include

The future CLI output must not include:

- full private paths;
- raw filenames;
- client names;
- project names;
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
- thumbnail data;
- absolute paths;
- relative source paths;
- environment variables;
- user account names;
- hostnames.

## Future CLI stderr boundary

The future CLI may write only sanitized diagnostics to stderr.

Allowed stderr content:

- generic usage errors;
- generic validation failure labels;
- result status;
- exit code;
- generic remediation messages.

Forbidden stderr content:

- private paths;
- raw filenames;
- stack traces by default;
- environment dumps;
- local usernames;
- hostnames;
- media-derived metadata;
- media-derived content.

## Future CLI runtime boundary

The future CLI must call:

`run_real_preflight_check(request: RealPreflightRequest)`

The future CLI must not duplicate traversal logic outside the runtime.

The future CLI may parse arguments and convert them into a request object.

The future CLI may serialize the sanitized result object.

The future CLI must not import scanner modules, synthetic visible report modules, media probing wrappers, transcription modules, translation modules, sync modules, subtitle modules, NLE export modules, SaaS modules, database modules, billing modules, licensing modules, upload modules, network clients, or process execution helpers.

## Future CLI no-write boundary

The future CLI must not write inside:

- the selected input folder;
- the selected output folder.

The future CLI must not create:

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

## Future CLI local-only boundary

The future CLI must remain local-only.

The future CLI must not:

- upload files;
- transfer files to cloud services;
- call remote APIs;
- send telemetry;
- connect to SaaS services;
- connect to databases;
- invoke desktop apps;
- invoke NLE apps;
- invoke media tools.

## Future CLI import boundary

The future CLI may use only standard-library modules required for:

- argument parsing;
- JSON serialization;
- exit code handling;
- importing the approved runtime module.

A later implementation contract must enumerate the exact allowed imports before implementation.

## Operations still blocked

This contract does not authorize:

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

- the CLI contract document exists;
- the phase is documentation/test-only;
- the future CLI target file is named;
- the future CLI test file is named;
- the future CLI implementation phase is named;
- allowed CLI arguments are enumerated;
- forbidden CLI arguments are enumerated;
- result-to-exit-code mapping is enumerated;
- sanitized CLI output payload is enumerated;
- prohibited CLI output fields are enumerated;
- stderr privacy boundary is enumerated;
- CLI runtime boundary is enumerated;
- no-write behavior is required;
- local-only behavior is required;
- import boundaries are defined;
- blocked operations remain blocked;
- the existing runtime file remains present;
- the existing runtime QA gate remains present;
- no CLI source file is created by this phase.
