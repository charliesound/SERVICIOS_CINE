# CID Local Media Agent - controlled local demo runner operator smoke execution gate V1

Phase:
CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.INSTALLED.CONTROLLED.LOCAL.DEMO.RUNNER.OPERATOR.SMOKE.EXECUTION.GATE.V1

Purpose:
Freeze a controlled operator smoke execution of the installed local demo runner command.

Baseline:
HEAD d332e539c8568e496873017a04925e596d387f13
Tag cid-dev-stable-local-media-agent-controlled-local-demo-runner-operator-readme-gate-v1-20260630
Command cid-local-media-agent-controlled-local-demo-runner
Boundary DEMO_TECNICA_LOCAL_CONTROLADA_ONLY
Artifact controlled_visible_report.controlled.txt
Artifact SHA256 277bca892ae1591c3dec5c36935a0fc0489d31ed0796c3e3703f8c63b3ec3c6f
Artifact bytes 167

Smoke commands:
cid-local-media-agent-controlled-local-demo-runner --help
cid-local-media-agent-controlled-local-demo-runner --result-json
cid-local-media-agent-controlled-local-demo-runner --result-json --keep-output

Smoke expectations:
help exposes --result-json and --keep-output.
default JSON returns CONTROLLED_LOCAL_DEMO_RUNNER_VERIFIED.
default JSON removes output_root.
keep-output JSON preserves output_root for inspection.
keep-output artifact exists before cleanup.
operator smoke removes the kept output_root before completion.

JSON expectations:
operational_boundary DEMO_TECNICA_LOCAL_CONTROLADA_ONLY
dry_run.verification_status DRY_RUN_ONLY
write.verification_status VERIFIED
negative_path.verification_status REJECTED
artifact_sha256 277bca892ae1591c3dec5c36935a0fc0489d31ed0796c3e3703f8c63b3ec3c6f
artifact_bytes 167

Safety:
No client demo.
No public demo.
No production.
No installer.
No real media.
No scanner.
No ffprobe.
No FFmpeg.
No network.
No SaaS.
No database.
No repository write.
No overwrite.
No unattended execution.
No pyproject change.
No runner implementation change.

Closure requires:
operator smoke execution gate test PASS
operator README gate test PASS
installed CLI QA gate test PASS
runner implementation tests PASS
packaging transition tests PASS
write-enabled export integration tests PASS
WSL guard PASS
database regression guard PASS
only this operator smoke execution gate doc and test staged

Expected result:
LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_OPERATOR_SMOKE_EXECUTION_GATE_V1_CLOSED
