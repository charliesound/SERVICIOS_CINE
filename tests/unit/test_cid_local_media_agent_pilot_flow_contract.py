from __future__ import annotations

from contextlib import contextmanager
from copy import deepcopy
import os
from pathlib import Path

from scripts.editorial_intelligence.transcription.transcription import (
    FakeTranscriptionBackend,
    TranscriptionResult,
)
from scripts.local_media_agent.pilot_flow import (
    PilotFlowDependencies,
    PilotFlowRequest,
    STATUS_COMPLETED_FLOW,
    STATUS_OUTPUT_INTEGRITY_FAILED,
    STATUS_PREFLIGHT_FAILED,
    STATUS_TRANSCRIPTION_FAILED,
    run_pilot_flow,
)


def _request(tmp_path: Path) -> PilotFlowRequest:
    root = tmp_path / "selected-media"
    root.mkdir()
    media = root / "interview.MOV"
    media.write_bytes(b"fixture media marker")
    model = tmp_path / "local-model"
    model.mkdir()
    return PilotFlowRequest(
        input_root=root,
        selected_media_path=media,
        asset_id="asset-001",
        model_local_path=model,
        language_hint=None,
    )


def _dependencies(calls: list[str], *, transcription_failure: bool = False) -> PilotFlowDependencies:
    def scanner(root):
        calls.append("scan")
        return {"status": "READ_ONLY_FOLDER_SCAN_COMPLETED", "privacy": {"original_media_modified": False}}

    def prober(asset_id, source_path):
        calls.append("probe")
        return {
            "media_probe_state": "PROBE_COMPLETED",
            "asset_id": asset_id,
            "source_reference": {
                "internal_local_source_reference": str(source_path),
                "sanitized_external_source_label": Path(source_path).name,
            },
            "container": {"duration_seconds": 12.0, "start_time_seconds": 0.0},
            "audio": {
                "has_audio": True,
                "preferred_audio_stream_index": 0,
                "streams": [{"stream_index": 0, "channels": 1}],
            },
            "timecode": {"TIMECODE_PRESENT": False, "embedded_timecode_status": "absent"},
        }

    @contextmanager
    def audio_extractor(probe_result, **kwargs):
        calls.append("audio")
        result = {
            "state": "AUDIO_EXTRACTION_COMPLETED",
            "asset_id": probe_result["asset_id"],
            "audio": {
                "source_audio_stream_index": 0,
                "extracted_audio_temp_ref": "/tmp/private.wav",
                "extracted_audio_start_seconds": 0.0,
                "duration_seconds": 12.0,
            },
        }

        class Result:
            state = "AUDIO_EXTRACTION_COMPLETED"
            path = Path("/tmp/private.wav")

            def to_dict(self):
                return result

        yield Result()
        assert calls[-1] in {"transcribe", "provenance"}

    def transcriber(request, backend):
        calls.append("transcribe")
        if transcription_failure:
            return TranscriptionResult(
                {
                    "status": "MODEL_NOT_AVAILABLE",
                    "asset_id": request.asset_id,
                    "detected_language": "es",
                    "language_probability": 0.9,
                    "segments": [],
                }
            )
        return TranscriptionResult(
            {
                "status": "TRANSCRIPTION_COMPLETED",
                "asset_id": request.asset_id,
                "source_audio_stream_index": 0,
                "detected_language": "es",
                "language_probability": 0.9,
                "segments": [
                    {
                        "segment_index": 0,
                        "start_seconds": 1.0,
                        "end_seconds": 2.5,
                        "source_start_seconds": 1.0,
                        "source_end_seconds": 2.5,
                        "text": "Original bilingual interview text",
                    }
                ],
            },
            segments=[
                {
                    "segment_index": 0,
                    "start_seconds": 1.0,
                    "end_seconds": 2.5,
                    "source_start_seconds": 1.0,
                    "source_end_seconds": 2.5,
                    "text": "Original bilingual interview text",
                }
            ],
        )

    def provenance(payload, **kwargs):
        calls.append("provenance")
        from scripts.editorial_intelligence.transcript_provenance.transcript_segment import (
            transcription_result_to_transcript_segments,
        )

        return transcription_result_to_transcript_segments(payload, **kwargs)

    return PilotFlowDependencies(
        scanner=scanner,
        prober=prober,
        audio_extractor=audio_extractor,
        transcriber=transcriber,
        provenance_builder=provenance,
        backend_factory=lambda *args, **kwargs: FakeTranscriptionBackend(),
        tool_checker=lambda name: f"/usr/bin/{name}",
    )


