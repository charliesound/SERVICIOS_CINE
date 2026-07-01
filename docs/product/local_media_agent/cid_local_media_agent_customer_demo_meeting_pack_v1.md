# CID Local Media Agent - Customer Demo Meeting Pack V1

PHASE:
CID.LOCAL_MEDIA_AGENT.READ_ONLY.SINGLE_FILE.METADATA.CLI.CONTROLLED_FIXTURE.SMOKE.VISIBLE_REPORT.CLI.CONTROLLED_MARKDOWN_EXPORT.CUSTOMER_DEMO.PACKAGING.GATE.V1

EXPECTED_RESULT:
LOCAL_MEDIA_AGENT_READ_ONLY_SINGLE_FILE_METADATA_CLI_CONTROLLED_FIXTURE_SMOKE_VISIBLE_REPORT_CLI_CONTROLLED_MARKDOWN_EXPORT_CUSTOMER_DEMO_PACKAGING_GATE_V1_CLOSED

BASE_HEAD:
5d664840018db93502db3d487a80a0ae92692f87

BASE_COMMIT:
5d66484 test: add CID Local Media Agent customer demo packaging readiness gate

BASE_TAG:
cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-customer-demo-packaging-readiness-gate-v1-20260701

STATUS:
SAFE_CUSTOMER_DEMO_MEETING_PACK_CREATED

PACK_TYPE:
Safe controlled customer demo meeting pack.

PACK_OWNER:
Owner/operator only.

PACK_LANGUAGE:
Spanish meeting copy with technical evidence preserved.

PACK_USE:
Private one-to-one meeting with a trusted producer, executive producer, postproduction supervisor, distributor, exhibitor, or school decision-maker.

PACK_NOT_FOR:
Public launch.
Paid delivery.
Downloadable product.
Installer distribution.
Unsupervised execution.
Workshop with participant files.
Real project processing.
Customer media ingestion.
Production workflow replacement.

MEETING_TITLE:
CID Local Media Agent - Demo controlada para productores audiovisuales

ONE_SENTENCE_PITCH:
CID Local Media Agent está pensado para ayudar a equipos de cine, televisión y postproducción a entender material audiovisual localmente antes de ingesta, sincronización, transcripción, montaje, entrega o archivo.

EXECUTIVE_SUMMARY_FOR_PRODUCER:
CID Local Media Agent es una línea de producto local-first dentro del ecosistema CID.
La dirección comercial es clara: ayudar a productoras y equipos de postproducción a reducir desorden, riesgo y pérdida de tiempo cuando reciben material audiovisual.
La demo actual no procesa material real.
La demo actual no procesa material de cliente.
La demo actual enseña una base técnica controlada: validar un archivo permitido, generar un informe visible, exportarlo de forma controlada, verificarlo, limpiar el artefacto temporal y dejar el workspace limpio.
La utilidad futura para un productor es tener visibilidad temprana del material recibido antes de que cause problemas de rodaje, postproducción, entrega o archivo.

OPENING_SCRIPT:
Esto es una demo técnica controlada, no una versión comercial final.
La filosofía del producto es local-first: el material del cliente debe quedarse en su máquina.
Hoy no voy a procesar material real, sonido real, material confidencial ni archivos del cliente.
Voy a usar un fixture interno no sensible para enseñar la cadena de prueba: validación, informe visible, exportación controlada, verificación, limpieza y evidencia.
El objetivo de esta reunión no es vender una promesa cerrada, sino validar si este tipo de herramienta resuelve un problema real en vuestra operativa.

DEMO_BOUNDARY_SCRIPT:
Esta demo no demuestra todavía escaneo de carpetas reales.
Esta demo no demuestra transcripción.
Esta demo no demuestra sincronización.
Esta demo no demuestra integración con DaVinci Resolve o Avid.
Esta demo no demuestra entrega en producción.
Esta demo solo demuestra que la cadena local de reporte controlado ya está funcionando y auditada.

WHAT_TO_SHOW_ON_SCREEN:
1. Terminal en /opt/SERVICIOS_CINE.
2. Rama main.
3. HEAD estable esperado.
4. Tag estable esperado.
5. Workspace limpio.
6. Fixture interno no cliente.
7. Comando de informe visible por stdout.
8. Resultado PASS del informe.
9. Comando de exportación Markdown controlada.
10. Marcador CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK.
11. Archivo customer_demo_visible_report.md generado dentro de tests/tmp/local_media_agent/controlled_visible_report_exports.
12. Verificación de título, ruta relativa permitida y SHA256 del fixture.
13. SHA256 del reporte generado.
14. Limpieza del directorio temporal.
15. Workspace final limpio.

SAFE_PRE_MEETING_PREFLIGHT:
Workdir must be /opt/SERVICIOS_CINE.
Virtual environment must be active.
Branch must be main.
HEAD must be 5d664840018db93502db3d487a80a0ae92692f87 or a later explicitly approved stable customer-demo packaging head.
Workspace must be clean.
Controlled export root must be absent before execution.
No real media path may be used.
No customer path may be used.
No production path may be used.
No cloud upload may be shown.
No SaaS screen may be shown.
No database screen may be shown.
No installer may be shown.
No binary package may be shown.

