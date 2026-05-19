from __future__ import annotations

import io
import os
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.script_file_normalization_service import ScriptFileNormalizationService


def _build_minimal_docx_bytes(paragraphs: list[str]) -> bytes:
    xml_parts = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>']
    for paragraph in paragraphs:
        xml_parts.append(f'<w:p><w:r><w:t>{paragraph}</w:t></w:r></w:p>')
    xml_parts.append('</w:body></w:document>')
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('word/document.xml', ''.join(xml_parts))
    return buffer.getvalue()


def test_normalize_txt_keeps_sluglines() -> None:
    service = ScriptFileNormalizationService()
    result = service.normalize_script_file(
        file_bytes=b"59 EXT/INT. PARKING/COCHE. DIA.\nMANU corre hacia el coche.\n",
        filename='script.txt',
        content_type='text/plain',
    )
    assert '59 EXT/INT. PARKING/COCHE. DIA.' in result['script_text']
    assert result['source_format'] == 'txt'


def test_normalize_md_keeps_sluglines() -> None:
    service = ScriptFileNormalizationService()
    result = service.normalize_script_file(
        file_bytes=b"## Bloque\n60 INT. PASILLO HOTEL. DIA.\nTension en el pasillo.\n",
        filename='script.md',
        content_type='text/markdown',
    )
    assert '60 INT. PASILLO HOTEL. DIA.' in result['script_text']
    assert result['source_format'] == 'md'


def test_pdf_without_extractable_text_returns_warning(monkeypatch: pytest.MonkeyPatch) -> None:
    service = ScriptFileNormalizationService()

    def fake_convert_uploaded_script_to_markdown(*, path, mime_type=None):
        return {
            'detected_format': 'pdf',
            'extraction_method': 'pdf_ocr_required',
            'raw_text': '',
            'markdown_text': '',
            'analysis_text': '',
        }

    monkeypatch.setattr(
        'services.script_file_normalization_service.script_document_conversion_service.convert_uploaded_script_to_markdown',
        fake_convert_uploaded_script_to_markdown,
    )
    result = service.normalize_script_file(file_bytes=b'%PDF-1.4', filename='script.pdf', content_type='application/pdf')
    assert result['warnings']
    assert result['script_text'] == ''


def test_docx_extracts_paragraphs_and_keeps_headings() -> None:
    service = ScriptFileNormalizationService()
    payload = _build_minimal_docx_bytes([
        '59 EXT/INT. PARKING/COCHE. DÍA.',
        'MANU observa el retrovisor.',
        '60 INT. PASILLO HOTEL. DÍA.',
    ])
    result = service.normalize_script_file(
        file_bytes=payload,
        filename='script.docx',
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    )
    assert '59 EXT/INT. PARKING/COCHE. DÍA.' in result['script_text']
    assert '60 INT. PASILLO HOTEL. DÍA.' in result['script_text']
    assert result['source_format'] == 'docx'


def test_doc_returns_controlled_error() -> None:
    service = ScriptFileNormalizationService()
    with pytest.raises(ValueError, match='DOCX, PDF'):
        service.normalize_script_file(file_bytes=b'legacy doc', filename='script.doc', content_type='application/msword')
