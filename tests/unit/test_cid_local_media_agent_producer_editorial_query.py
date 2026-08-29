from __future__ import annotations

import io
import json

import pytest

from scripts.local_media_agent import cid_cli, producer_editorial_query
from scripts.local_media_agent.producer_editorial_query import (
    AUDIO_ONLY_STATUS,
    EDITOR_HANDOFF_FORMAT,
    EDITOR_HANDOFF_REASON_AUDIO_ONLY,
    EDITOR_HANDOFF_REASON_CANDIDATE_NOT_FOUND,
    MAPPED_STATUS,
    NAVIGATION_AVAILABLE,
    NAVIGATION_REASON_AUDIO_ONLY,
    NAVIGATION_REASON_CANDIDATE_NOT_FOUND,
    NAVIGATION_UNAVAILABLE,
    STATUS_NO_RESULTS,
    STATUS_RESULTS,
    STATUS_UNSUPPORTED_CHARACTER,
    STATUS_UNSUPPORTED_TOPIC,
    build_editor_handoff_package,
    build_evidence_navigation,
    query_producer_evidence,
    resolve_editor_handoff_by_candidate_id,
    resolve_navigation_by_candidate_id,
)

EVIDENCE_PATH = "/tmp/opencode/producer_editorial_query_synthetic_v1.json"


def _record(
    cid: str,
    subject: str,
    topic: str,
    *,
    mapped: bool = True,
) -> dict:
    audio_start = 100.0
    audio_end = 200.0
    if mapped:
        return {
            "candidate_id": cid,
            "project": "Siruela",
            "interview_subject": subject,
            "topic": topic,
            "LEXICAL_HIT_TEXT": "hit",
            "HIT_AUDIO_START": 105.0,
            "HIT_AUDIO_END": 110.0,
            "HIT_VIDEO_MAPPING_STATUS": MAPPED_STATUS,
            "PRODUCER_CONTEXT_EXCERPT": f"excerpt for {cid}",
            "EXCERPT_SEGMENT_START_INDEX": 1,
            "EXCERPT_SEGMENT_END_INDEX": 1,
            "EXCERPT_SEGMENT_COUNT": 1,
            "EXCERPT_AUDIO_START": audio_start,
            "EXCERPT_AUDIO_END": audio_end,
            "EXCERPT_VIDEO_MAPPING_STATUS": MAPPED_STATUS,
            "video_clip": "CLIP.MP4",
            "EXCERPT_VIDEO_RELATIVE_START": 12.25,
            "EXCERPT_VIDEO_RELATIVE_END": 12.75,
            "SPEAKER_ATTRIBUTION": "UNKNOWN",
            "HUMAN_LABEL": "RELEVANT",
            "HUMAN_PRODUCER_ELIGIBLE": True,
            "EDITORIAL_NOTE": f"note {cid}",
        }
    return {
        "candidate_id": cid,
        "project": "Siruela",
        "interview_subject": subject,
        "topic": topic,
        "LEXICAL_HIT_TEXT": "hit",
        "HIT_AUDIO_START": 105.0,
        "HIT_AUDIO_END": 110.0,
        "HIT_VIDEO_MAPPING_STATUS": AUDIO_ONLY_STATUS,
        "PRODUCER_CONTEXT_EXCERPT": f"excerpt for {cid} (audio only)",
        "EXCERPT_SEGMENT_START_INDEX": 1,
        "EXCERPT_SEGMENT_END_INDEX": 1,
        "EXCERPT_SEGMENT_COUNT": 1,
        "EXCERPT_AUDIO_START": audio_start,
        "EXCERPT_AUDIO_END": audio_end,
        "EXCERPT_VIDEO_MAPPING_STATUS": AUDIO_ONLY_STATUS,
        "video_clip": None,
        "EXCERPT_VIDEO_RELATIVE_START": None,
        "EXCERPT_VIDEO_RELATIVE_END": None,
        "SPEAKER_ATTRIBUTION": "UNKNOWN",
        "HUMAN_LABEL": "RELEVANT",
        "HUMAN_PRODUCER_ELIGIBLE": True,
        "EDITORIAL_NOTE": f"note {cid}",
    }


