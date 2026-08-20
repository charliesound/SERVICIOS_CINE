# CID Local Media Agent - Diagnostic and Support Bundle Spec V1

PHASE:
CID.LMA.FIRST_EXTERNAL_PRODUCER_PILOT_PREPARATION.DIAGNOSTIC.V1

PURPOSE:
Define the exact safe diagnostic bundle and support procedure for the first external
Windows producer pilot, without adding a new GUI button and without exposing
media, transcripts, SRT content, secrets, or model files.

DIAGNOSTIC_POLICY:
Diagnostic data is collected only to resolve pilot defects.
Diagnostic data never includes producer media.
Diagnostic data never includes transcripts or SRT text content.
Diagnostic data never includes secrets, tokens, credentials, or model files.
Diagnostic export is performed by the operator with explicit producer consent.

SUPPORT_PATH:
The installed CID app writes logs under:
%LOCALAPPDATA%\CID\LocalMediaAgent\logs

Log files present:
cid_gui.log (timestamped CID-controlled diagnostic lines)
worker_*.log (transcription worker stderr only)

SOURCE_OF_LOG_CONTENT:
cid_gui.log: cid_gui.py _write_log lines (error details, folder events, cancellation).
worker_*.log: stderr from cid_transcription_worker (errors, no media/transcript content).

DIAGNOSTIC_BUNDLE_FILES (exact safe set):
%LOCALAPPDATA%\CID\LocalMediaAgent\logs\*.log
%LOCALAPPDATA%\CID\LocalMediaAgent\preferences.json (results_root only; never secrets)
cid_diagnostic_info.txt (operator-generated: CID version, Windows version, DaVinci version, pilot record id)

DIAGNOSTIC_BUNDLE_MUST_EXCLUDE:
Producer media and source material.
Transcript .txt files.
SRT files and their text content.
davinci_handoff.json content.
Model files under models/.
Secrets, tokens, credentials, API keys.
Any cloud or SaaS configuration.

DIAGNOSTIC_BUNDLE_SAFETY_CHECK:
DIAGNOSTIC_MEDIA_INCLUDED=False
DIAGNOSTIC_TRANSCRIPT_INCLUDED=False
DIAGNOSTIC_SRT_INCLUDED=False
DIAGNOSTIC_HANDOFF_INCLUDED=False
DIAGNOSTIC_MODEL_INCLUDED=False
DIAGNOSTIC_SECRET_INCLUDED=False

GENERATION_PROCEDURE:
1. Ask the producer to close CID.
2. Operator reads only the logs directory listed above.
3. Operator creates cid_diagnostic_info.txt with non-sensitive pilot metadata.
4. Operator bundles the exact file set into a local ZIP.
5. Operator verifies the safety flags above before sharing.

CONSUMPTION_PROCEDURE:
Support consumes the bundle locally in the operator environment.
No upload to external diagnostic services.
No storage of the bundle in the public repository.
Bundles are deleted after the defect is resolved.

DO_NOT_FORCE_GUI_BUTTON:
A new "Exportar diagnóstico" GUI button would enlarge scope. Not implemented now.
The log-path-based procedure above satisfies the pilot requirement.

VERIFIED_OBSERVATION:
worker logs capture stderr only (batch_transcription.py worker_*.log).
cid_gui.log captures timestamped diagnostic lines.
Neither log contains media content or transcript text.

VALIDATION_COMMANDS:
cd /opt/SERVICIOS_CINE && source .venv/bin/activate
PYTHONPATH=src pytest -q tests/unit/test_lma_gui_safe_cancellation.py
python -m py_compile scripts/local_media_agent/cid_gui.py

STOP_CONDITIONS:
Stop if a diagnostic bundle would include media, transcripts, SRT content, or secrets.
Stop if logs are routed to a public or cloud service.
Stop if producer consent is not explicit.

NEXT_RECOMMENDED_PHASE:
CID.LMA.FIRST_EXTERNAL_WINDOWS_PRODUCER_PILOT.EXECUTION.V1