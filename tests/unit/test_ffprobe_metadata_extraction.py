from __future__ import annotations

import math

import pytest

from scripts.local_media_agent.ffprobe_metadata_extraction import _parse_ffprobe


def test_format_raw_duration_is_preferred_and_preserved() -> None:
    result = _parse_ffprobe(
        {
            "format": {"duration": "12.345678"},
            "streams": [{"codec_type": "video", "duration": "99.125"}],
        }
    )

    assert result["duration_raw"] == "12.345678"
    assert result["duration_origin"] == "format"
    assert result["duration_seconds"] == 12.346


@pytest.mark.parametrize("invalid", [None, "", "0", "-1", "nan", "inf"])
def test_first_video_stream_duration_fallback_requires_finite_positive(
    invalid: str | None,
) -> None:
    result = _parse_ffprobe(
        {
            "format": {"duration": invalid},
            "streams": [
                {"codec_type": "video", "duration": "20.000001"},
                {"codec_type": "video", "duration": "30.5"},
            ],
        }
    )

    assert result["duration_raw"] == "20.000001"
    assert result["duration_origin"] == "video_stream"
    if invalid in (None, ""):
        assert result["duration_seconds"] is None
    elif invalid == "nan":
        assert math.isnan(result["duration_seconds"])
    else:
        assert result["duration_seconds"] == float(invalid)


def test_invalid_format_and_first_video_duration_yield_no_duration() -> None:
    result = _parse_ffprobe(
        {
            "format": {"duration": "nan"},
            "streams": [
                {"codec_type": "video", "duration": "0"},
                {"codec_type": "video", "duration": "30"},
            ],
        }
    )

    assert result["duration_raw"] is None
    assert result["duration_origin"] is None
    assert math.isnan(result["duration_seconds"])


def test_video_stream_emits_exact_sar_dar_and_rotation() -> None:
    result = _parse_ffprobe(
        {
            "format": {"duration": "1.0"},
            "streams": [
                {
                    "codec_type": "video",
                    "duration": "1.0",
                    "width": "1920",
                    "height": "1080",
                    "sample_aspect_ratio": "4:3",
                    "display_aspect_ratio": "16:9",
                    "tags": {"rotate": "90"},
                }
            ],
        }
    )

    assert result["video"]["sample_aspect_ratio"] == {"numerator": 4, "denominator": 3}
    assert result["video"]["display_aspect_ratio"] == {"numerator": 16, "denominator": 9}
    assert result["video"]["rotation"] == 90


def test_absent_rationals_are_null_and_not_invented() -> None:
    result = _parse_ffprobe(
        {
            "format": {"duration": "1.0"},
            "streams": [
                {
                    "codec_type": "video",
                    "duration": "1.0",
                    "sample_aspect_ratio": "0:1",
                    "display_aspect_ratio": "N/A",
                }
            ],
        }
    )

    assert result["video"]["sample_aspect_ratio"] is None
    assert result["video"]["display_aspect_ratio"] is None


def test_rotation_normalized_and_prefers_explicit_metadata() -> None:
    result = _parse_ffprobe(
        {
            "format": {"duration": "1.0"},
            "streams": [
                {
                    "codec_type": "video",
                    "duration": "1.0",
                    "width": "1080",
                    "height": "1920",
                    "tags": {"rotate": "270"},
                }
            ],
        }
    )

    assert result["video"]["rotation"] == 270


def test_no_rotation_inferred_from_width_height() -> None:
    result = _parse_ffprobe(
        {
            "format": {"duration": "1.0"},
            "streams": [
                {
                    "codec_type": "video",
                    "duration": "1.0",
                    "width": "1080",
                    "height": "1920",
                }
            ],
        }
    )

    assert result["video"]["rotation"] is None


import threading
from pathlib import Path
from unittest.mock import patch

from scripts.local_media_agent.ffprobe_metadata_extraction import (
    ERROR_CATEGORY_METADATA,
    extract_metadata,
)