@pytest.fixture(scope="module", autouse=True)
def _write_synthetic_evidence():
    items = [
        _record("K-JOV-1", "Kiko Traza", "jóvenes/relevo generacional", mapped=False),
        _record("P-JOV-1", "Pruden", "jóvenes/relevo generacional"),
        _record("P-JOV-2", "Pruden", "jóvenes/relevo generacional"),
        _record("K-PROB-1", "Kiko Traza", "problemas/dificultades", mapped=False),
        _record("P-PROB-1", "Pruden", "problemas/dificultades"),
        _record("P-PROB-2", "Pruden", "problemas/dificultades"),
        _record("K-OVE-1", "Kiko Traza", "ovejas/ovino"),
        _record("P-OVE-1", "Pruden", "ovejas/ovino", mapped=False),
        _record("P-OVE-2", "Pruden", "ovejas/ovino", mapped=False),
        _record("P-OVE-3", "Pruden", "ovejas/ovino"),
    ]
    with open(EVIDENCE_PATH, "w", encoding="utf-8") as handle:
        json.dump({"PROJECT": "Siruela", "items": items}, handle, ensure_ascii=False)


def _query(query: str, character: str | None = None):
    return query_producer_evidence(EVIDENCE_PATH, query, character=character)


def test_relevo_generacional_returns_both_characters() -> None:
    result = _query("relevo generacional")
    assert result.status == STATUS_RESULTS
    assert result.topic == "jóvenes/relevo generacional"
    assert {item.interview_subject for item in result.results} == {"Kiko Traza", "Pruden"}
    assert result.total == 3


def test_problemas_returns_both_characters() -> None:
    result = _query("problemas")
    assert result.status == STATUS_RESULTS
    assert result.topic == "problemas/dificultades"
    assert {item.interview_subject for item in result.results} == {"Kiko Traza", "Pruden"}
    assert result.total == 3


def test_character_kiko_filters_to_kiko_traza() -> None:
    result = _query("ovejas", character="Kiko")
    assert result.character == "Kiko Traza"
    assert {item.interview_subject for item in result.results} == {"Kiko Traza"}
    assert result.total == 1


def test_unknown_topic_is_controlled() -> None:
    result = _query("presupuesto")
    assert result.status == STATUS_UNSUPPORTED_TOPIC
    assert result.total == 0
    assert result.results == ()
    assert result.topic is None


def test_audio_only_never_invents_video_positions() -> None:
    result = _query("ovejas", character="Pruden")
    for item in result.results:
        if item.excerpt_video_mapping_status == AUDIO_ONLY_STATUS:
            assert item.video_clip is None
            assert item.excerpt_video_relative_start is None
            assert item.excerpt_video_relative_end is None
        else:
            assert item.excerpt_video_mapping_status == MAPPED_STATUS
            assert item.excerpt_video_relative_start is not None
    assert result.audio_only == 2
    assert result.mapped == 1


def test_mapped_preserves_exact_v2_navigation_values() -> None:
    result = _query("relevo generacional", character="Pruden")
    pruden_jov = [item for item in result.results if item.interview_subject == "Pruden"]
    assert len(pruden_jov) == 2
    navigable = [item for item in pruden_jov if item.excerpt_video_mapping_status == MAPPED_STATUS]
    assert navigable
    item = navigable[0]
    assert item.video_clip == "CLIP.MP4"
    assert item.excerpt_video_relative_start == 12.25
    assert item.excerpt_video_relative_end == 12.75


def test_cli_dispatches_editorial_query_and_renders_human_readable() -> None:
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = cid_cli.run_cli(
        [
            "editorial-query",
            "--evidence-path",
            EVIDENCE_PATH,
            "--query",
            "relevo generacional",
        ],
        stdout,
        stderr,
    )
    assert code == 0
    output = stdout.getvalue()
    assert "CID — Producer Editorial Evidence" in output
    assert "INTERVIEW: Kiko Traza" in output
    assert "INTERVIEW: Pruden" in output


def test_cli_json_unsupported_topic_returns_controlled_no_results() -> None:
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = cid_cli.run_cli(
        ["editorial-query", "--evidence-path", EVIDENCE_PATH, "--query", "presupuesto", "--json"],
        stdout,
        stderr,
    )
    assert code == 0
    payload = json.loads(stdout.getvalue())
    assert payload["status"] == STATUS_UNSUPPORTED_TOPIC
    assert payload["results"] == []
    assert payload["total"] == 0


