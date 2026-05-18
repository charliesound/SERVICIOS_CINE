from __future__ import annotations

import importlib.util
import mimetypes
import zipfile
from pathlib import Path
from typing import Any, Optional
from xml.etree import ElementTree as ET

from services.script_document_classifier import SCENE_HEADING_RE


class ScriptDocumentConversionService:
    SUPPORTED_FORMATS = {"txt", "md", "pdf", "docx"}

    def detect_document_type(self, path: str | Path, mime_type: str | None) -> str:
        file_path = Path(path)
        extension = file_path.suffix.lower().lstrip(".")
        normalized_mime = (mime_type or mimetypes.guess_type(str(file_path))[0] or "").strip().lower()
        if extension in self.SUPPORTED_FORMATS:
            return extension
        if normalized_mime in {"text/plain"}:
            return "txt"
        if normalized_mime in {"text/markdown", "text/x-markdown"}:
            return "md"
        if normalized_mime == "application/pdf":
            return "pdf"
        if normalized_mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return "docx"
        return extension or "unknown"

    def extract_text_from_pdf(self, path: str | Path) -> str:
        from pypdf import PdfReader

        reader = PdfReader(str(path))
        parts: list[str] = []
        for page in reader.pages:
            text = page.extract_text() or ""
            if text.strip():
                parts.append(text.strip())
        return "\n\n".join(parts).strip()

    def pdf_needs_ocr(self, path: str | Path) -> bool:
        return not bool(self.extract_text_from_pdf(path).strip())

    def ocr_pdf_to_text(self, path: str | Path) -> str:
        if not self._ocr_is_available():
            raise RuntimeError("OCR dependencies are not available")

        from pdf2image import convert_from_path
        import pytesseract

        pages = convert_from_path(str(path))
        parts: list[str] = []
        for page in pages:
            text = pytesseract.image_to_string(page) or ""
            if text.strip():
                parts.append(text.strip())
        return "\n\n".join(parts).strip()

    def docx_to_text(self, path: str | Path) -> str:
        namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        parts: list[str] = []
        with zipfile.ZipFile(path) as archive:
            for member in archive.namelist():
                if not member.startswith("word/") or not member.endswith(".xml"):
                    continue
                root = ET.fromstring(archive.read(member))
                for paragraph in root.findall(".//w:p", namespace):
                    text_nodes = [node.text or "" for node in paragraph.findall(".//w:t", namespace)]
                    joined = "".join(text_nodes).strip()
                    if joined:
                        parts.append(joined)
        return "\n".join(parts).strip()

    def text_to_markdown(self, text: str) -> str:
        normalized_lines = [line.rstrip() for line in (text or "").replace("\r\n", "\n").replace("\r", "\n").split("\n")]
        markdown_lines: list[str] = []
        previous_blank = True

        for raw_line in normalized_lines:
            line = raw_line.strip()
            if not line:
                if not previous_blank:
                    markdown_lines.append("")
                previous_blank = True
                continue

            if SCENE_HEADING_RE.match(line):
                if markdown_lines and markdown_lines[-1] != "":
                    markdown_lines.append("")
                markdown_lines.append(line.upper())
                markdown_lines.append("")
                previous_blank = True
                continue

            markdown_lines.append(line)
            previous_blank = False

        while markdown_lines and markdown_lines[-1] == "":
            markdown_lines.pop()
        return "\n".join(markdown_lines).strip()

    def convert_uploaded_script_to_markdown(
        self,
        *,
        path: str | Path,
        mime_type: str | None = None,
    ) -> dict[str, Any]:
        file_path = Path(path)
        detected_format = self.detect_document_type(file_path, mime_type)
        extracted_text = ""
        extraction_method = "unsupported"

        if detected_format == "txt":
            extracted_text = self._read_text(file_path)
            extraction_method = "text_direct"
        elif detected_format == "md":
            extracted_text = self._read_text(file_path)
            extraction_method = "markdown_direct"
        elif detected_format == "pdf":
            extracted_text = self.extract_text_from_pdf(file_path)
            if extracted_text.strip():
                extraction_method = "pdf_text"
            elif self._ocr_is_available():
                extracted_text = self.ocr_pdf_to_text(file_path)
                extraction_method = "pdf_ocr"
            else:
                extraction_method = "pdf_ocr_required"
        elif detected_format == "docx":
            extracted_text = self.docx_to_text(file_path)
            extraction_method = "docx_text"
        else:
            raise RuntimeError(f"Unsupported script format: {detected_format}")

        markdown_text = extracted_text if detected_format == "md" else self.text_to_markdown(extracted_text)
        markdown_available = bool(markdown_text.strip())
        return {
            "detected_format": detected_format,
            "extraction_method": extraction_method,
            "raw_text": extracted_text,
            "markdown_text": markdown_text,
            "analysis_text": markdown_text or extracted_text,
            "markdown_available": markdown_available,
            "text_length": len((markdown_text or extracted_text).strip()),
        }

    def _read_text(self, path: Path) -> str:
        for encoding in ("utf-8-sig", "utf-8", "latin-1"):
            try:
                return path.read_text(encoding=encoding)
            except UnicodeDecodeError:
                continue
        return path.read_text(errors="ignore")

    def _ocr_is_available(self) -> bool:
        return bool(importlib.util.find_spec("pytesseract") and importlib.util.find_spec("pdf2image"))


script_document_conversion_service = ScriptDocumentConversionService()


def detect_document_type(path: str | Path, mime_type: str | None) -> str:
    return script_document_conversion_service.detect_document_type(path, mime_type)


def extract_text_from_pdf(path: str | Path) -> str:
    return script_document_conversion_service.extract_text_from_pdf(path)


def pdf_needs_ocr(path: str | Path) -> bool:
    return script_document_conversion_service.pdf_needs_ocr(path)


def ocr_pdf_to_text(path: str | Path) -> str:
    return script_document_conversion_service.ocr_pdf_to_text(path)


def docx_to_text(path: str | Path) -> str:
    return script_document_conversion_service.docx_to_text(path)


def text_to_markdown(text: str) -> str:
    return script_document_conversion_service.text_to_markdown(text)


def convert_uploaded_script_to_markdown(*, path: str | Path, mime_type: str | None = None) -> dict[str, Any]:
    return script_document_conversion_service.convert_uploaded_script_to_markdown(path=path, mime_type=mime_type)
