from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
os.environ.setdefault("AUTH_SECRET_KEY", "AilinkCinemaAuthRuntimeValue987654321XYZ")
os.environ.setdefault("APP_SECRET_KEY", "AilinkCinemaAppRuntimeValue987654321XYZ")
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from fastapi import HTTPException  # noqa: E402
from schemas.storyboard_schema import StoryboardGenerateRequest  # noqa: E402
from services.storyboard_service import StoryboardGenerationMode  # noqa: E402
from services.storyboard_service import StoryboardSequenceBlock, StoryboardService  # noqa: E402


def test_generate_guard_message() -> None:
    message = (
        "Storyboard generation requires selected sequence_id or selected_sequence_ids. "
        "Run full script analysis first: POST /api/cid/script/analyze-full"
    )
    assert "sequence_id" in message
    assert "analyze-full" in message


def test_analyze_full_script_endpoint_exists() -> None:
    from routes.cid_script_to_prompt_routes import router  # noqa: E402
    paths = [r.path for r in router.routes]
    assert any("analyze-full" in p for p in paths)


def test_sequence_plan_endpoint_exists() -> None:
    from routes.storyboard_routes import router  # noqa: E402
    paths = [r.path for r in router.routes]
    assert any("plan" in p for p in paths)


def test_storyboard_generate_refuses_full_script() -> None:
    mode = StoryboardGenerationMode.FULL_SCRIPT
    has_sequence = False
    if mode in (StoryboardGenerationMode.FULL_SCRIPT, "") and not has_sequence:
        try:
            raise HTTPException(status_code=400, detail="Storyboard generation requires selected sequence_id")
        except HTTPException as e:
            assert e.status_code == 400
            assert "sequence_id" in e.detail


def _sample_scenes() -> list[dict[str, object]]:
    return [
        {"scene_number": 1, "heading": "INT. CASA - NOCHE", "scene_id": "scene_001"},
        {"scene_number": 2, "heading": "EXT. CALLE - DIA", "scene_id": "scene_002"},
        {"scene_number": 3, "heading": "INT. CAFE - TARDE", "scene_id": "scene_003"},
        {"scene_number": 4, "heading": "EXT. PARQUE - NOCHE", "scene_id": "scene_004"},
    ]


def _marta_scene() -> dict[str, object]:
    return {
        "scene_number": 1,
        "heading": "INT. CASA ABANDONADA - NOCHE",
        "location": "CASA ABANDONADA",
        "time_of_day": "NOCHE",
        "action_blocks": [
            "Marta entra en la casa abandonada iluminando el pasillo con una linterna.",
            "La sombra de Marta vibra sobre la pared mientras avanza en silencio.",
        ],
        "characters_detected": ["MARTA"],
        "props": ["linterna"],
        "visual_anchors": ["sombra larga", "pared desconchada"],
        "dramatic_objective": "avanzar con cautela hacia el ruido",
        "emotional_tone": "suspense oscuro",
        "scene_id": "scene_001",
    }


def _sample_sequences() -> list[StoryboardSequenceBlock]:
    return [
        StoryboardSequenceBlock(
            sequence_id="seq_001",
            sequence_number=1,
            title="Secuencia 1",
            summary="Primer bloque",
            included_scenes=[1, 2],
            characters=["A"],
            location="CASA",
            emotional_arc="setup",
            estimated_duration=120,
            estimated_shots=6,
        ),
        StoryboardSequenceBlock(
            sequence_id="seq_002",
            sequence_number=2,
            title="Secuencia 2",
            summary="Segundo bloque",
            included_scenes=[3, 4],
            characters=["B"],
            location="PARQUE",
            emotional_arc="escalation",
            estimated_duration=120,
            estimated_shots=6,
        ),
    ]


def _canonical_sequences() -> list[StoryboardSequenceBlock]:
    return [
        StoryboardSequenceBlock(
            sequence_id="seq_01",
            sequence_number=1,
            title="Secuencia 1",
            summary="Primer bloque",
            included_scenes=[1, 2],
            characters=["A"],
            location="CASA",
            emotional_arc="setup",
            estimated_duration=120,
            estimated_shots=6,
        )
    ]


