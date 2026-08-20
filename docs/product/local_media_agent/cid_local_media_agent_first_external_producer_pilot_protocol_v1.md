# CID Local Media Agent - First External Producer Pilot Protocol V1

PHASE:
CID.LMA.FIRST_EXTERNAL_PRODUCER_PILOT_PREPARATION.PROTOCOL.V1

EXPECTED_RESULT:
CID_LMA_FIRST_EXTERNAL_PRODUCER_PILOT_PROTOCOL_DEFINED

PURPOSE:
Define the controlled protocol and structured record schema for the first external
Windows producer pilot of CID Local Media Agent 0.3.0-beta1. The pilot evaluates
install experience, first-run producer UX, transcription value, and DaVinci import
on real producer material using the frozen release artifact.

PILOT_ARTIFACT:
CID-Local-Media-Agent-0.3.0-beta1-win64.zip

PILOT_ARTIFACT_SHA256:
D2FB24B030AF885E6CB83E08EF11A71EE67FD92483318A1BA218B681316083D4

PILOT_ARTIFACT_COMMIT:
b0efff9e5c4c5dd97b0913422063f4910ba2f000

PILOT_ARTIFACT_TAG:
cid-lma-v0.3.0-beta1

SCOPE:
Install and launch.
Select producer material folder.
CID analysis and recommendation.
Transcribe the recommended audio.
Open results (SRT + transcript + DaVinci handoff).
Import SRT into DaVinci Resolve.
Collect structured feedback.

OUT_OF_SCOPE:
No paid delivery.
No SaaS credentials or cloud services.
No remote troubleshooting of the producer's machine beyond the diagnostic bundle.
No guarantee of sync validation (REAL_VIDEO_EXTERNAL_AUDIO_SYNC_VALIDATED=False).
No model changes, no dependency changes, no network operations.

PRODUCER_ROLE:
Spanish-speaking documentary producer with DaVinci Resolve access.
Producer must not need Python, Whisper, FFmpeg, WSL, Git, or manifests.

PILOT_DURATION:
20 to 40 minutes guided.

DELIVERY_METHOD:
Direct delivery of the frozen ZIP by the operator.
No public download link.
No public artifact hosting.

OPERATOR:
Internal CID operator only.

SUPPORT_DURING_PILOT:
Live support while the pilot runs.
Fallback: diagnostic bundle collected from the producer machine
without media, transcripts, SRT content, secrets, or model files.

PRIVACY_MESSAGE_VERIFIED_BEHAVIOR:
Processing is local and offline.
No upload of material to any service.
No network required.
Source files are read-only and unmodified.
Results are stored locally under the producer Documents folder.

PILOT_STEP_SEQUENCE:
STEP 1: Confirm the producer's Windows version and DaVinci version.
STEP 2: Confirm the producer machine is the pilot machine (no other machine).
STEP 3: Give the producer the frozen ZIP and LEEME_PRIMERO.txt.
STEP 4: Ask the producer to extract the ZIP and run install.cmd.
STEP 5: Record install experience and any Windows security warnings (do not bypass controls).
STEP 6: Ask the producer to launch CID Local Media Agent from the Start menu.
STEP 7: Ask the producer to select the material folder for one recording group.
STEP 8: Observe if the flow is self-explanatory (Analizar material, Grabaciones, Recomendación CID).
STEP 9: Ask the producer to accept the CID recommendation and transcribe one recording.
STEP 10: Record transcription duration and result.
STEP 11: Ask the producer to open results and locate the SRT.
STEP 12: Ask the producer to import the SRT into DaVinci Resolve.
STEP 13: Ask the producer to open the transcript and verify text quality.
STEP 14: Collect qualitative feedback and product requests.
STEP 15: Ask the producer to close CID and confirm the material folder was untouched.
STEP 16: On success, optionally offer the diagnostic export or collect the log path.
STEP 17: Record the structured pilot record (schema below) and classify GO/NO-GO.

