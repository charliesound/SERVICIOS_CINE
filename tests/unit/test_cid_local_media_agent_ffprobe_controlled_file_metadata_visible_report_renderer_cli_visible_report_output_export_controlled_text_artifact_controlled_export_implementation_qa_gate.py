from pathlib import Path
import ast
import hashlib
import importlib


DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_qa_gate_v1.md"
)

IMPLEMENTATION_DOC_PATH = Path(
    "docs/product/local_media_agent/"
    "cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation_v1.md"
)

IMPLEMENTATION_SCRIPT_PATH = Path(
    "scripts/local_media_agent/"
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_exporter.py"
)

IMPLEMENTATION_TEST_PATH = Path(
    "tests/unit/"
    "test_cid_local_media_agent_ffprobe_controlled_file_metadata_visible_report_renderer_cli_visible_report_output_export_controlled_text_artifact_controlled_export_implementation.py"
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

PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.IMPLEMENTATION.QA.GATE.V1"

PREVIOUS_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.IMPLEMENTATION.V1"

PREVIOUS_RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_IMPLEMENTATION_PASS_READY_FOR_QA_GATE"

RESULT = "LOCAL_MEDIA_AGENT_FFPROBE_CONTROLLED_FILE_METADATA_VISIBLE_REPORT_RENDERER_CLI_VISIBLE_REPORT_OUTPUT_EXPORT_CONTROLLED_TEXT_ARTIFACT_CONTROLLED_EXPORT_IMPLEMENTATION_QA_GATE_PASS_CLOSED"

NEXT_PHASE = "CID.LOCAL_MEDIA_AGENT.FFPROBE.CONTROLLED.FILE.METADATA.PREFLIGHT.VISIBLE.REPORT.RENDERER.CLI.VISIBLE.REPORT.OUTPUT.EXPORT.CONTROLLED.TEXT.ARTIFACT.CONTROLLED.EXPORT.IMPLEMENTATION.QA.GATE.CLOSURE.REVIEW.V1"

MODULE_NAME = (
    "scripts.local_media_agent."
    "ffprobe_controlled_file_metadata_visible_report_controlled_text_artifact_exporter"
)


def _module():
    return importlib.import_module(MODULE_NAME)


def _read_doc() -> str:
    return DOC_PATH.read_text(encoding="utf-8")


def _read_implementation_doc() -> str:
    return IMPLEMENTATION_DOC_PATH.read_text(encoding="utf-8")


def _read_implementation_source() -> str:
    return IMPLEMENTATION_SCRIPT_PATH.read_text(encoding="utf-8")


def test_controlled_export_implementation_qa_gate_files_exist():
    assert DOC_PATH.exists()
    assert IMPLEMENTATION_DOC_PATH.exists()
    assert IMPLEMENTATION_SCRIPT_PATH.exists()
    assert IMPLEMENTATION_TEST_PATH.exists()
    assert PREVIOUS_CLOSURE_TEST_PATH.exists()
    assert PREVIOUS_QA_GATE_TEST_PATH.exists()
    assert PREVIOUS_CONTRACT_TEST_PATH.exists()


def test_controlled_export_implementation_qa_gate_declares_phase_result_and_next_phase():
    text = _read_doc()

    assert f"`{PHASE}`" in text
    assert RESULT in text
    assert NEXT_PHASE in text
    assert "Required Next Phase" in text


def test_controlled_export_implementation_qa_gate_links_implementation_under_test():
    text = _read_doc()

    assert str(IMPLEMENTATION_DOC_PATH) in text
    assert str(IMPLEMENTATION_SCRIPT_PATH) in text
    assert str(IMPLEMENTATION_TEST_PATH) in text
    assert PREVIOUS_PHASE in text
    assert PREVIOUS_RESULT in text


def test_controlled_export_implementation_qa_gate_is_documentation_and_test_only():
    text = _read_doc()

    required_phrases = [
        "This phase is documentation and test-only.",
        "It does not add new runtime behavior.",
        "It does not modify the implementation.",
        "It does not write output files.",
        "It does not create filesystem artifacts.",
        "It does not read real media.",
        "It does not scan folders.",
        "It does not execute ffprobe or FFmpeg.",
        "It does not spawn subprocesses or processes.",
        "It does not access network resources.",
        "It does not touch SaaS systems or database systems.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_qa_gate_lists_assertions():
    text = _read_doc()

    required_phrases = [
        "Exposes `build_controlled_text_artifact_descriptor`.",
        "Produces a deterministic in-memory descriptor.",
        "Preserves controlled visible report text as `content_text`.",
        "Produces deterministic `line_count`.",
        "Produces deterministic `byte_count`.",
        "Produces deterministic `content_sha256`.",
        "Produces a sanitized deterministic `suggested_filename`.",
        "Declares `write_performed` as false.",
        "Declares `artifact_created_on_disk` as false.",
        "Declares complete safety flags.",
        "Imports no filesystem, network, process, media, SaaS, or database tooling.",
        "Performs no file writes.",
        "Performs no process execution.",
        "Provides no CLI entrypoint.",
        "Accepts no arbitrary filesystem path argument.",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_qa_gate_descriptor_contract_is_deterministic():
    module = _module()

    text = "Controlled Visible Report\nScene: 01\nStatus: SAFE\n"
    first = module.build_controlled_text_artifact_descriptor(
        visible_report_text=text,
        controlled_source_id="qa gate/scene 01",
    )
    second = module.build_controlled_text_artifact_descriptor(
        visible_report_text=text,
        controlled_source_id="qa gate/scene 01",
    )

    assert first == second
    assert first["artifact_format"] == "text/plain; charset=utf-8"
    assert first["suggested_filename"] == "qa_gate_scene_01.controlled_visible_report.txt"
    assert first["content_text"] == text
    assert first["line_count"] == 3
    assert first["byte_count"] == len(text.encode("utf-8"))
    assert first["content_sha256"] == hashlib.sha256(text.encode("utf-8")).hexdigest()
    assert first["source_boundary"] == "already_safe_controlled_visible_report_text"
    assert first["write_performed"] is False
    assert first["artifact_created_on_disk"] is False


def test_controlled_export_implementation_qa_gate_safety_flags_are_complete_and_true():
    module = _module()

    descriptor = module.build_controlled_text_artifact_descriptor(
        visible_report_text="Controlled Visible Report\n",
        controlled_source_id="qa gate",
    )

    expected_flags = {
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

    assert set(descriptor["safety_flags"]) == expected_flags
    assert all(descriptor["safety_flags"].values())


def test_controlled_export_implementation_qa_gate_safety_flags_are_defensive_copies():
    module = _module()

    descriptor = module.build_controlled_text_artifact_descriptor(
        visible_report_text="Controlled Visible Report\n",
        controlled_source_id="qa gate",
    )
    descriptor["safety_flags"]["no_network_access"] = False

    fresh_descriptor = module.build_controlled_text_artifact_descriptor(
        visible_report_text="Controlled Visible Report\n",
        controlled_source_id="qa gate",
    )

    assert fresh_descriptor["safety_flags"]["no_network_access"] is True


def test_controlled_export_implementation_qa_gate_rejects_invalid_inputs():
    module = _module()

    invalid_values = [None, "", "   ", 123, b"bytes"]

    for value in invalid_values:
        try:
            module.build_controlled_text_artifact_descriptor(
                visible_report_text=value,
                controlled_source_id="qa gate",
            )
        except (TypeError, ValueError):
            pass
        else:
            raise AssertionError(f"invalid visible_report_text accepted: {value!r}")

        try:
            module.build_controlled_text_artifact_descriptor(
                visible_report_text="Controlled Visible Report\n",
                controlled_source_id=value,
            )
        except (TypeError, ValueError):
            pass
        else:
            raise AssertionError(f"invalid controlled_source_id accepted: {value!r}")


def test_controlled_export_implementation_qa_gate_filename_sanitization_blocks_path_semantics():
    module = _module()

    descriptor = module.build_controlled_text_artifact_descriptor(
        visible_report_text="Controlled Visible Report\n",
        controlled_source_id="../bad path/scene:01",
    )

    filename = descriptor["suggested_filename"]

    assert filename == "bad_path_scene_01.controlled_visible_report.txt"
    assert "/" not in filename
    assert "\\" not in filename
    assert ".." not in filename
    assert not filename.startswith(".")


def test_controlled_export_implementation_qa_gate_source_has_no_forbidden_imports():
    tree = ast.parse(_read_implementation_source())

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


def test_controlled_export_implementation_qa_gate_source_has_no_file_write_or_execution_calls():
    tree = ast.parse(_read_implementation_source())

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


def test_controlled_export_implementation_qa_gate_source_has_no_cli_or_path_arguments():
    source = _read_implementation_source().lower()

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
        "upload",
        "download",
    ]

    for phrase in forbidden_phrases:
        assert phrase not in source

    assert "no_ffprobe_execution" in source
    assert "no_ffmpeg_execution" in source


def test_controlled_export_implementation_qa_gate_validates_implementation_doc_boundary():
    text = _read_implementation_doc()

    required_phrases = [
        PREVIOUS_PHASE,
        PREVIOUS_RESULT,
        "pure in-memory controlled text artifact descriptor",
        "It does not write output files.",
        "It does not create filesystem artifacts.",
        "It does not accept arbitrary output paths.",
        "It does not accept arbitrary input folders.",
        "It does not read real media.",
        "It does not scan folders.",
        "It does not execute ffprobe or FFmpeg.",
        "It does not access network resources.",
        "It does not touch SaaS systems or database systems.",
        "Closing this implementation only authorizes a pure in-memory controlled text artifact descriptor",
    ]

    for phrase in required_phrases:
        assert phrase in text


def test_controlled_export_implementation_qa_gate_lists_required_validation_evidence():
    text = _read_doc()

    required_phrases = [
        "Python compile check for this QA gate test.",
        "This QA gate unit test.",
        "Previous implementation unit test.",
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


def test_controlled_export_implementation_qa_gate_does_not_claim_disk_export_or_client_readiness():
    combined = f"{_read_doc()}\n{_read_implementation_doc()}\n{_read_implementation_source()}".lower()

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


def test_controlled_export_implementation_qa_gate_test_source_has_no_external_execution_or_network_imports():
    tree = ast.parse(TEST_PATH.read_text(encoding="utf-8"))

    forbidden_import_roots = {
        "subprocess",
        "socket",
        "requests",
        "httpx",
        "urllib",
        "ftplib",
        "smtplib",
    }

    imported_roots = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert imported_roots.isdisjoint(forbidden_import_roots)