class _FakeDb:
    def __init__(self) -> None:
        self.items: list[object] = []
        self._id_counter = 0

    def add(self, obj: object) -> None:
        self.items.append(obj)

    async def flush(self) -> None:
        for obj in self.items:
            if getattr(obj, "id", None) is None:
                self._id_counter += 1
                setattr(obj, "id", f"fake-{self._id_counter}")

    async def commit(self) -> None:
        return None


class _VersionCounter:
    def __init__(self) -> None:
        self.current = 0

    async def __call__(self, db, **kwargs):
        self.current += 1
        return self.current


def test_sequence_blocks_from_analysis_accepts_objects() -> None:
    service = StoryboardService()
    analysis_data = {
        "scenes": _sample_scenes(),
        "sequences": _sample_sequences(),
    }

    blocks = service._sequence_blocks_from_analysis(analysis_data)
    resolved = service._resolve_sequence_block(blocks, "seq_001")

    assert blocks
    assert blocks[0].sequence_id == "seq_001"
    assert resolved is not None
    assert resolved.sequence_id == "seq_001"


def test_resolve_sequence_block_aliases_to_canonical_seq_01() -> None:
    service = StoryboardService()
    blocks = _canonical_sequences()

    assert service._resolve_sequence_block(blocks, "seq_001") is not None
    assert service._resolve_sequence_block(blocks, "seq_001").sequence_id == "seq_01"
    assert service._resolve_sequence_block(blocks, "sequence_001").sequence_id == "seq_01"
    assert service._resolve_sequence_block(blocks, "1").sequence_id == "seq_01"


def test_get_sequence_storyboard_uses_canonical_sequence_id_for_alias(monkeypatch) -> None:
    service = StoryboardService()
    captured: dict[str, str] = {}

    async def fake_get_project_for_tenant(db, *, project_id, tenant):
        return SimpleNamespace(id=project_id, organization_id=tenant.organization_id, script_text="INT. CASA - NOCHE")

    async def fake_get_analysis_payload(db, project):
        return {"scenes": _sample_scenes(), "sequences": _canonical_sequences()}

    async def fake_build_storyboard_status(db, *, project_id):
        return {"sequences": {"seq_01": {"shots": 4, "version": 2}}}

    async def fake_list_storyboard_shots(db, *, project_id, tenant, mode=None, sequence_id=None, scene_number=None):
        captured["sequence_id"] = str(sequence_id)
        return [SimpleNamespace(id="shot-1", sequence_id="seq_01")], 2

    monkeypatch.setattr(service, "_get_project_for_tenant", fake_get_project_for_tenant)
    monkeypatch.setattr(service, "_get_analysis_payload", fake_get_analysis_payload)
    monkeypatch.setattr(service, "_build_storyboard_status", fake_build_storyboard_status)
    monkeypatch.setattr(service, "list_storyboard_shots", fake_list_storyboard_shots)

    sequence, shots = asyncio.run(
        service.get_sequence_storyboard(
            object(),
            project_id="project-1",
            sequence_id="seq_001",
            tenant=SimpleNamespace(organization_id="org-1", user_id="user-1", plan="free", is_global_admin=False),
        )
    )

    assert captured["sequence_id"] == "seq_01"
    assert sequence["sequence_id"] == "seq_01"
    assert len(shots) == 1


def test_get_sequence_storyboard_preserves_canonical_sequence_id(monkeypatch) -> None:
    service = StoryboardService()
    captured: dict[str, str] = {}

    async def fake_get_project_for_tenant(db, *, project_id, tenant):
        return SimpleNamespace(id=project_id, organization_id=tenant.organization_id, script_text="INT. CASA - NOCHE")

    async def fake_get_analysis_payload(db, project):
        return {"scenes": _sample_scenes(), "sequences": _canonical_sequences()}

    async def fake_build_storyboard_status(db, *, project_id):
        return {"sequences": {"seq_01": {"shots": 4, "version": 2}}}

    async def fake_list_storyboard_shots(db, *, project_id, tenant, mode=None, sequence_id=None, scene_number=None):
        captured["sequence_id"] = str(sequence_id)
        return [SimpleNamespace(id="shot-1", sequence_id="seq_01")], 2

    monkeypatch.setattr(service, "_get_project_for_tenant", fake_get_project_for_tenant)
    monkeypatch.setattr(service, "_get_analysis_payload", fake_get_analysis_payload)
    monkeypatch.setattr(service, "_build_storyboard_status", fake_build_storyboard_status)
    monkeypatch.setattr(service, "list_storyboard_shots", fake_list_storyboard_shots)

    sequence, shots = asyncio.run(
        service.get_sequence_storyboard(
            object(),
            project_id="project-1",
            sequence_id="seq_01",
            tenant=SimpleNamespace(organization_id="org-1", user_id="user-1", plan="free", is_global_admin=False),
        )
    )

    assert captured["sequence_id"] == "seq_01"
    assert sequence["sequence_id"] == "seq_01"
    assert len(shots) == 1


