from core.i18n import get_no_context_answer, get_system_prompt, normalize_language


def test_normalize_language_spanish_variants():
    assert normalize_language("es") == "es"
    assert normalize_language("es-ES") == "es"
    assert normalize_language("castellano") == "es"
    assert normalize_language("spanish") == "es"


def test_normalize_language_english_variants():
    assert normalize_language("en") == "en"
    assert normalize_language("en-US") == "en"
    assert normalize_language("en_GB") == "en"
    assert normalize_language("english") == "en"


def test_normalize_language_fallback_to_spanish():
    assert normalize_language(None) == "es"
    assert normalize_language("") == "es"
    assert normalize_language("unknown") == "es"


def test_get_system_prompt_spanish():
    prompt = get_system_prompt("es")
    assert "español/castellano" in prompt.lower()


def test_get_system_prompt_english():
    prompt = get_system_prompt("en")
    assert "professional english" in prompt.lower()


def test_get_no_context_answer_spanish():
    answer = get_no_context_answer("es")
    assert "no tengo suficiente contexto" in answer.lower()


def test_get_no_context_answer_english():
    answer = get_no_context_answer("en")
    assert "not have enough project context" in answer.lower()
