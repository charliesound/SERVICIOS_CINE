from src.services.screenplay_parser_service import ScreenplayParserService


def test_parse_single_scene_heading_and_action() -> None:
    service = ScreenplayParserService()

    script = """
INT. CASA DE CARLOS - NOCHE

Carlos entra lentamente en la cocina y enciende la luz.
"""

    scenes = service.parse_script(script)

    assert len(scenes) == 1
    assert scenes[0]["heading"] == "INT. CASA DE CARLOS - NOCHE"
    assert scenes[0]["location"] == "CASA DE CARLOS"
    assert scenes[0]["time_of_day"] == "NOCHE"
    assert scenes[0]["action_blocks"] == ["Carlos entra lentamente en la cocina y enciende la luz."]


def test_parse_multiple_int_ext_scenes() -> None:
    service = ScreenplayParserService()

    script = """
INT. CASA - DIA

Ana recoge una carpeta del suelo.

EXT. CALLE - NOCHE

Un coche frena frente a la acera.
"""

    scenes = service.parse_script(script)

    assert len(scenes) == 2
    assert scenes[0]["heading"] == "INT. CASA - DIA"
    assert scenes[1]["heading"] == "EXT. CALLE - NOCHE"


def test_parse_dialogue_with_character_cue() -> None:
    service = ScreenplayParserService()

    script = """
INT. OFICINA - DIA

MARTA
No podemos seguir así.
"""

    scenes = service.parse_script(script)

    assert len(scenes) == 1
    assert len(scenes[0]["dialogue_blocks"]) == 1
    assert scenes[0]["dialogue_blocks"][0]["character"] == "Marta"
    assert scenes[0]["dialogue_blocks"][0]["text"] == "No podemos seguir así."
    assert "Marta" in scenes[0]["characters_detected"]


def test_parse_multiline_dialogue_same_character() -> None:
    service = ScreenplayParserService()

    script = """
EXT. AZOTEA - NOCHE

LUCIA
No voy a caer.
Aunque tenga miedo,
voy a seguir avanzando.
"""

    scenes = service.parse_script(script)

    assert len(scenes) == 1
    assert len(scenes[0]["dialogue_blocks"]) == 1
    assert scenes[0]["dialogue_blocks"][0]["character"] == "Lucia"
    assert scenes[0]["dialogue_blocks"][0]["text"] == "No voy a caer. Aunque tenga miedo, voy a seguir avanzando."


def test_parse_without_scene_headings_returns_empty() -> None:
    service = ScreenplayParserService()

    script = "Carlos entra en la cocina. Marta lo mira. Discuten en silencio."

    scenes = service.parse_script(script)

    assert scenes == []
