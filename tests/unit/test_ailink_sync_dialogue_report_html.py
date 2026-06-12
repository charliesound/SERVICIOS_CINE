from __future__ import annotations

from pathlib import Path
from dataclasses import replace

from ailink_tools.sync_dialogue.report_html import write_report_html
from ailink_tools.sync_dialogue.schemas import (
    SyncDialogueMatchSuggestion,
    SyncDialogueMediaFile,
    SyncDialogueScanResult,
)


def _media(
    relative_path: str,
    *,
    kind: str,
    probe_status: str = "ok",
    duration: float | None = 12.0,
    timecode: str | None = "01:00:00:00",
) -> SyncDialogueMediaFile:
    filename = relative_path.rsplit("/", 1)[-1]
    extension = "." + filename.rsplit(".", 1)[-1]
    return SyncDialogueMediaFile(
        path=f"/project/{relative_path}",
        relative_path=relative_path,
        filename=filename,
        extension=extension,
        kind=kind,  # type: ignore[arg-type]
        size_bytes=10,
        probe_status=probe_status,
        duration_seconds=duration,
        timecode=timecode,
        fps=24.0 if kind == "video" else None,
        audio_channels=2 if kind == "audio" else None,
        codec_name="prores" if kind == "video" else "pcm_s24le",
        format_name="mov" if kind == "video" else "wav",
    )


def _result(
    media_files: list[SyncDialogueMediaFile],
    *,
    root_path: str = "/project",
    unsupported_count: int = 0,
    match_suggestions: list[SyncDialogueMatchSuggestion] | None = None,
) -> SyncDialogueScanResult:
    return SyncDialogueScanResult(
        root_path=root_path,
        total_files=len(media_files) + unsupported_count,
        video_count=sum(1 for media_file in media_files if media_file.kind == "video"),
        audio_count=sum(1 for media_file in media_files if media_file.kind == "audio"),
        unsupported_count=unsupported_count,
        media_files=media_files,
        match_suggestions=match_suggestions or [],
    )


def _sample_result() -> SyncDialogueScanResult:
    suggestion = SyncDialogueMatchSuggestion(
        video_relative_path="video/clip.mov",
        audio_relative_path="audio/clip.wav",
        confidence="high",
        score=0.95,
        strategy="timecode",
        reasons=["matching_timecode"],
        video_timecode="01:00:00:00",
        audio_timecode="01:00:00:00",
        video_duration_seconds=12.0,
        audio_duration_seconds=12.0,
        duration_delta_seconds=0.0,
    )
    return _result(
        [
            _media("video/clip.mov", kind="video"),
            _media("audio/clip.wav", kind="audio"),
        ],
        unsupported_count=1,
        match_suggestions=[suggestion],
    )


def test_write_report_html_creates_file(tmp_path: Path) -> None:
    output_path = write_report_html(_sample_result(), tmp_path / "reports" / "report.html")

    assert output_path.exists()


def test_html_contains_title_and_summary_counts(tmp_path: Path) -> None:
    output_path = write_report_html(_sample_result(), tmp_path / "report.html")
    html = output_path.read_text(encoding="utf-8")

    assert "AILink Sync Dialogue — Ingest Report" in html
    assert "Local scan report" in html
    assert "Total files" in html
    assert "Video count" in html
    assert "Audio count" in html
    assert "Unsupported count" in html
    assert "Match suggestions count" in html


def test_html_contains_video_audio_and_match_tables(tmp_path: Path) -> None:
    output_path = write_report_html(_sample_result(), tmp_path / "report.html")
    html = output_path.read_text(encoding="utf-8")

    assert "Video files" in html
    assert "Audio files" in html
    assert "Match suggestions" in html
    assert "video/clip.mov" in html
    assert "audio/clip.wav" in html
    assert "matching_timecode" in html


def test_html_contains_alert_when_no_videos(tmp_path: Path) -> None:
    output_path = write_report_html(_result([_media("audio/a.wav", kind="audio")]), tmp_path / "r.html")

    assert "No video files detected." in output_path.read_text(encoding="utf-8")


def test_html_contains_alert_when_no_audios(tmp_path: Path) -> None:
    output_path = write_report_html(_result([_media("video/a.mov", kind="video")]), tmp_path / "r.html")

    assert "No audio files detected." in output_path.read_text(encoding="utf-8")


