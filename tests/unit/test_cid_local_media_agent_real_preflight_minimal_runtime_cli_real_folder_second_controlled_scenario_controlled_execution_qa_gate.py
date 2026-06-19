from pathlib import Path

QA_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_controlled_execution_qa_gate_v1.md"
)
EXECUTION_DOC = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_real_preflight_minimal_runtime_cli_real_folder_second_controlled_scenario_controlled_execution_v1.md"
)


def read(path):
    return path.read_text(encoding="utf-8")


def test_second_controlled_scenario_execution_qa_gate_docs_exist():
    assert QA_DOC.exists()
    assert EXECUTION_DOC.exists()


def test_second_controlled_scenario_execution_qa_gate_phase_declared():
    t = read(QA_DOC)
    assert "SECOND.CONTROLLED.SCENARIO.CONTROLLED.EXECUTION.QA.GATE.V1" in t
    assert "SECOND.CONTROLLED.SCENARIO.CONTROLLED.EXECUTION.V1" in t
    assert "docs/test-only" in t
    assert "does not repeat the CLI execution" in t


def test_second_controlled_scenario_execution_qa_gate_validates_upstream_result():
    t = read(QA_DOC)
    required = [
        "execution result is PREFLIGHT_PASS",
        "CLI exit code is 0",
        "leak check exit code is 0",
        "media file count is 2",
        "accepted extension counts are .mov:1 and .wav:1",
        "rejected extension counts are .exe:1 and .txt:1",
        "ignored extension counts are empty",
        "maximum detected scan depth is 3",
        "selected media size bucket is LE_100MB",
        "failed check identifiers are empty",
        "remediation items are empty",
        "sanitized folder labels are generic",
        "repository remained clean after execution",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_qa_gate_status_is_pass_with_observation():
    t = read(QA_DOC)
    required = [
        "qa_status=PASS_WITH_OBSERVATION",
        "execution_status=PREFLIGHT_PASS",
        "privacy_status=PASS",
        "sanitization_status=PASS",
        "contract_shape_status=PASS_WITH_OBSERVATION",
        "observation_status=NON_BLOCKING_FOR_PRIVACY_AND_SANITIZATION",
        "follow_up_required=true",
        "This QA gate accepts the execution record only as PASS_WITH_OBSERVATION.",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_qa_gate_privacy_conditions_are_validated():
    t = read(QA_DOC)
    required = [
        "no private paths were copied into the record",
        "no machine names were copied into the record",
        "no user names were copied into the record",
        "no concrete temporary folder names were copied into the record",
        "no concrete synthetic file names were copied into the record",
        "no raw command output was copied into the record",
        "no raw evidence payload was copied into the record",
        "no stack trace was copied into the record",
        "no project name or client name was copied into the record",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_qa_gate_boundaries_are_validated():
    t = read(QA_DOC)
    required = [
        "no real client media was used",
        "no personal data was used",
        "no mounted Windows path was used",
        "no cloud-synced folder was used",
        "no network share was used",
        "no scanner integration was used",
        "no ffprobe or ffmpeg was used",
        "no media probing was performed",
        "no media decoding was performed",
        "no report generation was performed",
        "no transcription was performed",
        "no translation was performed",
        "no subtitles were produced",
        "no sync was performed",
        "no edit decision output was produced",
        "no export was produced",
        "no upload was performed",
        "no SaaS integration was performed",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_qa_gate_observation_is_explicit():
    t = read(QA_DOC)
    required = [
        "expected the ignored extension category to be present",
        "ignored_extension_counts as empty",
        "classified the synthetic non-accepted extensions under rejected_extension_counts",
        "does not block privacy, sanitization, cleanup, or dry-run execution validation",
        "must remain visible as a follow-up",
        "before treating ignored versus rejected extension behavior as final product behavior",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_qa_gate_blocks_scope_expansion():
    t = read(QA_DOC)
    required = [
        "This QA gate does not authorize:",
        "real client media",
        "sensitive media",
        "personal data processing",
        "mounted Windows paths",
        "cloud-synced folders",
        "network shares",
        "scanner integration",
        "ffprobe or ffmpeg",
        "media probing",
        "media decoding",
        "report generation",
        "transcription",
        "translation",
        "subtitles",
        "sync",
        "edit decision output",
        "export",
        "upload",
        "desktop app",
        "installer",
        "licensing",
        "SaaS integration",
        "backend changes",
        "frontend changes",
        "database changes",
        "Docker changes",
        "Alembic changes",
        "Stripe changes",
        "AI Jobs changes",
        "credits",
        "ledger changes",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_qa_gate_allowed_next_step_is_limited():
    t = read(QA_DOC)
    assert "post-second-controlled-scenario execution boundary contract only" in t
    assert "no repeat execution unless a later phase explicitly authorizes it" in t


def test_second_controlled_scenario_execution_record_supports_qa_gate():
    t = read(EXECUTION_DOC)
    required = [
        "execution_status=PREFLIGHT_PASS",
        "cli_exit_code=0",
        "leak_check_exit_code=0",
        "privacy_status=PASS",
        "sanitization_status=PASS",
        "contract_shape_status=PASS_WITH_OBSERVATION",
        "ignored_extension_counts={}",
        "rejected_extension_counts=.exe:1,.txt:1",
        "observation_status=NON_BLOCKING_FOR_PRIVACY_AND_SANITIZATION",
        "follow_up_required=true",
    ]
    for item in required:
        assert item in t


def test_second_controlled_scenario_execution_qa_gate_private_tokens_are_absent():
    combined = read(QA_DOC) + "\n" + read(EXECUTION_DOC)
    forbidden = ["DESKTOP-", "A001_C001", "CID_LOCAL_MEDIA_AGENT_CONTROLLED_DRY_RUN"]
    forbidden += ["clip_alpha", "sound_alpha", "readme.txt", "reject_alpha"]
    forbidden += ["/" + "home/", "/" + "opt/", "/" + "mnt/"]
    forbidden += ["C:" + "\\\\", "\\\\" + "\\\\" + "wsl.localhost"]
    for token in forbidden:
        assert token not in combined
