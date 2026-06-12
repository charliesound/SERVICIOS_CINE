from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path
import re

from ailink_tools.sync_dialogue.schemas import (
    SyncDialogueMatchSuggestion,
    SyncDialogueMediaFile,
    SyncDialogueScanResult,
)

SUPPORTED_LANGUAGES = {"en", "es"}

TEXT = {
    "en": {
        "html_lang": "en",
        "title": "AILink Sync Dialogue — Ingest Report",
        "subtitle": "Local scan report",
        "root_path": "Root path",
        "generated": "Generated",
        "summary": "Summary",
        "total_files": "Total files",
        "video_count": "Video count",
        "audio_count": "Audio count",
        "unsupported_count": "Unsupported count",
        "match_suggestions_count": "Match suggestions count",
        "alerts": "Alerts",
        "video_files": "Video files",
        "audio_files": "Audio files",
        "match_suggestions": "Match suggestions",
        "no_rows": "No rows.",
        "footer": "Generated locally by AILink Sync Dialogue. Media files were not uploaded.",
        "no_video": "No video files detected.",
        "no_audio": "No audio files detected.",
        "unsupported": "{count} unsupported files were ignored.",
        "ffprobe_missing": "ffprobe was not available for metadata extraction.",
        "ffprobe_failed": "ffprobe failed for {count} media files.",
        "no_matches": "No match suggestions found. Check timecode/metadata.",
    },
    "es": {
        "html_lang": "es",
        "title": "AILink Sync Dialogue — Informe de ingesta",
        "subtitle": "Informe de escaneo local",
        "root_path": "Ruta raíz",
        "generated": "Generado",
        "summary": "Resumen",
        "total_files": "Total de archivos",
        "video_count": "Vídeos detectados",
        "audio_count": "Audios detectados",
        "unsupported_count": "Archivos no compatibles",
        "match_suggestions_count": "Sugerencias encontradas",
        "alerts": "Avisos",
        "video_files": "Archivos de vídeo",
        "audio_files": "Archivos de audio",
        "match_suggestions": "Sugerencias de sincronía",
        "no_rows": "Sin filas.",
        "footer": "Generado localmente por AILink Sync Dialogue. Los archivos de media no se han subido.",
        "no_video": "No se han detectado archivos de vídeo.",
        "no_audio": "No se han detectado archivos de audio.",
        "unsupported": "Se han ignorado {count} archivos no compatibles.",
        "ffprobe_missing": "ffprobe no estaba disponible para extraer metadata.",
        "ffprobe_failed": "ffprobe ha fallado en {count} archivos de media.",
        "no_matches": "No se han encontrado sugerencias de sincronía. Revisa timecode/metadata.",
    },
}

COLUMN_LABELS = {
    "en": {
        "scene_take": "scene_take",
        "video_scene_take": "video_scene_take",
        "audio_scene_take": "audio_scene_take",
    },
    "es": {
        "relative_path": "ruta_relativa",
        "scene_take": "escena_take",
        "duration_seconds": "duración_segundos",
        "timecode": "timecode",
        "fps": "fps",
        "codec_name": "codec",
        "format_name": "formato",
        "probe_status": "estado_análisis",
        "size_bytes": "tamaño_bytes",
        "audio_channels": "canales_audio",
        "video_relative_path": "ruta_vídeo",
        "audio_relative_path": "ruta_audio",
        "video_scene_take": "escena_take_vídeo",
        "audio_scene_take": "escena_take_audio",
        "confidence": "confianza",
        "score": "puntuación",
        "strategy": "estrategia",
        "reasons": "motivos",
        "duration_delta_seconds": "diferencia_duración_segundos",
        "video_timecode": "timecode_vídeo",
        "audio_timecode": "timecode_audio",
    },
}


def write_report_html(
    result: SyncDialogueScanResult,
    output_path: str | Path,
    *,
    language: str = "en",
) -> Path:
    _validate_language(language)
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_report(result, language=language), encoding="utf-8")
    return path


def _validate_language(language: str) -> None:
    if language not in SUPPORTED_LANGUAGES:
        supported = ", ".join(sorted(SUPPORTED_LANGUAGES))
        raise ValueError(f"unsupported report language: {language!r}; expected one of: {supported}")