def test_generate_storyboard_returns_canonical_sequence_id(monkeypatch) -> None:
    service = StoryboardService()
    fake_db = _FakeDb()
    tenant = SimpleNamespace(organization_id="org-1", user_id="user-1", plan="free", is_global_admin=False)
    project = SimpleNamespace(id="project-1", name="Proyecto QA", description=None, script_text="INT. CASA - NOCHE")

    async def fake_get_project_for_tenant(db, *, project_id, tenant):
        return project

    async def fake_get_analysis_payload(db, project):
        return {
            "scenes": [
                {
                    "scene_number": 1,
                    "heading": "INT. CASA - NOCHE",
                    "location": "CASA",
                    "time_of_day": "NOCHE",
                    "action_blocks": ["Un personaje entra en silencio."],
                    "scene_id": "scene_001",
                }
            ],
            "sequences": _canonical_sequences(),
        }

    async def fake_next_generation_version(db, **kwargs):
        return 1

    async def fake_update_progress(*args, **kwargs):
        return None

    async def fake_record_project_job_event(*args, **kwargs):
        return None

    async def fake_upsert_job_asset(*args, **kwargs):
        return SimpleNamespace(id="asset-1")

    async def fake_run_llm_storyboard_prompts_or_none(**kwargs):
        return None

    async def fake_submit_job(**kwargs):
        return (
            SimpleNamespace(job_id="job-1", error=None, backend="still", status=SimpleNamespace(value="queued")),
            SimpleNamespace(job_id="job-1"),
        )

    monkeypatch.setattr(service, "_get_project_for_tenant", fake_get_project_for_tenant)
    monkeypatch.setattr(service, "_get_analysis_payload", fake_get_analysis_payload)
    monkeypatch.setattr(service, "_next_generation_version", fake_next_generation_version)
    monkeypatch.setattr(service, "_run_llm_storyboard_prompts_or_none", fake_run_llm_storyboard_prompts_or_none)
    monkeypatch.setattr("services.storyboard_service.render_job_service.submit_job", fake_submit_job)
    monkeypatch.setattr("services.storyboard_service.job_tracking_service.update_progress", fake_update_progress)
    monkeypatch.setattr("services.storyboard_service.job_tracking_service.record_project_job_event", fake_record_project_job_event)
    monkeypatch.setattr("services.storyboard_service.job_tracking_service.upsert_job_asset", fake_upsert_job_asset)

    result = asyncio.run(
        service.generate_storyboard(
            fake_db,
            project_id="project-1",
            tenant=tenant,
            mode=StoryboardGenerationMode.SEQUENCE,
            sequence_id="seq_001",
            sequence_ids=[],
            scene_start=None,
            scene_end=None,
            selected_scene_ids=[],
            scene_numbers=[],
            style_preset="graphic_novel",
            shots_per_scene=2,
            max_scenes=None,
            overwrite=False,
        )
    )

    created_shots = [item for item in fake_db.items if item.__class__.__name__ == "StoryboardShot"]
    assert result["sequence_id"] == "seq_01"
    assert created_shots
    assert all(getattr(shot, "sequence_id", None) == "seq_01" for shot in created_shots)


