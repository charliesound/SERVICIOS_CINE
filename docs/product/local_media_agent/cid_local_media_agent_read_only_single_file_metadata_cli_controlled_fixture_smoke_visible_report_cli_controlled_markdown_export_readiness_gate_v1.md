# CID Local Media Agent - Read-only Single-file Metadata CLI Controlled Fixture Smoke Visible Report CLI Controlled Markdown Export Readiness Gate V1

## Phase

CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.READINESS.GATE.V1

## Expected result

LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_READINESS_GATE_V1_CLOSED

## Purpose

Doc/test-only readiness gate for a future controlled Markdown export implementation.

This phase prepares the future implementation of --visible-report-output but does not implement it. It freezes the allowed implementation files, controlled output root, expected test coverage, safety boundaries, and closure criteria before any parser or filesystem export behavior is added.

## Current stable base

Base HEAD: 60993d8aabbc113fb9c2d9ec1f559d72f38fc54d

Base stable tag: cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-contract-qa-gate-v1-20260701

## Prior closed contract phase

CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CONTRACT.V1

## Prior closed contract QA phase

CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CONTRACT.QA.GATE.V1

## Prior closed contract artifacts

- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_contract_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_contract.py
- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_contract_qa_gate_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_contract_qa_gate.py

## Existing runtime artifacts

- scripts/local_media_agent/read_only_single_file_metadata_cli.py
- scripts/local_media_agent/read_only_single_file_metadata.py
- scripts/local_media_agent/controlled_fixture_smoke_visible_report_in_memory_integration.py
- scripts/local_media_agent/controlled_fixture_smoke_visible_report_renderer.py

## Future reserved CLI flag

--visible-report-output

## Existing implemented CLI flag

--visible-report-markdown

## Existing JSON flag

--result-json

## Controlled fixture identity

Fixture root: tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1

Target path: tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt

Allowed relative path: media/controlled_plain_text_marker.txt

Fixture id: controlled_plain_text_marker_v1

Expected bytes: 239

Expected SHA256: a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a

Existing baseline support files inside fixture:

- README.md
- manifest.controlled.json

These are baseline fixture support files, not generated report artifacts.

## Future controlled output root

The future implementation must use this controlled output root for tests:

tests/tmp/local_media_agent/controlled_visible_report_exports

The implementation phase may create this directory only inside the future test setup. The CLI must not create arbitrary parent directories.

## Future allowed implementation files

A future implementation gate may modify only:

- scripts/local_media_agent/read_only_single_file_metadata.py

A future implementation gate may add only:

- docs/product/local_media_agent/cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_gate_v1.md
- tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_implementation_gate.py

The public wrapper must remain unchanged:

- scripts/local_media_agent/read_only_single_file_metadata_cli.py

## Future implementation requirements

The future implementation must:

- Add --visible-report-output to the implementation parser only.
- Keep the wrapper delegating to implementation.run_cli(argv).
- Keep --visible-report-output explicit and opt-in.
- Require --visible-report-markdown when --visible-report-output is used.
- Accept exactly one output file path.
- Resolve the output path safely.
- Allow output only inside tests/tmp/local_media_agent/controlled_visible_report_exports for the controlled implementation gate.
- Reject missing parent directories.
- Reject output paths whose parent is a symlink.
- Reject output file paths that are symlinks.
- Reject output paths outside the controlled output root.
- Reject output paths inside tests/fixtures.
- Reject output paths inside tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1.
- Reject output paths that resolve to the repository root.
- Reject Windows-style path strings inside WSL.
- Reject paths with suffix other than .md.
- Reject overwrite by default.
- Use a future explicit overwrite flag only after a separate contract if overwrite is needed.
- Write UTF-8 Markdown text only.
- Write exactly the Markdown currently emitted by --visible-report-markdown.
- Keep stdout behavior deterministic after successful export.
- Keep default status output unchanged.
- Keep --result-json behavior unchanged.
- Keep --visible-report-markdown stdout-only behavior unchanged when no output path is provided.
- Preserve exit code 0 for accepted metadata and valid export.
- Preserve exit code 2 for rejected metadata or rejected output policy.
- Return deterministic rejection without writing when output policy fails.
- Avoid creating report artifacts on rejected paths.
- Avoid writing absolute host-private media paths.
- Preserve redacted paths only.
- Preserve controlled fixture identity.
- Preserve human review placeholders.

