# CID Local Media Agent — Controlled Local Demo Runner Failure Modes & Recovery Gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.INSTALLED.CONTROLLED.LOCAL.DEMO.RUNNER.FAILURE.MODES.RECOVERY.GATE.V1`

## Expected closure result

`LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_FAILURE_MODES_RECOVERY_GATE_V1_CLOSED`

## Purpose

This gate defines the internal failure-mode and recovery protocol for the controlled local demo runner.

The goal is not to add features. The goal is to prevent improvisation during a private technical demo when the operator sees an unexpected state.

This document turns the previous operator runbook into a controlled stop-and-recover procedure. It helps the operator explain limits clearly, preserve trust, and avoid over-promising.

## Scope

Allowed in this gate:

- Documentation.
- QA test for the documentation.
- Internal operator language.
- Failure-mode classification.
- Recovery decision tree.
- Demo stop policy.
- Evidence policy.
- Manual cleanup policy for preserved output.

Forbidden in this gate:

- Runtime implementation.
- `pyproject.toml` changes.
- Command changes.
- Scanner changes.
- Real media inspection.
- Real probe execution.
- Real transcoding or decoding.
- Network calls.
- SaaS integration.
- Database work.
- Installer work.
- Backend work.
- Frontend work.
- Customer material.
- Public demo material.
- Production claims.

## Baseline already achieved

The controlled local demo runner line already has:

1. Installed export command.
2. Installed controlled local demo runner command.
3. Operator smoke path.
4. Internal evidence pack.
5. Demo narrative.
6. Operator runbook.

This failure-mode gate sits after those gates. It does not replace them.

## Stable demo invariants

The operator must treat the following as fixed invariants of the current controlled demo:

- The artifact name is `controlled_visible_report.controlled.txt`.
- The stable SHA256 is `277bca892ae1591c3dec5c36935a0fc0489d31ed0796c3e3703f8c63b3ec3c6f`.
- The stable byte count is `167`.
- The demo is controlled.
- The demo is local.
- The demo uses fixture-only write authorization.
- The demo does not inspect real client media.
- The demo does not run real probe tooling.
- The demo does not run transcoding or decoding.
- The demo does not call SaaS services.
- The demo does not write into the repository.
- The demo must not overwrite existing output.

## Operator principle

When a demo failure happens, the operator must not improvise a technical explanation.

The correct response is:

1. Stop the demo flow.
2. Name the observed failure in plain language.
3. State that the current demo is intentionally controlled.
4. Avoid product promises.
5. Capture the evidence if safe.
6. Recover only through documented steps.
7. Resume only if the recovery returns to a known safe state.
8. Otherwise close the session cleanly.

Exact stop rule: resume only if the recovery returns to a known safe state.
## Failure severity levels

### Level 0 — Cosmetic issue

Examples:

- Terminal line wrapping.
- Prompt pasted twice.
- Help output is longer than expected.
- Operator opens the wrong terminal tab but no command has failed.

Allowed recovery:

- Reorient the terminal.
- Repeat the planned command.
- Continue if no state has changed.

Operator language:

> This is only an operator display issue. The controlled demo state has not changed, so I will continue with the planned command sequence.

### Level 1 — Local execution setup issue

Examples:

- Virtual environment not active.
- Command not found.
- Current directory is not `/opt/SERVICIOS_CINE`.
- Operator is not inside WSL Ubuntu.
- Repository path cannot be found.

Allowed recovery:

- Return to `/opt/SERVICIOS_CINE`.
- Activate `.venv`.
- Re-run the command availability check.
- Do not modify packaging or runtime during the demo.

Stop condition:

- If the command remains unavailable after activating `.venv`, stop the demo.

Operator language:

> The demo depends on the installed controlled command entrypoint. I will not patch anything during the session. I will either recover through the prepared environment or stop here.

### Level 2 — Controlled runner output mismatch

Examples:

- JSON cannot be parsed.
- Artifact name does not match `controlled_visible_report.controlled.txt`.
- SHA256 does not match the stable expected value.
- Byte count does not match `167`.
- Expected controlled marker is absent.
- Keep-output mode does not preserve the temporary output as expected.

Allowed recovery:

- Do not edit the artifact.
- Do not regenerate by hand.
- Re-run the exact same command once from a clean temporary output root.
- If mismatch repeats, stop the demo.

Stop condition:

- Any repeated SHA, byte, artifact-name, or marker mismatch must stop the demo.

Operator language:

> This demo uses deterministic evidence. If the hash or byte count does not match, I stop instead of explaining it away.

### Level 3 — Cleanup issue

Examples:

- Default mode leaves an output directory unexpectedly.
- Keep-output mode preserves output but manual cleanup fails.
- Temporary output root cannot be deleted.
- File permissions prevent cleanup.

Allowed recovery:

- Do not force-delete outside the known temporary output root.
- Verify the path is outside the repository.
- Remove only the controlled temporary output directory.
- If cleanup is uncertain, stop and record the path.

Stop condition:

- Any uncertainty about the path being cleaned must stop the demo.

Operator language:

> Cleanup is part of the safety story. I will only remove the known controlled temporary output path. If I cannot prove the path is safe, I stop.

### Level 4 — Repository safety issue

Examples:

- Worktree is dirty before applying a doc/test gate.
- Unexpected staged file appears.
- Sensitive file is staged.
- A guard fails.
- Target tag already exists.
- HEAD or origin/main does not match the expected baseline.

Allowed recovery:

- Do not commit.
- Do not tag.
- Do not push.
- Inspect status.
- Unstage only files from the current attempted gate if needed.
- Ask for a deliberate next decision before continuing.

Stop condition:

- Any unexpected staged path or guard failure stops the closure.

Operator language:

> The repo safety gate is more important than closing the phase. I will not commit, tag, or push while the staged state is not exactly expected.

### Level 5 — Scope breach

Examples:

- Runtime file changes appear.
- Packaging file changes appear.
- Scanner file changes appear.
- Real probe or transcoding work is introduced.
- SaaS, database, installer, backend, or frontend files appear.
- Real customer media appears in the flow.

Allowed recovery:

- Stop immediately.
- Do not stage the breach.
- Do not commit the breach.
- Record the unexpected path or action.
- Return to the last stable tag before planning a new phase.

Operator language:

> This is outside the current controlled demo gate. I am stopping here because expanding scope during a demo would create false confidence.

## Decision tree

Use this sequence when something fails:

1. Did the failure change repository state?
   - Yes: stop closure path and inspect status.
   - No: continue to step 2.

2. Did the failure involve command availability or environment setup?
   - Yes: recover only through `.venv`, WSL, and `/opt/SERVICIOS_CINE` checks.
   - No: continue to step 3.

3. Did the failure involve runner JSON, SHA, bytes, artifact name, marker, or output cleanup?
   - Yes: re-run once from a clean temporary output root, then stop if repeated.
   - No: continue to step 4.

4. Did the failure involve guard, staged scope, tag, or baseline mismatch?
   - Yes: do not commit, tag, or push.
   - No: continue to step 5.

5. Is the operator unsure what happened?
   - Yes: stop.
   - No: continue only if the state returns to the documented safe path.

## Recovery commands that are allowed during an internal repo closure

The operator may use these command classes during a doc/test-only gate closure:

- `git status --short`
- `git diff --cached --name-only`
- `git rev-parse HEAD`
- `git rev-parse origin/main`
- `git describe --exact-match --tags HEAD`
- `git ls-remote --tags origin <target-tag>`
- `python -m py_compile <target-test>`
- `python -m pytest <target-test> -q`
- `bash scripts/dev/guard_wsl_repo.sh`
- the repository PostgreSQL-only regression guard

These commands are part of the repo safety shell, not part of the product runtime.

## Recovery commands that are not allowed during the demo

The operator must not use recovery commands that mutate product behavior, packaging, runtime, or deployment during the demo.

Not allowed:

- Editing runtime modules.
- Editing packaging configuration.
- Installing new dependencies to make the demo pass.
- Running real probe tooling on customer files.
- Running transcoding or decoding tools.
- Starting SaaS services.
- Running database migrations.
- Touching installer files.
- Using real customer media.
- Patching command entrypoints live.

## Evidence policy

If a failure happens, the operator may record:

- The exact command that failed.
- The terminal output.
- `git status --short` if repository state is involved.
- The expected SHA256 and byte count.
- whether the failure was recovered or the demo was stopped.
- The reason for stopping.

The operator must not record:

- Customer media paths.
- Customer file names.
- Secrets.
- Environment files.
- Database files.
- Private keys.
- Public marketing claims.

## How to explain a stop to a producer, school, or potential client

Use direct language:

> I am stopping here because this is a controlled technical demo. The point is to show the safety discipline, not to fake a product state that is not closed yet.

Then clarify:

- The current demo validates the controlled local reporting chain.
- It does not yet claim final product readiness.
- It does not yet process real client media in this gate.
- It does not yet demonstrate full scanner, real probe tooling, transcription, sync, installer, licensing, or SaaS integration.
- The stop protects the project and the client relationship.

## What not to say

Do not say:

- This already processes a real production folder.
- This already handles all codecs.
- This is already a final installer.
- This is already customer-ready.
- This already performs real media analysis.
- This already does full sync, transcription, translation, and edit preparation.
- This can be sold as a complete product today.

## What can be said safely

The operator may say:

- This is a controlled local technical demo.
- The current chain demonstrates installed commands and deterministic controlled output.
- The artifact evidence is stable through SHA256 and byte count.
- The default behavior cleans up temporary output.
- Keep-output mode can preserve evidence for inspection.
- Safety gates prevent accidental scope expansion.
- Real media work is a later, explicit phase.
- Productization remains separate from this controlled demo.

## Closure criteria

This gate can be closed only if:

- The failure-mode document exists.
- The QA test exists.
- The document declares the phase name.
- The document declares the expected closure result.
- The document includes severity levels 0 through 5.
- The document includes stop conditions.
- The document includes recovery rules.
- The document includes evidence policy.
- The document includes safe client-facing language.
- The document includes what not to say.
- The document preserves the controlled demo limits.
- The staged scope contains only this document and its QA test.
- The previous demo narrative and operator runbook gates still pass.
- WSL/repo guard passes.
- PostgreSQL-only regression guard passes.

## Final status token

When closed, the phase status is:

`LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_FAILURE_MODES_RECOVERY_GATE_V1_CLOSED`
