# CID Local Media Agent — write-enabled export CLI package entrypoint installed invocation QA gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.INSTALLED.INVOCATION.QA.GATE.V1`

## Purpose

This doc/test-only QA gate records that the root package entry point can be made available inside the controlled WSL `.venv` by editable installation and that the installed command exposes the expected help surface.

This phase does not modify runtime, does not use real media, does not run scanner behavior, and does not add client-facing behavior.

## Stable baseline

- Baseline HEAD: `8263448844844f43dd49dc77a27d3d85a877e5eb`
- Baseline tag: `cid-dev-stable-local-media-agent-write-enabled-export-cli-root-packaging-metadata-controlled-implementation-v1-20260630`
- Accepted command name: `cid-local-media-agent-visible-report-write-enabled-export`
- Accepted target: `scripts.local_media_agent.ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_write_enabled_export_cli:main`

## Controlled installed invocation evidence

The command was not available in the active `.venv` before editable installation.

After controlled editable installation with dependency installation disabled, the command became available at:

`/opt/SERVICIOS_CINE/.venv/bin/cid-local-media-agent-visible-report-write-enabled-export`

The installed command help output exposed the expected options:

- `--visible-report-text`
- `--controlled-output-root`
- `--write-authorization`
- `--result-json`
- `--dry-run`

The generated `cid_local_media_agent.egg-info/` folder was removed from the repository worktree after the editable installation check.

The installed command remained available from the active `.venv` after removing the generated repository-local egg-info folder.

## Required invariants

This QA gate requires:

- Root `pyproject.toml` exists.
- Exactly one package script entry exists for the accepted command.
- The script target points to the accepted module and callable.
- The nested `ai-dubbing-legal-studio/pyproject.toml` remains untouched by the Local Media Agent command.
- No root `setup.py` exists.
- No root `setup.cfg` exists.
- No repository-local `cid_local_media_agent.egg-info/` folder remains.
- The active `.venv` exposes the accepted command after editable installation.

## Explicitly blocked in this phase

- Editing runtime implementation.
- Editing the accepted write primitive.
- Running real scanner code.
- Running real media probing tools.
- Running network behavior.
- Adding SaaS persistence behavior.
- Backend work.
- Frontend work.
- Installer work.
- Client demo.
- Public demo.
- Production execution.
- Real media material.

## Closure validation

This phase can close only when:

- The installed invocation QA gate test passes.
- The root packaging metadata controlled implementation test still passes.
- The updated package entrypoint readiness gate test still passes.
- The updated target selection gate test still passes.
- The updated root packaging metadata contract test still passes.
- The updated root packaging metadata readiness gate test still passes.
- The updated existence transition compatibility gate test still passes.
- The corrected QA gate test still passes.
- The accepted controlled implementation test still passes.
- WSL guard passes.
- Database regression guard passes.
- Only this installed invocation QA gate doc and test are staged.
- The target tag is absent locally and remotely before tag creation.

## Expected result

`LOCAL_MEDIA_AGENT_WRITE_ENABLED_EXPORT_CLI_PACKAGE_ENTRYPOINT_INSTALLED_INVOCATION_QA_GATE_V1_CLOSED`
