from __future__ import annotations

from pathlib import Path

import pytest

from scripts.local_media_agent.sony_sidecar_parser import (
    CONFIDENCE_CONFIRMED,
    CONFIDENCE_PARTIAL,
    CONFIDENCE_UNAVAILABLE,
    MONITORING_LUT_NOT_RECORDED,
    MONITORING_LUT_RECORDED,
    SOURCE_COLOR_PROFILE_UNAVAILABLE,
    SonySidecarError,
    SONY_SIDECAR_ERROR_MALFORMED,
    build_source_color_profile,
    extract_sony_sidecar_color_metadata,
    resolve_sony_sidecar,
)

FIXTURE_ROOT = (
    Path("tests/fixtures/local_media_agent/scanner_cli/sony_xml_sidecar/input")
)

SONY_STANDARD = """<?xml version="1.0" encoding="UTF-8"?>
<SonyXmlSidecar>
  <ClipName>SYNTH</ClipName>
  <ConfigItem Name="CaptureGammaEquation">
    <Value>s-log3-cine</Value>
  </ConfigItem>
  <ConfigItem Name="CaptureColorPrimaries">
    <Value>s-gamut3-cine</Value>
  </ConfigItem>
  <ConfigItem Name="CodingEquations">
    <Value>rec709</Value>
  </ConfigItem>
</SonyXmlSidecar>
"""


def _write(tmp_path: Path, name: str, content: str) -> Path:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def test_sibling_exact_resolution(tmp_path: Path) -> None:
    media = _write(tmp_path, "A7IV_SL31404.MP4", "SYNTH")
    sidecar = _write(tmp_path, "A7IV_SL31404M01.XML", SONY_STANDARD)
    assert resolve_sony_sidecar(media) == sidecar


def test_sidecar_with_upper_suffix_extension() -> None:
    media = FIXTURE_ROOT / "A7IV_SL31404.MP4"
    assert resolve_sony_sidecar(media).name == "A7IV_SL31404M01.XML"


def test_non_mp4_media_never_resolves(tmp_path: Path) -> None:
    media = _write(tmp_path, "clip.mov", "SYNTH")
    _write(tmp_path, "clipM01.XML", SONY_STANDARD)
    assert resolve_sony_sidecar(media) is None


def test_sidecar_absent(tmp_path: Path) -> None:
    media = _write(tmp_path, "A7IV_SL31410.MP4", "SYNTH")
    assert resolve_sony_sidecar(media) is None


def test_no_cross_directory_association(tmp_path: Path) -> None:
    media = _write(tmp_path, "A7IV_SL31404.MP4", "SYNTH")
    _write(tmp_path, "A7IV_SL31404M01.XML", SONY_STANDARD)
    other = tmp_path / "OTHER" / "A7IV_SL31404.MP4"
    other.parent.mkdir()
    other.write_bytes(b"SYNTH")
    _write(other.parent, "A7IV_SL31404M01.XML", SONY_STANDARD)
    assert resolve_sony_sidecar(media) == tmp_path / "A7IV_SL31404M01.XML"
    assert resolve_sony_sidecar(other) == other.parent / "A7IV_SL31404M01.XML"


def test_malformed_xml_raises_on_extract(tmp_path: Path) -> None:
    malformed = _write(tmp_path, "bad.XML", "<not-closed>")
    with pytest.raises(SonySidecarError, match=SONY_SIDECAR_ERROR_MALFORMED):
        extract_sony_sidecar_color_metadata(malformed)
    assert build_source_color_profile(malformed) == SOURCE_COLOR_PROFILE_UNAVAILABLE


def test_valid_xml_without_color_is_unavailable_not_error(tmp_path: Path) -> None:
    no_color = _write(
        tmp_path,
        "no_color.XML",
        '<?xml version="1.0"?><SonyXmlSidecar><ConfigItem Name="FirmwareVersion">'
        "<Value>1.00</Value></ConfigItem></SonyXmlSidecar>",
    )
    profile = build_source_color_profile(no_color)
    assert profile["metadata_confidence"] == CONFIDENCE_UNAVAILABLE
    assert profile == SOURCE_COLOR_PROFILE_UNAVAILABLE