def _t(language: str, key: str) -> str:
    return TEXT[language][key]


def _column_label(language: str, column: str) -> str:
    return COLUMN_LABELS.get(language, {}).get(column, column)


def _render_report(result: SyncDialogueScanResult, *, language: str = "en") -> str:
    _validate_language(language)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    videos = [media_file for media_file in result.media_files if media_file.kind == "video"]
    audios = [media_file for media_file in result.media_files if media_file.kind == "audio"]
    alerts = _build_alerts(result, language=language)
    return "\n".join(
        [
            "<!doctype html>",
            f'<html lang="{escape(_t(language, "html_lang"))}">',
            "<head>",
            '<meta charset="utf-8">',
            f"<title>{escape(_t(language, 'title'))}</title>",
            "<style>",
            _css(),
            "</style>",
            "</head>",
            "<body>",
            "<header>",
            f"<h1>{escape(_t(language, 'title'))}</h1>",
            f"<p class=\"subtitle\">{escape(_t(language, 'subtitle'))}</p>",
            f"<p><strong>{escape(_t(language, 'root_path'))}:</strong> {escape(result.root_path)}</p>",
            f"<p><strong>{escape(_t(language, 'generated'))}:</strong> {escape(generated_at)}</p>",
            "</header>",
            _summary_table(result, language=language),
            _alerts_section(alerts, language=language),
            _media_table(_t(language, "video_files"), videos, _video_columns(), language=language),
            _media_table(_t(language, "audio_files"), audios, _audio_columns(), language=language),
            _matches_table(result.match_suggestions, language=language),
            "<footer>",
            escape(_t(language, "footer")),
            "</footer>",
            "</body>",
            "</html>",
            "",
        ]
    )


def _css() -> str:
    return """
body { font-family: Arial, sans-serif; color: #1f2933; margin: 24px; }
h1 { margin-bottom: 4px; }
h2 { margin-top: 28px; border-bottom: 1px solid #cbd5e1; padding-bottom: 6px; }
.subtitle { color: #52616b; margin-top: 0; }
table { width: 100%; border-collapse: collapse; margin: 12px 0 20px; font-size: 12px; }
th, td { border: 1px solid #cbd5e1; padding: 6px 8px; text-align: left; vertical-align: top; }
th { background: #eef2f7; }
.alerts { border: 1px solid #f5c542; background: #fff8db; padding: 10px 14px; }
.empty { color: #697586; font-style: italic; }
footer { margin-top: 36px; padding-top: 12px; border-top: 1px solid #cbd5e1; font-size: 12px; color: #52616b; }
@media print {
  body { margin: 12mm; }
  table { font-size: 10px; page-break-inside: auto; }
  tr { page-break-inside: avoid; page-break-after: auto; }
}
""".strip()


def _summary_table(result: SyncDialogueScanResult, *, language: str = "en") -> str:
    rows = [
        (_t(language, "total_files"), result.total_files),
        (_t(language, "video_count"), result.video_count),
        (_t(language, "audio_count"), result.audio_count),
        (_t(language, "unsupported_count"), result.unsupported_count),
        (_t(language, "match_suggestions_count"), len(result.match_suggestions)),
    ]
    body = "".join(
        f"<tr><th>{escape(label)}</th><td>{escape(str(value))}</td></tr>"
        for label, value in rows
    )
    return f"<section><h2>{escape(_t(language, 'summary'))}</h2><table>{body}</table></section>"


def _build_alerts(result: SyncDialogueScanResult, *, language: str = "en") -> list[str]:
    alerts: list[str] = []
    if result.video_count == 0:
        alerts.append(_t(language, "no_video"))
    if result.audio_count == 0:
        alerts.append(_t(language, "no_audio"))
    if result.unsupported_count > 0:
        alerts.append(_t(language, "unsupported").format(count=result.unsupported_count))
    missing_count = sum(
        1 for media_file in result.media_files if media_file.probe_status == "ffprobe_missing"
    )
    if missing_count:
        alerts.append(_t(language, "ffprobe_missing"))
    failed_count = sum(
        1 for media_file in result.media_files if media_file.probe_status == "failed"
    )
    if failed_count:
        alerts.append(_t(language, "ffprobe_failed").format(count=failed_count))
    if not result.match_suggestions and result.video_count > 0 and result.audio_count > 0:
        alerts.append(_t(language, "no_matches"))
    return alerts