def test_navigation_mapped_available_preserves_exact_v2_values() -> None:
    result = _query("relevo generacional", character="Pruden")
    mapped = [
        item
        for item in result.results
        if item.excerpt_video_mapping_status == MAPPED_STATUS
    ]
    assert mapped
    navigation = build_evidence_navigation(mapped[0])
    assert navigation["navigation_status"] == NAVIGATION_AVAILABLE
    assert navigation["navigation_available"] is True
    assert navigation["navigation_reason"] is None
    assert navigation["video_clip"] == "CLIP.MP4"
    assert navigation["video_relative_start"] == 12.25
    assert navigation["video_relative_end"] == 12.75


def test_navigation_audio_only_never_invents_video() -> None:
    result = _query("ovejas", character="Pruden")
    audio_only = [
        item
        for item in result.results
        if item.excerpt_video_mapping_status == AUDIO_ONLY_STATUS
    ]
    assert audio_only
    navigation = build_evidence_navigation(audio_only[0])
    assert navigation["navigation_status"] == NAVIGATION_UNAVAILABLE
    assert navigation["navigation_available"] is False
    assert navigation["navigation_reason"] == NAVIGATION_REASON_AUDIO_ONLY
    assert navigation["video_clip"] is None
    assert navigation["video_relative_start"] is None
    assert navigation["video_relative_end"] is None
    assert navigation["navigation_descriptor"] is None


def test_navigation_resolve_by_candidate_audio_only() -> None:
    result = _query("ovejas", character="Pruden")
    audio_only_items = [
        item
        for item in result.results
        if item.excerpt_video_mapping_status == AUDIO_ONLY_STATUS
    ]
    navigation = resolve_navigation_by_candidate_id(
        result, audio_only_items[0].candidate_id
    )
    assert navigation["navigation_available"] is False
    assert navigation["navigation_reason"] == NAVIGATION_REASON_AUDIO_ONLY


def test_navigation_candidate_not_found_controlled() -> None:
    result = _query("problemas")
    navigation = resolve_navigation_by_candidate_id(result, "DOES-NOT-EXIST")
    assert navigation["navigation_available"] is False
    assert navigation["navigation_reason"] == NAVIGATION_REASON_CANDIDATE_NOT_FOUND
    assert navigation["video_clip"] is None


def test_cli_navigate_mapped_returns_navigation_json() -> None:
    result = _query("relevo generacional", character="Pruden")
    mapped = [
        item
        for item in result.results
        if item.excerpt_video_mapping_status == MAPPED_STATUS
    ][0]
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = cid_cli.run_cli(
        [
            "editorial-query",
            "--evidence-path",
            EVIDENCE_PATH,
            "--query",
            "relevo generacional",
            "--character",
            "Pruden",
            "--navigate",
            mapped.candidate_id,
        ],
        stdout,
        stderr,
    )
    assert code == 0
    payload = json.loads(stdout.getvalue())
    assert payload["navigation_available"] is True
    assert payload["video_clip"] == "CLIP.MP4"
    assert payload["video_relative_start"] == 12.25
    assert payload["video_relative_end"] == 12.75


def test_cli_navigate_audio_only_returns_controlled_unavailable() -> None:
    result = _query("ovejas", character="Pruden")
    audio_only = [
        item
        for item in result.results
        if item.excerpt_video_mapping_status == AUDIO_ONLY_STATUS
    ][0]
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = cid_cli.run_cli(
        [
            "editorial-query",
            "--evidence-path",
            EVIDENCE_PATH,
            "--query",
            "ovejas",
            "--character",
            "Pruden",
            "--navigate",
            audio_only.candidate_id,
        ],
        stdout,
        stderr,
    )
    assert code == 0
    payload = json.loads(stdout.getvalue())
    assert payload["navigation_available"] is False
    assert payload["navigation_reason"] == NAVIGATION_REASON_AUDIO_ONLY
    assert payload["video_clip"] is None


def test_editor_handoff_mapped_preserves_exact_v2_source_interval() -> None:
    result = _query("relevo generacional", character="Pruden")
    mapped = [
        item
        for item in result.results
        if item.excerpt_video_mapping_status == MAPPED_STATUS
    ]
    assert mapped
    package = build_editor_handoff_package(mapped[0])
    assert package["format"] == EDITOR_HANDOFF_FORMAT
    assert package["editor_handoff_available"] is True
    assert package["video_clip"] == "CLIP.MP4"
    marker = package["markers"][0]
    assert marker["video_clip"] == "CLIP.MP4"
    assert marker["source_in_seconds"] == 12.25
    assert marker["source_out_seconds"] == 12.75
    assert marker["candidate_id"] == mapped[0].candidate_id
    assert marker["topic"] == mapped[0].topic
    assert marker["interview_subject"] == mapped[0].interview_subject
    assert marker["excerpt"] == mapped[0].producer_context_excerpt
    assert marker["speaker_attribution"] == "UNKNOWN"