def test_raw_preservation_exact_slog3(tmp_path: Path) -> None:
    sidecar = _write(tmp_path, "A7IV_SL31404M01.XML", SONY_STANDARD)
    profile = build_source_color_profile(sidecar, relative_sidecar_path="A7IV_SL31404M01.XML")
    assert profile["capture_gamma_raw"] == "s-log3-cine"
    assert profile["capture_color_primaries_raw"] == "s-gamut3-cine"
    assert profile["coding_equations_raw"] == "rec709"
    assert profile["capture_gamma_display"] == "S-Log3"
    assert profile["capture_gamut_display"] == "S-Gamut3.Cine"
    assert profile["metadata_confidence"] == CONFIDENCE_CONFIRMED
    assert profile["metadata_source"] == "SONY_XML_SIDECAR"


def test_ex_cine1_and_rec709_fixture() -> None:
    sidecar = FIXTURE_ROOT / "A7IV_SL31405M01.XML"
    profile = build_source_color_profile(sidecar, relative_sidecar_path="A7IV_SL31405M01.XML")
    assert profile["capture_gamma_raw"] == "ex-cine1"
    assert profile["capture_gamma_display"] == "Ex-Cine1"
    assert profile["capture_color_primaries_raw"] == "rec709"
    assert profile["capture_gamut_display"] == "Rec.709"


def test_s_cinetone_and_rec709_fixture() -> None:
    sidecar = FIXTURE_ROOT / "A7IV_SL31406M01.XML"
    profile = build_source_color_profile(sidecar, relative_sidecar_path="A7IV_SL31406M01.XML")
    assert profile["capture_gamma_raw"] == "s-cinetone"
    assert profile["capture_gamma_display"] == "S-Cinetone"
    assert profile["capture_color_primaries_raw"] == "rec709"
    assert profile["capture_gamut_display"] == "Rec.709"


def test_rec709_and_rec709_fixture() -> None:
    sidecar = FIXTURE_ROOT / "A7IV_SL31407M01.XML"
    profile = build_source_color_profile(sidecar, relative_sidecar_path="A7IV_SL31407M01.XML")
    assert profile["capture_gamma_raw"] == "rec709"
    assert profile["capture_gamma_display"] == "Rec.709"
    assert profile["capture_color_primaries_raw"] == "rec709"
    assert profile["capture_gamut_display"] == "Rec.709"


def test_coding_equations_isolation_critical_slog3() -> None:
    sidecar = FIXTURE_ROOT / "A7IV_SL31404M01.XML"
    profile = build_source_color_profile(sidecar, relative_sidecar_path="A7IV_SL31404M01.XML")
    assert profile["capture_gamma_display"] == "S-Log3"
    assert profile["capture_gamut_display"] == "S-Gamut3.Cine"
    assert profile["coding_equations_raw"] == "rec709"
    assert profile["capture_gamma_raw"] == "s-log3-cine"


def test_lut_not_recorded_when_absent() -> None:
    sidecar = FIXTURE_ROOT / "A7IV_SL31411M01.XML"
    profile = build_source_color_profile(sidecar, relative_sidecar_path="A7IV_SL31411M01.XML")
    assert profile["monitoring_lut_status"] == MONITORING_LUT_NOT_RECORDED
    assert profile["monitoring_lut_identity"] is None


def test_no_lut_inference_on_standard() -> None:
    sidecar = FIXTURE_ROOT / "A7IV_SL31404M01.XML"
    profile = build_source_color_profile(sidecar, relative_sidecar_path="A7IV_SL31404M01.XML")
    assert profile["monitoring_lut_status"] == MONITORING_LUT_NOT_RECORDED
    assert profile["monitoring_lut_identity"] is None


def test_explicit_lut_metadata_captured_not_applied() -> None:
    sidecar = FIXTURE_ROOT / "A7IV_SL31412M01.XML"
    profile = build_source_color_profile(sidecar, relative_sidecar_path="A7IV_SL31412M01.XML")
    assert profile["monitoring_lut_status"] == MONITORING_LUT_RECORDED
    assert profile["monitoring_lut_identity"] == "S-Cinetone Monitor [synthetic]"
    assert profile["capture_gamma_display"] == "S-Log3"
    assert profile["metadata_confidence"] == CONFIDENCE_CONFIRMED


