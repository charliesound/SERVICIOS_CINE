from __future__ import annotations

import io
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from scripts.local_media_agent.editorial_selection import (
    DAVINCI_GENERATED,
    DAVINCI_UNAVAILABLE,
    REASON_AUDIO_ONLY,
    ROLE_DIRECTOR,
    ROLE_EDITOR,
    ROLE_PRODUCER,
    STATUS_IN_EDIT,
    STATUS_READY_FOR_EDITOR,
    STATUS_REJECTED,
    STATUS_SELECTED,
    STATUS_USED,
    SelectionStore,
    apply_transition,
    create_selection,
)
from scripts.local_media_agent.editorial_selection_cli import run_cli
from scripts.local_media_agent.editorial_selection_davinci import (
    ERR_ALREADY_GENERATED,
    ERR_EVIDENCE_MISMATCH,
    ERR_NOT_READY,
    ERR_OUTPUT_EXISTS,
    ERR_UNAVAILABLE,
    prepare_davinci_reference_for_selection,
)

MEDIA_PATH = "F:/SIRUELA/Pruden/Entrevista/PRIVATE1/M4ROOT/CLIP/A7IV_SL31277.MP4"
FRAME_DURATION = "1/25s"
SOURCE_TC_START = "21:42:10:23"
SOURCE_DURATION = "3209.76"


def _write_evidence(tmp_path: Path, *, ctx_045=None, **overrides) -> str:
    base_045 = {
        "candidate_id": "SIRUELA-CTX-045",
        "interview_subject": "Pruden",
        "topic": "problemas/dificultades",
        "PRODUCER_CONTEXT_EXCERPT": "en las vacas si no son capaces de echar la cría",
        "EXCERPT_AUDIO_START": 902.17,
        "EXCERPT_AUDIO_END": 908.27,
        "EXCERPT_VIDEO_MAPPING_STATUS": "MAPPED",
        "video_clip": "A7IV_SL31277.MP4",
        "EXCERPT_VIDEO_RELATIVE_START": 554.125,
        "EXCERPT_VIDEO_RELATIVE_END": 560.225,
        "SPEAKER_ATTRIBUTION": "UNKNOWN",
        "EDITORIAL_NOTE": "Calving difficulty and a calf's high economic value.",
    }
    if ctx_045 is not None:
        base_045.update(ctx_045)
    base_022 = {
        "candidate_id": "SIRUELA-CTX-022",
        "interview_subject": "Pruden",
        "topic": "ovejas/ovino",
        "PRODUCER_CONTEXT_EXCERPT": "el rebaño por la mañana",
        "EXCERPT_AUDIO_START": 10.0,
        "EXCERPT_AUDIO_END": 12.0,
        "EXCERPT_VIDEO_MAPPING_STATUS": "AUDIO_ONLY_VIDEO_UNMAPPED",
        "video_clip": None,
        "EXCERPT_VIDEO_RELATIVE_START": None,
        "EXCERPT_VIDEO_RELATIVE_END": None,
        "SPEAKER_ATTRIBUTION": "UNKNOWN",
        "EDITORIAL_NOTE": "Audio-only recollection.",
    }
    items = [base_045, base_022]
    if overrides:
        items[0].update(overrides)
    evidence = {
        "REFERENCE_SET_TYPE": "producer",
        "PROJECT": "Siruela",
        "items": items,
    }
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / "evidence.json"
    path.write_text(
        __import__("json").dumps(evidence, ensure_ascii=False), encoding="utf-8"
    )
    return str(path)


@pytest.fixture()
def evidence(tmp_path: Path) -> str:
    return _write_evidence(tmp_path)


@pytest.fixture()
def store(tmp_path: Path) -> str:
    return str(tmp_path / "selections")




def _prepare_cli(argv_args: list[str]) -> dict:
    out = io.StringIO()
    err = io.StringIO()
    code = run_cli(argv_args, stdout=out, stderr=err)
    return {"code": code, "out": out.getvalue(), "err": err.getvalue()}


def _prepare_args(store, selection_id, evidence_path, output) -> list[str]:
    return [
        "prepare-davinci",
        "--store", store,
        "--selection", selection_id,
        "--evidence-path", evidence_path,
        "--media-path", MEDIA_PATH,
        "--frame-duration", FRAME_DURATION,
        "--source-timecode-start", SOURCE_TC_START,
        "--source-duration", SOURCE_DURATION,
        "--output", output,
    ]


