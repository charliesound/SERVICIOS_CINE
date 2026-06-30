# CID Local Media Agent — write-enabled export CLI package entrypoint installed controlled local demo runner QA gate V1

## Phase

`CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.INSTALLED.CONTROLLED.LOCAL.DEMO.RUNNER.QA.GATE.V1`

## Purpose

This doc/test-only QA gate freezes the operational contract of the controlled local demo runner already implemented for the installed write-enabled export CLI.

This phase does not modify the runner implementation. It validates and documents the runner behavior as a controlled internal technical demo surface.

## Stable baseline

- Baseline HEAD: `41e29338223645ee3427766f1bfebf001d931344`
- Baseline tag: `cid-dev-stable-local-media-agent-write-enabled-export-cli-package-entrypoint-installed-controlled-local-demo-runner-implementation-v1-20260630`
- Runner path: `scripts/local_media_agent/cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner.py`
- Runner test path: `tests/unit/test_cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner.py`
- Installed command: `cid-local-media-agent-visible-report-write-enabled-export`
- Installed command path: `/opt/SERVICIOS_CINE/.venv/bin/cid-local-media-agent-visible-report-write-enabled-export`
- Controlled write authorization token: `CONTROLLED_WRITE_ENABLED_EXPORT_FIXTURE_ONLY`
- Controlled dry-run authorization token: `CONTROLLED_DRY_RUN_ACCEPTED`
- Operational boundary: `DEMO_TECNICA_LOCAL_CONTROLADA_ONLY`

## Runner contract frozen by this QA gate

The runner must execute only the following controlled sequence:

1. Installed command availability check.
2. Installed command help invocation.
3. Installed dry-run result JSON invocation.
4. Installed controlled write of exactly one `.txt` artifact.
5. Installed negative path fail-closed validation.
6. Deterministic summary generation.

## Required runner status

The successful JSON summary must expose:

- `status=CONTROLLED_LOCAL_DEMO_RUNNER_VERIFIED`
- `operational_boundary=DEMO_TECNICA_LOCAL_CONTROLADA_ONLY`
- `output_root_removed=true` by default.
- `artifact_available_after_runner=false` by default.
- `dry_run.verification_status=DRY_RUN_ONLY`
- `write.verification_status=VERIFIED`
- `negative_path.verification_status=REJECTED`
- a 64-character SHA256 for the controlled artifact generated during the positive write step.
- a positive artifact byte count.
- the expected ordered step list.

## Required output policy

By default, the runner must remove the fixture-owned temporary output root after the run.

When `--keep-output` is used, the runner may keep the temporary output root only under the fixture-owned temporary area.

The runner must not write inside the repository worktree.

The runner must not overwrite an existing controlled artifact.

## Required safety flags

The successful JSON summary must keep these safety values:

- `demo_runner_only=true`
- `fixture_owned_output_root=true`
- `writes_inside_repository=false`
- `real_media_used=false`
- `scanner_used=false`
- `ffprobe_used=false`
- `ffmpeg_used=false`
- `network_used=false`
- `saas_used=false`
- `database_used=false`
- `installer_used=false`
- `client_demo=false`
- `public_demo=false`
- `single_artifact_write=true`
- `overwrite_used=false`

## Explicitly blocked

This QA gate does not authorize:

- client demo.
- public demo.
- production execution.
- installer packaging.
- real media material.
- real scanner execution.
- real ffprobe execution.
- real FFmpeg execution.
- network behavior.
- SaaS persistence.
- backend work.
- frontend work.
- database persistence.
- multi-artifact export.
- unattended automation.

## QA evidence required for closure

This phase can close only when:

- The new controlled local demo runner QA gate test passes.
- The existing runner implementation test still passes.
- The controlled local demo script readiness gate test still passes.
- The installed command block still passes.
- The root packaging and transition tests still pass.
- The write-enabled export integration tests still pass.
- Direct runner JSON execution passes.
- The runner `--keep-output` QA path is inspected and cleaned by the test.
- WSL guard passes.
- Database regression guard passes.
- Only this QA gate doc and test are staged.

## Expected result

`LOCAL_MEDIA_AGENT_WRITE_ENABLED_EXPORT_CLI_PACKAGE_ENTRYPOINT_INSTALLED_CONTROLLED_LOCAL_DEMO_RUNNER_QA_GATE_V1_CLOSED`
