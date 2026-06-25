from pathlib import Path
import ast
import hashlib
import importlib


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_v1.md"
)

SCRIPT_PATH = Path(
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_exporter.py"
)

PREVIOUS_CLOSURE_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_contract_qa_gate_closure_review_v1.md"
)

PREVIOUS_CLOSURE_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_contract_qa_gate_closure_review.py"
)

PREVIOUS_QA_GATE_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_contract_qa_gate.py"
)

PREVIOUS_CONTRACT_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_contract.py"
)

TEST_PATH = Path(__file__)

PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.IMPLEMENTATION.V1"

PREVIOUS_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.IMPLEMENTATION.CONTRACT.QA.GATE.CLOSURE.REVIEW.V1"

PREVIOUS_RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_IMPLEMENTATION_CONTRACT_QA_GATE_CLOSURE_REVIEW_PASS_READY_FOR_CONTROLLED_EXPORT_IMPLEMENTATION"

RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_IMPLEMENTATION_PASS_READY_FOR_QA_GATE"

NEXT_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.IMPLEMENTATION.QA.GATE.V1"

MODULE_NAME = (
    "scripts.local_media_agent."
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_exporter"
)


def _module():
    return importlib.import_module(MODULE_NAME)


def _read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def _read_script_source() -> str:
    return SCRIPT_PATH.read_text(encoding="utf-8")


def _read_previous_closure_doc() -> str:
    return PREVIOUS_CLOSURE_DOC_PATH.read_text(encoding="utf-8")


def test_controlled_export_implementation_files_exist():
    assert DOC_PATH.exists()
    assert SCRIPT_PATH.exists()
    assert TEST_PATH.exists()


def test_controlled_export_implementation_dependencies_exist():
    assert PREVIOUS_CLOSURE_DOC_PATH.exists()
    assert PREVIOUS_CLOSURE_TEST_PATH.exists()
    assert PREVIOUS_QA_GATE_TEST_PATH.exists()
    assert PREVIOUS_CONTRACT_TEST_PATH.exists()


def test_controlled_export_implementation_doc_declares_phase_result_and_next_phase():
    text = _read_doc()

    assert f"`{PHASE}`" in text
    assert RESULT in text
    assert NEXT_PHASE in text
    assert "Required Next Phase" in text


def test_controlled_export_implementation_doc_links_previous_closure_review():
    text = _read_doc()

    assert str(PREVIOUS_CLOSURE_DOC_PATH) in text
    assert str(PREVIOUS_CLOSURE_TEST_PATH) in text
    assert PREVIOUS_PHASE in text
    assert PREVIOUS_RESULT in text