def test_successful_flow_orders_existing_components_and_preserves_text(tmp_path: Path) -> None:
    calls: list[str] = []
    result = run_pilot_flow(_request(tmp_path), dependencies=_dependencies(calls))

    assert result["status"] == STATUS_COMPLETED_FLOW
    assert calls == ["scan", "probe", "audio", "transcribe", "provenance"]
    segment = result["transcript_segments"][0]
    assert segment["text"] == "Original bilingual interview text"
    assert segment["source_start_seconds"] == 1.0
    assert segment["source_end_seconds"] == 2.5
    assert result["language"] == {
        "detected_language": "es",
        "language_probability": 0.9,
        "interpretation": "document_level_metadata_only",
    }
    assert result["privacy"]["source_media_modified"] is False
    assert "internal_local_source_reference" not in result["metadata"]["source_reference"]
    assert "extracted_audio_temp_ref" not in result["audio"]["audio"]


def test_preflight_short_circuits_before_scan(tmp_path: Path) -> None:
    calls: list[str] = []
    base = _dependencies(calls)
    deps = PilotFlowDependencies(
        scanner=base.scanner,
        prober=base.prober,
        audio_extractor=base.audio_extractor,
        transcriber=base.transcriber,
        provenance_builder=base.provenance_builder,
        backend_factory=base.backend_factory,
        tool_checker=lambda name: None,
    )

    result = run_pilot_flow(_request(tmp_path), dependencies=deps)

    assert result["status"] == STATUS_PREFLIGHT_FAILED
    assert result["error"]["error_code"] == "FFPROBE_NOT_AVAILABLE"
    assert calls == []


def test_transcription_failure_does_not_build_provenance(tmp_path: Path) -> None:
    calls: list[str] = []
    result = run_pilot_flow(
        _request(tmp_path),
        dependencies=_dependencies(calls, transcription_failure=True),
    )

    assert result["status"] == STATUS_TRANSCRIPTION_FAILED
    assert result["failed_stage"] == "transcription"
    assert calls == ["scan", "probe", "audio", "transcribe"]
    assert "transcript_segments" not in result


def test_empty_provenance_output_cannot_complete_flow(tmp_path: Path) -> None:
    calls: list[str] = []
    base = _dependencies(calls)
    deps = PilotFlowDependencies(
        scanner=base.scanner,
        prober=base.prober,
        audio_extractor=base.audio_extractor,
        transcriber=base.transcriber,
        provenance_builder=lambda payload, **kwargs: [],
        backend_factory=base.backend_factory,
        tool_checker=base.tool_checker,
    )

    result = run_pilot_flow(_request(tmp_path), dependencies=deps)

    assert result["status"] == STATUS_OUTPUT_INTEGRITY_FAILED
    assert result["failed_stage"] == "output_preflight"
    assert result["error"]["error_code"] == "TRANSCRIPT_SEGMENTS_EMPTY"
    assert "transcript_segments" not in result


