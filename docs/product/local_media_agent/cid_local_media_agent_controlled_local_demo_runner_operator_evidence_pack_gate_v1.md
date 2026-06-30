# CID Local Media Agent - controlled local demo runner operator evidence pack gate V1

Phase:
CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.INSTALLED.CONTROLLED.LOCAL.DEMO.RUNNER.OPERATOR.EVIDENCE.PACK.GATE.V1

Purpose:
Freeze the internal evidence pack for presenting and verifying the installed controlled local demo runner.

Baseline:
HEAD d92b64f3bb20dcfd57174b02ac6e41d4e000633c
Tag cid-dev-stable-local-media-agent-controlled-local-demo-runner-operator-smoke-execution-gate-v1-20260630
Command cid-local-media-agent-controlled-local-demo-runner
Boundary DEMO_TECNICA_LOCAL_CONTROLADA_ONLY
Artifact controlled_visible_report.controlled.txt
Artifact SHA256 277bca892ae1591c3dec5c36935a0fc0489d31ed0796c3e3703f8c63b3ec3c6f
Artifact bytes 167

Evidence commands:
cid-local-media-agent-controlled-local-demo-runner --help
cid-local-media-agent-controlled-local-demo-runner --result-json
cid-local-media-agent-controlled-local-demo-runner --result-json --keep-output

Evidence to show:
help output with --result-json and --keep-output.
default JSON with status CONTROLLED_LOCAL_DEMO_RUNNER_VERIFIED.
default JSON with output_root_removed true.
default JSON with artifact_available_after_runner false.
keep-output JSON with output_root_removed false.
keep-output JSON with artifact_available_after_runner true.
controlled artifact exists before cleanup.
controlled artifact is removed after cleanup of output_root.

Expected JSON:
status CONTROLLED_LOCAL_DEMO_RUNNER_VERIFIED
operational_boundary DEMO_TECNICA_LOCAL_CONTROLADA_ONLY
dry_run.verification_status DRY_RUN_ONLY
write.verification_status VERIFIED
negative_path.verification_status REJECTED
artifact_name controlled_visible_report.controlled.txt
artifact_sha256 277bca892ae1591c3dec5c36935a0fc0489d31ed0796c3e3703f8c63b3ec3c6f
artifact_bytes 167

Evidence limits:
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

Operator cleanup:
When --keep-output is used, the evidence owner must remove the reported output_root after inspection.
The output_root must be a cid-lma-controlled-demo-* path under the system temporary directory.

Closure requires:
operator evidence pack gate test PASS
operator smoke execution gate test PASS
operator README gate test PASS
installed CLI QA gate test PASS
runner implementation tests PASS
packaging transition tests PASS
write-enabled export integration tests PASS
WSL guard PASS
database regression guard PASS
only this operator evidence pack doc and test staged

Expected result:
LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_OPERATOR_EVIDENCE_PACK_GATE_V1_CLOSED