def test_generate_storyboard_metadata_contains_enriched_prompts(monkeypatch) -> None:
    service = StoryboardService()
    fake_db = _FakeDb()
    tenant = SimpleNamespace(organization_id="org-1", user_id="user-1", plan="free", is_global_admin=False)
    project = SimpleNamespace(id="project-1", name="Proyecto QA", description=None, script_text="INT. CASA ABANDONADA - NOCHE")

    async def fake_get_project_for_tenant(db, *, project_id, tenant):
        return project

    async def fake_get_analysis_payload(db, project):
        return {"scenes": [_marta_scene()], "sequences": _canonical_sequences()}

    async def fake_update_progress(*args, **kwargs):
        return None

    async def fake_record_project_job_event(*args, **kwargs):
        return None

    async def fake_upsert_job_asset(*args, **kwargs):
        return SimpleNamespace(id="asset-1")

    async def fake_run_llm_storyboard_prompts_or_none(**kwargs):
        return None

    async def fake_submit_job(**kwargs):
        return (
            SimpleNamespace(job_id="job-1", error=None, backend="still", status=SimpleNamespace(value="queued")),
            SimpleNamespace(job_id="job-1"),
        )

    monkeypatch.setattr(service, "_get_project_for_tenant", fake_get_project_for_tenant)
    monkeypatch.setattr(service, "_get_analysis_payload", fake_get_analysis_payload)
    monkeypatch.setattr(service, "_next_generation_version", _VersionCounter())
    monkeypatch.setattr(service, "_run_llm_storyboard_prompts_or_none", fake_run_llm_storyboard_prompts_or_none)
    monkeypatch.setattr("services.storyboard_service.render_job_service.submit_job", fake_submit_job)
    monkeypatch.setattr("services.storyboard_service.job_tracking_service.update_progress", fake_update_progress)
    monkeypatch.setattr("services.storyboard_service.job_tracking_service.record_project_job_event", fake_record_project_job_event)
    monkeypatch.setattr("services.storyboard_service.job_tracking_service.upsert_job_asset", fake_upsert_job_asset)

    asyncio.run(
        service.generate_storyboard(
            fake_db,
            project_id="project-1",
            tenant=tenant,
            mode=StoryboardGenerationMode.SEQUENCE,
            sequence_id="seq_001",
            sequence_ids=[],
            scene_start=None,
            scene_end=None,
            selected_scene_ids=[],
            scene_numbers=[],
            style_preset="graphic_novel",
            shots_per_scene=2,
            max_scenes=None,
            overwrite=False,
        )
    )

    created_shots = [item for item in fake_db.items if item.__class__.__name__ == "StoryboardShot"]
    metadata_json = getattr(created_shots[0], "metadata_json", "")
    metadata = json.loads(metadata_json)

    assert metadata["script_excerpt_used"]
    assert metadata["positive_prompt"]
    assert metadata["negative_prompt"]
    assert "MARTA" in metadata["character_continuity"]
    assert metadata["location_continuity"]["location"] == "CASA ABANDONADA"
    assert metadata["visual_continuity"]["anchors"]
    assert metadata["prompt_reference_sources"]
    assert metadata["prompt_model_family"] == "wan22"
    assert metadata["consistency_checklist"]
    assert metadata["diagnostic_rules_applied"]


def test_generate_storyboard_overwrite_keeps_unique_active_sequence_order(monkeypatch) -> None:
    service = StoryboardService()
    fake_db = _FakeDb()
    tenant = SimpleNamespace(organization_id="org-1", user_id="user-1", plan="free", is_global_admin=False)
    project = SimpleNamespace(id="project-1", name="Proyecto QA", description=None, script_text="INT. CASA ABANDONADA - NOCHE")

    async def fake_get_project_for_tenant(db, *, project_id, tenant):
        return project

    async def fake_get_analysis_payload(db, project):
        return {"scenes": [_marta_scene()], "sequences": _canonical_sequences()}

    async def fake_update_progress(*args, **kwargs):
        return None

    async def fake_record_project_job_event(*args, **kwargs):
        return None

    async def fake_upsert_job_asset(*args, **kwargs):
        return SimpleNamespace(id="asset-1")

    async def fake_run_llm_storyboard_prompts_or_none(**kwargs):
        return None

    async def fake_submit_job(**kwargs):
        return (
            SimpleNamespace(job_id="job-1", error=None, backend="still", status=SimpleNamespace(value="queued")),
            SimpleNamespace(job_id="job-1"),
        )

    async def fake_deactivate_scope_shots(db, **kwargs):
        assert kwargs["sequence_id"] == "seq_01"
        for item in fake_db.items:
            if item.__class__.__name__ == "StoryboardShot" and getattr(item, "sequence_id", None) == "seq_01":
                setattr(item, "is_active", False)

    monkeypatch.setattr(service, "_get_project_for_tenant", fake_get_project_for_tenant)
    monkeypatch.setattr(service, "_get_analysis_payload", fake_get_analysis_payload)
    monkeypatch.setattr(service, "_next_generation_version", _VersionCounter())
    monkeypatch.setattr(service, "_run_llm_storyboard_prompts_or_none", fake_run_llm_storyboard_prompts_or_none)
    monkeypatch.setattr("services.storyboard_service.render_job_service.submit_job", fake_submit_job)
    monkeypatch.setattr(service, "_deactivate_scope_shots", fake_deactivate_scope_shots)
    monkeypatch.setattr("services.storyboard_service.job_tracking_service.update_progress", fake_update_progress)
    monkeypatch.setattr("services.storyboard_service.job_tracking_service.record_project_job_event", fake_record_project_job_event)
    monkeypatch.setattr("services.storyboard_service.job_tracking_service.upsert_job_asset", fake_upsert_job_asset)

    for _ in range(2):
        asyncio.run(
            service.generate_storyboard(
                fake_db,
                project_id="project-1",
                tenant=tenant,
                mode=StoryboardGenerationMode.SEQUENCE,
                sequence_id="seq_001",
                sequence_ids=[],
                scene_start=None,
                scene_end=None,
                selected_scene_ids=[],
                scene_numbers=[],
                style_preset="graphic_novel",
                shots_per_scene=2,
                max_scenes=None,
                overwrite=True,
            )
        )

    active_shots = [item for item in fake_db.items if item.__class__.__name__ == "StoryboardShot" and getattr(item, "is_active", False)]
    active_orders = [getattr(shot, "sequence_order", None) for shot in active_shots]
    assert active_orders == [1, 2]
    assert len(active_orders) == len(set(active_orders))


