from __future__ import annotations

import io
import re
import tempfile
from pathlib import Path
from typing import Any

from services.script_document_conversion_service import script_document_conversion_service


class ScriptFileNormalizationService:
    DOC_ERROR_MESSAGE = (
        "Formato .doc no soportado directamente. Convierte el archivo a DOCX, PDF, TXT o MD."
    )

    _SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx", ".doc"}
    _DOC_EXTENSIONS = {".doc"}

    def normalize_script_file(
        self,
        *,
        file_bytes: bytes,
        filename: str,
        content_type: str | None = None,
    ) -> dict[str, Any]:
        path = Path(filename)
        extension = path.suffix.lower()

        if extension in self._DOC_EXTENSIONS:
            raise ValueError(self.DOC_ERROR_MESSAGE)

        if extension not in self._SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Formato no soportado: {extension}. Usa PDF, DOCX, TXT o MD."
            )

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=extension, dir=tempfile.gettempdir()
        ) as tmp:
            tmp.write(file_bytes)
            tmp.flush()
            tmp_path = tmp.name

        try:
            conversion = script_document_conversion_service.convert_uploaded_script_to_markdown(
                path=tmp_path,
                mime_type=content_type,
            )
        finally:
            Path(tmp_path).unlink(missing_ok=True)

        script_text = str(conversion.get("analysis_text") or conversion.get("raw_text") or "")
        markdown_text = str(conversion.get("markdown_text") or script_text)

        warnings: list[str] = []
        detected_format = str(conversion.get("detected_format") or extension.lstrip("."))
        extraction_method = str(conversion.get("extraction_method") or "unknown")

        if extraction_method == "pdf_ocr_required":
            warnings.append(
                "El PDF no contiene texto extraíble. Se requiere OCR para leer el contenido completo."
            )
            script_text = ""
            markdown_text = ""

        normalized_text = self._normalize_script_text(script_text)
        normalized_markdown = self._normalize_script_text(markdown_text) if markdown_text != script_text else normalized_text

        word_count = len(normalized_text.split()) if normalized_text.strip() else 0
        character_count = len(normalized_text)

        return {
            "script_text": normalized_text,
            "markdown_text": normalized_markdown,
            "source_format": detected_format,
            "warnings": warnings,
            "page_count": None,
            "word_count": word_count,
            "character_count": character_count,
        }

    def _normalize_script_text(self, text: str) -> str:
        if not text:
            return ""
        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        normalized = re.sub(r"[^\S\n]+", " ", normalized)
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)
        normalized = normalized.strip()
        return normalized


script_file_normalization_service = ScriptFileNormalizationService()
