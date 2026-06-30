# CID Local Media Agent - controlled local demo runner installed CLI QA gate V1

Phase:
CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.INSTALLED.CONTROLLED.LOCAL.DEMO.RUNNER.INSTALLED.CLI.QA.GATE.V1

Purpose:
Freeze the installed command behavior of cid-local-media-agent-controlled-local-demo-runner.

Baseline:
HEAD 721cd50cdbe5c1e730d1a5a0d833548a45d8a631
Tag cid-dev-stable-local-media-agent-controlled-local-demo-runner-cli-entrypoint-implementation-v1-20260630
Command cid-local-media-agent-controlled-local-demo-runner
Target scripts.local_media_agent.cid_local_media_agent_write_enabled_export_cli_installed_controlled_local_demo_runner:main
Boundary DEMO_TECNICA_LOCAL_CONTROLADA_ONLY
Artifact controlled_visible_report.controlled.txt
Artifact SHA256 277bca892ae1591c3dec5c36935a0fc0489d31ed0796c3e3703f8c63b3ec3c6f
Artifact bytes 167

Installed CLI surface under QA:
cid-local-media-agent-controlled-local-demo-runner --help
cid-local-media-agent-controlled-local-demo-runner --result-json
cid-local-media-agent-controlled-local-demo-runner --result-json --keep-output

Required JSON:
status CONTROLLED_LOCAL_DEMO_RUNNER_VERIFIED
operational_boundary DEMO_TECNICA_LOCAL_CONTROLADA_ONLY
dry_run.verification_status DRY_RUN_ONLY
write.verification_status VERIFIED
negative_path.verification_status REJECTED

Default mode:
output_root_removed true
artifact_available_after_runner false

Keep-output mode:
output_root_removed false
artifact_available_after_runner true
The QA test must inspect and clean the kept fixture-owned temporary output root.

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
No pyproject change.
No runner implementation change.

Closure requires:
installed CLI QA test PASS
runner implementation test PASS
runner QA gate test PASS
installed command block PASS
root packaging transition tests PASS
write-enabled export integration tests PASS
WSL guard PASS
database regression guard PASS
only this QA doc and test staged

Expected result:
LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_INSTALLED_CLI_QA_GATE_V1_CLOSED