def test_unexpected_orchestration_failures_are_sanitized(tmp_path: Path) -> None:
    calls: list[str] = []
    base = _dependencies(calls)

    def failing_scanner(root):
        raise RuntimeError(
            "Traceback (most recent call last): /private/repository/root "
            "/private/source/media.mov"
        )

    deps = PilotFlowDependencies(
        scanner=failing_scanner,
        prober=base.prober,
        audio_extractor=base.audio_extractor,
        transcriber=base.transcriber,
        provenance_builder=base.provenance_builder,
        backend_factory=base.backend_factory,
        tool_checker=base.tool_checker,
    )

    result = run_pilot_flow(_request(tmp_path), dependencies=deps)

    assert result["status"] == "PILOT_FLOW_SCAN_FAILED"
    assert result["error"] == {
        "error_code": "SCAN_ORCHESTRATION_FAILED",
        "message_sanitized": "SCAN_ORCHESTRATION_FAILED",
    }
    assert "Traceback (most recent call last):" not in str(result)
    assert "/private/repository/root" not in str(result)
    assert "/private/source/media.mov" not in str(result)


def test_noncanonical_provenance_output_cannot_complete_flow(tmp_path: Path) -> None:
    calls: list[str] = []
    base = _dependencies(calls)

    class MalformedSegment:
        def to_dict(self):
            return {
                "phase": "unexpected",
                "asset_id": "asset-001",
                "segment_index": 0,
                "text": "unrepaired text",
            }

    deps = PilotFlowDependencies(
        scanner=base.scanner,
        prober=base.prober,
        audio_extractor=base.audio_extractor,
        transcriber=base.transcriber,
        provenance_builder=lambda payload, **kwargs: [MalformedSegment()],
        backend_factory=base.backend_factory,
        tool_checker=base.tool_checker,
    )

    result = run_pilot_flow(_request(tmp_path), dependencies=deps)

    assert result["status"] == STATUS_OUTPUT_INTEGRITY_FAILED
    assert result["failed_stage"] == "output_preflight"
    assert result["error"]["error_code"] == "TRANSCRIPT_SEGMENTS_NOT_CANONICAL"
    assert "transcript_segments" not in result
    assert result["status"] != STATUS_COMPLETED_FLOW


def test_full_keyset_with_invalid_canonical_values_cannot_complete_flow(
    tmp_path: Path,
) -> None:
    base = _dependencies([])
    canonical_segment = base.provenance_builder(
        {
            "status": "TRANSCRIPTION_COMPLETED",
            "asset_id": "asset-001",
            "source_audio_stream_index": 0,
            "audio_duration_seconds": 12.0,
            "segments": [
                {
                    "segment_index": 0,
                    "start_seconds": 1.0,
                    "end_seconds": 2.5,
                    "source_start_seconds": 1.0,
                    "source_end_seconds": 2.5,
                    "text": "Original bilingual interview text",
                }
            ],
        },
        audio_extraction_payload={
            "audio": {"extracted_audio_start_seconds": 0.0},
        },
        media_probe_payload={
            "timecode": {
                "TIMECODE_PRESENT": False,
                "embedded_timecode_status": "absent",
            },
        },
    )[0].to_dict()

    invalid_cases = {
        "asset_id": lambda value: value.update(asset_id="other-asset"),
        "segment_identity": lambda value: value.update(segment_index="0"),
        "negative_segment_identity": lambda value: value.update(segment_index=-1),
        "text": lambda value: value.update(text=123),
        "timing_type": lambda value: value.update(source_start_seconds="1.0"),
        "timing_order": lambda value: value.update(source_end_seconds=0.5),
        "timecode": lambda value: value["source_timecode"].update(status="invalid"),
        "provenance": lambda value: value["provenance"].update(asset_id="other-asset"),
    }

    for case_name, mutate in invalid_cases.items():
        segment = deepcopy(canonical_segment)
        mutate(segment)

        class InvalidSegment:
            def to_dict(self):
                return segment

        deps = PilotFlowDependencies(
            scanner=base.scanner,
            prober=base.prober,
            audio_extractor=base.audio_extractor,
            transcriber=base.transcriber,
            provenance_builder=lambda payload, **kwargs: [InvalidSegment()],
            backend_factory=base.backend_factory,
            tool_checker=base.tool_checker,
        )
        case_dir = tmp_path / case_name
        case_dir.mkdir()
        result = run_pilot_flow(
            _request(case_dir),
            dependencies=deps,
        )

        assert result["status"] == STATUS_OUTPUT_INTEGRITY_FAILED
        assert result["failed_stage"] == "output_preflight"
        assert result["error"]["error_code"] == "TRANSCRIPT_SEGMENTS_NOT_CANONICAL"
        assert "transcript_segments" not in result


