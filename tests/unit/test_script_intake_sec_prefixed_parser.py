from __future__ import annotations

import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
os.environ.setdefault("AUTH_SECRET_KEY", "AilinkCinemaAuthRuntimeValue987654321XYZ")
os.environ.setdefault("APP_SECRET_KEY", "AilinkCinemaAppRuntimeValue987654321XYZ")
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from services.script_document_classifier import is_probable_screenplay  # noqa: E402
from services.script_intake_service import AnalysisService, ScriptIntakeService  # noqa: E402


SEC_PREFIXED_SCRIPT = """Sec 1 INT. CASA ABANDONADA - NOCHE

MARTA entra con una linterna. La casa está en silencio. El suelo cruje bajo sus pies.

MARTA
¿Hay alguien ahí?

Una sombra cruza al fondo del pasillo. Marta se queda quieta.

Sec 3 EXT. BOSQUE - NOCHE

Marta sale corriendo de la casa. La linterna parpadea. Detrás de ella, una figura aparece en la puerta.
"""


class _ExecuteResult:
    def scalar_one_or_none(self):
        return None


class FakeAsyncSession:
    def __init__(self) -> None:
        self.added: list[object] = []
        self.commits = 0

    async def execute(self, *_args, **_kwargs):
        return _ExecuteResult()

    def add(self, instance: object) -> None:
        self.added.append(instance)

    async def commit(self) -> None:
        self.commits += 1


def test_sec_prefixed_headings_create_scenes_and_explicit_sequences() -> None:
    service = ScriptIntakeService()

    scenes = service.parse_script(SEC_PREFIXED_SCRIPT)

    assert len(scenes) == 2
    assert [scene["scene_number"] for scene in scenes] == [1, 3]
    assert scenes[0]["normalized_heading"] == "INT. CASA ABANDONADA - NOCHE"
    assert scenes[0]["heading"] == "INT. CASA ABANDONADA - NOCHE"
    assert scenes[0]["int_ext"] == "INT"
    assert scenes[0]["scene_type"] == "INT"
    assert scenes[0]["interior_exterior"] == "INT"
    assert scenes[0]["location"] == "CASA ABANDONADA"
    assert scenes[0]["location"] != "Sec 1 INT. CASA ABANDONADA"
    assert scenes[0]["time_of_day"] == "NOCHE"
    assert scenes[0]["source_sequence_number"] == 1
    assert scenes[0]["source_sequence_label"] == "Sec 1"
    assert scenes[1]["normalized_heading"] == "EXT. BOSQUE - NOCHE"
    assert scenes[1]["heading"] == "EXT. BOSQUE - NOCHE"
    assert scenes[1]["scene_type"] == "EXT"
    assert scenes[1]["location"] == "BOSQUE"
    assert scenes[1]["source_sequence_number"] == 3
    assert scenes[1]["source_sequence_label"] == "Sec 3"
    assert scenes[0]["characters_detected"] == ["MARTA"]
    assert scenes[0]["dialogue_blocks"][0]["character"] == "MARTA"
    assert "¿Hay alguien ahí?" in scenes[0]["dialogue_blocks"][0]["text"]

    sequences = service.build_sequence_blocks(scenes)

    assert [sequence["sequence_number"] for sequence in sequences] == [1, 3]
    assert sequences[0]["sequence_id"] == "seq_001"
    assert sequences[1]["sequence_id"] == "seq_003"

    breakdowns = service.build_scene_breakdowns(scenes)
    departments = service.build_department_breakdown(breakdowns, total_sequences=len(sequences))
    assert departments["summary"]["total_scenes"] == 2
    assert departments["summary"]["total_sequences"] == 2
    assert departments["summary"]["total_characters"] >= 1
    assert departments["summary"]["total_locations"] >= 2
    assert departments["summary"]["int_scenes"] == 1
    assert departments["summary"]["ext_scenes"] == 1
    assert departments["summary"]["night_scenes"] == 2


def test_sec_prefixed_screenplay_is_classified_as_probable_script() -> None:
    is_screenplay, confidence, signals = is_probable_screenplay(SEC_PREFIXED_SCRIPT)

    assert is_screenplay is True
    assert confidence >= 0.55
    assert signals.scene_heading_count >= 2
    assert signals.character_cue_count >= 1


async def _run_analysis(script_text: str) -> dict[str, object]:
    service = AnalysisService()

    async def _no_llm(_script_text: str):
        return None

    service._run_llm_analysis_or_none = _no_llm  # type: ignore[method-assign]
    db = FakeAsyncSession()
    return await service.run_analysis(
        db=db,
        project_id="proj-script-intake",
        organization_id="org-script-intake",
        script_text=script_text,
        document_context={"doc_type": "script", "confidence_score": 0.8, "source_kind": "script_text"},
        structured_payload={},
    )


def test_non_empty_script_without_headings_returns_degraded_warning() -> None:
    import asyncio

    result = asyncio.run(_run_analysis("Marta entra en silencio sin encabezados ni escenas formales."))

    assert result["status"] == "degraded"
    assert result["scenes_count"] == 0
    assert result["warnings"] == ["No se detectaron escenas. Revisa formato de encabezados o parser."]


def test_empty_script_returns_basic_empty_warning() -> None:
    import asyncio

    result = asyncio.run(_run_analysis("   \n\n  "))

    assert result["status"] == "basic_empty"
    assert result["scenes_count"] == 0
    assert result["warnings"] == ["Script vacio. No hay texto para analizar."]