def test_partial_confidence_when_only_marginal_color_data(
    tmp_path: Path,
) -> None:
    lut_only = _write(
        tmp_path,
        "lut_only.XML",
        '<?xml version="1.0"?><SonyXmlSidecar><ConfigItem Name="Look">'
        "<Value>foo</Value></ConfigItem></SonyXmlSidecar>",
    )
    profile = build_source_color_profile(lut_only)
    assert profile["metadata_confidence"] == CONFIDENCE_PARTIAL
    assert profile["capture_gamma_raw"] is None
    assert profile["monitoring_lut_status"] == MONITORING_LUT_RECORDED
    assert profile["monitoring_lut_identity"] == "foo"


def test_unknown_raw_preserved_no_display_invention(tmp_path: Path) -> None:
    unknown = _write(
        tmp_path,
        "unknown.XML",
        '<?xml version="1.0"?><SonyXmlSidecar><ConfigItem Name="CaptureGammaEquation">'
        "<Value>custom-propritary</Value></ConfigItem></SonyXmlSidecar>",
    )
    profile = build_source_color_profile(unknown)
    assert profile["capture_gamma_raw"] == "custom-propritary"
    assert profile["capture_gamma_display"] is None
    assert profile["metadata_confidence"] == CONFIDENCE_CONFIRMED


def test_uavailable_constant_shape() -> None:
    assert set(SOURCE_COLOR_PROFILE_UNAVAILABLE) == {
        "capture_gamma_raw",
        "capture_color_primaries_raw",
        "coding_equations_raw",
        "capture_gamma_display",
        "capture_gamut_display",
        "monitoring_lut_status",
        "monitoring_lut_identity",
        "metadata_source",
        "metadata_confidence",
        "sidecar_path",
    }
    assert SOURCE_COLOR_PROFILE_UNAVAILABLE["metadata_source"] == "UNKNOWN"
    assert SOURCE_COLOR_PROFILE_UNAVAILABLE["metadata_confidence"] == CONFIDENCE_UNAVAILABLE


def test_ffprobe_failure_does_not_invalidate_valid_sidecar(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import scripts.local_media_agent.ffprobe_metadata_extraction as extraction

    def failing_probe(tool: str, path: Path) -> dict:
        raise RuntimeError("moov atom not found")

    monkeypatch.setattr(extraction, "_probe_one", failing_probe)
    result = extraction.extract_metadata(
        FIXTURE_ROOT,
        {"extension_summary": {".mp4": 9}},
        ffprobe_path="ffprobe",
    )
    errors = {entry["relative_path"]: entry for entry in result["errors"]}
    assert "A7IV_SL31404.MP4" in errors
    profile = errors["A7IV_SL31404.MP4"]["source_color_profile"]
    assert profile["capture_gamma_raw"] == "s-log3-cine"
    assert profile["capture_gamma_display"] == "S-Log3"
    assert profile["metadata_confidence"] == CONFIDENCE_CONFIRMED


def test_ffprobe_success_attaches_sidecar_color_profile(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import scripts.local_media_agent.ffprobe_metadata_extraction as extraction

    synthetic_meta = {
        "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
        "duration_raw": "12.340000",
        "duration_origin": "format",
        "timecode": None,
        "video": {
            "codec": "h264",
            "width": 3840,
            "height": 2160,
            "frame_rate": {
                "display": "25",
                "raw_avg": "25/1",
                "raw_frame": "25/1",
                "variable": False,
            },
        },
        "audio": None,
    }

    def succeeding_probe(tool: str, path: Path) -> dict:
        return synthetic_meta

    monkeypatch.setattr(extraction, "_probe_one", succeeding_probe)
    result = extraction.extract_metadata(
        FIXTURE_ROOT,
        {"extension_summary": {".mp4": 9}},
        ffprobe_path="ffprobe",
    )
    matches = [e for e in result["results"] if e["relative_path"] == "A7IV_SL31404.MP4"]
    assert len(matches) == 1
    profile = matches[0]["source_color_profile"]
    assert profile["capture_gamma_raw"] == "s-log3-cine"
    assert profile["capture_gamut_display"] == "S-Gamut3.Cine"
    assert profile["sidecar_path"] == "A7IV_SL31404M01.XML"