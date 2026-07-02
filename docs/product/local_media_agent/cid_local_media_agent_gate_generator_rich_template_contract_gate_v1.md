# CID Local Media Agent — Gate Generator — Rich Template Contract Gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.GATE_GENERATOR.RICH_TEMPLATE.CONTRACT.GATE.V1`

## Expected closure result

`LOCAL_MEDIA_AGENT_GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_GATE_V1_CLOSED`

## Starting state

`LOCAL_MEDIA_AGENT_GATE_GENERATOR_TEMPLATE_QA_PASSED_READY_FOR_ACCELERATED_GATE_USE`

## Target next state

`LOCAL_MEDIA_AGENT_GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_DEFINED_READY_FOR_IMPLEMENTATION_GATE`

## Gate purpose

This contract gate defines the next rich CID gate template capability for the local gate generator.

This gate is documentation and test only.

This gate does not modify the existing generator module.

This gate does not write generated artifacts through the generator.

This gate does not execute shell commands through the generator.

This gate does not auto-commit generated output.

This gate does not auto-tag generated output.

This gate does not auto-push generated output.

This gate does not touch media files.

This gate does not access local operator material.

This gate does not scan folders.

This gate does not inspect real file metadata.

This gate does not execute FFmpeg.

This gate does not execute ffprobe.

This gate does not execute scanner logic.

This gate does not touch SaaS backend.

This gate does not touch SaaS frontend.

This gate does not touch databases.

This gate does not touch Docker.

This gate does not touch Alembic.

This gate does not touch Stripe.

This gate does not touch AI Jobs.

This gate does not touch credits or ledger.

## Source gate generator template QA gate

`CID.LOCAL_MEDIA_AGENT.GATE_GENERATOR.TEMPLATE_QA.GATE.V1`

## Source gate generator template QA result

`LOCAL_MEDIA_AGENT_GATE_GENERATOR_TEMPLATE_QA_GATE_V1_CLOSED`

## Source gate generator template QA state

`LOCAL_MEDIA_AGENT_GATE_GENERATOR_TEMPLATE_QA_PASSED_READY_FOR_ACCELERATED_GATE_USE`

## Source generator

| Field | Value |
| --- | --- |
| `SOURCE_GENERATOR_RECORD_ID` | `gate_generator_001` |
| `SOURCE_GENERATOR_HANDLE` | `LOCAL_MEDIA_AGENT_GATE_GENERATOR_HANDLE_001` |
| `SOURCE_GENERATOR_MODULE_PATH` | `scripts/local_media_agent/gate_generator.py` |
| `SOURCE_GENERATOR_STATUS` | `template_qa_passed` |
| `SOURCE_GENERATOR_CURRENT_SCOPE` | `generic_text_only_gate_generation` |

## Rich template contract record

| Field | Value |
| --- | --- |
| `GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_RECORD_ID` | `gate_generator_rich_template_contract_001` |
| `GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_SOURCE_RECORD_ID` | `gate_generator_001` |
| `GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_SOURCE_HANDLE` | `LOCAL_MEDIA_AGENT_GATE_GENERATOR_HANDLE_001` |
| `GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_SCOPE_STATUS` | `contract_only` |
| `GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_CODE_CHANGE_STATUS` | `no_generator_code_changed` |
| `GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_WRITE_STATUS` | `no_file_write_performed_by_generator` |
| `GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_COMMAND_STATUS` | `no_command_execution_performed_by_generator` |
| `GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_MEDIA_STATUS` | `no_media_access` |
| `GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_SAAS_STATUS` | `no_saas_integration` |
| `GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_VERDICT` | `rich_cid_gate_template_contract_defined_for_future_generator_extension` |

## Required rich template inputs

A future rich CID gate template should support these explicit inputs:

1. `phase_identifier`
2. `phase_slug`
3. `title`
4. `expected_closure_result`
5. `starting_state`
6. `target_next_state`
7. `source_phase_identifier`
8. `source_closure_result`
9. `source_state`
10. `record_id`
11. `record_handle`
12. `source_record_id`
13. `source_record_handle`
14. `doc_artifact_path`
15. `test_artifact_path`
16. `implementation_artifact_paths`
17. `created_artifacts`
18. `required_checks`
19. `forbidden_changes`
20. `safety_boundaries`
21. `positive_assertions`
22. `closure_criteria`
23. `recommended_next_phase`
24. `commit_message`
25. `tag_name`

## Required rich template document sections

A future rich CID gate document should generate these standard sections:

1. Phase
2. Expected closure result
3. Starting state
4. Target next state
5. Gate purpose
6. Source phase
7. Source result
8. Source state
9. Created artifacts
10. Record table
11. Safety boundary
12. Positive assertions
13. Explicitly forbidden changes
14. Required checks before closing
15. Closure
16. Closing state
17. Recommended next phase

## Required rich template test sections

A future rich CID gate test template should generate tests for:

1. Document exists.
2. Phase identifier is present.
3. Expected closure result is present.
4. Starting state is present.
5. Target next state is present.
6. Source phase is present.
7. Source closure result is present.
8. Source state is present.
9. Record ID is present.
10. Record handle is present.
11. Created artifacts are present.
12. Required checks are present.
13. Forbidden changes are present.
14. Safety boundaries are present.
15. Positive assertions are present.
16. Closing state is present.
17. Recommended next phase is present when provided.
18. Windows and mount path fragments are absent from generated docs.
19. Runtime invocation patterns are absent from generated source when source inspection is included.
20. Generator output remains deterministic.

## Standard forbidden changes for rich CID gates

A future rich template should make it easy to include these standard forbidden changes:

1. Touching SaaS backend.
2. Touching SaaS frontend.
3. Touching databases.
4. Touching Docker.
5. Touching Alembic.
6. Touching Stripe.
7. Touching AI Jobs.
8. Touching credits or ledger.
9. Executing FFmpeg.
10. Executing ffprobe.
11. Executing scanner logic.
12. Reading local media files.
13. Scanning local folders.
14. Inspecting real file metadata.
15. Recording real local paths.
16. Recording sensitive filenames.
17. Recording parent folders.
18. Auto-committing generated files.
19. Auto-tagging generated files.
20. Auto-pushing generated files.

## Standard required checks for rich CID gates

A future rich template should support:

1. Current gate test.
2. Previous gate test.
3. Previous chain tests.
4. Generator tests when generator output is used.
5. WSL repo guard script.
6. PostgreSQL-only regression guard script.
7. Explicit git status check.
8. Explicit HEAD verification.
9. Explicit staged file list check.
10. Explicit remote tag verification when closing.

## Expected future public API extension

A future implementation gate may extend the generator with:

1. `RichGateDefinition`
2. `RichGateArtifactPlan`
3. `build_rich_gate_document`
4. `build_rich_gate_test_stub`
5. `build_rich_validation_plan`
6. `build_rich_gate_artifact_plan`
7. `describe_rich_gate_template_contract`

## Acceptance criteria for future implementation

The future rich template implementation must:

1. Preserve the existing generic generator API.
2. Remain deterministic.
3. Return text and structured plans only.
4. Avoid writing files.
5. Avoid modifying existing files.
6. Avoid executing commands.
7. Avoid subprocess execution.
8. Avoid media access.
9. Avoid folder scanning.
10. Avoid SaaS coupling.
11. Avoid database coupling.
12. Avoid Docker coupling.
13. Avoid Alembic coupling.
14. Avoid Stripe coupling.
15. Avoid AI Jobs coupling.
16. Avoid credits or ledger coupling.
17. Preserve current generator tests.
18. Add rich template tests.
19. Keep manual review mandatory.
20. Keep explicit commit and tag closure mandatory.

## Explicitly forbidden in this contract gate

This gate does not authorize:

1. Modifying `scripts/local_media_agent/gate_generator.py`.
2. Auto-writing generated files.
3. Auto-committing generated files.
4. Auto-tagging generated files.
5. Auto-pushing generated files.
6. Executing generated shell commands.
7. Modifying existing runtime code.
8. Modifying existing CLI runtime.
9. Reading local media files.
10. Scanning local folders.
11. Inspecting real file metadata.
12. Probing media.
13. Decoding media.
14. Transcribing media.
15. Executing FFmpeg.
16. Executing ffprobe.
17. Executing scanner logic.
18. Touching SaaS backend.
19. Touching SaaS frontend.
20. Touching databases.
21. Touching Docker.
22. Touching Alembic.
23. Touching Stripe.
24. Touching AI Jobs.
25. Touching credits or ledger.

## Boundary for the next phase

The next conservative phase may implement the rich template extension in the generator.

That future implementation phase may modify `scripts/local_media_agent/gate_generator.py` only if explicitly scoped.

That future implementation phase must preserve all existing generator behavior.

That future implementation phase must remain text-only and non-executing.

## Required checks before closing

Before closing this gate, validate:

1. This gate generator rich template contract gate test.
2. The previous gate generator template QA gate test.
3. The previous gate generator isolated implementation gate test.
4. The previous controlled stat implementation dry-run QA gate test.
5. The previous controlled stat implementation gate test.
6. The previous controlled stat implementation readiness gate test.
7. The previous code skeleton isolated contract QA gate test.
8. The previous code skeleton gate test.
9. The previous code skeleton readiness gate test.
10. The previous real media preflight readiness gate test.
11. The WSL repo guard script.
12. The PostgreSQL-only regression guard script.

## Closure

`LOCAL_MEDIA_AGENT_GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_GATE_V1_CLOSED`

## Closing state

`LOCAL_MEDIA_AGENT_GATE_GENERATOR_RICH_TEMPLATE_CONTRACT_DEFINED_READY_FOR_IMPLEMENTATION_GATE`
