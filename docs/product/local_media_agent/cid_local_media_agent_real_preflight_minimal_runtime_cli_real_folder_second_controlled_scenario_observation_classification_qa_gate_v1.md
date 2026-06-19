# CID Local Media Agent — Second Controlled Scenario Observation Classification QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.OBSERVATION.CLASSIFICATION.QA.GATE.V1`

## Objective

This QA gate validates that the second controlled scenario observation classification contract is present, bounded, and correctly interpreted.

The gate exists to prevent the live observation from being silently downgraded into a clean pass or incorrectly promoted into a final product decision.

## Upstream stable baseline

This QA gate depends on the closed upstream contract:

- Commit: `252d7b4de89cd8ea3374b0e7e4f54223d71cd254`
- Tag: `cid-dev-stable-local-media-agent-real-preflight-minimal-runtime-cli-real-folder-second-controlled-scenario-observation-classification-contract-v1-20260619`
- Phase: `CID.LOCAL_MEDIA_AGENT.REAL.PREFLIGHT.MINIMAL.RUNTIME.CLI.REAL_FOLDER.SECOND.CONTROLLED.SCENARIO.OBSERVATION.CLASSIFICATION.CONTRACT.V1`

## Required upstream artifacts

The QA gate requires the following upstream artifacts to exist:

- `docs/product/local_media_agent/cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_observation_classification_contract_v1.md`
- `tests/unit/test_cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_observation_classification_contract.py`

## Gate decision

The accepted gate result is:

`QA_GATE_PASS_WITH_ACTIVE_OBSERVATION`

This means:

- The controlled scenario remains passed for preflight, privacy, and boundary purposes.
- The observation remains active.
- The observation must remain visible to downstream readiness gates.
- The observation must not be converted into unconditional `PASS`.
- The observation must not be hidden by later QA language.
- Ignored versus rejected product semantics remain undecided.

## Required preserved facts

This QA gate must preserve these facts from the contract:

- `controlled_execution_status=PREFLIGHT_PASS`
- `cli_exit_code=0`
- `leak_check_exit_code=0`
- `media_file_count=2`
- `accepted_extension_counts=.mov:1,.wav:1`
- `ignored_extension_counts={}`
- `rejected_extension_counts=.exe:1,.txt:1`
- `maximum_detected_scan_depth=3`
- `total_selected_media_size_bucket=LE_100MB`

## Required observation interpretation

This QA gate validates that:

1. `.mov` and `.wav` were accepted as media.
2. `.txt` and `.exe` were classified as rejected.
3. `.txt` and `.exe` were not classified as ignored.
4. `ignored_extension_counts` remained empty.
5. This is not a privacy failure.
6. This is not a sanitization failure.
7. This is not an execution boundary failure.
8. This is a classification semantics observation.
9. Product semantics for ignored versus rejected remain undecided.
10. A future product classification contract is required before making client-facing claims.

## Downstream blocking rule

This QA gate blocks any future phase from claiming a clean pass for extension classification unless a later authorized product classification contract explicitly resolves ignored versus rejected behavior.

This QA gate does not block the already validated preflight, privacy, leak-check, and boundary result.

It only blocks misrepresentation of the classification semantics.

## Out-of-scope actions

This QA gate does not authorize:

- Runtime code changes.
- Scanner behavior changes.
- FFmpeg or ffprobe execution.
- Media probing or decoding.
- Real client media.
- Personal data processing.
- Report generation.
- Transcription.
- Translation.
- Subtitle generation.
- Synchronization.
- DaVinci Resolve, Avid, NLE, export, or upload workflows.
- SaaS application changes.
- Database changes.
- Docker changes.
- Alembic changes.
- Stripe, AI Jobs, credits, or ledger changes.

## Completion criteria

This phase is complete only when:

- This QA gate document exists.
- The QA gate unit test exists.
- The upstream observation classification contract document exists.
- The upstream observation classification contract test exists.
- The QA gate validates `QA_GATE_PASS_WITH_ACTIVE_OBSERVATION`.
- The QA gate validates that `PASS_WITH_OBSERVATION` remains active.
- The QA gate validates that `.txt` and `.exe` remain rejected, not ignored.
- The QA gate validates that ignored versus rejected product semantics remain undecided.
- The QA gate validates that runtime and product changes are out of scope.
- The staged diff contains only this QA gate document and its unit test.
- Repository guards pass.
