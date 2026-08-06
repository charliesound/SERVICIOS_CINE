from __future__ import annotations

import re
from pathlib import Path

RECORD_DOC = Path(
    "docs/product/local_media_agent/cid_local_media_agent_controlled_own_real_material_single_scan_sanitized_execution_record_v1.md"
)

RECORD_PHASE = (
    "CID.LOCAL_MEDIA_AGENT.READ_ONLY_FOLDER_SCANNER.COMMERCIAL_ALIAS.WINDOWS_HOST_DRIVE."
    "CONTROLLED_OWN_REAL_MATERIAL.SINGLE_SCAN.SANITIZED_EXECUTION.RECORD.V1"
)
RECORD_RESULT = "CID_LOCAL_MEDIA_AGENT_CONTROLLED_OWN_REAL_MATERIAL_SINGLE_SCAN_SANITIZED_EXECUTION_RECORD_V1_COMPLETED"

ALLOWED_CODE_HASHES = {
    "1d0dc95cff6d69cf973780452eea3087cc86af0ff5b07a63595157d77f3722c7",
    "1d8df7aeaf9a94df112f7f55ffcbdf95564188c9bafcf5dc1359aebffa49a2f6",
    "255cc5630a9bf2f32b20bdfb91fd498396624d8c064d708af53be5bc1d12fe59",
    "f48ce145afef969a2fc2866ce1b40f50cd699f3ea3d2bfa96d1454337de399b2",
    "ed0909b210356d4861fdf2781f8305ddbe83ce056bceb185d1bfbd505af63855",
}


def _text() -> str:
    return RECORD_DOC.read_text(encoding="utf-8")


def _assert_all_present(text: str, items: list[str]) -> None:
    for item in items:
        assert item in text


def _sha256_hex_occurrences(text: str) -> set[str]:
    return set(re.findall(r"\b[0-9a-f]{64}\b", text))


def test_01_record_doc_exists_and_is_utf8() -> None:
    assert RECORD_DOC.is_file()
    assert not RECORD_DOC.is_symlink()
    text = _text()
    assert isinstance(text, str)
    assert text.strip()


def test_02_phase_identity_and_formal_result() -> None:
    text = _text()
    assert RECORD_PHASE in text
    assert RECORD_RESULT in text


def test_03_stable_git_identity_and_tag() -> None:
    text = _text()
    _assert_all_present(text, [
        "STABLE_COMMIT_SHA=",
        "e97cd06f2e2fa84b01e64cac16cae8fe62ab3d74",
        "STABLE_TREE_SHA=",
        "299c402c9ca64864c3cae49ca1b7e97613c3de66",
        "STABLE_PARENT_SHA=",
        "34a0dc2f6da8701ec70785c4dbc7be206b79823b",
        "STABLE_COMMIT_SUBJECT=",
        "feat: add CID Local Media Agent Windows host path portability",
        "STABLE_TAG=",
        "cid-dev-stable-local-media-agent-read-only-folder-scanner-commercial-alias-windows-host-drive-path-portability-v1-20260806",
    ])


def test_04_schema_status_label_execution_count_and_exit_code() -> None:
    text = _text()
    _assert_all_present(text, [
        "SCAN_STATUS=READ_ONLY_FOLDER_SCAN_COMPLETED",
        "SCAN_SCHEMA_VERSION=cid.local_media_agent.read_only_folder_scanner.v1",
        "SCAN_INPUT_LABEL=SANITIZED_LOCAL_FOLDER_INPUT",
        "SCAN_EXECUTION_COUNT=1",
        "SCAN_EXIT_CODE=0",
    ])


def test_05_aggregated_counts_exact() -> None:
    text = _text()
    _assert_all_present(text, [
        "FILES_SEEN=249",
        "DIRECTORIES_SEEN=146",
        "MEDIA_CANDIDATES=160",
        "VIDEO_FILES=16",
        "AUDIO_FILES=136",
        "IMAGE_FILES=8",
        "NON_MEDIA_FILES=89",
        "ERROR_COUNT=0",
        "WARNING_COUNT=0",
    ])


def test_06_three_arithmetic_invariants() -> None:
    text = _text()
    _assert_all_present(text, [
        "FILES_ACCOUNTING_FORMULA=249=160+89",
        "MEDIA_ACCOUNTING_FORMULA=160=16+136+8",
        "TOTAL_CLASSIFICATION_FORMULA=249=16+136+8+89",
        "FILES_ACCOUNTING_VALID=True",
        "MEDIA_ACCOUNTING_VALID=True",
        "TOTAL_CLASSIFICATION_VALID=True",
    ])


def test_07_limits_depth_and_no_truncation() -> None:
    text = _text()
    _assert_all_present(text, [
        "MAX_FILES=5000",
        "MAX_DEPTH=8",
        "MAX_ERRORS=100",
        "MAX_OBSERVED_DEPTH=7",
        "TRUNCATED=False",
        "MAX_FILES_REACHED=False",
        "MAX_DEPTH_REACHED=False",
        "MAX_ERRORS_REACHED=False",
    ])


def test_08_errors_warnings_and_stderr() -> None:
    text = _text()
    _assert_all_present(text, [
        "ERROR_COUNT=0",
        "WARNING_COUNT=0",
        "SCAN_STDERR_BYTES=0",
        "The scan completed without errors.",
        "The scan completed without warnings.",
        "The scan produced no stderr.",
    ])