## Future implementation test requirements

The future implementation test must cover:

- Parser exposes --visible-report-output.
- Parser still exposes --visible-report-markdown.
- Parser still exposes --result-json.
- Wrapper remains unchanged and does not implement --visible-report-output.
- Default status output remains exact.
- --result-json remains valid JSON and does not create Markdown files.
- --visible-report-markdown remains stdout-only when no output path is provided.
- Valid controlled output path writes one .md file inside the controlled output root.
- Written .md file content exactly matches the in-memory Markdown output.
- Existing output file is rejected by default.
- Missing parent directory is rejected.
- Symlink parent directory is rejected.
- Symlink output file is rejected.
- Output path inside fixture root is rejected.
- Output path inside tests/fixtures is rejected.
- Output path at repository root is rejected.
- Windows-style path string is rejected.
- Non-.md suffix is rejected.
- Rejected output policy leaves no new report file.
- Controlled fixture remains byte-for-byte unchanged.
- pyproject remains unchanged and has no new console script.

## Explicitly forbidden for this readiness phase

- No implementation of --visible-report-output.
- No parser change.
- No CLI behavior change.
- No wrapper behavior change.
- No renderer behavior change.
- No in-memory integration behavior change.
- No report file generation.
- No export behavior.
- No filesystem writes except adding this readiness document and test.
- No persistent output path.
- No subprocess.
- No shell execution.
- No fixture modification.
- No scanner integration.
- No batch processing.
- No recursive product traversal.
- No FFmpeg.
- No ffprobe.
- No pyproject modification.
- No console script registration.
- No SaaS integration.
- No database access.
- No backend changes.
- No frontend changes.
- No installer work.
- No Docker work.
- No Alembic work.
- No Stripe work.
- No AI Jobs work.
- No credits or ledger work.
- No real material.
- No customer material.

## Readiness QA requirements

The readiness test must verify:

- This readiness document exists.
- This readiness document declares phase, result, base HEAD, and base tag.
- Prior contract and contract QA artifacts exist.
- Runtime artifacts exist.
- Future --visible-report-output is declared but not implemented.
- Existing implementation parser does not expose --visible-report-output yet.
- Existing implementation parser still exposes --visible-report-markdown and --result-json.
- Existing wrapper does not expose --visible-report-output.
- Existing wrapper remains a delegating layer.
- Current status, JSON, and Markdown stdout behavior remain unchanged.
- No root report artifacts are created by this readiness phase.
- Controlled fixture remains byte-for-byte unchanged.
- Existing fixture support files remain present.
- The future controlled output root is declared.
- Future allowed implementation files are declared.
- Future implementation requirements are declared.
- Future implementation test requirements are declared.
- Forbidden scope is declared.
- pyproject does not register a console script for the future mode.

## Required validation commands

- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_readiness_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_contract_qa_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_controlled_markdown_export_contract.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_cli_in_memory_report_wrapper_smoke_execution_qa_gate.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_controlled_fixture_smoke_visible_report_contract.py
- pytest -q tests/unit/test_cid_local_media_agent_read_only_single_file_metadata_cli_contract_gate.py
- bash scripts/dev/guard_wsl_repo.sh
- Mandatory PostgreSQL-only regression guard.

## Closure criteria

- New controlled Markdown export readiness test passes.
- Related contract QA, contract, wrapper smoke QA, visible report contract, and CLI contract tests pass.
- Mandatory guards pass.
- Only this readiness document and readiness unit test are staged.
- No forbidden integration boundary is touched.
- Commit is created.
- Stable tag is created.
- main is pushed.
- Tag is pushed.

## Suggested commit

test: add CID Local Media Agent read-only single-file metadata CLI controlled Markdown export readiness gate

## Suggested tag

cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-readiness-gate-v1-20260701