def test_nonmonotonic_segment_indices_preserve_canonical_order(tmp_path: Path) -> None:
    base = _dependencies([])
    canonical_segments = base.provenance_builder(
        {
            "status": "TRANSCRIPTION_COMPLETED",
            "asset_id": "asset-001",
            "source_audio_stream_index": 0,
            "audio_duration_seconds": 12.0,
            "segments": [
                {
                    "segment_index": 7,
                    "start_seconds": 1.0,
                    "end_seconds": 1.5,
                    "source_start_seconds": 1.0,
                    "source_end_seconds": 1.5,
                    "text": "First canonical segment",
                },
                {
                    "segment_index": 2,
                    "start_seconds": 2.0,
                    "end_seconds": 2.5,
                    "source_start_seconds": 2.0,
                    "source_end_seconds": 2.5,
                    "text": "Second canonical segment",
                },
            ],
        },
        audio_extraction_payload={"audio": {"extracted_audio_start_seconds": 0.0}},
        media_probe_payload={
            "timecode": {"TIMECODE_PRESENT": False, "embedded_timecode_status": "absent"}
        },
    )
    deps = PilotFlowDependencies(
        scanner=base.scanner,
        prober=base.prober,
        audio_extractor=base.audio_extractor,
        transcriber=base.transcriber,
        provenance_builder=lambda payload, **kwargs: canonical_segments,
        backend_factory=base.backend_factory,
        tool_checker=base.tool_checker,
    )

    result = run_pilot_flow(_request(tmp_path), dependencies=deps)

    assert result["status"] == STATUS_COMPLETED_FLOW
    assert [item["segment_index"] for item in result["transcript_segments"]] == [7, 2]
    assert [item["source_start_seconds"] for item in result["transcript_segments"]] == [1.0, 2.0]


def test_nonmonotonic_source_starts_preserve_canonical_values(tmp_path: Path) -> None:
    base = _dependencies([])
    canonical_segments = base.provenance_builder(
        {
            "status": "TRANSCRIPTION_COMPLETED",
            "asset_id": "asset-001",
            "source_audio_stream_index": 0,
            "audio_duration_seconds": 12.0,
            "segments": [
                {
                    "segment_index": 0,
                    "start_seconds": 1.0,
                    "end_seconds": 1.5,
                    "source_start_seconds": 10.0,
                    "source_end_seconds": 11.0,
                    "text": "First canonical segment",
                },
                {
                    "segment_index": 1,
                    "start_seconds": 2.0,
                    "end_seconds": 2.5,
                    "source_start_seconds": 5.0,
                    "source_end_seconds": 6.0,
                    "text": "Second canonical segment",
                },
            ],
        },
        audio_extraction_payload={"audio": {"extracted_audio_start_seconds": 0.0}},
        media_probe_payload={
            "timecode": {"TIMECODE_PRESENT": False, "embedded_timecode_status": "absent"}
        },
    )
    deps = PilotFlowDependencies(
        scanner=base.scanner,
        prober=base.prober,
        audio_extractor=base.audio_extractor,
        transcriber=base.transcriber,
        provenance_builder=lambda payload, **kwargs: canonical_segments,
        backend_factory=base.backend_factory,
        tool_checker=base.tool_checker,
    )

    result = run_pilot_flow(_request(tmp_path), dependencies=deps)

    assert result["status"] == STATUS_COMPLETED_FLOW
    assert [item["source_start_seconds"] for item in result["transcript_segments"]] == [10.0, 5.0]
    assert [item["source_end_seconds"] for item in result["transcript_segments"]] == [11.0, 6.0]
    assert [item["text"] for item in result["transcript_segments"]] == [
        "First canonical segment",
        "Second canonical segment",
    ]