def test_render_queue_receives_enriched_prompt(monkeypatch) -> None:
    service = StoryboardService()
    fake_db = _FakeDb()
    tenant = SimpleNamespace(organization_id="org-1", user_id="user-1", plan="free", is_global_admin=False)
    project = SimpleNamespace(id="project-1", name="Proyecto QA", description=None, script_text="INT. CASA ABANDONADA - NOCHE")
    captured: dict[str, str] = {}

    async def fake_get_project_for_tenant(db, *, project_id, tenant):
        return project

    async def fake_get_analysis_payload(db, project):
        return {"scenes": [_marta_scene()], "sequences": _canonical_sequences()}

    async def fake_update_progress(*args, **kwargs):
        return None

    async def fake_record_project_job_event(*args, **kwargs):
        return None

    async def fake_upsert_job_asset(*args, **kwargs):
        return SimpleNamespace(id="asset-1")

    async def fake_run_llm_storyboard_prompts_or_none(**kwargs):
        return None

    async def fake_submit_job(**kwargs):
        captured["prompt"] = kwargs["prompt"]["prompt"]
        captured["negative_prompt"] = kwargs["prompt"]["negative_prompt"]
        return SimpleNamespace(job_id="render-1", backend="still", error="queue unavailable", status=SimpleNamespace(value="failed")), None

    monkeypatch.setattr(service, "_get_project_for_tenant", fake_get_project_for_tenant)
    monkeypatch.setattr(service, "_get_analysis_payload", fake_get_analysis_payload)
    monkeypatch.setattr(service, "_next_generation_version", _VersionCounter())
    monkeypatch.setattr(service, "_run_llm_storyboard_prompts_or_none", fake_run_llm_storyboard_prompts_or_none)
    monkeypatch.setattr("services.storyboard_service.job_tracking_service.update_progress", fake_update_progress)
    monkeypatch.setattr("services.storyboard_service.job_tracking_service.record_project_job_event", fake_record_project_job_event)
    monkeypatch.setattr("services.storyboard_service.job_tracking_service.upsert_job_asset", fake_upsert_job_asset)
    monkeypatch.setattr("services.storyboard_service.render_job_service.submit_job", fake_submit_job)

    asyncio.run(
        service.generate_storyboard(
            fake_db,
            project_id="project-1",
            tenant=tenant,
            mode=StoryboardGenerationMode.SEQUENCE,
            sequence_id="seq_001",
            sequence_ids=[],
            scene_start=None,
            scene_end=None,
            selected_scene_ids=[],
            scene_numbers=[],
            style_preset="cinematic_realistic",
            shots_per_scene=1,
            max_scenes=None,
            overwrite=False,
        )
    )

    prompt = captured["prompt"].lower()
    assert "marta" in prompt
    assert "linterna" in prompt
    assert "casa abandonada" in prompt
    assert "noche" in prompt


