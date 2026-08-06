from __future__ import annotations

import re
from pathlib import Path

RECORD_QA_DOC = Path(
    "docs/product/local_media_agent/cid_local_media_agent_controlled_own_real_material_single_scan_sanitized_execution_record_qa_gate_v1.md"
)
RECORD_DOC = Path(
    "docs/product/local_media_agent/cid_local_media_agent_controlled_own_real_material_single_scan_sanitized_execution_record_v1.md"
)

AUTHORIZED_PATHS = [
    RECORD_DOC,
    Path("tests/unit/test_cid_local_media_agent_controlled_own_real_material_single_scan_sanitized_execution_record.py"),
    RECORD_QA_DOC,
    Path("tests/unit/test_cid_local_media_agent_controlled_own_real_material_single_scan_sanitized_execution_record_qa_gate_v1.py"),
]

QA_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.COMMERCIAL_ALIAS.WINDOWS_HOST_DRIVE."
    "CONTROLLED_OWN_REAL_MATERIAL.SANITIZED_EXECUTION_EVIDENCE.PERSISTENCE.QA.GATE.V1"
)
IMPLEMENTATION_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.COMMERCIAL_ALIAS.WINDOWS_HOST_DRIVE."
    "CONTROLLED_OWN_REAL_MATERIAL.SANITIZED_EXECUTION_EVIDENCE.PERSISTENCE.IMPLEMENTATION.GATE.V1"
)
QA_RESULT = "CID_LOCAL_MEDIA_AGENT_CONTROLLED_OWN_REAL_MATERIAL_SANITIZED_EXECUTION_EVIDENCE_PERSISTENCE_QA_GATE_V1_COMPLETED"


def _qa_text() -> str:
    return RECORD_QA_DOC.read_text(encoding="utf-8")


def _record_text() -> str:
    return RECORD_DOC.read_text(encoding="utf-8")


def _assert_all_present(text: str, items: list[str]) -> None:
    for item in items:
        assert item in text


def test_01_qa_doc_exists_and_is_utf8() -> None:
    assert RECORD_QA_DOC.is_file()
    assert not RECORD_QA_DOC.is_symlink()
    text = _qa_text()
    assert isinstance(text, str)
    assert text.strip()


def test_02_qa_phase_and_implementation_phase_identity() -> None:
    text = _qa_text()
    assert QA_PHASE in text
    assert IMPLEMENTATION_PHASE in text


def test_03_authorized_path_set_declared() -> None:
    text = _qa_text()
    assert "AUTHORIZED_PATH_COUNT=4" in text
    for path in AUTHORIZED_PATHS:
        assert path.name in text
        assert path.exists()
        assert path.is_file()


def test_04_no_production_change_and_no_scan_reexecution() -> None:
    text = _qa_text()
    _assert_all_present(text, [
        "PRODUCTION_RUNTIME_CHANGED=False",
        "SCAN_REEXECUTED=False",
        "REAL_MEDIA_ACCESSED=False",
        "No existing file was modified.",
        "No file was deleted.",
        "No file was renamed.",
    ])


def test_05_content_based_privacy_validation_and_commercial_neutrality() -> None:
    text = _qa_text()
    record = _record_text()
    _assert_all_present(text, [
        "DOCUMENT_HASH_PIN_USED=False",
        "CONTENT_VALIDATION_USED=True",
        "PRIVACY_NEGATIVE_ASSERTIONS_USED=True",
        "ARITHMETIC_ASSERTIONS_USED=True",
        "COMMIT_IDENTITY_ASSERTIONS_USED=True",
        "TAG_IDENTITY_ASSERTIONS_USED=True",
        "TEST_EXECUTION_HOST_VOLUME_REDACTED=True",
        "SPECIFIC_WINDOWS_DRIVE_PERSISTED=False",
        "WINDOWS_DRIVE_LETTER_HARD_CODED=False",
        "DEFAULT_WINDOWS_DRIVE_REQUIRED=False",
        "CLIENT_SELECTED_LOCAL_ROOT_ACCEPTED=True",
        "COMMERCIAL_PATH_POLICY_IS_VOLUME_AGNOSTIC=True",
        "COMMERCIAL_PATH_POLICY_IS_CROSS_PLATFORM=True",
        "AUTOMATIC_DRIVE_ENUMERATION=False",
        "WSL_DEVELOPMENT_BRIDGE_ONLY=True",
        "WSL_REQUIRED_FOR_CUSTOMERS=False",
        "CUSTOMER_MEDIA_COPY_REQUIRED=False",
    ])
    _assert_all_present(record, [
        "CLIENT_SELECTED_LOCAL_ROOT_REQUIRED=True",
        "CLIENT_SELECTED_LOCAL_VOLUME_SUPPORTED=True",
        "CLIENT_SELECTED_ROOT_ONLY=True",
        "WINDOWS_DRIVE_LETTER_HARD_CODED=False",
        "DEFAULT_WINDOWS_DRIVE_REQUIRED=False",
        "SPECIFIC_WINDOWS_DRIVE_REQUIRED=False",
        "WSL_DEVELOPMENT_BRIDGE_ONLY=True",
        "WSL_REQUIRED_FOR_CUSTOMERS=False",
        "CUSTOMER_MEDIA_COPY_REQUIRED=False",
        "SANITIZED_CLIENT_SELECTED_LOCAL_ROOT",
        "SANITIZED_HOST_VOLUME",
    ])


