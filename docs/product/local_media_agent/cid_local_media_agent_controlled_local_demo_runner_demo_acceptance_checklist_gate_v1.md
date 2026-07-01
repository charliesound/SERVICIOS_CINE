# CID Local Media Agent — Controlled Local Demo Runner Demo Acceptance Checklist Gate V1

## Gate identity

- Phase: `CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.INSTALLED.CONTROLLED.LOCAL.DEMO.RUNNER.DEMO.ACCEPTANCE.CHECKLIST.GATE.V1`
- Result token when closed: `LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_DEMO_ACCEPTANCE_CHECKLIST_GATE_V1_CLOSED`
- Scope: documentation and QA only.
- Purpose: define the minimum internal acceptance checklist before the controlled technical demo is shown to a producer, film school, distributor, post house, or other potential stakeholder.

## Why this gate exists

The previous gates proved that the controlled local demo runner can be executed, explained, evidenced, operated, and recovered from expected failure conditions. This gate defines the final internal acceptance boundary before using that demo in a controlled conversation with a potential external stakeholder.

The acceptance boundary is intentionally conservative. Passing this checklist does not mean the Local Media Agent is a finished product. It only means the current controlled technical demo is acceptable to show as an internal/product-development demonstration under explicit limits.

## Non-negotiable framing

The operator must state that the demonstration is:

- a controlled technical demo;
- local-only;
- based on controlled fixture output;
- intended to demonstrate command packaging, reproducible evidence, operator flow, and safe temporary-output behavior;
- not a production workflow;
- not a public sales demo;
- not a client-real-media workflow;
- not a scanner-real workflow;
- not a real metadata-extraction workflow;
- not a transcription, sync, edit, delivery, or SaaS workflow;
- not evidence that the future full product is already complete.

The operator must not present the demo as if it already scans real rushes, reads camera originals, analyzes real media, performs real conforming, produces legal delivery, handles client files, or integrates with CID SaaS.

## Acceptance decision

The demo is accepted for controlled external conversation only if all acceptance groups below are PASS.

If any group fails, the correct decision is:

`DEMO_ACCEPTANCE_BLOCKED`

If all groups pass, the correct decision is:

`CONTROLLED_DEMO_ACCEPTED_FOR_LIMITED_STAKEHOLDER_CONVERSATION`

This acceptance decision does not authorize public launch, client onboarding, paid deployment, installer delivery, real material processing, or product claims beyond the current controlled demo.

## Acceptance group A — repository and environment readiness

The operator must verify the following before showing the demo:

1. The repo is the canonical WSL repo: `/opt/SERVICIOS_CINE`.
2. The active shell is WSL Ubuntu.
3. The virtual environment is active.
4. The worktree is clean before applying or running closure checks.
5. `HEAD` and `origin/main` match the expected stable baseline for the current gate.
6. The target tag for this gate is absent locally and remotely before closure.
7. No nested repo copy is being used.
8. No Windows path is used for repo operations.
9. No private configuration file, backup, DB artifact, frontend, backend, installer, SaaS module, runtime module, scanner module, or command packaging file is modified by this gate.

Acceptance result for group A:

- PASS only if all checks are true.
- FAIL if any operator cannot explain or verify the repo and environment state.

## Acceptance group B — installed commands readiness

The following installed commands must be available inside the repo virtual environment:

- `/opt/SERVICIOS_CINE/.venv/bin/cid-local-media-agent-visible-report-write-enabled-export`
- `/opt/SERVICIOS_CINE/.venv/bin/cid-local-media-agent-controlled-local-demo-runner`

The operator must be able to run:

```bash
cid-local-media-agent-controlled-local-demo-runner --help
cid-local-media-agent-controlled-local-demo-runner --result-json
cid-local-media-agent-controlled-local-demo-runner --result-json --keep-output
```

Acceptance result for group B:

- PASS only if the installed commands exist and the runner commands execute successfully.
- FAIL if the operator must edit code, reinstall packaging, change pyproject, or patch runtime to make the demo work.

## Acceptance group C — stable evidence readiness

The controlled artifact evidence must match the known stable values:

- artifact name: `controlled_visible_report.controlled.txt`
- SHA256: `277bca892ae1591c3dec5c36935a0fc0489d31ed0796c3e3703f8c63b3ec3c6f`
- bytes: `167`

The operator must explain the evidence in simple terms:

- the artifact is intentionally tiny and deterministic;
- the hash proves the exact content is stable;
- the byte count proves the output size is stable;
- stability matters because the demo should be repeatable and auditable;
- the evidence does not prove real media scanning or real production readiness.

Acceptance result for group C:

- PASS only if artifact name, SHA, and byte count match.
- FAIL if evidence differs, is missing, is ambiguous, or cannot be explained without overclaiming.

## Acceptance group D — output cleanup readiness

The operator must demonstrate both output modes:

1. Default run cleans temporary output automatically.
2. `--keep-output` preserves the controlled output for inspection.
3. The preserved output is manually cleaned afterwards.
4. The repo remains free of generated output artifacts.

Acceptance result for group D:

- PASS only if automatic cleanup and manual cleanup are both verified.
- FAIL if generated output remains in the repo, if the operator cannot identify where output was written, or if cleanup requires improvisation.

## Acceptance group E — operator narrative readiness

The operator must follow the existing demo narrative and runbook. The minimum narrative order is:

1. State the current demo boundary.
2. Show `--help` to establish operator-facing usage.
3. Run `--result-json` to show structured, auditable output.
4. Explain the artifact name, SHA, and bytes.
5. Run `--result-json --keep-output` to show preserved inspection mode.
6. Explain cleanup.
7. Re-state current limits.
8. Invite feedback on product value, not on nonexistent production features.