STOP_CONDITIONS:
Stop if the producer machine differs from the agreed pilot machine.
Stop if a Windows security control would need to be bypassed.
Stop if the producer asks for paid delivery, SaaS, or cloud features.
Stop if source material modification or upload is requested.
Stop if sync with camera audio is assumed as validated.
Stop if the producer requests macOS or Linux support.

PILOT_RECORD_SCHEMA:
PILOT_ID:
STRING (e.g. cid-lma-external-producer-pilot-001)

CID_VERSION:
STRING (fixed 0.3.0-beta1)

WINDOWS_VERSION:
STRING

DAVINCI_VERSION:
STRING

MEDIA_TYPE:
STRING (e.g. interview, documentary)

TOTAL_MEDIA_COUNT:
INTEGER

RECORDING_GROUP_COUNT:
INTEGER

CID_RECOMMENDED_SOURCE:
STRING (master label)

PRODUCER_ACCEPTED_RECOMMENDATION:
BOOLEAN

TRANSCRIPTION_DURATION_SECONDS:
INTEGER

TRANSCRIPTION_RESULT:
STRING (SUCCESS | PARTIAL | FAILED)

SRT_CUES_CREATED:
INTEGER

TRANSCRIPT_TEXT_LENGTH_CHARS:
INTEGER

SRT_IMPORTED_TO_DAVINCI:
BOOLEAN

SRT_IMPORT_OUTCOME:
STRING (ALIGNED | OFFSET | UNUSABLE | NOT_TESTED)

CANCELLATION_USED:
BOOLEAN

CANCELLATION_OUTCOME:
STRING

UX_PROBLEMS:
ARRAY_OF_STRING (producer-facing issues observed)

INSTALL_PROBLEMS:
ARRAY_OF_STRING

WINDOWS_SECURITY_WARNING_OBSERVED:
BOOLEAN

WINDOWS_SECURITY_WARNING_BYPASSED:
BOOLEAN (must stay FALSE)

PRODUCT_REQUESTS:
ARRAY_OF_STRING

BLOCKING_DEFECTS:
ARRAY_OF_STRING

NOTES:
STRING

PILOT_OUTCOME:
STRING (GO | NO_GO)

GO_CRITERIA:
No blocking defect observed.
Producer completed install, analysis, transcription, and results without operator intervention beyond the protocol.
Producer opened SRT and imported it into DaVinci.
Source material remained unmodified.
No secret or private artifact leaked.

NO_GO_CRITERIA:
Blocking defect in install, launch, analysis, transcription, or results.
Producer could not complete the flow with protocol-level guidance.
DaVinci import failed for a product reason.
Source material modified.
Windows security control bypassed.

VALIDATION_COMMANDS:
cd /opt/SERVICIOS_CINE && source .venv/bin/activate
PYTHONPATH=src pytest -q tests/unit/test_audio_source_intelligence.py tests/unit/test_lma_results_ux.py tests/unit/test_lma_gui_safe_cancellation.py
python -m py_compile scripts/windows/build_beta_package.py
git status --short

KNOWN_LIMITATIONS:
REAL_VIDEO_EXTERNAL_AUDIO_SYNC_VALIDATED=False (sync with genuine paired camera media is not mandatory for this first basic pilot, but genuine paired material is valuable input).
Windows-only beta; macOS portability is a separate objective.

SAFETY_CONFIRMATION:
No public download link is created by this protocol.
No cloud service is used.
No network operation is required.
No source material modification is allowed.
No diagnostic bundle contains media, transcripts, SRT content, secrets, or model files.

NEXT_RECOMMENDED_PHASE:
CID.LMA.FIRST_EXTERNAL_WINDOWS_PRODUCER_PILOT.EXECUTION.V1

NEXT_RECOMMENDED_RESULT:
CID_LMA_FIRST_EXTERNAL_WINDOWS_PRODUCER_PILOT_EXECUTION_COMPLETED_WITH_RECORD