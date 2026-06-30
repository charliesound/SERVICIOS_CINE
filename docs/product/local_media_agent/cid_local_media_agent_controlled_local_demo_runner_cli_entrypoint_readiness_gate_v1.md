# CID Local Media Agent — controlled local demo runner CLI entrypoint readiness gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.INSTALLED.CONTROLLED.LOCAL.DEMO.RUNNER.CLI.ENTRYPOINT.READINESS.GATE.V1`

## Purpose

This doc/test-only readiness gate prepares a future installed command entry point for the controlled local demo runner.

This phase does not modify `pyproject.toml`.

This phase does not install the future runner command.

This phase validates that the current installed command remains the only project script and that the future runner command name is still absent before implementation.

## Stable baseline

- Baseline HEAD: `0ca48ee058731c28c9783e34b528e3e09bc36654`
- Baseline tag: `cid-dev-stable-local-media-agent-write-enabled-export-cli-package-entrypoint-installed-controlled-local-demo-runner-qa-gate-v1-20260630`
- Current installed command: `cid-local-media-agent-visible-report-write-enabled-export`
- Current installed command path: `/opt/SERVICIOS_CINE/.venv/bin/cid-local-media-agent-visible-report-write-enabled-export`
- Current installed command target: `scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli:main`
- Future runner command candidate: `cid-local-media-agent-controlled-local-demo-runner`
- Future runner command target candidate: `scripts.local_media_agent.cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner:main`
- Runner module path: `scripts/local_media_agent/cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner.py`
- Operational boundary: `DEMO_TECNICA_LOCAL_CONTROLADA_ONLY`

## Current readiness state

At readiness gate closure, the root `pyproject.toml` must still expose exactly one script:

`cid-local-media-agent-visible-report-write-enabled-export`

At readiness gate closure, the future runner command must not yet be present in `pyproject.toml`.

At readiness gate closure, the future runner command must not yet be available in the active `.venv`.

During a later controlled implementation transition, `pyproject.toml` may expose exactly two scripts only if the second entry is:

`cid-local-media-agent-controlled-local-demo-runner = scripts.local_media_agent.cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner:main`

During that later transition, the future runner command may be available in the active `.venv` only if it executes the same controlled local demo runner contract.

The future runner target must already be importable and callable.

The future runner target must already execute the controlled local demo sequence successfully through Python import.

## Future allowed package metadata transition

A later implementation phase may add exactly one additional script entry:

`cid-local-media-agent-controlled-local-demo-runner = scripts.local_media_agent.cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner:main`

That future implementation must preserve the existing write-enabled export command without changing its name or target.

## Future runner command expected behavior

The future installed runner command must expose the same controlled behavior already frozen by the runner QA gate:

- deterministic `--result-json` output.
- optional `--keep-output`.
- default temporary output cleanup.
- fixture-owned temporary output roots only.
- no repository worktree writes.
- one controlled `.txt` artifact in the positive write step.
- one negative path fail-closed validation.
- final status `CONTROLLED_LOCAL_DEMO_RUNNER_VERIFIED`.
- operational boundary `DEMO_TECNICA_LOCAL_CONTROLADA_ONLY`.

## Explicitly blocked in this readiness phase

- Editing `pyproject.toml`.
- Adding the future runner command to `[project.scripts]`.
- Installing the future runner command.
- Editing the runner implementation.
- Editing the current write-enabled export command implementation.
- Changing the current installed command name.
- Changing the current installed command target.
- Client demo.
- Public demo.
- Production execution.
- Installer packaging.
- Real media material.
- Real scanner execution.
- Real ffprobe execution.
- Real FFmpeg execution.
- Network behavior.
- SaaS persistence.
- Backend work.
- Frontend work.
- Database persistence.
- Multi-artifact export.
- Unattended automation.

## QA evidence required for closure

This phase can close only when:

- The new CLI entrypoint readiness gate test passes.
- The runner QA gate test still passes.
- The runner implementation test still passes.
- The controlled local demo script readiness gate test still passes.
- The installed command block still passes.
- The root packaging and transition tests still pass.
- The write-enabled export integration tests still pass.
- Direct runner JSON execution passes.
- At readiness gate closure, the root `pyproject.toml` still has exactly one script entry.
- At readiness gate closure, the future runner command is still absent from the active `.venv`.
- During a later controlled implementation transition, the root `pyproject.toml` may have exactly two script entries: the existing write-enabled export command and the controlled local demo runner command.
- During that later transition, the controlled local demo runner command may be present in the active `.venv` only if direct JSON execution preserves the controlled local demo runner contract.
- WSL guard passes.
- Database regression guard passes.
- Only this CLI entrypoint readiness gate doc and test are staged.

## Expected result

`LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_CLI_ENTRYPOINT_READINESS_GATE_V1_CLOSED`