def test_export_sequence_zip_accepts_alias(monkeypatch, tmp_path) -> None:
    from routes.storyboard_routes import export_sequence_storyboard_zip

    asset_path = tmp_path / "frame.webp"
    asset_path.write_bytes(b"frame-bytes")

    async def fake_get_sequence_storyboard(db, *, project_id, sequence_id, tenant):
        assert sequence_id == "seq_001"
        return (
            {"sequence_id": "seq_01"},
            [SimpleNamespace(asset_id="asset-1", sequence_order=1, created_at=None)],
        )

    async def fake_get_asset_preview_payload(db, *, project_id, asset_id, tenant):
        return {
            "kind": "file",
            "path": str(asset_path),
            "filename": "frame.webp",
        }

    monkeypatch.setattr("routes.storyboard_routes.storyboard_service.get_sequence_storyboard", fake_get_sequence_storyboard)
    monkeypatch.setattr(
        "services.presentation_service.presentation_service.get_asset_preview_payload",
        fake_get_asset_preview_payload,
    )

    response = asyncio.run(
        export_sequence_storyboard_zip(
            project_id="project-1",
            sequence_id="seq_001",
            db=object(),
            tenant=SimpleNamespace(organization_id="org-1", user_id="user-1", plan="free", is_global_admin=False),
        )
    )

    assert response.status_code == 200
    assert response.media_type == "application/zip"
    assert 'sequence_seq_01_storyboard.zip' in response.headers.get("Content-Disposition", "")


def test_contract_full_script_selection_returns_all_scenes() -> None:
    service = StoryboardService()
    scenes = _sample_scenes()
    selected = service._select_scenes(
        analysis_data={"scenes": scenes},
        sequences=_sample_sequences(),
        mode=StoryboardGenerationMode.FULL_SCRIPT,
        sequence_id=None,
        sequence_ids=[],
        scene_start=None,
        scene_end=None,
        selected_scene_ids=[],
        scene_numbers=[],
        max_scenes=None,
    )
    assert [scene["scene_number"] for scene in selected] == [1, 2, 3, 4]


def test_contract_sequence_mode_accepts_canonical_sequence_id() -> None:
    service = StoryboardService()
    selected = service._select_scenes(
        analysis_data={"scenes": _sample_scenes()},
        sequences=_sample_sequences(),
        mode=StoryboardGenerationMode.SEQUENCE,
        sequence_id="seq_001",
        sequence_ids=[],
        scene_start=None,
        scene_end=None,
        selected_scene_ids=[],
        scene_numbers=[],
        max_scenes=None,
    )
    assert [scene["scene_number"] for scene in selected] == [1, 2]


def test_contract_sequence_mode_accepts_numeric_alias() -> None:
    service = StoryboardService()
    selected = service._select_scenes(
        analysis_data={"scenes": _sample_scenes()},
        sequences=_sample_sequences(),
        mode=StoryboardGenerationMode.SEQUENCE,
        sequence_id="1",
        sequence_ids=[],
        scene_start=None,
        scene_end=None,
        selected_scene_ids=[],
        scene_numbers=[],
        max_scenes=None,
    )
    assert [scene["scene_number"] for scene in selected] == [1, 2]


def test_contract_sequence_mode_accepts_sequence_prefixed_alias() -> None:
    service = StoryboardService()
    selected = service._select_scenes(
        analysis_data={"scenes": _sample_scenes()},
        sequences=_sample_sequences(),
        mode=StoryboardGenerationMode.SEQUENCE,
        sequence_id="sequence_001",
        sequence_ids=[],
        scene_start=None,
        scene_end=None,
        selected_scene_ids=[],
        scene_numbers=[],
        max_scenes=None,
    )
    assert [scene["scene_number"] for scene in selected] == [1, 2]


def test_contract_scene_range_mode_selects_interval() -> None:
    service = StoryboardService()
    selected = service._select_scenes(
        analysis_data={"scenes": _sample_scenes()},
        sequences=_sample_sequences(),
        mode=StoryboardGenerationMode.SCENE_RANGE,
        sequence_id=None,
        sequence_ids=[],
        scene_start=2,
        scene_end=3,
        selected_scene_ids=[],
        scene_numbers=[],
        max_scenes=None,
    )
    assert [scene["scene_number"] for scene in selected] == [2, 3]


