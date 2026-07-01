# CID Local Media Agent — Controlled Local Demo Runner Demo-to-Pilot Roadmap Gate V1

## Gate identity

- Phase: `CID.LOCAL_MEDIA_AGENT.CONTROLLED.LOCAL.DEMO.RUNNER.DEMO.TO.PILOT.ROADMAP.GATE.V1`
- Expected closure result: `LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_DEMO_TO_PILOT_ROADMAP_GATE_V1_CLOSED`
- Gate type: documentation and QA only.
- Product area: CID Local Media Agent.
- Current baseline: controlled local demo runner.
- Roadmap target: future real pilot readiness, not pilot execution.

## Purpose

This gate creates the internal roadmap between the current controlled technical demo and a future controlled pilot.

The current state proves that the installed export command and controlled local demo runner can produce a deterministic evidence artifact in a fixture-owned temporary output root. This gate does not expand runtime capability. It only defines the ordered technical and operational gaps that must be closed before any real pilot can be considered.

The goal is to avoid a dangerous jump from "we can show a controlled demo" to "we can process real material for a client". Those are different maturity levels.

## Closure statement

`LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_DEMO_TO_PILOT_ROADMAP_GATE_V1_CLOSED` means that the roadmap from controlled demo to future pilot has been documented and covered by QA.

It does not mean that a pilot is approved.

It does not mean that real media can be used.

It does not mean that external installation can proceed.

It does not mean that scanner, media probing, synchronization, transcription, translation, packaging, support, pricing, legal handling, or production use is complete.

## Current approved capability

The approved capability remains limited to the controlled local demo runner chain:

1. Installed export command is available.
2. Installed controlled local demo runner is available.
3. Runner can show help.
4. Runner can emit structured JSON evidence.
5. Runner can preserve temporary output only when explicitly requested.
6. Runner can clean fixture-owned temporary output.
7. Runner verifies the controlled text artifact.
8. Runner confirms stable artifact name, bytes, and digest.
9. Runner remains demo-only.
10. Runner does not process real media.

## Roadmap principle

The roadmap must preserve this rule:

> A controlled demo can inform a future pilot, but it must not silently become a pilot.

Every step toward a pilot must have an explicit gate, a narrow scope, and a stop condition.

## Roadmap stages

### Stage 1 — Controlled synthetic-to-controlled-media readiness

Objective: move from a deterministic text artifact to controlled non-client media fixtures, without touching client material.

Required future work:

- Define approved non-client fixture media.
- Define fixture ownership.
- Define retention and cleanup rules.
- Define allowed file sizes and formats.
- Define what metadata may be extracted.
- Define what output may be written.
- Define how evidence is recorded.
- Define how operator mistakes are contained.

Blocked until a dedicated gate exists:

- Any real production material.
- Any client footage or sound.
- Any uncontrolled folder scan.
- Any recursive processing of user media.
- Any public demonstration using non-approved files.

### Stage 2 — Real media preflight architecture

Objective: define how the local agent will inspect real media safely before real probing is enabled.

Required future work:

- File boundary policy.
- Input path allowlist policy.
- Output path policy.
- Metadata minimization policy.
- Failure mode policy.
- Redaction policy.
- Operator-visible report contract.
- Dry-run behavior.
- No-overwrite behavior.
- Local-only evidence handling.

Blocked until a dedicated gate exists:

- Actual media probing in client folders.
- Broad scanner execution.
- Batch processing.
- Background watch mode.
- Any cloud transfer.

### Stage 3 — ffprobe and FFmpeg capability gates

Objective: introduce external media tooling only after command safety, path safety, timeout policy, output redaction, and fixture boundaries are closed.

Required future work:

- Command construction without shell.
- Timeout rules.
- Environment restrictions.
- Output size limits.
- Error classification.
- Redacted stdout and stderr policy.
- Deterministic fixture tests.
- Operator failure guidance.
- Evidence capture without exposing sensitive path data.

Blocked until a dedicated gate exists:

- Production decoding.
- Unbounded probing.
- Client media probing.
- Use on uncontrolled folders.
- Any automatic repair or transcoding.

### Stage 4 — Scanner capability gates

Objective: move from a single controlled artifact to a controlled local scanner path.

Required future work:

- Scan root validation.
- Recursion limits.
- File type policy.
- Hidden/system file policy.
- Symlink policy.
- Permission failure behavior.
- Partial result behavior.
- Report aggregation.
- Stop-on-risk behavior.
- Operator review before any write.

Blocked until a dedicated gate exists:

- Full folder automation.
- Client folder execution.
- Writes near source media.
- Destructive operations.
- Large production tree scanning.

### Stage 5 — Human-visible report maturity

Objective: make results understandable to a producer, production manager, school operator, or post team.

Required future work:

- Report sections for operator and stakeholder.
- Safety boundary display.
- Technical evidence display.
- Limitations display.
- Recommended next action.
- No-promise language.
- Export format policy.
- Naming policy.
- Evidence retention policy.

Blocked until a dedicated gate exists:

- Client-facing reports.
- Public demo reports.
- Paid deliverables.
- Reports implying final product completeness.

### Stage 6 — Packaging and local installation readiness

Objective: prepare future local installation without confusing the current command-line demo with a finished installer.

Required future work:

- Platform matrix.
- Dependency checks.
- Installer boundary.
- Uninstall and cleanup behavior.
- Version display.
- Local logs.
- Crash handling.
- Update policy.
- Offline grace policy if licensing is later introduced.
- Operator support policy.

Blocked until a dedicated gate exists:

- External installation.
- Client device deployment.
- Signed installer claims.
- Support commitments.
- License activation promises.

### Stage 7 — Privacy, legal, and pilot agreement readiness

Objective: define the minimum documentation before any pilot uses real material.

Required future work:

- Written permission.
- Confidentiality handling.
- Data boundary.
- Local-only statement.
- Retention and deletion plan.
- Who can access outputs.
- What evidence can be shared.
- What is excluded.
- Stop condition.
- Contact owner at client side.

Blocked until a dedicated gate exists:

- Processing real client material.
- Accepting sensitive material.
- Recording client-specific results in uncontrolled documents.
- Sharing pilot outputs without approval.

### Stage 8 — Pilot execution readiness

Objective: only after prior roadmap stages exist, decide whether a small real pilot can be opened.

Required future work:

- Approved scope.
- Approved risk register.
- Approved evidence plan.
- Approved exit criteria.
- Approved operator.
- Approved environment.
- Approved material class.
- Approved stop/rollback procedure.
- Approved communication plan.
- Approved final review.

Blocked until a dedicated gate exists:

- Real pilot launch.
- Live client workflow dependency.
- Commercial promise.
- Price commitment.
- Contract commitment.
- Public reference.

## Technical gaps before pilot

The following technical gaps remain open:

1. Real media fixture policy.
2. Safe media probing implementation.
3. External tool execution safety.
4. Scanner runtime readiness.
5. Human-readable report maturity.
6. Controlled output retention.
7. Packaging readiness.
8. Local installation readiness.
9. Privacy boundary implementation.
10. Pilot evidence automation.
11. Operator recovery workflow.
12. Regression coverage for controlled media fixtures.

## Product gaps before pilot

The following product gaps remain open:

1. Pilot value hypothesis per stakeholder.
2. Pilot success metric.
3. Pilot stop condition.
4. Client-side responsible person.
5. Stakeholder feedback loop.
6. Scope approval.
7. Risk approval.
8. Evidence approval.
9. Exit decision approval.
10. Commercial non-promise wording.

## Explicit non-authorizations

This gate does not authorize:

- Real pilot.
- Real client material.
- Public demo.
- External installation.
- Client device deployment.
- Scanner runtime.
- ffprobe runtime against real client media.
- FFmpeg runtime against real client media.
- Background processing.
- Network transfer.
- SaaS integration.
- Database access.
- Installer work.
- Pricing.
- Contracting.
- Support obligations.
- Production delivery.
- Claims of final product readiness.

## Ordered next gates after this roadmap

The roadmap recommends that future work move in this order:

1. Controlled media fixture policy gate.
2. Controlled real-media preflight contract gate.
3. Controlled external tool execution readiness gate.
4. Controlled scanner runtime readiness gate.
5. Controlled human-visible report maturity gate.
6. Controlled packaging readiness gate.
7. Controlled privacy and pilot agreement readiness gate.
8. Controlled pilot execution gate.

No later gate should skip the safety and scope boundaries defined here.

## Operator guidance

When discussing the roadmap with a stakeholder, the operator may say:

> The current demo proves a controlled local evidence chain. It does not yet process your real material. The roadmap defines what must be closed before we can responsibly consider a pilot.

The operator must not say:

> We can run this on your production folders now.

The operator must not say:

> This is ready as a finished product.

The operator must not say:

> Send me your material and I will test it.

## Acceptance checklist

This roadmap is acceptable only if:

- It preserves the current demo boundary.
- It lists technical gaps before pilot.
- It lists product gaps before pilot.
- It defines ordered future gates.
- It blocks real client material.
- It blocks external installation.
- It blocks scanner and external media tooling until dedicated gates exist.
- It blocks support, pricing, contract, and public claims.
- It remains documentation and QA only.
- It keeps the repository scope limited to this document and its QA test.

## Final closure

If this gate closes, the only approved result is:

`LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_DEMO_TO_PILOT_ROADMAP_GATE_V1_CLOSED`

The next recommended phase is a controlled media fixture policy gate, not a real pilot.
