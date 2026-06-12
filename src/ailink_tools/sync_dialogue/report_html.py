from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path

from ailink_tools.sync_dialogue.schemas import (
    SyncDialogueMatchSuggestion,
    SyncDialogueMediaFile,
    SyncDialogueScanResult,
)


def write_report_html(result: SyncDialogueScanResult, output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_report(result), encoding="utf-8")
    return path


def _render_report(result: SyncDialogueScanResult) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    videos = [media_file for media_file in result.media_files if media_file.kind == "video"]
    audios = [media_file for media_file in result.media_files if media_file.kind == "audio"]
    alerts = _build_alerts(result)
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            "<title>AILink Sync Dialogue — Ingest Report</title>",
            "<style>",
            _css(),
            "</style>",
            "</head>",
            "<body>",
            "<header>",
            "<h1>AILink Sync Dialogue — Ingest Report</h1>",
            "<p class=\"subtitle\">Local scan report</p>",
            f"<p><strong>Root path:</strong> {escape(result.root_path)}</p>",
            f"<p><strong>Generated:</strong> {escape(generated_at)}</p>",
            "</header>",
            _summary_table(result),
            _alerts_section(alerts),
            _media_table("Video files", videos, _video_columns()),
            _media_table("Audio files", audios, _audio_columns()),
            _matches_table(result.match_suggestions),
            "<footer>",
            "Generated locally by AILink Sync Dialogue. Media files were not uploaded.",
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


def _summary_table(result: SyncDialogueScanResult) -> str:
    rows = [
        ("Total files", result.total_files),
        ("Video count", result.video_count),
        ("Audio count", result.audio_count),
        ("Unsupported count", result.unsupported_count),
        ("Match suggestions count", len(result.match_suggestions)),
    ]
    body = "".join(
        f"<tr><th>{escape(label)}</th><td>{escape(str(value))}</td></tr>"
        for label, value in rows
    )
    return f"<section><h2>Summary</h2><table>{body}</table></section>"


def _build_alerts(result: SyncDialogueScanResult) -> list[str]:
    alerts: list[str] = []
    if result.video_count == 0:
        alerts.append("No video files detected.")
    if result.audio_count == 0:
        alerts.append("No audio files detected.")
    if result.unsupported_count > 0:
        alerts.append(f"{result.unsupported_count} unsupported files were ignored.")
    missing_count = sum(
        1 for media_file in result.media_files if media_file.probe_status == "ffprobe_missing"
    )
    if missing_count:
        alerts.append("ffprobe was not available for metadata extraction.")
    failed_count = sum(
        1 for media_file in result.media_files if media_file.probe_status == "failed"
    )
    if failed_count:
        alerts.append(f"ffprobe failed for {failed_count} media files.")
    if not result.match_suggestions and result.video_count > 0 and result.audio_count > 0:
        alerts.append("No match suggestions found. Check timecode/metadata.")
    return alerts


def _alerts_section(alerts: list[str]) -> str:
    if not alerts:
        return ""
    items = "".join(f"<li>{escape(alert)}</li>" for alert in alerts)
    return f"<section><h2>Alerts</h2><div class=\"alerts\"><ul>{items}</ul></div></section>"


def _video_columns() -> list[str]:
    return [
        "relative_path",
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
        "duration_seconds",
        "timecode",
        "audio_channels",
        "codec_name",
        "format_name",
        "probe_status",
        "size_bytes",
    ]


def _media_table(
    title: str, media_files: list[SyncDialogueMediaFile], columns: list[str]
) -> str:
    if not media_files:
        return f"<section><h2>{escape(title)}</h2><p class=\"empty\">No rows.</p></section>"
    header = "".join(f"<th>{escape(column)}</th>" for column in columns)
    rows = "".join(_media_row(media_file, columns) for media_file in media_files)
    return f"<section><h2>{escape(title)}</h2><table><thead><tr>{header}</tr></thead><tbody>{rows}</tbody></table></section>"


def _media_row(media_file: SyncDialogueMediaFile, columns: list[str]) -> str:
    row = media_file.to_dict()
    cells = "".join(f"<td>{_safe_cell(row.get(column))}</td>" for column in columns)
    return f"<tr>{cells}</tr>"


def _matches_table(suggestions: list[SyncDialogueMatchSuggestion]) -> str:
    columns = [
        "video_relative_path",
        "audio_relative_path",
        "confidence",
        "score",
        "strategy",
        "reasons",
        "duration_delta_seconds",
        "video_timecode",
        "audio_timecode",
    ]
    if not suggestions:
        return "<section><h2>Match suggestions</h2><p class=\"empty\">No rows.</p></section>"
    header = "".join(f"<th>{escape(column)}</th>" for column in columns)
    rows = "".join(_match_row(suggestion, columns) for suggestion in suggestions)
    return f"<section><h2>Match suggestions</h2><table><thead><tr>{header}</tr></thead><tbody>{rows}</tbody></table></section>"


def _match_row(suggestion: SyncDialogueMatchSuggestion, columns: list[str]) -> str:
    row = suggestion.to_dict()
    row["reasons"] = "; ".join(suggestion.reasons)
    cells = "".join(f"<td>{_safe_cell(row.get(column))}</td>" for column in columns)
    return f"<tr>{cells}</tr>"


def _safe_cell(value: object) -> str:
    if value is None:
        return ""
    return escape(str(value))
