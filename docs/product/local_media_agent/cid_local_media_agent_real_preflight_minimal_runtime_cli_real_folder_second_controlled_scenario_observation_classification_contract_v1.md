# CID Local Media Agent — Second Controlled Scenario Observation Classification Contract v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.OBSERVATION.CLASSIFICATION.CONTRACT.V1`

## Objective

This contract formalizes the live observation from the second controlled scenario after the post-execution boundary QA gate.

The observation is intentionally preserved as:

`PASS_WITH_OBSERVATION`

This phase does not change product behavior, runtime behavior, scanner behavior, extension policy, media handling, report generation, synchronization, transcription, translation, subtitles, NLE export, or any SaaS surface.

## Upstream stable baseline

The upstream stable baseline for this contract is:

- Commit: `6b34c8e565c08e9a771a5d25e4da352ca1356347`
- Tag: `cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-second-controlled-scenario-post-execution-boundary-qa-gate-v1-20260619`
- Phase: `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.POST.EXECUTION.BOUNDARY.QA.GATE.V1`

## Preserved controlled execution result

The observed controlled execution remains:

- `controlled_execution_status=PREFLIGHT_PASS`
- `cli_exit_code=0`
- `leak_check_exit_code=0`
- `media_file_count=2`
- `accepted_extension_counts=.mov:1,.wav:1`
- `ignored_extension_counts={}`
- `rejected_extension_counts=.exe:1,.txt:1`
- `maximum_detected_scan_depth=3`
- `total_selected_media_size_bucket=LE_100MB`

## Classification observation

The second controlled scenario showed that:

- `.mov` was accepted as media.
- `.wav` was accepted as media.
- `.txt` was classified as rejected.
- `.exe` was classified as rejected.
- `ignored_extension_counts` remained empty.
- `.txt` and `.exe` were not classified as ignored.

This is a real observation from the controlled scenario record. It is not a failure of privacy, sanitization, or execution boundary guarantees.

## Contract decision

For this phase, the classification behavior is documented as an observation only.

This contract explicitly does not decide that rejected is the final product behavior for all non-media files.

This contract explicitly does not decide that ignored is the final product behavior for all non-media files.

This contract explicitly does not convert `PASS_WITH_OBSERVATION` into unconditional `PASS`.

A future product classification contract is required before changing or freezing the product semantics of ignored versus rejected extension handling.

## Required downstream interpretation

Downstream phases must preserve the following interpretation:

1. The second controlled scenario passed its privacy and boundary checks.
2. The extension classification result still carries an active observation.
3. The active observation concerns classification semantics, not media leakage.
4. The active observation must be visible in any future readiness gate that depends on this scenario.
5. The active observation must not be silently normalized into a clean pass.
6. Product behavior for ignored versus rejected extensions remains undecided.
7. Any runtime change to classification behavior requires a separate authorized implementation phase.
8. Any client-facing claim about ignored or rejected extension behavior requires a separate product contract.

## Non-goals

This phase does not authorize:

- Real client media.
- Personal data processing.
- Scanner execution.
- Media probing or decoding.
- FFmpeg or ffprobe execution.
- Report generation.
- Transcription.
- Translation.
- Subtitle generation.
- Synchronization.
- DaVinci Resolve, Avid, NLE, export, or upload workflows.
- SaaS application changes.
- Database changes.
- Billing, credit, or ledger changes.
- Any runtime code change.

## Safety boundary

This contract remains documentation and unit-test only.

It may only validate that the observation is captured, bounded, and not misrepresented.

It must not add product functionality.

It must not make the Local Media Agent appear more complete than the controlled evidence supports.

## Completion criteria

This phase is complete only when:

- The contract document exists.
- The contract test exists.
- The contract test validates the active `PASS_WITH_OBSERVATION` state.
- The contract test validates the preserved execution metrics.
- The contract test validates that ignored versus rejected product semantics remain undecided.
- The contract test validates that runtime changes are out of scope.
- The staged diff contains only this document and its unit test.
- The repository guards pass.