def test_controlled_export_implementation_doc_declares_runtime_boundary():
    text = _read_doc()

    required_phrases = [
        "pure in-memory controlled text artifact descriptor",
        "`build_controlled_text_artifact_descriptor`",
        "`visible_report_text`, which must already be safe controlled visible report text.",
        "`controlled_source_id`, which is used only to derive a deterministic safe suggested filename.",
        "`write_performed`",
        "`artifact_created_on_disk`",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_doc_rejects_unsafe_scope():
    text = _read_doc()

    required_phrases = [
        "It does not write output files.",
        "It does not create filesystem artifacts.",
        "It does not accept arbitrary output paths.",
        "It does not accept arbitrary input folders.",
        "It does not read real media.",
        "It does not scan folders.",
        "It does not execute ffprobe or FFmpeg.",
        "It does not spawn subprocesses or processes.",
        "It does not access network resources.",
        "It does not touch SaaS systems or database systems.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_descriptor_shape_and_hash_are_deterministic():
    module = _module()

    text = "CID Controlled Visible Report\nClip count: 2\nStatus: SAFE\n"
    descriptor = module.build_controlled_text_artifact_descriptor(
        visible_report_text=text,
        controlled_source_id="fixture alpha/scene 01",
    )
    repeated_descriptor = module.build_controlled_text_artifact_descriptor(
        visible_report_text=text,
        controlled_source_id="fixture alpha/scene 01",
    )

    assert descriptor == repeated_descriptor
    assert descriptor["artifact_format"] == "text/plain; charset=utf-8"
    assert descriptor["suggested_filename"] == "fixture_alpha_scene_01.controlled_visible_report.txt"
    assert descriptor["content_text"] == text
    assert descriptor["line_count"] == 3
    assert descriptor["byte_count"] == len(text.encode("utf-8"))
    assert descriptor["content_sha256"] == hashlib.sha256(text.encode("utf-8")).hexdigest()
    assert descriptor["source_boundary"] == "already_safe_controlled_visible_report_text"
    assert descriptor["write_performed"] is False
    assert descriptor["artifact_created_on_disk"] is False


def test_controlled_export_implementation_descriptor_contains_complete_safety_flags():
    module = _module()

    descriptor = module.build_controlled_text_artifact_descriptor(
        visible_report_text="Controlled report\n",
        controlled_source_id="controlled fixture",
    )

    expected_true_flags = {
        "no_real_media",
        "no_arbitrary_folders",
        "no_scanner_execution",
        "no_ffprobe_execution",
        "no_ffmpeg_execution",
        "no_subprocess_execution",
        "no_process_execution",
        "no_audio_extraction",
        "no_sync",
        "no_transcription",
        "no_subtitles",
        "no_timeline_export",
        "no_network_access",
        "no_saas_db_access",
        "no_installer_behavior",
        "no_public_demo_behavior",
        "no_client_demo_behavior",
        "no_sales_demo_behavior",
        "no_production_behavior",
    }

    assert set(descriptor["safety_flags"]) == expected_true_flags
    assert all(descriptor["safety_flags"].values())


def test_controlled_export_implementation_descriptor_safety_flags_are_defensive_copies():
    module = _module()

    first = module.build_controlled_text_artifact_descriptor(
        visible_report_text="Controlled report A\n",
        controlled_source_id="fixture-a",
    )
    first["safety_flags"]["no_real_media"] = False

    second = module.build_controlled_text_artifact_descriptor(
        visible_report_text="Controlled report A\n",
        controlled_source_id="fixture-a",
    )

    assert second["safety_flags"]["no_real_media"] is True


def test_controlled_export_implementation_rejects_invalid_visible_report_text():
    module = _module()

    invalid_values = [None, "", "   ", 123, b"bytes"]

    for value in invalid_values:
        try:
            module.build_controlled_text_artifact_descriptor(
                visible_report_text=value,
                controlled_source_id="fixture",
            )
        except (TypeError, ValueError):
            continue

        raise AssertionError(f"invalid value was accepted: {value!r}")


def test_controlled_export_implementation_rejects_invalid_controlled_source_id():
    module = _module()

    invalid_values = [None, "", "   ", 123, b"bytes"]

    for value in invalid_values:
        try:
            module.build_controlled_text_artifact_descriptor(
                visible_report_text="Controlled report\n",
                controlled_source_id=value,
            )
        except (TypeError, ValueError):
            continue

        raise AssertionError(f"invalid value was accepted: {value!r}")


def test_controlled_export_implementation_filename_sanitization_is_deterministic_and_safe():
    module = _module()

    descriptor = module.build_controlled_text_artifact_descriptor(
        visible_report_text="Controlled report\n",
        controlled_source_id="../unsafe path/with spaces:scene#1",
    )

    filename = descriptor["suggested_filename"]

    assert filename == "unsafe_path_with_spaces_scene_1.controlled_visible_report.txt"
    assert "/" not in filename
    assert "\\" not in filename
    assert ".." not in filename
    assert not filename.startswith(".")


def test_controlled_export_implementation_source_has_no_forbidden_imports():
    tree = ast.parse(_read_script_source())

    forbidden_import_roots = {
        "subprocess",
        "socket",
        "requests",
        "httpx",
        "urllib",
        "pathlib",
        "os",
        "shutil",
        "tempfile",
        "sqlite3",
        "psycopg",
        "sqlalchemy",
    }

    imported_roots = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert imported_roots.isdisjoint(forbidden_import_roots)


def test_controlled_export_implementation_source_has_no_file_write_or_execution_calls():
    tree = ast.parse(_read_script_source())

    forbidden_attribute_names = {
        "write" + "_text",
        "write" + "_bytes",
        "open",
        "mkdir",
        "unlink",
        "rename",
        "replace",
        "rmdir",
        "touch",
        "run",
        "Popen",
        "system",
        "execv",
        "execve",
        "spawn",
    }

    forbidden_call_names = {
        "open",
        "exec",
        "eval",
        "compile",
    }

    observed_forbidden_attributes = {
        node.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute) and node.attr in forbidden_attribute_names
    }

    observed_forbidden_calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in forbidden_call_names
    }

    assert observed_forbidden_attributes == set()
    assert observed_forbidden_calls == set()


def test_controlled_export_implementation_source_has_no_cli_or_path_arguments():
    source = _read_script_source().lower()

    forbidden_phrases = [
        "argparse",
        "click",
        "typer",
        "sys.argv",
        "output_path",
        "input_path",
        "media_folder",
        "folder_path",
        "ffprobe command",
        "ffmpeg command",
        "ffprobe_path",
        "ffmpeg_path",
        "ffprobe_binary",
        "ffmpeg_binary",
        "upload",
        "download",
    ]

    for phrase in forbidden_phrases:
        assert phrase not in source

    allowed_negative_safety_flags = [
        "no_ffprobe_execution",
        "no_ffmpeg_execution",
    ]

    for phrase in allowed_negative_safety_flags:
        assert phrase in source


def test_controlled_export_implementation_validates_previous_closure_review_boundary():
    previous_text = _read_previous_closure_doc()

    required_phrases = [
        PREVIOUS_PHASE,
        PREVIOUS_RESULT,
        "the chain may proceed only to a future explicitly named controlled export implementation phase.",
        "pure local-only in-memory descriptor for already-safe controlled visible report text.",
        "That future phase must not write output files.",
        "That future phase must not create filesystem artifacts.",
        "That future phase must not read real media.",
        "That future phase must not execute ffprobe or FFmpeg.",
        "That future phase must not access network resources.",
    ]

    for phrase in required_phrases:
        assert phrase in previous_text


def test_controlled_export_implementation_does_not_claim_disk_export_or_client_readiness():
    combined = f"{_read_doc()}\n{_read_script_source()}".lower()

    forbidden_claims = [
        "ready for production",
        "client-ready",
        "sales-ready",
        "public demo ready",
        "real media ready",
        "disk export ready",
        "export file created",
        "artifact created on disk",
        "runtime exporter writes files",
        "users can export",
        "installer ready",
    ]

    for claim in forbidden_claims:
        assert claim not in combined


def test_controlled_export_implementation_lists_required_validation_evidence():
    text = _read_doc()

    required_phrases = [
        "Python compile check for the implementation file.",
        "Python compile check for this implementation test.",
        "This implementation unit test.",
        "Previous contract QA gate closure review unit test.",
        "Previous contract QA gate unit test.",
        "Previous contract unit test.",
        "WSL repository guard.",
        "Database backend regression guard.",
        "Diff check.",
        "Protected files check.",
        "Target tag absence check locally and remotely.",
    ]

    for phrase in required_phrases:
        assert phrase in text