def test_09_full_privacy_contract() -> None:
    text = _text()
    _assert_all_present(text, [
        "PRIVACY_FILE_CONTENTS_OPENED=False",
        "PRIVACY_CONTENT_HASHES_COMPUTED=False",
        "PRIVACY_FFPROBE_EXECUTED=False",
        "PRIVACY_FFMPEG_EXECUTED=False",
        "PRIVACY_NETWORK_USED=False",
        "PRIVACY_DATABASE_USED=False",
        "PRIVACY_SUBPROCESS_USED=False",
        "PRIVACY_ORIGINAL_MEDIA_MODIFIED=False",
        "PRIVACY_SAAS_USED=False",
        "PRIVACY_ARTIFACT_WRITTEN=False",
        "READ_ONLY_CONTRACT_PRESERVED=True",
        "METADATA_ONLY_CONTRACT_PRESERVED=True",
        "PRIVACY_CONTRACT_VALID=True",
    ])


def test_10_read_only_metadata_only_contract_and_root_scope() -> None:
    text = _text()
    _assert_all_present(text, [
        "AUTHORIZED_ROOT_ONLY=True",
        "OTHER_DRIVES_ENUMERATED=False",
        "DRIVE_ROOT_ACCESSED=False",
        "PARENT_DIRECTORY_SCANNED=False",
        "SIBLING_DIRECTORY_SCANNED=False",
        "DIRECT_MNT_INPUT_USED=False",
        "SANITIZED_CLIENT_SELECTED_LOCAL_ROOT",
        "SANITIZED_HOST_VOLUME",
    ])


def test_11_wsl_scope_demonstrated_and_windows_unc_non_claims() -> None:
    text = _text()
    _assert_all_present(text, [
        "WSL_REAL_FILESYSTEM_BRIDGE_EMPIRICALLY_EXECUTED=True",
        "CONTROLLED_WINDOWS_HOST_PATH_ACCEPTED=True",
        "CONTROLLED_WINDOWS_HOST_PATH_TRANSLATED=True",
        "CONTROLLED_REAL_FOLDER_ENUMERATED=True",
        "CONTROLLED_REAL_FILESYSTEM_METADATA_READ=True",
        "WINDOWS_NATIVE_RUNTIME_EMPIRICALLY_EXECUTED=False",
        "WINDOWS_NATIVE_INSTALLER_VALIDATED=False",
        "WINDOWS_NATIVE_CI_REQUIRED_LATER=True",
        "UNC_SUPPORT_VALIDATED=False",
        "NETWORK_SHARE_SUPPORT_VALIDATED=False",
        "CUSTOMER_WSL_REQUIREMENT_INFERRED=False",
        "CUSTOMER_MEDIA_COPY_REQUIREMENT_INFERRED=False",
        "WINDOWS_DRIVE_LETTER_HARD_CODED=False",
        "DEFAULT_WINDOWS_DRIVE_REQUIRED=False",
        "SPECIFIC_WINDOWS_DRIVE_REQUIRED=False",
        "AUTOMATIC_DRIVE_ENUMERATION=False",
        "WSL_DEVELOPMENT_BRIDGE_ONLY=True",
        "WSL_REQUIRED_FOR_CUSTOMERS=False",
        "CUSTOMER_MEDIA_COPY_REQUIRED=False",
        "CLIENT_SELECTED_LOCAL_ROOT_ACCEPTED=True",
        "CLIENT_SELECTED_LOCAL_ROOT_ENUMERATED=True",
        "CLIENT_SELECTED_LOCAL_ROOT_METADATA_READ=True",
        "TEST_EXECUTION_HOST_VOLUME_REDACTED=True",
        "COMMERCIAL_PRODUCT_SUPPORTS_CLIENT_SELECTED_LOCAL_ROOT=True",
        "COMMERCIAL_PATH_POLICY_IS_VOLUME_AGNOSTIC=True",
        "COMMERCIAL_PATH_POLICY_IS_CROSS_PLATFORM=True",
        "CLIENT_SELECTED_LOCAL_ROOT_REQUIRED=True",
        "CLIENT_SELECTED_LOCAL_VOLUME_SUPPORTED=True",
        "CLIENT_SELECTED_ROOT_ONLY=True",
        "PARENT_DIRECTORY_ENUMERATION=False",
        "SIBLING_DIRECTORY_ENUMERATION=False",
        "OTHER_VOLUME_ENUMERATION=False",
        "WINDOWS_NATIVE_RUNTIME_EXPECTS_DIRECT_HOST_PATH=True",
        "TEST_EXECUTION_USED_ONE_REDACTED_LOCAL_VOLUME=True",
        "TEST_EXECUTION_VOLUME_IS_NOT_PRODUCT_DEFAULT=True",
        "TEST_EXECUTION_PATH_IS_NOT_PRODUCT_DEFAULT=True",
    ])


def test_12_structural_absence_of_sensitive_data() -> None:
    text = _text()
    assert re.search(r"[A-Za-z]:[\\/]", text) is None
    assert "/mnt/" not in text
    assert "/tmp/" not in text
    assert "\\\\" not in text
    _assert_all_present(text, [
        "RECORD_CONTAINS_REAL_MEDIA_PATH=False",
        "RECORD_CONTAINS_REAL_FILE_NAMES=False",
        "RECORD_CONTAINS_MEDIA_HASHES=False",
    ])
    for sensitive_key in [
        "file_names",
        "subdirectory_names",
        "file_name",
        "subdirectory_name",
        "media_sha256",
        "media_hash",
        "individual_file_size",
        "individual_file_timestamp",
        "individual_file_permission",
        "individual_file_inode",
    ]:
        assert sensitive_key not in text
    assert "```json" not in text
    assert '"files"' not in text
    assert '"scanned_files"' not in text
    found_hashes = _sha256_hex_occurrences(text)
    assert found_hashes and found_hashes == ALLOWED_CODE_HASHES