def test_editor_handoff_marker_name_is_deterministic() -> None:
    result = _query("relevo generacional", character="Pruden")
    mapped = [
        item
        for item in result.results
        if item.excerpt_video_mapping_status == MAPPED_STATUS
    ][0]
    a = build_editor_handoff_package(mapped)["markers"][0]["marker_name"]
    b = build_editor_handoff_package(mapped)["markers"][0]["marker_name"]
    assert a == b
    assert a.startswith("CID | ")
    assert mapped.interview_subject in a
    assert mapped.candidate_id in a


def test_editor_handoff_audio_only_never_invents_video() -> None:
    result = _query("ovejas", character="Pruden")
    audio_only = [
        item
        for item in result.results
        if item.excerpt_video_mapping_status == AUDIO_ONLY_STATUS
    ]
    assert audio_only
    package = build_editor_handoff_package(audio_only[0])
    assert package["editor_handoff_available"] is False
    assert package["editor_handoff_reason"] == EDITOR_HANDOFF_REASON_AUDIO_ONLY
    assert package["video_clip"] is None
    assert package["markers"] == []


def test_editor_handoff_no_media_or_timeline_mutation_flags() -> None:
    result = _query("relevo generacional", character="Pruden")
    mapped = [
        item
        for item in result.results
        if item.excerpt_video_mapping_status == MAPPED_STATUS
    ][0]
    package = build_editor_handoff_package(mapped)
    assert package["source_media_mutation"] is False
    assert package["davinci_project_mutation"] is False


def test_editor_handoff_resolve_by_candidate_audio_only_controlled() -> None:
    result = _query("ovejas", character="Pruden")
    audio_only = [
        item
        for item in result.results
        if item.excerpt_video_mapping_status == AUDIO_ONLY_STATUS
    ][0]
    package = resolve_editor_handoff_by_candidate_id(
        result, audio_only.candidate_id
    )
    assert package["editor_handoff_available"] is False
    assert package["editor_handoff_reason"] == EDITOR_HANDOFF_REASON_AUDIO_ONLY
    assert package["video_clip"] is None
    assert package["markers"] == []


def test_editor_handoff_candidate_not_found_controlled() -> None:
    result = _query("problemas")
    package = resolve_editor_handoff_by_candidate_id(result, "DOES-NOT-EXIST")
    assert package["editor_handoff_available"] is False
    assert package["editor_handoff_reason"] == EDITOR_HANDOFF_REASON_CANDIDATE_NOT_FOUND
    assert package["video_clip"] is None
    assert package["markers"] == []


def test_cli_editor_handoff_mapped_writes_marker_package_to_file(
    tmp_path,
) -> None:
    result = _query("relevo generacional", character="Pruden")
    mapped = [
        item
        for item in result.results
        if item.excerpt_video_mapping_status == MAPPED_STATUS
    ][0]
    out_file = tmp_path / "handoff.json"
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = cid_cli.run_cli(
        [
            "editorial-query",
            "--evidence-path",
            EVIDENCE_PATH,
            "--query",
            "relevo generacional",
            "--character",
            "Pruden",
            "--navigate",
            mapped.candidate_id,
            "--editor-handoff",
            str(out_file),
        ],
        stdout,
        stderr,
    )
    assert code == 0
    assert out_file.exists()
    package = json.loads(out_file.read_text(encoding="utf-8"))
    assert package["format"] == EDITOR_HANDOFF_FORMAT
    assert package["editor_handoff_available"] is True
    assert package["video_clip"] == "CLIP.MP4"
    assert package["markers"][0]["candidate_id"] == mapped.candidate_id


def test_cli_editor_handoff_without_navigate_is_rejected() -> None:
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = cid_cli.run_cli(
        [
            "editorial-query",
            "--evidence-path",
            EVIDENCE_PATH,
            "--query",
            "problemas",
            "--editor-handoff",
            "/tmp/opencode/should_not_exist.json",
        ],
        stdout,
        stderr,
    )
    assert code == 2
    assert "ARGUMENTS_REJECTED" in stderr.getvalue()