def _build_ready(evidence_path, store, candidate="SIRUELA-CTX-045", role=ROLE_DIRECTOR):
    sel = create_selection(evidence_path, candidate, ROLE_PRODUCER, note="nota")
    ssel = SelectionStore(store)
    ssel.write(sel)
    ready = apply_transition(sel, STATUS_READY_FOR_EDITOR, role)
    ssel.write(ready)
    return ready


def test_ready_mapped_generates_fcpxml(tmp_path, evidence, store) -> None:
    ready = _build_ready(evidence, store)
    output = str(tmp_path / "ref.fcpxml")
    res = _prepare_cli(_prepare_args(store, ready["selection_id"], evidence, output))
    assert res["code"] == 0
    root = ET.fromstring(Path(output).read_text(encoding="utf-8"))
    assert root.tag == "fcpxml"
    assert root.get("version") == "1.10"


@pytest.mark.parametrize(
    "to_status_actor",
    [
        (STATUS_SELECTED, None),
        (STATUS_IN_EDIT, ROLE_EDITOR),
        (STATUS_USED, ROLE_EDITOR),
        (STATUS_REJECTED, ROLE_EDITOR),
    ],
)
def test_wrong_editorial_status_refused(
    tmp_path, evidence, store, to_status_actor
) -> None:
    to_status, actor = to_status_actor
    sel = create_selection(evidence, "SIRUELA-CTX-045", ROLE_PRODUCER)
    ssel = SelectionStore(store)
    ssel.write(sel)
    if to_status == STATUS_SELECTED:
        stored = sel
    elif to_status == STATUS_IN_EDIT:
        ready = apply_transition(sel, STATUS_READY_FOR_EDITOR, ROLE_DIRECTOR)
        stored = apply_transition(ready, STATUS_IN_EDIT, ROLE_EDITOR)
        ssel.write(stored)
    elif to_status == STATUS_USED:
        ready = apply_transition(sel, STATUS_READY_FOR_EDITOR, ROLE_DIRECTOR)
        in_edit = apply_transition(ready, STATUS_IN_EDIT, ROLE_EDITOR)
        stored = apply_transition(in_edit, STATUS_USED, ROLE_EDITOR)
        ssel.write(stored)
    else:  # REJECTED
        ready = apply_transition(sel, STATUS_READY_FOR_EDITOR, ROLE_DIRECTOR)
        stored = apply_transition(
            ready, STATUS_REJECTED, ROLE_EDITOR, editor_note="no coverage"
        )
        ssel.write(stored)
    output = str(tmp_path / "ref.fcpxml")
    res = _prepare_cli(_prepare_args(store, stored["selection_id"], evidence, output))
    assert res["code"] == 2
    assert ERR_NOT_READY in res["err"]
    assert not Path(output).exists()


def test_audio_only_refused_safely(tmp_path, evidence, store) -> None:
    sel = create_selection(evidence, "SIRUELA-CTX-022", ROLE_DIRECTOR)
    ssel = SelectionStore(store)
    ssel.write(sel)
    ready = apply_transition(sel, STATUS_READY_FOR_EDITOR, ROLE_DIRECTOR)
    ssel.write(ready)
    output = str(tmp_path / "ref.fcpxml")
    res = _prepare_cli(_prepare_args(store, ready["selection_id"], evidence, output))
    assert res["code"] == 2
    assert ERR_UNAVAILABLE in res["err"]
    assert REASON_AUDIO_ONLY in res["err"]
    assert not Path(output).exists()
    rec = SelectionStore(store).read(ready["selection_id"])
    assert rec["status"] == STATUS_READY_FOR_EDITOR
    assert rec["davinci_reference_status"] == DAVINCI_UNAVAILABLE


def test_existing_output_refused(tmp_path, evidence, store) -> None:
    ready = _build_ready(evidence, store)
    output = tmp_path / "ref.fcpxml"
    output.write_text("existing", encoding="utf-8")
    res = _prepare_cli(
        _prepare_args(store, ready["selection_id"], evidence, str(output))
    )
    assert res["code"] == 2
    assert ERR_OUTPUT_EXISTS in res["err"]


def test_already_generated_refused(tmp_path, evidence, store) -> None:
    ready = _build_ready(evidence, store)
    output = str(tmp_path / "ref.fcpxml")
    res1 = _prepare_cli(_prepare_args(store, ready["selection_id"], evidence, output))
    assert res1["code"] == 0
    res2 = _prepare_cli(
        _prepare_args(store, ready["selection_id"], evidence, str(tmp_path / "o.fcpxml"))
    )
    assert res2["code"] == 2
    assert ERR_ALREADY_GENERATED in res2["err"]