def _make_asset(root: Path, rel: str, size: int = 16) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"\x00" * size)
    return path


def _scanner(root: Path) -> dict:
    exts: dict[str, int] = {}
    for path in root.rglob("*"):
        if path.is_file():
            exts[path.suffix.lower()] = exts.get(path.suffix.lower(), 0) + 1
    return {"extension_summary": exts}


def _probe_ok(tool, path) -> dict:
    return {
        "format_name": "mov,mp4",
        "duration_seconds": 5.0,
        "video": {"codec": "h264", "width": 1920, "height": 1080},
    }


def _probe_fail(tool, path) -> dict:
    raise RuntimeError("moov atom not found")


def test_legacy_call_without_new_args_still_works(tmp_path: Path) -> None:
    _make_asset(tmp_path, "a.MP4")
    with patch(
        "scripts.local_media_agent.ffprobe_metadata_extraction._probe_one",
        side_effect=_probe_ok,
    ) as probe:
        meta = extract_metadata(tmp_path, _scanner(tmp_path), ffprobe_path="/fake/ffprobe")
    assert meta["metadata_success_count"] == 1
    assert probe.call_count == 1
    assert "incremental" in meta


def test_unchanged_valid_cached_item_skips_ffprobe(tmp_path: Path) -> None:
    _make_asset(tmp_path, "a.MP4")
    reuse = {
        "a.MP4": {
            "ffprobe_metadata": {"duration_seconds": 5.0, "video": {"codec": "h264"}},
            "source_color_profile": {"gamma": "ex-cine1"},
        }
    }
    with patch(
        "scripts.local_media_agent.ffprobe_metadata_extraction._probe_one",
        side_effect=_probe_ok,
    ) as probe:
        meta = extract_metadata(
            tmp_path,
            _scanner(tmp_path),
            ffprobe_path="/fake/ffprobe",
            reuse_metadata=reuse,
            only_paths=set(),
        )
    assert probe.call_count == 0
    assert meta["incremental"]["reused"] == 1
    assert meta["incremental"]["analyzed"] == 0
    assert meta["results"][0]["duration_seconds"] == 5.0
    assert meta["results"][0]["source_color_profile"]["gamma"] == "ex-cine1"


def test_new_item_invokes_ffprobe(tmp_path: Path) -> None:
    _make_asset(tmp_path, "a.MP4")
    with patch(
        "scripts.local_media_agent.ffprobe_metadata_extraction._probe_one",
        side_effect=_probe_ok,
    ) as probe:
        meta = extract_metadata(
            tmp_path,
            _scanner(tmp_path),
            ffprobe_path="/fake/ffprobe",
            only_paths={"a.MP4"},
        )
    assert probe.call_count == 1
    assert meta["incremental"]["analyzed"] == 1


def test_modified_item_invokes_ffprobe(tmp_path: Path) -> None:
    _make_asset(tmp_path, "a.MP4")
    reuse = {"a.MP4": {"ffprobe_metadata": {"duration_seconds": 5.0}}}
    with patch(
        "scripts.local_media_agent.ffprobe_metadata_extraction._probe_one",
        side_effect=_probe_ok,
    ) as probe:
        meta = extract_metadata(
            tmp_path,
            _scanner(tmp_path),
            ffprobe_path="/fake/ffprobe",
            reuse_metadata=reuse,
            only_paths={"a.MP4"},
        )
    assert probe.call_count == 1
    assert meta["incremental"]["analyzed"] == 1


def test_probe_failure_produces_metadata_error_and_retains_item(tmp_path: Path) -> None:
    _make_asset(tmp_path, "broken.MP4")
    with patch(
        "scripts.local_media_agent.ffprobe_metadata_extraction._probe_one",
        side_effect=_probe_fail,
    ):
        meta = extract_metadata(tmp_path, _scanner(tmp_path), ffprobe_path="/fake/ffprobe")
    assert meta["metadata_error_count"] == 1
    error = meta["errors"][0]
    assert error["relative_path"] == "broken.MP4"
    assert error["error_category"] == ERROR_CATEGORY_METADATA
    assert "moov atom not found" in error["error"]
    assert meta["media_attempted"] == 1


