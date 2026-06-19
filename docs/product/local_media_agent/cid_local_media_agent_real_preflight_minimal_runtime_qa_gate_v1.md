# CID Local Media Agent — Real Preflight Minimal Runtime QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.QA.GATE.V1`

## Objective

This phase audits the minimal real preflight runtime implementation after its first implementation phase.

This phase is a QA gate.

It does not add runtime features. It does not widen the implementation scope. It does not modify CLI behavior. It does not modify scanner behavior. It does not generate reports. It does not process media content.

The only purpose of this phase is to verify that the existing minimal runtime remains inside the approved contract boundary.

## Runtime under audit

The runtime file under audit is:

`scripts/cid_local_media_agent_real_preflight.py`

## Contract under audit

The governing contract remains:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CONTRACT.V1`

The implementation phase under audit is:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.IMPLEMENTATION.V1`

## QA decision states

This QA gate may produce only these conceptual decisions:

- `QA_PASS`
- `QA_FAIL`
- `QA_BLOCKED`

`QA_PASS` means the current runtime remains inside the approved minimal filesystem-metadata boundary.

`QA_FAIL` means one or more expected checks failed and must be corrected before continuing.

`QA_BLOCKED` means the runtime appears to cross a privacy, media-processing, integration, repository, dependency, or scope boundary.

## Required runtime properties

The runtime must remain:

- local-only;
- fail-closed;
- privacy-safe;
- deterministic for synthetic local fixtures;
- limited to filesystem metadata;
- standard-library-only;
- free of scanner integration;
- free of media tool invocation;
- free of network transfer;
- free of report generation;
- free of database, SaaS, billing, licensing, packaging, installer, and desktop integration.

## Required public surface

The runtime may expose:

- `RealPreflightRequest`;
- `RealPreflightResult`;
- `run_real_preflight_check`.

The only public runtime function authorized by the current contract is:

`run_real_preflight_check`

## Required request fields

The request shape must preserve:

- `input_folder_path`;
- `output_folder_path`;
- `max_file_count`;
- `max_total_size_bytes`;
- `max_scan_depth`;
- `accepted_extensions`;
- `follow_symlinks`.

## Required result fields

The result shape must preserve:

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
- `remediation_items`.

## Required result states

The runtime must preserve exactly these result states:

- `PREFLIGHT_PASS`
- `PREFLIGHT_FAIL`
- `PREFLIGHT_BLOCKED`

## Privacy requirements

The runtime result must not expose:

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
- thumbnail data.

## Filesystem-only inspection requirements

The runtime may inspect only:

- directory existence;
- directory type;
- directory entries;
- file extensions;
- file sizes;
- traversal depth;
- permission availability;
- basic stat-like availability;
- symlink presence without following symlinks.

The runtime must not read file bytes.

The runtime must not parse media headers.

The runtime must not open media streams.

The runtime must not infer audiovisual content.

## Required fail-closed behavior

The runtime must block when:

- input request is invalid;
- input path is missing;
- input path is not a directory;
- selected path is not local;
- output path is not safely preparable;
- output overlaps input;
- symlink following is requested;
- symlinks are detected in the selected input tree;
- scan depth exceeds the configured limit;
- file count exceeds the configured limit;
- total selected size exceeds the configured limit;
- filesystem access cannot be classified safely.

## Required no-write behavior

The runtime must not create, modify, or delete files in:

- the selected input folder;
- the selected output folder.

The runtime must not create:

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

## Import and dependency boundary

The runtime may use standard-library filesystem/path utilities only.

The runtime must not import or invoke:

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

- the QA gate document exists;
- the QA gate states that it does not widen runtime scope;
- the runtime file exists;
- the implementation test file exists;
- the contract file exists;
- the public function boundary is verified;
- request and result shapes are verified;
- result states are verified;
- import boundaries are verified;
- blocked operation terms are absent from runtime source;
- synthetic fixtures prove pass, fail, and blocked behavior;
- synthetic fixtures prove no private path or filename leakage;
- synthetic fixtures prove no writes in selected folders;
- synthetic fixtures prove symlink blocking when supported;
- previous implementation and contract tests still pass;
- repository guards still pass.