def test_selected_media_must_be_explicitly_inside_root(tmp_path: Path) -> None:
    request = _request(tmp_path)
    outside = tmp_path / "outside.mp4"
    outside.write_bytes(b"outside")
    request = PilotFlowRequest(
        input_root=request.input_root,
        selected_media_path=outside,
        asset_id=request.asset_id,
        model_local_path=request.model_local_path,
    )

    result = run_pilot_flow(request, dependencies=_dependencies([]))

    assert result["status"] == STATUS_PREFLIGHT_FAILED
    assert result["error"]["error_code"] == "SELECTED_MEDIA_OUTSIDE_INPUT_ROOT"


def test_in_root_selected_media_symlink_is_rejected_before_downstream_stages(
    tmp_path: Path,
) -> None:
    request = _request(tmp_path)
    real_media = request.input_root / "real_media.mp4"
    real_media.write_bytes(b"real media")
    symlink_media = request.input_root / "alias_media.mp4"
    os.symlink(real_media, symlink_media)
    calls: list[str] = []
    request = PilotFlowRequest(
        input_root=request.input_root,
        selected_media_path=symlink_media,
        asset_id=request.asset_id,
        model_local_path=request.model_local_path,
    )

    result = run_pilot_flow(request, dependencies=_dependencies(calls))

    assert result["status"] == STATUS_PREFLIGHT_FAILED
    assert result["error"]["error_code"] == "SELECTED_MEDIA_SYMLINK_REJECTED"
    assert calls == []


def test_out_of_root_selected_media_symlink_is_rejected_before_downstream_stages(
    tmp_path: Path,
) -> None:
    request = _request(tmp_path)
    outside_media = tmp_path / "outside-media.mp4"
    outside_media.write_bytes(b"outside media")
    symlink_media = request.input_root / "outside_alias.mp4"
    os.symlink(outside_media, symlink_media)
    calls: list[str] = []
    request = PilotFlowRequest(
        input_root=request.input_root,
        selected_media_path=symlink_media,
        asset_id=request.asset_id,
        model_local_path=request.model_local_path,
    )

    result = run_pilot_flow(request, dependencies=_dependencies(calls))

    assert result["status"] == STATUS_PREFLIGHT_FAILED
    assert result["error"]["error_code"] == "SELECTED_MEDIA_SYMLINK_REJECTED"
    assert calls == []


def test_root_symlink_is_rejected_before_downstream_stages(tmp_path: Path) -> None:
    request = _request(tmp_path)
    real_root = request.input_root
    symlink_root = tmp_path / "root-alias"
    os.symlink(real_root, symlink_root, target_is_directory=True)
    calls: list[str] = []
    request = PilotFlowRequest(
        input_root=symlink_root,
        selected_media_path=real_root / "interview.MOV",
        asset_id=request.asset_id,
        model_local_path=request.model_local_path,
    )

    result = run_pilot_flow(request, dependencies=_dependencies(calls))

    assert result["status"] == STATUS_PREFLIGHT_FAILED
    assert result["error"]["error_code"] == "ROOT_SYMLINK_REJECTED"
    assert calls == []


def test_in_root_parent_directory_symlink_is_rejected_before_downstream_stages(
    tmp_path: Path,
) -> None:
    request = _request(tmp_path)
    real_dir = request.input_root / "real-dir"
    real_dir.mkdir()
    media = real_dir / "clip.mp4"
    media.write_bytes(b"real media")
    alias_dir = request.input_root / "alias-dir"
    os.symlink(real_dir, alias_dir, target_is_directory=True)
    calls: list[str] = []
    request = PilotFlowRequest(
        input_root=request.input_root,
        selected_media_path=alias_dir / "clip.mp4",
        asset_id=request.asset_id,
        model_local_path=request.model_local_path,
    )

    result = run_pilot_flow(request, dependencies=_dependencies(calls))

    assert result["status"] == STATUS_PREFLIGHT_FAILED
    assert result["error"]["error_code"] == "SELECTED_MEDIA_PARENT_SYMLINK_REJECTED"
    assert calls == []