def test_06_pytest_history_and_final_counts() -> None:
    text = _qa_text()
    _assert_all_present(text, [
        "PYTHONPATH=src /opt/SERVICIOS_CINE/.venv/bin/python -m pytest",
        "ORIGINAL_IMPLEMENTATION_GATE_PYTEST_EXECUTION_LIMIT=2",
        "ORIGINAL_IMPLEMENTATION_GATE_PYTEST_EXECUTION_COUNT=4",
        "ORIGINAL_IMPLEMENTATION_GATE_EXTRA_PYTEST_EXECUTION_COUNT=2",
        "ORIGINAL_IMPLEMENTATION_GATE_RUN_1_COLLECTED=20",
        "ORIGINAL_IMPLEMENTATION_GATE_RUN_1_PASSED=20",
        "ORIGINAL_IMPLEMENTATION_GATE_RUN_1_FAILED=0",
        "ORIGINAL_IMPLEMENTATION_GATE_RUN_1_ERRORS=0",
        "ORIGINAL_IMPLEMENTATION_GATE_RUN_1_EXIT_CODE=0",
        "ORIGINAL_IMPLEMENTATION_GATE_RUN_2_COLLECTED=20",
        "ORIGINAL_IMPLEMENTATION_GATE_RUN_2_PASSED=20",
        "ORIGINAL_IMPLEMENTATION_GATE_RUN_2_FAILED=0",
        "ORIGINAL_IMPLEMENTATION_GATE_RUN_2_ERRORS=0",
        "ORIGINAL_IMPLEMENTATION_GATE_RUN_2_EXIT_CODE=0",
        "ORIGINAL_IMPLEMENTATION_GATE_RUN_3_COLLECTED=20",
        "ORIGINAL_IMPLEMENTATION_GATE_RUN_3_PASSED=20",
        "ORIGINAL_IMPLEMENTATION_GATE_RUN_3_FAILED=0",
        "ORIGINAL_IMPLEMENTATION_GATE_RUN_3_ERRORS=0",
        "ORIGINAL_IMPLEMENTATION_GATE_RUN_3_EXIT_CODE=0",
        "ORIGINAL_IMPLEMENTATION_GATE_RUN_4_COLLECTED=20",
        "ORIGINAL_IMPLEMENTATION_GATE_RUN_4_PASSED=20",
        "ORIGINAL_IMPLEMENTATION_GATE_RUN_4_FAILED=0",
        "ORIGINAL_IMPLEMENTATION_GATE_RUN_4_ERRORS=0",
        "ORIGINAL_IMPLEMENTATION_GATE_RUN_4_EXIT_CODE=0",
        "ORIGINAL_IMPLEMENTATION_GATE_THIRD_PYTEST_EXECUTION_PERFORMED=True",
        "ORIGINAL_IMPLEMENTATION_GATE_FOURTH_PYTEST_EXECUTION_PERFORMED=True",
        "ORIGINAL_IMPLEMENTATION_GATE_FIFTH_PYTEST_EXECUTION_PERFORMED=False",
        "PROCEDURAL_DEVIATION_REVIEW_CLASSIFICATION=MATERIAL_PROCEDURAL_DEVIATION",
        "PROCEDURAL_DEVIATION_REVIEW_RESULT=",
        "CID_LOCAL_MEDIA_AGENT_CONTROLLED_OWN_REAL_MATERIAL_SANITIZED_EXECUTION_EVIDENCE_PERSISTENCE_IMPLEMENTATION_PROCEDURAL_DEVIATION_REVIEW_GATE_V1_BLOCKED",
        "PROCEDURAL_HISTORY_CORRECTION_IMPLEMENTED=True",
        "ORIGINAL_FOUR_RUN_HISTORY_PRESERVED=True",
        "HISTORY_REWRITTEN=False",
        "CORRECTION_GATE_VALIDATION_IS_SEPARATE_PHASE=True",
        "CORRECTION_GATE_VALIDATION_NOT_INCLUDED_IN_ORIGINAL_IMPLEMENTATION_COUNT=True",
        "QA_TESTS_COLLECTED=20",
        "QA_TESTS_PASSED=20",
        "QA_TESTS_FAILED=0",
        "QA_TESTS_ERRORS=0",
        "FINAL_PYTEST_EXIT_CODE=0",
    ])
    assert "PYTEST_EXECUTION_COUNT=3" not in text


def test_07_qa_formal_result_and_deviation_history_corrected() -> None:
    text = _qa_text()
    assert QA_RESULT in text
    assert "The original implementation gate executed pytest four times." in text
    assert "The original implementation gate limit was two executions." in text
    assert "Two additional executions occurred." in text
    assert "The procedural deviation review classified the deviation as material." in text
    assert "The correction gate validation is a separate phase." in text


def test_08_structural_absence_of_sensitive_data_in_both_documents() -> None:
    for text in (_qa_text(), _record_text()):
        assert re.search(r"[A-Za-z]:[\\/]", text) is None
        assert "/mnt/" not in text
        assert "/tmp/" not in text
        assert "\\\\" not in text
        for sensitive_key in [
            "file_names",
            "subdirectory_names",
            "real_folder_name",
            "real_file_name",
            "real_subdirectory_name",
            "media_sha256",
            "media_hash",
        ]:
            assert sensitive_key not in text
        assert "```json" not in text