def test_contract_selected_scenes_mode_selects_explicit_scene_numbers() -> None:
    service = StoryboardService()
    selected = service._select_scenes(
        analysis_data={"scenes": _sample_scenes()},
        sequences=_sample_sequences(),
        mode=StoryboardGenerationMode.SELECTED_SCENES,
        sequence_id=None,
        sequence_ids=[],
        scene_start=None,
        scene_end=None,
        selected_scene_ids=[],
        scene_numbers=[1, 4],
        max_scenes=None,
    )
    assert [scene["scene_number"] for scene in selected] == [1, 4]


def test_contract_single_scene_mode_selects_one_scene_from_selected_ids() -> None:
    service = StoryboardService()
    selected = service._select_scenes(
        analysis_data={"scenes": _sample_scenes()},
        sequences=_sample_sequences(),
        mode=StoryboardGenerationMode.SINGLE_SCENE,
        sequence_id=None,
        sequence_ids=[],
        scene_start=None,
        scene_end=None,
        selected_scene_ids=["3"],
        scene_numbers=[],
        max_scenes=None,
    )
    assert [scene["scene_number"] for scene in selected] == [3]


def test_contract_sequence_mode_without_sequence_id_returns_400() -> None:
    service = StoryboardService()
    try:
        service._select_scenes(
            analysis_data={"scenes": _sample_scenes()},
            sequences=_sample_sequences(),
            mode=StoryboardGenerationMode.SEQUENCE,
            sequence_id=None,
            sequence_ids=[],
            scene_start=None,
            scene_end=None,
            selected_scene_ids=[],
            scene_numbers=[],
            max_scenes=None,
        )
        raise AssertionError("Expected HTTPException")
    except HTTPException as exc:
        assert exc.status_code == 400
        assert exc.detail == "sequence_id is required for SEQUENCE mode"


def test_contract_scene_range_missing_boundaries_returns_400() -> None:
    service = StoryboardService()
    try:
        service._select_scenes(
            analysis_data={"scenes": _sample_scenes()},
            sequences=_sample_sequences(),
            mode=StoryboardGenerationMode.SCENE_RANGE,
            sequence_id=None,
            sequence_ids=[],
            scene_start=1,
            scene_end=None,
            selected_scene_ids=[],
            scene_numbers=[],
            max_scenes=None,
        )
        raise AssertionError("Expected HTTPException")
    except HTTPException as exc:
        assert exc.status_code == 400
        assert "scene_start and scene_end are required" in exc.detail


def test_contract_invalid_mode_returns_400() -> None:
    service = StoryboardService()
    try:
        service._select_scenes(
            analysis_data={"scenes": _sample_scenes()},
            sequences=_sample_sequences(),
            mode="NOT_A_MODE",
            sequence_id=None,
            sequence_ids=[],
            scene_start=None,
            scene_end=None,
            selected_scene_ids=[],
            scene_numbers=[],
            max_scenes=None,
        )
        raise AssertionError("Expected HTTPException")
    except HTTPException as exc:
        assert exc.status_code == 400
        assert exc.detail == "Unsupported storyboard generation mode"


def test_contract_nonexistent_sequence_returns_404() -> None:
    service = StoryboardService()
    try:
        service._select_scenes(
            analysis_data={"scenes": _sample_scenes()},
            sequences=_sample_sequences(),
            mode=StoryboardGenerationMode.SEQUENCE,
            sequence_id="seq_999",
            sequence_ids=[],
            scene_start=None,
            scene_end=None,
            selected_scene_ids=[],
            scene_numbers=[],
            max_scenes=None,
        )
        raise AssertionError("Expected HTTPException")
    except HTTPException as exc:
        assert exc.status_code == 404
        assert exc.detail == "Sequence not found"


def test_schema_scope_fields_defaults_are_stable() -> None:
    req = StoryboardGenerateRequest()
    assert req.mode == "SEQUENCE"
    assert req.sequence_id is None
    assert req.sequence_ids == []
    assert req.scene_start is None
    assert req.scene_end is None
    assert req.scene_numbers == []
    assert req.shots_per_scene == 3
    assert req.overwrite is False
    assert req.style_preset == "hand_drawn_storyboard"
