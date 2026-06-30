# CID Local Media Agent — write-enabled export CLI package entrypoint installed controlled local demo script readiness gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.INSTALLED.CONTROLLED.LOCAL.DEMO.SCRIPT.READINESS.GATE.V1`

## Purpose

This doc/test-only readiness gate prepares the future implementation of a controlled local demo script for the installed package entry point.

This phase does not create the demo runner. It only defines the allowed future scope, execution sequence, safety boundaries, and implementation constraints.

## Stable baseline

- Baseline HEAD: `0cc56b03d5a5ba8c0247dda0a2e67844de8ebdd9`
- Baseline tag: `cid-dev-stable-local-media-agent-write-enabled-export-cli-package-entrypoint-installed-command-operational-summary-qa-gate-v1-20260630`
- Accepted command name: `cid-local-media-agent-visible-report-write-enabled-export`
- Accepted installed command path: `/opt/SERVICIOS_CINE/.venv/bin/cid-local-media-agent-visible-report-write-enabled-export`
- Accepted package target: `scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli:main`
- Controlled write authorization token: `CONTROLLED_WRITE_ENABLED_EXPORT_FIXTURE_ONLY`
- Controlled dry-run authorization token: `CONTROLLED_DRY_RUN_ACCEPTED`
- Operational boundary: `DEMO_TECNICA_LOCAL_CONTROLADA_ONLY`

## Future demo runner candidate

The future controlled local demo runner may be introduced only in a later implementation phase.

Allowed future candidate path:

`scripts/local_media_agent/cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner.py`

At readiness gate closure, this path must not exist yet. In a later controlled implementation transition, this same path may exist only if it remains limited to the approved controlled local technical demo runner scope.

## Future allowed demo sequence

The future demo runner may orchestrate only the following deterministic sequence:

1. Installed command availability check.
2. Installed `--help` invocation.
3. Installed `--dry-run --result-json` invocation.
4. Installed controlled write execution creating exactly one `.txt` artifact.
5. One basic negative path proving fail-closed behavior without creating an unauthorized artifact.
6. Final visible summary suitable for a human-supervised local technical demo.

## Required future output boundary

The future demo runner must use only fixture-owned temporary output roots.

The future demo runner must not write inside the repository worktree.

The future demo runner must clean or isolate temporary artifacts clearly enough for repeatable local technical validation.

## Explicitly allowed future evidence

The future demo runner may print:

- command path.
- command help summary.
- dry-run JSON summary.
- controlled write JSON summary.
- created controlled artifact path.
- created controlled artifact SHA.
- basic negative path rejection summary.
- final local technical demo status.

## Explicitly blocked in this readiness phase

- Creating the demo runner.
- Editing runtime implementation.
- Editing package metadata.
- Editing the installed command target.
- Running real scanner code.
- Running real media probing tools.
- Running FFmpeg.
- Running ffprobe.
- Running network behavior.
- Adding SaaS persistence behavior.
- Backend work.
- Frontend work.
- Installer work.
- Client demo.
- Public demo.
- Production execution.
- Real media material.
- Multi-artifact export.
- Overwrite behavior.
- Unattended automation.

## Future implementation constraints

The future implementation phase must preserve:

- local WSL execution only.
- active `.venv` execution only.
- fixture-owned temporary output roots only.
- controlled visible report text fixtures only.
- deterministic JSON inspection.
- exactly one controlled `.txt` write in the positive write step.
- fail-closed negative path behavior.
- no real media access.
- no scanner execution.
- no ffprobe execution.
- no FFmpeg execution.
- no network access.
- no SaaS or database access.

## Prior closed gates required before future implementation

This readiness gate depends on the following closed gates:

- Installed invocation QA gate.
- Installed dry-run QA gate.
- Installed write execution controlled QA gate.
- Installed write execution negative paths QA gate.
- Installed command operational summary QA gate.

## Closure validation

This phase can close only when:

- The controlled local demo script readiness gate test passes.
- The installed command operational summary QA gate test still passes.
- The installed invocation, dry-run, write execution, and negative paths tests still pass.
- The root packaging metadata controlled implementation test still passes.
- The package entrypoint transition gates still pass.
- The write-enabled export integration tests still pass.
- WSL guard passes.
- Database regression guard passes.
- Only this controlled local demo script readiness gate doc and test are staged.
- At readiness gate closure, the future demo runner candidate path still does not exist.
- During a later controlled implementation transition, if the future demo runner candidate path exists, it must preserve the same controlled local technical demo boundary.
- The target tag is absent locally and remotely before tag creation.

## Expected result

`LOCAL_MEDIA_AGENT_WRITE_ENABLED_EXPORT_CLI_PACKAGE_ENTRYPOINT_INSTALLED_CONTROLLED_LOCAL_DEMO_SCRIPT_READINESS_GATE_V1_CLOSED`