SAFE_STDOUT_REPORT_COMMAND:
python scripts/local_media_agent/read_only_single_file_metadata_cli.py --target-path tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt --fixture-root tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1 --expected-sha256 a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a --expected-bytes 239 --allowed-relative-path media/controlled_plain_text_marker.txt --visible-report-markdown

SAFE_EXPORT_REPORT_COMMAND:
mkdir -p tests/tmp/local_media_agent/controlled_visible_report_exports
python scripts/local_media_agent/read_only_single_file_metadata_cli.py --target-path tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt --fixture-root tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1 --expected-sha256 a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a --expected-bytes 239 --allowed-relative-path media/controlled_plain_text_marker.txt --visible-report-markdown --visible-report-output tests/tmp/local_media_agent/controlled_visible_report_exports/customer_demo_visible_report.md

SAFE_VERIFY_COMMANDS:
test -f tests/tmp/local_media_agent/controlled_visible_report_exports/customer_demo_visible_report.md
grep -F "CID Local Media Agent - Controlled Fixture Smoke Visible Report" tests/tmp/local_media_agent/controlled_visible_report_exports/customer_demo_visible_report.md
grep -F "media/controlled_plain_text_marker.txt" tests/tmp/local_media_agent/controlled_visible_report_exports/customer_demo_visible_report.md
grep -F "a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a" tests/tmp/local_media_agent/controlled_visible_report_exports/customer_demo_visible_report.md
sha256sum tests/tmp/local_media_agent/controlled_visible_report_exports/customer_demo_visible_report.md

SAFE_CLEANUP_COMMAND:
rm -rf tests/tmp/local_media_agent/controlled_visible_report_exports

EXPECTED_SUCCESS_MARKER:
CONTROLLED_VISIBLE_REPORT_MARKDOWN_EXPORT_OK

CONTROLLED_FIXTURE_ID:
controlled_plain_text_marker_v1

CONTROLLED_FIXTURE_ROOT:
tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1

CONTROLLED_TARGET_PATH:
tests/fixtures/local_media_agent/controlled_non_customer_fixture_pack_v1/media/controlled_plain_text_marker.txt

ALLOWED_RELATIVE_PATH:
media/controlled_plain_text_marker.txt

EXPECTED_BYTES:
239

EXPECTED_FIXTURE_SHA256:
a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a

EXPECTED_REPORT_TITLE:
CID Local Media Agent - Controlled Fixture Smoke Visible Report

LAST_VERIFIED_EXECUTION_EVIDENCE:
Customer demo execution result: LOCAL_MEDIA_AGENT_CONTROLLED_CUSTOMER_DEMO_EXECUTION_PASS
Generated report size: 1795 bytes
Generated report SHA256: b7fb2312397b99030001eb67cfe91f2645b0be5d381b11bfa6e35dcacd4de8cd
Controlled fixture SHA256: a07f811ed8e94f402d9d4969c82fb1c5d78eac3bd556cb40a8f367fda476d67a
Final workspace: clean

BUSINESS_VALUE_HYPOTHESES:
Reduce chaos when several productions deliver material at the same time.
Give producers and production managers early visibility before material enters postproduction.
Help detect incomplete or suspicious handoffs before they become schedule problems.
Create local reports that can be reviewed without uploading sensitive files.
Prepare future workflows for camera files, sound files, transcription, subtitles, sync, edit handoff, delivery, and archive.
Offer a future bridge between local project material and CID production coordination.

PRODUCER_DISCOVERY_QUESTIONS:
How many active productions do you supervise at the same time?
How many production managers, coordinators, DITs, editors, or vendors send material to you?
Where does material control currently break: shooting, handoff, ingest, editing, delivery, or archive?
Who currently checks whether incoming material is complete and understandable?
Do you receive camera and sound material from several units or vendors?
How do you currently identify missing, duplicated, renamed, corrupted, or confusing files?
Would a local report before upload or handoff reduce operational risk?
What kind of first real-media preflight would be worth paying for?
Who would approve a private pilot?
What material cannot leave your premises under any circumstance?
Would your team prefer a local app, CLI workflow, or CID-integrated module?
What would make this useful enough for a September or October commercial conversation?

PRIVATE_PILOT_DISCUSSION_BOUNDARY:
A future private pilot may be discussed.
A future private pilot must have explicit scope.
A future private pilot must define accepted file types.
A future private pilot must define allowed test material.
A future private pilot must define what cannot be copied or uploaded.
A future private pilot must define success criteria.
A future private pilot must define who approves execution.
This meeting pack does not itself approve a private pilot.