def test_nested_parent_directory_symlink_is_rejected_before_downstream_stages(
    tmp_path: Path,
) -> None:
    request = _request(tmp_path)
    real_a = request.input_root / "real-a"
    real_b = real_a / "real-b"
    real_b.mkdir(parents=True)
    media = real_b / "clip.mp4"
    media.write_bytes(b"real media")
    safe_a = request.input_root / "safe-a"
    safe_a.mkdir()
    alias_b = safe_a / "alias-b"
    os.symlink(real_b, alias_b, target_is_directory=True)
    calls: list[str] = []
    request = PilotFlowRequest(
        input_root=request.input_root,
        selected_media_path=alias_b / "clip.mp4",
        asset_id=request.asset_id,
        model_local_path=request.model_local_path,
    )

    result = run_pilot_flow(request, dependencies=_dependencies(calls))

    assert result["status"] == STATUS_PREFLIGHT_FAILED
    assert result["error"]["error_code"] == "SELECTED_MEDIA_PARENT_SYMLINK_REJECTED"
    assert calls == []


def test_out_of_root_parent_directory_symlink_is_rejected_before_downstream_stages(
    tmp_path: Path,
) -> None:
    request = _request(tmp_path)
    outside_dir = tmp_path / "outside-dir"
    outside_dir.mkdir()
    (outside_dir / "clip.mp4").write_bytes(b"outside media")
    alias_dir = request.input_root / "outside-alias"
    os.symlink(outside_dir, alias_dir, target_is_directory=True)
    calls: list[str] = []
    request = PilotFlowRequest(
        input_root=request.input_root,
        selected_media_path=alias_dir / "clip.mp4",
        asset_id=request.asset_id,
        model_local_path=request.model_local_path,
    )

    result = run_pilot_flow(request, dependencies=_dependencies(calls))

    assert result["status"] == STATUS_PREFLIGHT_FAILED
    assert result["error"]["error_code"] == "SELECTED_MEDIA_PARENT_SYMLINK_REJECTED"
    assert calls == []


def test_broken_parent_directory_symlink_is_rejected_before_missing_file_error(
    tmp_path: Path,
) -> None:
    request = _request(tmp_path)
    alias_dir = request.input_root / "broken-alias"
    os.symlink(tmp_path / "missing-dir", alias_dir, target_is_directory=True)
    calls: list[str] = []
    request = PilotFlowRequest(
        input_root=request.input_root,
        selected_media_path=alias_dir / "clip.mp4",
        asset_id=request.asset_id,
        model_local_path=request.model_local_path,
    )

    result = run_pilot_flow(request, dependencies=_dependencies(calls))

    assert result["status"] == STATUS_PREFLIGHT_FAILED
    assert result["error"]["error_code"] == "SELECTED_MEDIA_PARENT_SYMLINK_REJECTED"
    assert calls == []


def test_normal_nested_regular_media_path_remains_accepted(tmp_path: Path) -> None:
    request = _request(tmp_path)
    nested_dir = request.input_root / "a" / "b"
    nested_dir.mkdir(parents=True)
    media = nested_dir / "clip.mp4"
    media.write_bytes(b"nested media")
    calls: list[str] = []
    request = PilotFlowRequest(
        input_root=request.input_root,
        selected_media_path=media,
        asset_id=request.asset_id,
        model_local_path=request.model_local_path,
    )

    result = run_pilot_flow(request, dependencies=_dependencies(calls))

    assert result["status"] == STATUS_COMPLETED_FLOW
    assert calls == ["scan", "probe", "audio", "transcribe", "provenance"]
