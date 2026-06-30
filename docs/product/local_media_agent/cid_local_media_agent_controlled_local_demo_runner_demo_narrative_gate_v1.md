# CID Local Media Agent - controlled local demo runner demo narrative gate V1

Phase:
CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.WRITE_ENABLED.EXPORT.CLI.PACKAGE.ENTRYPOINT.INSTALLED.CONTROLLED.LOCAL.DEMO.RUNNER.DEMO.NARRATIVE.GATE.V1

Purpose:
Define the internal demo narrative for explaining the installed controlled local demo runner without overstating product readiness.

Baseline:
HEAD bf36b80c0eb945166bf62aa70aa28fffce4ce0f7
Previous tag cid-dev-stable-local-media-agent-controlled-local-demo-runner-operator-evidence-pack-gate-v1-20260630
Recommended tag cid-dev-stable-local-media-agent-controlled-local-demo-runner-demo-narrative-gate-v1-20260630
Command cid-local-media-agent-controlled-local-demo-runner
Export command cid-local-media-agent-visible-report-write-enabled-export
Boundary DEMO_TECNICA_LOCAL_CONTROLADA_ONLY
Status CONTROLLED_LOCAL_DEMO_RUNNER_VERIFIED
Artifact controlled_visible_report.controlled.txt
Artifact SHA256 277bca892ae1591c3dec5c36935a0fc0489d31ed0796c3e3703f8c63b3ec3c6f
Artifact bytes 167

Required previous evidence:
docs/product/local_media_agent/cid_local_media_agent_controlled_local_demo_runner_operator_evidence_pack_gate_v1.md
tests/unit/test_cid_local_media_agent_controlled_local_demo_runner_operator_evidence_pack_gate.py

Narrative goal:
Move from technical evidence to a clear internal product explanation for a producer, school, or potential buyer conversation, while keeping the demo framed as controlled, local, fixture-only, and not final product delivery.

What to say first:
This is a local-only controlled technical demo of a future media agent capability.
It proves that an installed command can generate and verify one deterministic visible report text artifact under strict fixture-owned conditions.
It does not prove production readiness, customer onboarding, real media processing, SaaS integration, installer readiness, or public launch readiness.

Demo sequence:
1. Show command discovery with `cid-local-media-agent-controlled-local-demo-runner --help`.
2. Explain that `--help` is the safe operator entry point and shows only `--result-json` and `--keep-output`.
3. Run `cid-local-media-agent-controlled-local-demo-runner --result-json`.
4. Explain that the default JSON proves the demo can verify itself and clean the temporary output root automatically.
5. Point to `status CONTROLLED_LOCAL_DEMO_RUNNER_VERIFIED`.
6. Point to `operational_boundary DEMO_TECNICA_LOCAL_CONTROLADA_ONLY`.
7. Point to `dry_run.verification_status DRY_RUN_ONLY`.
8. Point to `write.verification_status VERIFIED`.
9. Point to `negative_path.verification_status REJECTED`.
10. Run `cid-local-media-agent-controlled-local-demo-runner --result-json --keep-output` only when manual artifact inspection is needed.
11. Explain that `--keep-output` temporarily preserves the fixture-owned output root and shifts cleanup responsibility to the operator.
12. After inspection, remove the reported output root and confirm the artifact is gone.

How to explain SHA and bytes:
The artifact name is `controlled_visible_report.controlled.txt`.
The expected SHA256 is `277bca892ae1591c3dec5c36935a0fc0489d31ed0796c3e3703f8c63b3ec3c6f`.
The expected byte count is `167`.
The SHA256 proves the bytes are exactly the same controlled text every time.
The byte count is a simple cross-check that the artifact size did not drift.
Do not describe the SHA as a watermark, signature, legal proof, content authenticity system, or customer delivery guarantee.

How to explain cleanup:
Default `--result-json` removes the temporary output root after verification.
Default JSON must show `output_root_removed true` and `artifact_available_after_runner false`.
`--keep-output` must show `output_root_removed false` and `artifact_available_after_runner true`.
The preserved path must be temporary, fixture-owned, and removed after inspection.
The demo must not write inside the repository.

Limits to repeat:
No client demo.
No public demo.
No sales demo.
No production.
No installer.
No real media.
No scanner.
No ffprobe.
No FFmpeg.
No network.
No SaaS.
No database service.
No repository write.
No overwrite.
No unattended execution.
No pyproject change.
No runner implementation change.
No export command implementation change.

What not to promise:
Do not promise real footage ingestion.
Do not promise scanner integration.
Do not promise ffprobe or FFmpeg execution.
Do not promise SaaS upload.
Do not promise customer workspace integration.
Do not promise installer packaging.
Do not promise production monitoring.
Do not promise timeline export.
Do not promise subtitles, sync, transcription, or audio extraction.
Do not promise security certification.
Do not promise delivery dates.

Controlled demo versus final product:
Controlled demo means installed local commands, fixture-owned output roots, deterministic JSON, one controlled text artifact, automatic cleanup by default, and explicit manual cleanup when output is preserved.
Final product still requires explicit future gates for packaging, installer, real operator onboarding, product support, customer data boundaries, deployment boundaries, and production release criteria.

Anti-hype rule:
If asked whether this is ready for a real customer workflow, answer: not yet; this is controlled local evidence that the internal command chain behaves safely and deterministically.
If asked whether it can process real media today, answer: not in this demo.
If asked whether the temporary artifact is a deliverable, answer: no; it is a controlled evidence artifact used to validate the command behavior.
If asked whether the demo can be shown externally, answer: only after a future explicit external-demo authorization gate.

Operator checklist:
Confirm installed command path before presenting.
Show `--help` before JSON.
Show default JSON before `--keep-output`.
Explain SHA256 and byte count together.
Explain default cleanup before manual inspection.
Clean preserved output roots after inspection.
Close with limits and next gates, not with product-ready claims.

Closure requires:
demo narrative gate test PASS
operator evidence pack gate test PASS
WSL guard PASS
database regression guard PASS
only this demo narrative gate doc and test staged

Expected result:
LOCAL_MEDIA_AGENT_CONTROLLED_LOCAL_DEMO_RUNNER_DEMO_NARRATIVE_GATE_V1_CLOSED