def test_html_contains_alert_for_unsupported_files(tmp_path: Path) -> None:
    output_path = write_report_html(_result([], unsupported_count=2), tmp_path / "r.html")

    assert "2 unsupported files were ignored." in output_path.read_text(encoding="utf-8")


def test_html_contains_alert_for_ffprobe_missing(tmp_path: Path) -> None:
    output_path = write_report_html(
        _result([_media("video/a.mov", kind="video", probe_status="ffprobe_missing")]),
        tmp_path / "r.html",
    )

    assert "ffprobe was not available" in output_path.read_text(encoding="utf-8")


def test_html_contains_alert_for_ffprobe_failed(tmp_path: Path) -> None:
    output_path = write_report_html(
        _result([_media("video/a.mov", kind="video", probe_status="failed")]),
        tmp_path / "r.html",
    )

    assert "ffprobe failed for 1 media files." in output_path.read_text(encoding="utf-8")


def test_html_contains_alert_when_no_matches_for_video_and_audio(tmp_path: Path) -> None:
    output_path = write_report_html(
        _result([
            _media("video/a.mov", kind="video"),
            _media("audio/a.wav", kind="audio"),
        ]),
        tmp_path / "r.html",
    )

    assert "No match suggestions found. Check timecode/metadata." in output_path.read_text(encoding="utf-8")


def test_html_escapes_dynamic_content(tmp_path: Path) -> None:
    result = _result(
        [_media("video/<script>.mov", kind="video")],
        root_path="/project/<unsafe>&root",
    )
    output_path = write_report_html(result, tmp_path / "report.html")
    html = output_path.read_text(encoding="utf-8")

    assert "&lt;unsafe&gt;&amp;root" in html
    assert "video/&lt;script&gt;.mov" in html
    assert "<script>.mov" not in html


def test_html_escapes_ampersand_angles_and_quotes_in_dynamic_fields(tmp_path: Path) -> None:
    media = replace(
        _media("video/a.mov", kind="video"),
        relative_path="video/A&B <clip> \"quote\" 'single'.mov",
        filename="A&B <clip> \"quote\" 'single'.mov",
        codec_name="codec<&>\"'",
        format_name="fmt<&>\"'",
        timecode="01:00:&<\"'",
    )
    suggestion = SyncDialogueMatchSuggestion(
        video_relative_path="video/A&B.mov",
        audio_relative_path="audio/A&B.wav",
        confidence="high",
        score=0.95,
        strategy="timecode",
        reasons=["reason<&>\"'"],
    )
    output_path = write_report_html(
        _result([media], match_suggestions=[suggestion], root_path="/root/&<\"'"),
        tmp_path / "report.html",
    )
    html = output_path.read_text(encoding="utf-8")

    assert "&amp;" in html
    assert "&lt;" in html
    assert "&gt;" in html
    assert "&quot;" in html
    assert "&#x27;" in html
    assert "reason&lt;&amp;&gt;&quot;&#x27;" in html


def test_html_does_not_contain_script_tag_even_with_script_input(tmp_path: Path) -> None:
    output_path = write_report_html(
        _result([_media("video/<script>alert.mov", kind="video")]),
        tmp_path / "report.html",
    )
    html = output_path.read_text(encoding="utf-8").lower()

    assert "<script" not in html


def test_html_contains_no_external_resources(tmp_path: Path) -> None:
    output_path = write_report_html(_sample_result(), tmp_path / "report.html")
    html = output_path.read_text(encoding="utf-8").lower()

    assert "http://" not in html
    assert "https://" not in html
    assert "cdn" not in html
    assert "<script" not in html
    assert "src=" not in html
    assert "href=" not in html


def test_html_contains_meta_charset_and_print_styles(tmp_path: Path) -> None:
    output_path = write_report_html(_sample_result(), tmp_path / "report.html")
    html = output_path.read_text(encoding="utf-8")

    assert '<meta charset="utf-8">' in html
    assert "@media print" in html


def test_matches_table_serializes_reasons_stably(tmp_path: Path) -> None:
    suggestion = SyncDialogueMatchSuggestion(
        video_relative_path="video/clip.mov",
        audio_relative_path="audio/clip.wav",
        confidence="high",
        score=0.95,
        strategy="timecode",
        reasons=["matching_timecode", "duration_delta_lte_1s"],
    )
    output_path = write_report_html(
        _result([
            _media("video/clip.mov", kind="video"),
            _media("audio/clip.wav", kind="audio"),
        ], match_suggestions=[suggestion]),
        tmp_path / "report.html",
    )

    assert "matching_timecode; duration_delta_lte_1s" in output_path.read_text(encoding="utf-8")


