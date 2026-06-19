# CID Local Media Agent — Real Preflight Minimal Runtime Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CONTRACT.V1`

## Objective

This phase defines the contract for a future minimal real preflight runtime implementation.

This phase is documentation/test-only.

It does not create runtime code. It does not create a real preflight module. It does not create a real preflight function. It does not modify CLI behavior. It does not modify scanner behavior. It does not generate real reports. It does not process real media.

The only purpose of this phase is to define the exact future target file, public function, request shape, result shape, test fixture boundaries, fail-closed behavior, and blocked operations for a later implementation phase.

## Current stable prerequisite

This contract depends on the already closed and valid phase:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.IMPLEMENTATION.READINESS.GATE.V1`

The valid stable tag for that prerequisite is:

`cid-dev-stable-local-media-agent-real-preflight-implementation-readiness-gate-v1-postgresql-only-recovery-20260619`

The earlier non-recovery readiness tag must not be used as stable for this contract.

## Future target runtime file

A later implementation phase may create this runtime file:

`scripts/cid_local_media_agent_real_preflight.py`

This current phase must not create that file.

## Future target implementation test file

A later implementation phase may create this implementation test file:

`tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime.py`

This current phase must not create that file.

## Future public function

The later implementation phase may expose one public function:

`run_real_preflight_check(request: RealPreflightRequest) -> RealPreflightResult`

No other public runtime entry point is authorized by this contract.

The function must remain local-only, synchronous or internally deterministic, side-effect limited, privacy-safe, and fail-closed.

## Future request shape

The future request object must contain only these conceptual fields:

- `input_folder_path`;
- `output_folder_path`;
- `max_file_count`;
- `max_total_size_bytes`;
- `max_scan_depth`;
- `accepted_extensions`;
- `follow_symlinks`.

Default future values must be:

- `max_file_count`: 25;
- `max_total_size_bytes`: 10737418240;
- `max_scan_depth`: 3;
- `accepted_extensions`: `.mov`, `.mp4`, `.mxf`, `.wav`, `.aif`, `.aiff`;
- `follow_symlinks`: false.

The request may hold local private paths in memory only because the user has selected local folders. Those paths must never be copied into logs, reports, serialized result payloads, telemetry, cloud payloads, SaaS payloads, or user-visible diagnostic text.

## Future result shape

The future result object must contain only these conceptual fields:

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

The future result object must not contain:

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

## Future result states

The future implementation must return exactly one of these result states:

- `PREFLIGHT_PASS`
- `PREFLIGHT_FAIL`
- `PREFLIGHT_BLOCKED`

## Future check identifiers

The later implementation may emit only these check identifiers:

- `INPUT_FOLDER_EXISTS`
- `INPUT_FOLDER_IS_DIRECTORY`
- `INPUT_FOLDER_LOCAL_ONLY`
- `INPUT_FOLDER_ACCESSIBLE`
- `OUTPUT_FOLDER_PREPARABLE`
- `INPUT_OUTPUT_SEPARATED`
- `SCAN_DEPTH_WITHIN_LIMIT`
- `MEDIA_FILE_COUNT_WITHIN_LIMIT`
- `TOTAL_MEDIA_SIZE_WITHIN_LIMIT`
- `ACCEPTED_EXTENSIONS_PRESENT`
- `REJECTED_EXTENSIONS_REPORTED`
- `SYMLINKS_NOT_FOLLOWED`
- `TRAVERSAL_DID_NOT_ESCAPE_INPUT`
- `PRIVATE_PATHS_NOT_REPORTED`
- `SANITIZED_PAYLOAD_READY`

If an unknown filesystem condition is encountered, the future implementation must classify it as blocked rather than inventing a permissive result.

## Future allowed filesystem behavior

The later implementation may use only local filesystem metadata:

- directory existence;
- directory type;
- directory entries;
- extension strings;
- file sizes;
- traversal depth;
- permission availability;
- basic stat-like availability;
- symlink detection without following symlinks.

The later implementation must not read media bytes.

The later implementation must not parse media headers.

The later implementation must not derive media fingerprints.

The later implementation must not open media streams.

The later implementation must not inspect codecs.

The later implementation must not infer audiovisual content.

## Future fixture boundary

The later implementation tests may use only synthetic local fixtures created inside test temporary directories.

Allowed future fixtures:

- temporary input folders;
- temporary output folders;
- empty placeholder files;
- tiny text placeholder files with accepted media-like extensions;
- generic synthetic filenames;
- nested synthetic folders up to and beyond the configured depth limit;
- symlink fixtures only when the platform supports them safely and tests do not follow them;
- permission-error simulation only when deterministic and local.

Forbidden future fixtures:

- real client media;
- real production media;
- real project folders;
- real camera files;
- real sound files;
- real location folders;
- real person names;
- real client names;
- real project names;
- copied user filenames;
- media samples from external sources;
- cloud-mounted media;
- network-mounted media.

## Future fail-closed behavior

The later implementation must return `PREFLIGHT_BLOCKED` when:

- input folder path is missing;
- input folder is not a directory;
- input folder cannot be accessed safely;
- selected folder is not local;
- output folder cannot be prepared safely;
- input and output folders overlap;
- traversal escapes the selected input folder;
- symlink following would be required;
- scan depth exceeds the configured limit;
- file count exceeds the configured limit;
- total selected media size exceeds the configured limit;
- sanitized result payload cannot be produced;
- privacy-safe reporting cannot be guaranteed;
- an unknown filesystem error cannot be classified safely.

The later implementation may return `PREFLIGHT_FAIL` only when the filesystem is reachable and safely classified, but one or more validation checks fail without triggering a safety boundary.

The later implementation may return `PREFLIGHT_PASS` only when every required check passes and the result payload remains sanitized.

## Future output separation rule

The later implementation must not write inside the selected input folder.

The later implementation must not create reports, caches, manifests, indexes, sidecars, transcripts, subtitles, thumbnails, waveform data, or temporary files inside the selected input folder.

The later implementation may validate or prepare an output folder only when it is separated from the input folder.

## Future logging rule

The later implementation may log only:

- phase identifier;
- result status;
- failed check identifiers;
- numeric counts;
- size buckets;
- generic remediation identifiers.

The later implementation must not log:

- full private paths;
- raw filenames;
- client names;
- project names;
- media-derived metadata;
- media-derived content.

## Future import boundary

The future runtime module must not import:

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
- upload modules.

The future runtime module may use only standard library filesystem/path utilities unless a later contract explicitly authorizes another dependency.

## Operations still blocked

This contract does not authorize:

- media decoding;
- stream probing;
- codec probing;
- container probing;
- ffprobe on real files;
- ffmpeg on real files;
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
- real report generation;
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

## Required later implementation phase name

The later implementation phase, if opened, should be:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.IMPLEMENTATION.V1`

That later phase must start from a clean repository precheck and must include tests before or with implementation.

## Acceptance criteria

This phase is accepted only if:

- the minimal runtime contract document exists;
- the phase is documentation/test-only;
- the future target runtime file is named;
- the future implementation test file is named;
- the future public function is named;
- the future request shape is enumerated;
- the future result shape is enumerated;
- the future result states are preserved;
- the future check identifiers are enumerated;
- local filesystem metadata is the only allowed inspection source;
- future fixtures are synthetic and local-only;
- fail-closed behavior is enumerated;
- output separation is required;
- logging remains privacy-safe;
- import boundaries are enumerated;
- blocked operations remain blocked;
- no runtime source file is created by this phase.