def _alerts_section(alerts: list[str], *, language: str = "en") -> str:
    if not alerts:
        return ""
    items = "".join(f"<li>{escape(alert)}</li>" for alert in alerts)
    return f"<section><h2>{escape(_t(language, 'alerts'))}</h2><div class=\"alerts\"><ul>{items}</ul></div></section>"


def _video_columns() -> list[str]:
    return [
        "relative_path",
        "scene_take",
        "duration_seconds",
        "timecode",
        "fps",
        "codec_name",
        "format_name",
        "probe_status",
        "size_bytes",
    ]


def _audio_columns() -> list[str]:
    return [
        "relative_path",
        "scene_take",
        "duration_seconds",
        "timecode",
        "audio_channels",
        "codec_name",
        "format_name",
        "probe_status",
        "size_bytes",
    ]


def _media_table(
    title: str,
    media_files: list[SyncDialogueMediaFile],
    columns: list[str],
    *,
    language: str = "en",
) -> str:
    if not media_files:
        return f"<section><h2>{escape(title)}</h2><p class=\"empty\">{escape(_t(language, 'no_rows'))}</p></section>"
    header = "".join(f"<th>{escape(_column_label(language, column))}</th>" for column in columns)
    rows = "".join(_media_row(media_file, columns) for media_file in media_files)
    return f"<section><h2>{escape(title)}</h2><table><thead><tr>{header}</tr></thead><tbody>{rows}</tbody></table></section>"


def _media_row(media_file: SyncDialogueMediaFile, columns: list[str]) -> str:
    row = media_file.to_dict()
    row["scene_take"] = _scene_take_hint(media_file.relative_path)
    cells = "".join(f"<td>{_safe_cell(row.get(column))}</td>" for column in columns)
    return f"<tr>{cells}</tr>"


def _matches_table(
    suggestions: list[SyncDialogueMatchSuggestion],
    *,
    language: str = "en",
) -> str:
    columns = [
        "video_relative_path",
        "audio_relative_path",
        "video_scene_take",
        "audio_scene_take",
        "confidence",
        "score",
        "strategy",
        "reasons",
        "duration_delta_seconds",
        "video_timecode",
        "audio_timecode",
    ]
    title = _t(language, "match_suggestions")
    if not suggestions:
        return f"<section><h2>{escape(title)}</h2><p class=\"empty\">{escape(_t(language, 'no_rows'))}</p></section>"
    header = "".join(f"<th>{escape(_column_label(language, column))}</th>" for column in columns)
    rows = "".join(_match_row(suggestion, columns) for suggestion in suggestions)
    return f"<section><h2>{escape(title)}</h2><table><thead><tr>{header}</tr></thead><tbody>{rows}</tbody></table></section>"


def _match_row(suggestion: SyncDialogueMatchSuggestion, columns: list[str]) -> str:
    row = suggestion.to_dict()
    row["video_scene_take"] = _scene_take_hint(suggestion.video_relative_path)
    row["audio_scene_take"] = _scene_take_hint(suggestion.audio_relative_path)
    row["reasons"] = "; ".join(suggestion.reasons)
    cells = "".join(f"<td>{_safe_cell(row.get(column))}</td>" for column in columns)
    return f"<tr>{cells}</tr>"


def _scene_take_hint(relative_path: str) -> str:
    filename = Path(relative_path).name
    match = re.search(
        r"(?:scene|escena|sc)[_\-\s]*([0-9A-Za-z]+).*?(?:take|toma|tk)[_\-\s]*([0-9A-Za-z]+)",
        filename,
        flags=re.IGNORECASE,
    )
    if not match:
        return ""
    scene, take = match.groups()
    return f"scene{scene}_take{take}"


def _safe_cell(value: object) -> str:
    if value is None:
        return ""
    return escape(str(value))
