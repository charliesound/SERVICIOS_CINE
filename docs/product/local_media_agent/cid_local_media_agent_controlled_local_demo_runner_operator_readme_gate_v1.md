# CID Local Media Agent - controlled local demo runner operator README gate V1

Phase:
CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.INSTALLED.CONTROLLED.LOCAL.DEMO.RUNNER.OPERATOR.README.GATE.V1

Purpose:
Provide an internal operator README for running the installed controlled local demo runner command safely.

Baseline:
HEAD 9d594cbeadd774eb5377dc45667f3ff80db8bc2d
Tag cid-dev-stable-local-media-agent-controlled-local-demo-runner-installed-cli-qa-gate-v1-20260630
Command cid-local-media-agent-controlled-local-demo-runner
Boundary DEMO_TECNICA_LOCAL_CONTROLADA_ONLY
Artifact controlled_visible_report.controlled.txt
Artifact SHA256 277bca892ae1591c3dec5c36935a0fc0489d31ed0796c3e3703f8c63b3ec3c6f
Artifact bytes 167

Operator commands:
cid-local-media-agent-controlled-local-demo-runner --help
cid-local-media-agent-controlled-local-demo-runner --result-json
cid-local-media-agent-controlled-local-demo-runner --result-json --keep-output

Default operator run:
Use --result-json for the normal internal check.
Expected status CONTROLLED_LOCAL_DEMO_RUNNER_VERIFIED.
Expected output_root_removed true.
Expected artifact_available_after_runner false.

Inspection operator run:
Use --result-json --keep-output only when manual artifact inspection is needed.
Expected output_root_removed false.
Expected artifact_available_after_runner true.
The operator must remove the reported output_root after inspection.

JSON interpretation:
dry_run.verification_status must be DRY_RUN_ONLY.
write.verification_status must be VERIFIED.
negative_path.verification_status must be REJECTED.
artifact_sha256 must be 277bca892ae1591c3dec5c36935a0fc0489d31ed0796c3e3703f8c63b3ec3c6f.
artifact_bytes must be 167.

Safety limits:
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

Cleanup:
When --keep-output is used, remove the JSON output_root with rm -rf only after confirming it is a cid-lma-controlled-demo-* path under the system temporary directory.

Closure requires:
operator README gate test PASS
installed CLI QA gate test PASS
runner implementation test PASS
runner QA gate test PASS
packaging transition tests PASS
write-enabled export integration tests PASS
WSL guard PASS
database regression guard PASS
only this operator README gate doc and test staged

Expected result:
LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_OPERATOR_README_GATE_V1_CLOSED
