# CID Local Media Agent — Visible Report Renderer Input Output Contract QA Gate v1

## Phase

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.RENDERER.INPUT_OUTPUT.CONTRACT.QA.GATE.V1`

## Objective

This phase validates the previously closed visible report renderer input/output contract before any renderer implementation readiness or renderer implementation work is allowed.

This phase is documentation/test-only.

It does not implement renderer code, generator code, loader code, template engine code, runtime code, scanner changes, SaaS integration, HTML report, PDF report, DOCX report, XLSX report, CSV report, Markdown report artifact, rendered report, filesystem write behavior, ffprobe execution, ffmpeg execution, media probing, media processing, subtitles, NLE export, installer behavior, licensing behavior, billing behavior, storage behavior, or real media processing.

## Upstream Input Output Contract

Phase:

`CID.LOCAL_MEDIA_AGENT.SYNTHETIC.END_TO_END.LOCAL_DEMO_REPORT.VISIBLE.REPORT.RENDERER.INPUT_OUTPUT.CONTRACT.V1`

Document:

`docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_input_output_contract_v1.md`

Unit test:

`tests/unit/test_cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_input_output_contract.py`

Commit:

`a5de7cb`

Tag:

`cid-dev-stable-local-media-agent-synthetic-end-to-end-local-demo-report-visible-report-renderer-input-output-contract-v1-20260618`

## Related Inputs

Implementation readiness gate:

`docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_implementation_readiness_gate_v1.md`

Renderer QA gate:

`docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_contract_qa_gate_v1.md`

Renderer contract:

`docs/product/local_media_agent/cid_local_media_agent_synthetic_end_to_end_local_demo_report_visible_report_renderer_contract_v1.md`

Synthetic fixture:

`tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json`

## Gate Status

`QA_GATE_READY_FOR_INTERNAL_VALIDATION`

`OPENCODE_AUDIT_PASS_RECORDED_BEFORE_FINAL_CLOSURE`

Final closure is blocked until internal validation passes and OpenCode audit is run, unless a documented human override is added.

Allowed final decisions:

- `PASS_WITH_OPENCODE_AUDIT`
- `PASS_WITH_HUMAN_OVERRIDE_AND_RECORDED_REASON`
- `FAIL_REQUIRES_INPUT_OUTPUT_CONTRACT_REVISION`

## OpenCode Role

OpenCode is allowed only as a read-only external auditor.

OpenCode must not edit files, stage files, commit, tag, push, create artifacts, create reports, implement renderer code, implement generator code, implement loader code, implement template engine code, implement runtime code, create filesystem write behavior, modify fixtures, modify scanner code, modify SaaS code, execute ffprobe, execute ffmpeg, inspect real media, process media, create HTML, create PDF, create DOCX, create XLSX, create CSV, create Markdown report artifact, create subtitles, create NLE exports, touch backend, touch frontend, touch database, touch Alembic, touch Docker, touch billing, touch licensing, touch installers, or touch storage.

## OpenCode Audit Brief

Audit read-only:

- input/output QA gate remains documentation/test-only
- input/output contract remains documentation/test-only
- Markdown is selected only as the first future controlled output format
- no Markdown artifact is created
- no renderer, generator, loader, template engine, runtime, scanner change, SaaS integration, or visible report artifact is created or authorized
- no HTML, PDF, DOCX, XLSX, CSV, rendered report, subtitles, NLE export, ffprobe execution, ffmpeg execution, media probing, media processing, or real media processing is created or authorized
- synthetic fixture is not modified
- local-only and local-first privacy are preserved
- Spanish-first stakeholder readability is preserved
- synthetic-only demonstration is preserved
- mandatory human review is preserved
- CID is presented as assistive and not substitutive
- exact input sections and required fields are defined
- render order is locked
- output path policy is safe
- artifact naming policy avoids real identifiers
- redaction policy blocks sensitive values
- safe overwrite is false by default
- render options are allowlisted and unsafe render options are blocked
- no false claims of real synchronization, transcription, translation, export, analysis, delivery validation, or postproduction completion
- risks before moving toward a minimal renderer implementation phase

OpenCode must return PASS or FAIL, concise findings, required fixes if any, and explicit confirmation that it did not edit files.

## Internal QA Requirements

The QA gate validates:

- input/output contract exists
- input/output contract references commit a5de7cb
- input/output contract is documentation/test-only
- Markdown future output is selected but not created
- exact future input sections are defined
- required input fields are defined
- input must be synthetic, sanitized, and validated
- render order is locked
- output path policy blocks unsafe targets
- artifact naming avoids real identifiers
- redaction policy blocks sensitive values
- safe overwrite is false by default
- allowed render options are defined
- blocked render options are defined
- claims policy blocks unsafe real-capability claims
- human review policy is visible
- renderer implementation is blocked in this phase
- artifact creation is blocked in this phase
- scanner changes are blocked
- SaaS integration is blocked
- ffprobe and ffmpeg execution are blocked
- real media processing is blocked
- fixture JSON is not modified
- OpenCode audit is required before final closure

## Fixture Integrity

The fixture file must not be modified:

`tests/fixtures/local_media_agent/synthetic_demo_report_fixture_v1.json`

Any staged change to that fixture is a failure.

## QA Status

`QA_GATE_READY_FOR_INTERNAL_VALIDATION`

Commit is blocked until internal validation passes.

Final closure is blocked until OpenCode audit is run or a documented human override is added.

## OpenCode Audit Result

`OPENCODE_AUDIT_RESULT=PASS`

Auditor mode:

`READ_ONLY_EXTERNAL_AUDITOR`

OpenCode findings:

- Input/output QA gate remains documentation/test-only and read-only audit scoped.
- Input/output contract remains documentation/test-only.
- Markdown is selected only as the first future controlled output format; no Markdown artifact is created.
- No renderer, generator, loader, template engine, runtime, scanner change, SaaS integration, visible report artifact, filesystem write behavior, or report creation is authorized.
- HTML, PDF, DOCX, XLSX, CSV, rendered report, subtitles, NLE export, ffprobe/ffmpeg execution, media probing, media processing, and real media processing remain blocked.
- Fixture JSON is not modified.
- Local-only/local-first privacy, Spanish-first readability, synthetic-only demo scope, mandatory human review, and assistive/not-substitutive CID framing are preserved.
- Exact input sections and required fields are defined.
- Render order is locked.
- Output path policy blocks unsafe targets.
- Artifact naming avoids real identifiers.
- Redaction policy blocks sensitive values.
- Safe overwrite is false by default.
- Render options are allowlisted and unsafe render options are blocked.
- No false claims were found for real synchronization, transcription, translation, export, analysis, delivery validation, or postproduction completion.
- No blocking risk was found before moving toward a minimal renderer implementation phase, provided the future implementation remains gated and follows this contract.

Required fixes:

`NONE`

Audit integrity confirmation:

- OpenCode did not edit files.
- OpenCode did not stage files.
- OpenCode did not commit, tag, or push.
- OpenCode did not create artifacts or reports.
- OpenCode did not implement renderer, generator, loader, runtime, or template engine code.
- OpenCode did not create filesystem write behavior.
- OpenCode did not execute ffprobe or ffmpeg.
- OpenCode did not inspect or process real media.

Human decision:

`PASS_WITH_OPENCODE_AUDIT`

Final closure may proceed only after tests and guards are rerun.
