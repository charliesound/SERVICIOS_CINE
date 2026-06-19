# CID Local Media Agent — Real Preflight Implementation Boundary Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.IMPLEMENTATION.BOUNDARY.CONTRACT.V1`

## Objective

This phase defines the exact implementation boundary for a future real preflight implementation before any runtime code is opened.

The phase is documentation/test-only.

It does not implement real preflight runtime behavior. It only defines what a later implementation phase may and may not do.

## Current stable prerequisite

This boundary contract depends on the already closed phase:

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.CONTRACT.QA.GATE.V1`

The previously validated contract remains authoritative.

## Scope

This phase is limited to:

- defining future allowed filesystem checks;
- defining future blocked runtime operations;
- defining fail-closed behavior;
- defining sanitized reporting boundaries;
- defining implementation-readiness constraints for a later phase.

This phase must not change production code, runtime scripts, CLI behavior, scanner behavior, packaging behavior, desktop behavior, SaaS behavior, database behavior, or billing behavior.

## Future implementation boundary

A later implementation phase may implement real preflight only if it remains limited to local filesystem validation.

The allowed future implementation may inspect:

- whether the selected input folder exists;
- whether the selected input folder is a directory;
- whether the selected input folder is locally accessible;
- whether the selected output folder exists or can be safely prepared;
- whether input and output locations remain separated;
- directory traversal depth;
- total media file count;
- accepted extension counts;
- ignored or rejected extension counts;
- approximate total selected media size bucket;
- basic filesystem errors;
- permission errors;
- symlink presence without following symlinks.

The future implementation may use filesystem metadata only.

Filesystem metadata means directory entries, extension strings, directory depth, file sizes, and basic stat-like availability information.

The future implementation must not read media bytes, parse media headers, derive media fingerprints, open streams, inspect codecs, or infer audiovisual content.

## Explicitly allowed future checks

A later real preflight implementation may check:

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
- `PRIVATE_PATHS_NOT_REPORTED`
- `SANITIZED_PAYLOAD_READY`

## Required default limits

The later implementation must preserve the previously defined conservative limits unless a later contract changes them explicitly:

- maximum selected media files: 25;
- maximum total selected media size: 10 GB;
- maximum scan depth: 3;
- accepted extensions: `.mov`, `.mp4`, `.mxf`, `.wav`, `.aif`, `.aiff`;
- symlink following: disabled by default;
- traversal outside selected folder: blocked by default.

## Output separation boundary

The future real preflight must fail closed when input and output locations overlap.

The future implementation must not write reports, temporary files, manifests, caches, thumbnails, indexes, transcripts, subtitles, waveform data, metadata dumps, or sidecar files inside the selected input media folder.

The future implementation may only prepare or validate an output location that is separated from the selected input folder.

## Result states

The future implementation must return exactly one of these result states:

- `PREFLIGHT_PASS`
- `PREFLIGHT_FAIL`
- `PREFLIGHT_BLOCKED`

## Result state meaning

`PREFLIGHT_PASS` means the selected folders and basic filesystem constraints are safe enough for the next human-approved phase.

`PREFLIGHT_FAIL` means the selected folders were reachable but did not satisfy one or more validation checks.

`PREFLIGHT_BLOCKED` means the operation was stopped before validation could continue because a safety, privacy, locality, traversal, permission, symlink, or scope boundary was triggered.

## Sanitized future payload

A future real preflight payload may include only:

- sanitized input folder label;
- sanitized output folder label;
- media file count;
- total selected media size bucket;
- maximum detected scan depth;
- accepted extension counts;
- ignored extension counts;
- rejected extension counts;
- failed check identifiers;
- remediation guidance without private full paths.

## Prohibited future payload

A future real preflight payload must not include:

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

## Explicitly blocked operations

The future real preflight implementation must not perform:

- media decoding;
- stream probing;
- codec probing;
- container probing;
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
- NLE export;
- EDL, XML, AAF, OTIO, or timeline generation;
- upload;
- cloud transfer;
- scanner integration;
- real report generation;
- packaging implementation;
- installer implementation;
- desktop application implementation;
- license activation;
- SaaS integration;
- backend changes;
- frontend changes;
- database changes;
- billing changes.

## Fail-closed requirements

The future implementation must fail closed when:

- the selected input folder is missing;
- the selected input folder is not a directory;
- the selected folder cannot be accessed safely;
- the output folder overlaps with the input folder;
- traversal escapes the selected input folder;
- symlinks would need to be followed;
- the scan depth limit is exceeded;
- the file count limit is exceeded;
- the total selected media size limit is exceeded;
- unsupported file types dominate the selection;
- privacy-safe reporting cannot be guaranteed;
- sanitized output cannot be produced;
- a filesystem error cannot be classified safely.

## Logging boundary

Future logs must remain privacy-safe.

Logs may include:

- phase identifier;
- result state;
- failed check identifiers;
- numeric counts;
- size buckets;
- generic remediation guidance.

Logs must not include:

- raw filenames;
- full folder paths;
- client names;
- project names;
- media-derived metadata;
- media-derived content.

## Non-goals

This phase does not authorize:

- runtime implementation;
- modifying existing CLI behavior;
- modifying scanner behavior;
- integrating with synthetic visible report generation;
- processing real media;
- invoking media tools;
- creating app packaging;
- creating shell launchers;
- creating a desktop app;
- creating installers;
- adding licensing;
- connecting to SaaS systems.

## Acceptance criteria

This phase is accepted only if:

- the contract file exists;
- the contract states that the phase is documentation/test-only;
- the future implementation boundary is limited to filesystem metadata;
- allowed future checks are enumerated;
- blocked operations are enumerated;
- sanitized payload fields are enumerated;
- prohibited payload fields are enumerated;
- fail-closed conditions are enumerated;
- output separation is required;
- no runtime source file is changed by this phase.

## Next phase after this one

Only after this boundary contract is validated, a later phase may open a real preflight implementation readiness gate.

That later phase must still remain conservative and must not automatically authorize media decoding, stream probing, scanner integration, report generation, transcription, translation, sync, subtitles, NLE export, upload, desktop packaging, licensing, SaaS integration, or billing integration.
