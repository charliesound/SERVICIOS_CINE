from __future__ import annotations

import asyncio
import os
import sys
import uuid
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
os.environ.setdefault("AUTH_SECRET_KEY", "AilinkCinemaAuthRuntimeValue987654321XYZ")
os.environ.setdefault("APP_SECRET_KEY", "AilinkCinemaAppRuntimeValue987654321XYZ")
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from models.document import ProjectDocumentType  # noqa: E402
from services.project_document_service import ProjectDocumentService  # noqa: E402
from services.script_document_conversion_service import ScriptDocumentConversionService  # noqa: E402
from services.script_intake_service import ScriptIntakeService  # noqa: E402


class _FakeDb:
    def add(self, obj) -> None:
        if getattr(obj, "id", None) is None:
            setattr(obj, "id", str(uuid.uuid4()))

    async def flush(self) -> None:
        return None

    async def commit(self) -> None:
        return None

    async def refresh(self, _obj) -> None:
        return None


def test_txt_generates_markdown(tmp_path: Path) -> None:
    service = ScriptDocumentConversionService()
    source = tmp_path / "script.txt"
    source.write_text("INT. CASA - NOCHE\n\nMarta entra con una linterna.", encoding="utf-8")

    result = service.convert_uploaded_script_to_markdown(path=source, mime_type="text/plain")

    assert result["detected_format"] == "txt"
    assert result["extraction_method"] == "text_direct"
    assert result["markdown_text"]
    assert "INT. CASA - NOCHE" in result["markdown_text"]


def test_md_is_preserved(tmp_path: Path) -> None:
    service = ScriptDocumentConversionService()
    source = tmp_path / "script.md"
    source.write_text("INT. CASA - NOCHE\n\nMarta entra con una linterna.", encoding="utf-8")

    result = service.convert_uploaded_script_to_markdown(path=source, mime_type="text/markdown")

    assert result["detected_format"] == "md"
    assert result["extraction_method"] == "markdown_direct"
    assert result["markdown_text"] == source.read_text(encoding="utf-8")


def test_pdf_with_text_does_not_launch_ocr(monkeypatch, tmp_path: Path) -> None:
    service = ScriptDocumentConversionService()
    source = tmp_path / "script.pdf"
    source.write_bytes(b"%PDF-1.4")

    monkeypatch.setattr(service, "extract_text_from_pdf", lambda _path: "INT. CASA - NOCHE\nMarta entra con una linterna.")

    def _unexpected_ocr(_path):
        raise AssertionError("OCR should not run when PDF text is available")

    monkeypatch.setattr(service, "ocr_pdf_to_text", _unexpected_ocr)

    result = service.convert_uploaded_script_to_markdown(path=source, mime_type="application/pdf")

    assert result["extraction_method"] == "pdf_text"
    assert result["markdown_available"] is True


def test_pdf_without_text_marks_ocr_required_when_unavailable(monkeypatch, tmp_path: Path) -> None:
    service = ScriptDocumentConversionService()
    source = tmp_path / "scan.pdf"
    source.write_bytes(b"%PDF-1.4")

    monkeypatch.setattr(service, "extract_text_from_pdf", lambda _path: "")
    monkeypatch.setattr(service, "_ocr_is_available", lambda: False)

    result = service.convert_uploaded_script_to_markdown(path=source, mime_type="application/pdf")

    assert result["extraction_method"] == "pdf_ocr_required"
    assert result["markdown_available"] is False


def test_output_contains_non_empty_markdown(tmp_path: Path) -> None:
    service = ScriptDocumentConversionService()
    source = tmp_path / "scene.txt"
    source.write_text("EXT. CALLE - DIA\n\nUn coche se detiene.", encoding="utf-8")

    result = service.convert_uploaded_script_to_markdown(path=source, mime_type="text/plain")

    assert result["markdown_text"].strip()
    assert result["text_length"] > 0


def test_analysis_uses_clean_markdown_text(tmp_path: Path) -> None:
    conversion = ScriptDocumentConversionService()
    intake = ScriptIntakeService()
    source = tmp_path / "analysis.txt"
    source.write_text(
        "INT. CASA ABANDONADA - NOCHE\n\nMarta entra con una linterna.\n\nEXT. PATIO - DIA\n\nUn perro ladra.",
        encoding="utf-8",
    )

    result = conversion.convert_uploaded_script_to_markdown(path=source, mime_type="text/plain")
    scenes = intake.parse_script(result["analysis_text"])

    assert len(scenes) == 2
    assert scenes[0]["heading"] == "INT. CASA ABANDONADA - NOCHE"


def test_project_document_import_updates_project_script_text(monkeypatch, tmp_path: Path) -> None:
    service = ProjectDocumentService()
    service.storage_root = tmp_path
    fake_db = _FakeDb()
    project = SimpleNamespace(id="project-1", organization_id="org-1", script_text=None)

    async def _index_document(_db, *, document, force=True):
        del force
        assert document.extracted_text
        return 1

    async def _enqueue_matcher(*args, **kwargs):
        return None

    monkeypatch.setattr("services.project_document_service.project_document_rag_service.index_document", _index_document)
    monkeypatch.setattr(service, "_enqueue_matcher_job_for_document_update", _enqueue_matcher)

    document = asyncio.run(
        service.import_document_bytes(
            fake_db,
            project=project,
            uploaded_by_user_id="user-1",
            document_type=ProjectDocumentType.SCRIPT,
            visibility_scope="project",
            file_name="script.txt",
            mime_type="text/plain",
            file_bytes=b"INT. CASA - NOCHE\n\nMarta entra con una linterna.",
        )
    )

    assert project.script_text
    assert "INT. CASA - NOCHE" in project.script_text
    assert document.extracted_text == project.script_text
    assert getattr(document, "detected_format", None) == "txt"
    assert getattr(document, "markdown_available", None) is True