def test_empty_video_audio_and_matches_tables_show_no_rows(tmp_path: Path) -> None:
    output_path = write_report_html(_result([]), tmp_path / "report.html")
    html = output_path.read_text(encoding="utf-8")

    assert html.count("No rows.") == 3


def test_media_absolute_paths_are_not_rendered_in_tables(tmp_path: Path) -> None:
    media = replace(
        _media("video/clip.mov", kind="video"),
        path="/very/sensitive/internal/video/clip.mov",
    )
    output_path = write_report_html(
        _result([media], root_path="/root/path/is/allowed"),
        tmp_path / "report.html",
    )
    html = output_path.read_text(encoding="utf-8")

    assert "/root/path/is/allowed" in html
    assert "/very/sensitive/internal/video/clip.mov" not in html


def test_html_contains_footer_media_not_uploaded(tmp_path: Path) -> None:
    output_path = write_report_html(_sample_result(), tmp_path / "report.html")

    assert "Media files were not uploaded." in output_path.read_text(encoding="utf-8")


def test_html_output_is_utf8(tmp_path: Path) -> None:
    output_path = write_report_html(_sample_result(), tmp_path / "report.html")

    assert output_path.read_bytes().decode("utf-8")


def test_html_supports_spanish_labels(tmp_path: Path) -> None:
    output_path = write_report_html(_sample_result(), tmp_path / "report_es.html", language="es")
    html = output_path.read_text(encoding="utf-8")

    assert '<html lang="es">' in html
    assert "AILink Sync Dialogue — Informe de ingesta" in html
    assert "Informe de escaneo local" in html
    assert "Ruta raíz" in html
    assert "Generado" in html
    assert "Resumen" in html
    assert "Total de archivos" in html
    assert "Vídeos detectados" in html
    assert "Audios detectados" in html
    assert "Archivos no compatibles" in html
    assert "Sugerencias encontradas" in html
    assert "Archivos de vídeo" in html
    assert "Archivos de audio" in html
    assert "Sugerencias de sincronía" in html
    assert "ruta_relativa" in html
    assert "duración_segundos" in html
    assert "confianza" in html
    assert "puntuación" in html
    assert "Generado localmente por AILink Sync Dialogue" in html


def test_html_supports_spanish_alerts(tmp_path: Path) -> None:
    output_path = write_report_html(
        _result([
            _media("video/a.mov", kind="video"),
            _media("audio/a.wav", kind="audio"),
        ], unsupported_count=2),
        tmp_path / "report_es.html",
        language="es",
    )
    html = output_path.read_text(encoding="utf-8")

    assert "Se han ignorado 2 archivos no compatibles." in html
    assert "No se han encontrado sugerencias de sincronía. Revisa timecode/metadata." in html


def test_write_report_html_rejects_unsupported_language(tmp_path: Path) -> None:
    output_path = tmp_path / "report.html"

    try:
        write_report_html(_sample_result(), output_path, language="fr")
    except ValueError as exc:
        assert "unsupported report language" in str(exc)
    else:
        raise AssertionError("expected unsupported language to raise ValueError")

    assert not output_path.exists()



def test_html_surfaces_scene_take_file_relationship_in_spanish_report(tmp_path: Path) -> None:
    suggestion = SyncDialogueMatchSuggestion(
        video_relative_path="video/scene01_take01.mov",
        audio_relative_path="audio/scene01_take01.wav",
        confidence="high",
        score=0.95,
        strategy="timecode",
        reasons=["matching_timecode"],
    )
    result = _result(
        [
            _media("video/scene01_take01.mov", kind="video"),
            _media("audio/scene01_take01.wav", kind="audio"),
        ],
        match_suggestions=[suggestion],
    )

    output_path = write_report_html(result, tmp_path / "report_es.html", language="es")
    html = output_path.read_text(encoding="utf-8")

    assert "escena_take" in html
    assert "escena_take_vídeo" in html
    assert "escena_take_audio" in html
    assert "scene01_take01" in html