def test_success_sets_generated_and_records_output(tmp_path, evidence, store) -> None:
    ready = _build_ready(evidence, store)
    output = str(tmp_path / "ref.fcpxml")
    res = _prepare_cli(_prepare_args(store, ready["selection_id"], evidence, output))
    assert res["code"] == 0
    rec = SelectionStore(store).read(ready["selection_id"])
    assert rec["davinci_reference_status"] == DAVINCI_GENERATED
    assert rec["davinci_reference_path"] == output


def test_success_preserves_status_and_editorial_fields(tmp_path, evidence, store) -> None:
    ready = _build_ready(evidence, store)
    before = {k: ready[k] for k in ready}
    output = str(tmp_path / "ref.fcpxml")
    _prepare_cli(_prepare_args(store, ready["selection_id"], evidence, output))
    rec = SelectionStore(store).read(ready["selection_id"])
    assert rec["status"] == STATUS_READY_FOR_EDITOR
    for key in (
        "subject",
        "topic",
        "excerpt",
        "editorial_note",
        "video_clip",
        "source_in_seconds",
        "source_out_seconds",
        "requested_by_role",
    ):
        assert rec[key] == before[key], key


def test_deterministic_two_independent_stores(tmp_path) -> None:
    ev_a = _write_evidence(tmp_path / "a")
    ev_b = _write_evidence(tmp_path / "b")
    store_a = str(tmp_path / "store_a")
    store_b = str(tmp_path / "store_b")
    ready_a = _build_ready(ev_a, store_a)
    ready_b = _build_ready(ev_b, store_b)
    assert ready_a["candidate_id"] == ready_b["candidate_id"]
    out_a = str(tmp_path / "a.fcpxml")
    out_b = str(tmp_path / "b.fcpxml")
    ra = _prepare_cli(_prepare_args(store_a, ready_a["selection_id"], ev_a, out_a))
    rb = _prepare_cli(_prepare_args(store_b, ready_b["selection_id"], ev_b, out_b))
    assert ra["code"] == 0
    assert rb["code"] == 0
    assert Path(out_a).read_text(encoding="utf-8") == Path(out_b).read_text(encoding="utf-8")


def test_clip_mismatch_refused(tmp_path) -> None:
    ev_baseline = _write_evidence(tmp_path / "base")
    ev_mismatch = _write_evidence(tmp_path / "mm", video_clip="OTHER.MP4")
    store = str(tmp_path / "s1")
    ready = _build_ready(ev_baseline, store)
    output = str(tmp_path / "ref.fcpxml")
    res = _prepare_cli(_prepare_args(store, ready["selection_id"], ev_mismatch, output))
    assert res["code"] == 2
    assert ERR_EVIDENCE_MISMATCH in res["err"]
    assert not Path(output).exists()
    rec = SelectionStore(store).read(ready["selection_id"])
    assert rec["davinci_reference_status"] != DAVINCI_GENERATED


def test_source_in_mismatch_refused(tmp_path) -> None:
    ev_baseline = _write_evidence(tmp_path / "base")
    ev_mismatch = _write_evidence(
        tmp_path / "mm", EXCERPT_VIDEO_RELATIVE_START=554.5
    )
    store = str(tmp_path / "s2")
    ready = _build_ready(ev_baseline, store)
    output = str(tmp_path / "ref.fcpxml")
    res = _prepare_cli(_prepare_args(store, ready["selection_id"], ev_mismatch, output))
    assert res["code"] == 2
    assert ERR_EVIDENCE_MISMATCH in res["err"]
    assert not Path(output).exists()


def test_source_out_mismatch_refused(tmp_path) -> None:
    ev_baseline = _write_evidence(tmp_path / "base")
    ev_mismatch = _write_evidence(
        tmp_path / "mm", EXCERPT_VIDEO_RELATIVE_END=561.0
    )
    store = str(tmp_path / "s3")
    ready = _build_ready(ev_baseline, store)
    output = str(tmp_path / "ref.fcpxml")
    res = _prepare_cli(_prepare_args(store, ready["selection_id"], ev_mismatch, output))
    assert res["code"] == 2
    assert ERR_EVIDENCE_MISMATCH in res["err"]
    assert not Path(output).exists()


