from src.services.cinematic_breakdown_service import CinematicBreakdownService
from src.services.screenplay_parser_service import ScreenplayParserService


def _parse(script: str):
    parser = ScreenplayParserService()
    return parser.parse_script(script)


def test_breakdown_extracts_characters_present_and_speaking_characters() -> None:
    service = CinematicBreakdownService()
    parsed_scenes = _parse(
        """
INT. COCINA - NOCHE

CARLOS
No deberiamos estar aqui.

Marta cierra la puerta.
"""
    )

    breakdowns = service.build_scene_breakdowns(parsed_scenes)

    assert len(breakdowns) == 1
    assert "Carlos" in breakdowns[0]["characters_present"]
    assert "Marta" in breakdowns[0]["characters_present"]
    assert breakdowns[0]["speaking_characters"] == ["Carlos"]


def test_breakdown_extracts_key_actions() -> None:
    service = CinematicBreakdownService()
    parsed_scenes = _parse(
        """
EXT. CALLE - DIA

Carlos corre hacia el coche. Marta abre la puerta y entra.
"""
    )

    breakdowns = service.build_scene_breakdowns(parsed_scenes)

    assert len(breakdowns[0]["key_actions"]) >= 1
    assert any("corre" in item.lower() or "abre" in item.lower() for item in breakdowns[0]["key_actions"])


def test_breakdown_detects_props_and_visual_elements() -> None:
    service = CinematicBreakdownService()
    parsed_scenes = _parse(
        """
INT. OFICINA - NOCHE

Una carpeta descansa sobre la mesa junto al telefono. La ventana deja entrar luz azul.
"""
    )

    breakdowns = service.build_scene_breakdowns(parsed_scenes)

    assert "carpeta" in breakdowns[0]["props_detected"]
    assert "telefono" in breakdowns[0]["props_detected"]
    assert "mesa" in breakdowns[0]["visual_elements"]
    assert "ventana" in breakdowns[0]["visual_elements"]


def test_breakdown_detects_moving_elements() -> None:
    service = CinematicBreakdownService()
    parsed_scenes = _parse(
        """
EXT. AUTOPISTA - NOCHE

El coche frena de golpe y gira hacia la salida.
"""
    )

    breakdowns = service.build_scene_breakdowns(parsed_scenes)

    assert any("frena" in item.lower() or "gira" in item.lower() for item in breakdowns[0]["moving_elements"])


def test_breakdown_detects_semi_moving_elements() -> None:
    service = CinematicBreakdownService()
    parsed_scenes = _parse(
        """
INT. SALON - NOCHE

La luz parpadea. El telefono suena sobre la mesa. La puerta se abre lentamente.
"""
    )

    breakdowns = service.build_scene_breakdowns(parsed_scenes)

    assert any("parpadea" in item.lower() or "suena" in item.lower() or "abre" in item.lower() for item in breakdowns[0]["semi_moving_elements"])


def test_breakdown_does_not_invent_too_much_in_sparse_scene() -> None:
    service = CinematicBreakdownService()
    parsed_scenes = _parse(
        """
INT. PASILLO - DIA

Silencio.
"""
    )

    breakdowns = service.build_scene_breakdowns(parsed_scenes)

    assert breakdowns[0]["props_detected"] == []
    assert breakdowns[0]["moving_elements"] == []
