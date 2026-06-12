"""Tests for AILink Sync Dialogue demo video subtitles and voiceover assets."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent.parent
VIDEO_DIR = ROOT / "docs" / "product" / "video"
SRT = VIDEO_DIR / "ailink_sync_dialogue_demo_video_subtitles_es_v1.srt"
VOICEOVER = VIDEO_DIR / "ailink_sync_dialogue_demo_video_voiceover_es_v1.txt"
README = VIDEO_DIR / "ailink_sync_dialogue_demo_video_subtitles_readme_v1.md"

TIMESTAMP_RE = re.compile(
    r"(?P<sh>\d{2}):(?P<sm>\d{2}):(?P<ss>\d{2}),(?P<sms>\d{3})"
    r" --> "
    r"(?P<eh>\d{2}):(?P<em>\d{2}):(?P<es>\d{2}),(?P<ems>\d{3})"
)

REQUIRED_TERMS = [
    "AILink Sync Dialogue",
    "timecode",
    "metadata",
    "score",
    "razones",
    "report.html",
    "media_files.csv",
    "match_suggestions.csv",
    "scan_result.json",
    "no se sube a la nube",
    "localmente",
    "beta privada",
    "casos controlados",
]

LIMITATIONS = [
    "waveform sync",
    "transcripción",
    "claqueta visual",
    "instalador final",
    "integración directa",
]

FORBIDDEN_POSITIVE_CLAIMS = [
    "promete sincronizar todo automáticamente",
    "sincronización automática completa disponible",
    "reemplaza al montador",
    "automatiza todo el trabajo del montador",
    "waveform sync ya disponible",
    "transcripción ya disponible",
    "claqueta visual ya disponible",
    "instalador final ya disponible",
    "integración directa ya disponible",
    "producto final listo para publicar",
    "sube tu material audiovisual",
    "envíanos tu material audiovisual",
]

FORBIDDEN_TECH_REFERENCES = [
    "DATABASE_URL",
    "TEST_DATABASE_URL",
    "FastAPI",
    "APIRouter",
    "AsyncSessionLocal",
    "CreditLedger",
    "AIJobRepository",
    "/mnt/",
    "\\\\wsl.localhost",
    "C:\\",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _timestamp_to_ms(hours: str, minutes: str, seconds: str, millis: str) -> int:
    return (
        int(hours) * 3_600_000
        + int(minutes) * 60_000
        + int(seconds) * 1_000
        + int(millis)
    )


def _parse_srt_blocks() -> list[tuple[int, int, int, str]]:
    content = _read(SRT).strip()
    blocks = content.split("\n\n")
    parsed: list[tuple[int, int, int, str]] = []

    for block in blocks:
        lines = block.splitlines()
        assert len(lines) >= 3, block

        index = int(lines[0])
        match = TIMESTAMP_RE.fullmatch(lines[1])
        assert match, lines[1]

        start = _timestamp_to_ms(
            match.group("sh"),
            match.group("sm"),
            match.group("ss"),
            match.group("sms"),
        )
        end = _timestamp_to_ms(
            match.group("eh"),
            match.group("em"),
            match.group("es"),
            match.group("ems"),
        )
        text = " ".join(lines[2:])
        parsed.append((index, start, end, text))

    return parsed


def test_subtitle_and_voiceover_files_exist():
    assert SRT.exists()
    assert VOICEOVER.exists()
    assert README.exists()


def test_srt_has_sequential_numbering():
    indexes = [index for index, _start, _end, _text in _parse_srt_blocks()]
    assert indexes == list(range(1, len(indexes) + 1))
    assert len(indexes) >= 12


def test_srt_timestamps_are_ordered_and_valid():
    previous_end = -1

    for _index, start, end, _text in _parse_srt_blocks():
        assert start >= 0
        assert end > start
        assert start >= previous_end
        previous_end = end

    assert previous_end <= 100_000


def test_srt_contains_required_terms():
    content = _read(SRT)
    for term in REQUIRED_TERMS:
        assert term in content


def test_voiceover_contains_same_core_message():
    content = _read(VOICEOVER)
    for term in REQUIRED_TERMS:
        assert term in content


def test_readme_documents_usage_and_non_goals():
    content = _read(README)
    for term in [
        "No renderiza vídeo",
        "no crea MP4",
        "Grabar voz en off",
        "Non-goals de esta fase",
        "Criterios de aceptación",
    ]:
        assert term in content


def test_subtitles_and_voiceover_communicate_limitations():
    combined = f"{_read(SRT)}\n{_read(VOICEOVER)}\n{_read(README)}"
    for limitation in LIMITATIONS:
        assert limitation in combined


def test_no_forbidden_positive_claims():
    combined = f"{_read(SRT)}\n{_read(VOICEOVER)}\n{_read(README)}".lower()
    for claim in FORBIDDEN_POSITIVE_CLAIMS:
        assert claim.lower() not in combined


def test_no_runtime_or_backend_references():
    combined = f"{_read(SRT)}\n{_read(VOICEOVER)}\n{_read(README)}"
    for pattern in FORBIDDEN_TECH_REFERENCES:
        assert pattern not in combined


def test_voiceover_is_plain_text_not_markdown_script():
    content = _read(VOICEOVER)
    assert "##" not in content
    assert "-->" not in content
    assert len(content.splitlines()) >= 8