def test_candidate_mismatch_refused_via_monkeypatch(
    tmp_path, evidence, store, monkeypatch
) -> None:
    import scripts.local_media_agent.editorial_selection_davinci as emod

    ready = _build_ready(evidence, store)
    original = emod.build_editor_handoff_package

    def _mismatched(item):
        package = original(item)
        clipped = dict(package)
        markers = [dict(m) for m in package.get("markers") or []]
        return {**clipped, "candidate_id": "SIRUELA-CTX-099", "markers": markers}

    monkeypatch.setattr(emod, "build_editor_handoff_package", _mismatched)
    output = str(tmp_path / "ref.fcpxml")
    res = _prepare_cli(_prepare_args(store, ready["selection_id"], evidence, output))
    assert res["code"] == 2
    assert ERR_EVIDENCE_MISMATCH in res["err"]
    assert not Path(output).exists()
    rec = SelectionStore(store).read(ready["selection_id"])
    assert rec["davinci_reference_status"] != DAVINCI_GENERATED


def test_normal_cli_output_redacts_internals(tmp_path, evidence, store) -> None:
    ready = _build_ready(evidence, store)
    output = str(tmp_path / "ref.fcpxml")
    res = _prepare_cli(_prepare_args(store, ready["selection_id"], evidence, output))
    assert res["code"] == 0
    out = res["out"]
    assert "Source: 09:14.125 → 09:20.225" in out
    assert "Status: READY_FOR_EDITOR" in out
    assert "DAVINCI_REFERENCE_READY=True" in out
    assert "candidate_id" not in out
    assert "SIRUELA-CTX-045" not in out
    assert "C:" not in out
    assert "F:/SIRUELA" not in out
    assert "media-rep" not in out
    assert "1953273" not in out
    assert "15737009" not in out


def test_generation_failure_leaves_no_output(tmp_path, evidence, store, monkeypatch) -> None:
    import scripts.local_media_agent.editorial_selection_davinci as emod

    ready = _build_ready(evidence, store)

    def _boom(*a, **k):
        raise RuntimeError("generation failure")

    monkeypatch.setattr(emod, "build_davinci_reference", _boom)
    output = str(tmp_path / "ref.fcpxml")
    res = _prepare_cli(_prepare_args(store, ready["selection_id"], evidence, output))
    assert res["code"] == 1
    assert not Path(output).exists()
    tmp_output = Path(output).with_name(f"{Path(output).name}.tmp")
    assert not tmp_output.exists()
    rec = SelectionStore(store).read(ready["selection_id"])
    assert rec["davinci_reference_status"] != DAVINCI_GENERATED


def test_selection_write_failure_removes_output(
    tmp_path, evidence, store, monkeypatch
) -> None:
    ready = _build_ready(evidence, store)
    output = str(tmp_path / "ref.fcpxml")

    def _failing_write(self, selection):
        raise OSError("selection write failure")

    monkeypatch.setattr(SelectionStore, "write", _failing_write)

    res = _prepare_cli(
        _prepare_args(store, ready["selection_id"], evidence, output)
    )

    assert res["code"] == 1

    target = Path(output)
    tmp_output = target.with_name(f"{target.name}.tmp")

    assert not target.exists()
    assert not tmp_output.exists()

    persisted = SelectionStore(store).read(ready["selection_id"])

    assert persisted["status"] == "READY_FOR_EDITOR"
    assert persisted["davinci_reference_status"] == "NOT_REQUESTED"
    assert persisted["davinci_reference_path"] is None
    assert persisted["davinci_reference_reason"] is None


def test_success_fcpxml_exact_reference_values(tmp_path, evidence, store) -> None:
    ready = _build_ready(evidence, store)
    output = str(tmp_path / "ref.fcpxml")
    res = _prepare_cli(_prepare_args(store, ready["selection_id"], evidence, output))
    assert res["code"] == 0
    root = ET.fromstring(Path(output).read_text(encoding="utf-8"))
    asset = root.find(".//asset")
    assert asset is not None
    assert asset.get("start") == "1953273/25s"
    assert asset.get("duration") == "80244/25s"
    clip = root.find(".//asset-clip")
    assert clip.get("start") == "15737009/200s"
    assert clip.get("duration") == "61/10s"
    marker = root.find(".//asset-clip/marker")
    assert marker.get("start") == "15737009/200s"
    assert marker.get("duration") == "1/25s"
    media_rep = root.find(".//media-rep")
    assert media_rep.get("src") == "file:///F:/SIRUELA/Pruden/Entrevista/PRIVATE1/M4ROOT/CLIP/A7IV_SL31277.MP4"