SAFE_FOLLOW_UP_OPTIONS:
Schedule a requirements call.
Collect only non-sensitive workflow requirements.
Define first real-media preflight requirements without taking files.
Request synthetic or non-confidential sample structures only.
Define a written private pilot boundary.
Define pilot success criteria.
Define pilot buyer, user, and technical approver.
Prepare a future real-media preflight readiness gate only after explicit authorization.

DO_NOT_PROMISE:
Do not promise production readiness.
Do not promise installer availability.
Do not promise Windows or macOS packaging from this demo.
Do not promise FFmpeg or ffprobe processing from this demo.
Do not promise transcription from this demo.
Do not promise sync from this demo.
Do not promise subtitles from this demo.
Do not promise DaVinci Resolve or Avid integration from this demo.
Do not promise SaaS integration from this demo.
Do not promise customer data processing from this demo.
Do not promise delivery dates without a scoped plan.

STOP_CONDITIONS:
Stop if the prospect asks to process real material during the meeting.
Stop if the prospect asks to send files.
Stop if the prospect wants to drag and drop customer media.
Stop if the prospect interprets the demo as production-ready.
Stop if the repo is not at the expected stable state.
Stop if the workspace is not clean.
Stop if the fixture path changes.
Stop if the export path leaves the controlled temporary root.
Stop if report verification fails.
Stop if cleanup fails.
Stop if any customer material appears on screen.

MEETING_CLOSE_OPTIONS:
Option 1: No fit now; record objections.
Option 2: Requirements call only.
Option 3: Define private pilot boundary.
Option 4: Prepare future first real-media preflight readiness.
Option 5: Discuss commercial buyer and pricing assumptions later.

PACKAGING_GATE_PASS_CRITERIA:
Meeting title is present.
One-sentence pitch is present.
Executive summary is present.
Opening script is present.
Demo boundary script is present.
Screen order is present.
Safe pre-meeting preflight is present.
Safe stdout report command is present.
Safe export report command is present.
Safe verify commands are present.
Safe cleanup command is present.
Controlled fixture identity is present.
Last verified execution evidence is present.
Business value hypotheses are present.
Producer discovery questions are present.
Private pilot boundary is present.
Safe follow-up options are present.
Do-not-promise list is present.
Stop conditions are present.
Meeting close options are present.
No real material is included.
No customer material is included.
No generated report artifact is committed.
No installer is created.
No binary package is created.

SAFETY_CONFIRMATION:
No real media is allowed.
No customer material is allowed.
No production material is allowed.
No confidential material is allowed.
No FFmpeg is allowed.
No ffprobe is allowed.
No scanner integration is allowed.
No batch traversal is allowed.
No recursive traversal is allowed.
No SaaS module is allowed.
No database is allowed.
No backend change is allowed.
No frontend change is allowed.
No Docker change is allowed.
No Alembic change is allowed.
No Stripe change is allowed.
No AI Jobs change is allowed.
No credits or ledger change is allowed.
No committed customer demo export artifact is allowed.
No installer is created.
No binary is created.

ALLOWED_SCOPE:
Add this customer demo meeting pack document.
Add one customer demo meeting pack unit test.
Inspect existing documents.
Inspect existing tests.
Run validation tests.
Run WSL repo guard.
Run PostgreSQL-only regression guard required by policy.
Commit, tag, and push after validation.

FORBIDDEN_SCOPE:
No implementation changes.
No parser changes.
No CLI behavior changes.
No wrapper changes.
No renderer changes.
No in-memory integration changes.
No fixture modification.
No committed export artifact.
No execution against real media.
No execution against customer material.
No FFmpeg.
No ffprobe.
No scanner integration.
No batch processing.
No recursive traversal.
No unsafe shell execution.
No pyproject modification.
No console script registration.
No SaaS integration.
No database access.
No backend changes.
No frontend changes.
No installer work.
No binary packaging.
No Docker work.
No Alembic work.
No Stripe work.
No AI Jobs work.
No credits or ledger work.

REQUIRED_VALIDATION_TARGETS:
Customer demo meeting pack test.
Customer demo packaging readiness gate test.
Customer demo execution QA gate test.
Customer demo execution gate test.
Customer demo execution readiness gate test.
Customer demo script gate test.
Customer demo readiness gate test.
Manual demo execution QA gate test.
Manual demo execution gate test.
Manual demo readiness gate test.
Controlled demo execution QA gate test.
Controlled demo execution gate test.
Wrapper smoke execution QA gate test.
Wrapper smoke execution gate test.
Implementation QA gate test.
Implementation gate test.
In-memory wrapper smoke execution QA gate test.
In-memory wrapper smoke execution gate test.
Visible report contract test.
CLI contract gate test.
WSL repo guard.
PostgreSQL-only regression guard required by policy.

SUGGESTED_COMMIT:
docs: add CID Local Media Agent customer demo meeting pack

SUGGESTED_TAG:
cid-dev-stable-local-media-agent-read-only-single-file-metadata-cli-controlled-fixture-smoke-visible-report-cli-controlled-markdown-export-customer-demo-packaging-gate-v1-20260701