def test_source_color_profile_survives_ffprobe_failure(tmp_path: Path) -> None:
    _make_asset(tmp_path, "broken.MP4")
    with patch(
        "scripts.local_media_agent.ffprobe_metadata_extraction._resolve_sidecar_color_profile",
        return_value={"gamma": "ex-cine1", "primaries": "rec709"},
    ), patch(
        "scripts.local_media_agent.ffprobe_metadata_extraction._probe_one",
        side_effect=_probe_fail,
    ):
        meta = extract_metadata(tmp_path, _scanner(tmp_path), ffprobe_path="/fake/ffprobe")
    error = meta["errors"][0]
    assert error["source_color_profile"]["gamma"] == "ex-cine1"
    assert error["source_color_profile"]["primaries"] == "rec709"


def test_progress_callback_receives_expected_lifecycle(tmp_path: Path) -> None:
    _make_asset(tmp_path, "a.MP4")
    _make_asset(tmp_path, "b.MP4")
    events: list[dict] = []
    with patch(
        "scripts.local_media_agent.ffprobe_metadata_extraction._probe_one",
        side_effect=_probe_ok,
    ):
        extract_metadata(
            tmp_path,
            _scanner(tmp_path),
            ffprobe_path="/fake/ffprobe",
            progress_callback=events.append,
        )
    kinds = [e["phase_event"] for e in events]
    assert kinds[0] == "phase_started"
    assert kinds[-1] == "phase_completed"
    assert "item_started" in kinds
    assert "item_completed" in kinds


def test_processed_never_exceeds_total(tmp_path: Path) -> None:
    _make_asset(tmp_path, "a.MP4")
    _make_asset(tmp_path, "b.MP4")
    events: list[dict] = []
    with patch(
        "scripts.local_media_agent.ffprobe_metadata_extraction._probe_one",
        side_effect=_probe_ok,
    ):
        extract_metadata(
            tmp_path,
            _scanner(tmp_path),
            ffprobe_path="/fake/ffprobe",
            progress_callback=events.append,
        )
    total = events[0]["total"]
    for e in events:
        assert e["processed"] <= total


def test_cancelled_before_first_item_no_probes(tmp_path: Path) -> None:
    _make_asset(tmp_path, "a.MP4")
    cancel = threading.Event()
    cancel.set()
    with patch(
        "scripts.local_media_agent.ffprobe_metadata_extraction._probe_one",
        side_effect=_probe_ok,
    ) as probe:
        meta = extract_metadata(
            tmp_path, _scanner(tmp_path), ffprobe_path="/fake/ffprobe", cancel_event=cancel
        )
    assert probe.call_count == 0
    assert meta["cancelled"] is True


def test_cancel_between_items_stops_before_next_and_retains_completed(tmp_path: Path) -> None:
    _make_asset(tmp_path, "a.MP4")
    _make_asset(tmp_path, "b.MP4")
    cancel = threading.Event()
    calls = {"n": 0}

    def probe_abort(tool, path) -> dict:
        calls["n"] += 1
        if calls["n"] >= 1:
            cancel.set()
        return _probe_ok(tool, path)

    with patch(
        "scripts.local_media_agent.ffprobe_metadata_extraction._probe_one",
        side_effect=probe_abort,
    ):
        meta = extract_metadata(
            tmp_path, _scanner(tmp_path), ffprobe_path="/fake/ffprobe", cancel_event=cancel
        )
    assert calls["n"] == 1
    assert meta["cancelled"] is True
    # completed items retained
    assert meta["metadata_success_count"] >= 1