Acceptance result for group E:

- PASS only if the operator can explain the demo in the approved order.
- FAIL if the operator starts promising real scanner, real media extraction, real sync, real transcription, delivery automation, SaaS orchestration, billing, licensing, or installer readiness.

## Acceptance group F — recovery readiness

The operator must know the recovery policy from the previous failure modes gate.

If any of the following happens, the operator stops the demo and does not improvise:

- command not found;
- virtual environment not active;
- JSON output missing or invalid;
- artifact name, SHA, or byte count mismatch;
- preserved output cannot be cleaned;
- repo is dirty before or after the demo;
- guard fails;
- target tag already exists;
- any unexpected file enters the staged diff;
- stakeholder asks for a real-client-material demonstration in the same session.

The operator may say:

> This is a controlled technical demo. I am going to stop here rather than imply a capability that is not yet part of this build.

Acceptance result for group F:

- PASS only if stop conditions are known before the demo.
- FAIL if the operator attempts to repair live, edit code, change repo state, use real material, or keep talking as if the failure was irrelevant.

## Acceptance group G — stakeholder suitability

This demo is suitable for:

- a producer evaluating whether the product direction is useful;
- a film school evaluating teaching or workflow value;
- a postproduction supervisor evaluating future local workflow possibilities;
- an internal team member checking repeatability;
- a trusted early stakeholder who understands controlled technical demos.

This demo is not suitable for:

- public launch;
- paid customer onboarding;
- contractual delivery;
- real project processing;
- benchmark comparison;
- security certification;
- press announcement;
- investor-style product-complete claim;
- installer handoff;
- unattended operation by a non-technical user.

Acceptance result for group G:

- PASS only if the audience is appropriate for a controlled technical demo.
- FAIL if the audience expects a finished product, a paid deployment, or real footage processing.

## Acceptance group H — claim discipline

Approved claims:

- The demo command is installed in the controlled development environment.
- The runner produces stable JSON evidence.
- The controlled artifact has stable SHA and byte count.
- The operator can demonstrate automatic cleanup and preserved output inspection.
- The current work is a foundation for a future local media workflow product.
- The workflow is being built with explicit boundaries and QA gates.

Forbidden claims:

- The product is finished.
- The product processes client footage today.
- The scanner is real in this demo.
- Real ffprobe or FFmpeg processing is demonstrated here.
- Transcription, sync, subtitle generation, rough edit, delivery, or SaaS integration is active in this demo.
- The demo can be installed by a client now.
- A stakeholder can use this build on a real production.
- The current demo proves commercial deployment readiness.

Acceptance result for group H:

- PASS only if claim discipline is maintained.
- FAIL if any forbidden claim is used.

## Acceptance group I — evidence pack readiness

Before showing the demo, the operator must know where the existing evidence and documentation live:

- operator evidence pack gate;
- demo narrative gate;
- operator runbook gate;
- failure modes and recovery gate;
- this acceptance checklist gate.

The operator must be able to summarize each layer:

- evidence pack: what the demo proves technically;
- narrative: how to explain the demo;
- runbook: how to execute the demo;
- recovery: when to stop and how to recover;
- acceptance checklist: when the demo is allowed to be shown.

Acceptance result for group I:

- PASS only if the operator can identify the documentation chain.
- FAIL if the demo is executed without knowing the supporting docs.

## Acceptance group J — closure validation readiness

This gate may close only after:

- the new QA test passes;
- the previous failure modes gate test passes;
- the previous operator runbook gate test passes;
- the previous demo narrative gate test passes;
- the previous operator evidence pack gate test passes;
- WSL/repo guard passes;
- PostgreSQL-only regression guard passes;
- staged scope contains exactly this document and its QA test;
- commit, tag, and push complete successfully;
- final verification shows HEAD, origin/main, and the tag on the same commit.

Acceptance result for group J:

- PASS only if all closure checks pass.
- FAIL if any check fails or if any extra file is staged.

## Final acceptance checklist

The operator must confirm:

- `[ ]` I can state that this is a controlled technical demo.
- `[ ]` I can show `--help` without confusion.
- `[ ]` I can run `--result-json` and explain the JSON evidence.
- `[ ]` I can run `--result-json --keep-output` and explain preserved output.
- `[ ]` I can verify artifact name, SHA, and byte count.
- `[ ]` I can explain automatic cleanup and manual cleanup.
- `[ ]` I know when to stop the demo.
- `[ ]` I know which claims are approved.
- `[ ]` I know which claims are forbidden.
- `[ ]` I will not use real client material.
- `[ ]` I will not imply real scanner, transcription, sync, delivery, installer, SaaS, or DB capability.
- `[ ]` I will ask for stakeholder feedback on value, priorities, and pain points, not pretend that unfinished features already exist.

## Gate decision rule

If every acceptance group is PASS:

`CONTROLLED_DEMO_ACCEPTED_FOR_LIMITED_STAKEHOLDER_CONVERSATION`

If any acceptance group is FAIL:

`DEMO_ACCEPTANCE_BLOCKED`

The only valid closure result for this gate is:

`LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_DEMO_ACCEPTANCE_CHECKLIST_GATE_V1_CLOSED`

## Scope integrity statement

This gate is documentation and QA only. It does not modify runtime behavior, command packaging, scanner logic, media processing, ffprobe/FFmpeg integration, SaaS/backend/frontend modules, DB behavior, installer logic, licensing, billing, customer data handling, or any real material workflow.
