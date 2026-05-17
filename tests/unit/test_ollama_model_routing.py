from config import get_llm_settings
from services.ollama_client_service import OllamaClientService


def test_script_analysis_uses_specific_model():
    settings = {"script_analysis_model": "qwen2.5:32b", "ollama_model": "qwen2.5:14b"}
    assert OllamaClientService.get_model_for_task("script_analysis", settings) == "qwen2.5:32b"


def test_script_analysis_falls_back_to_analysis_model():
    settings = {"analysis_model": "legacy-analysis", "ollama_model": "qwen2.5:14b"}
    assert OllamaClientService.get_model_for_task("script_analysis", settings) == "legacy-analysis"


def test_storyboard_prompt_uses_storyboard_model():
    settings = {"storyboard_prompt_model": "qwen2.5:14b", "ollama_model": "fallback"}
    assert OllamaClientService.get_model_for_task("storyboard_prompt", settings) == "qwen2.5:14b"


def test_quick_uses_quick_model():
    settings = {"quick_model": "qwen2.5:7b", "ollama_model": "fallback"}
    assert OllamaClientService.get_model_for_task("quick", settings) == "qwen2.5:7b"


def test_fallback_uses_fallback_model():
    settings = {"fallback_model": "mistral:7b", "ollama_model": "fallback"}
    assert OllamaClientService.get_model_for_task("fallback", settings) == "mistral:7b"


def test_unknown_task_falls_back_to_ollama_model():
    settings = {"ollama_model": "qwen2.5:14b"}
    assert OllamaClientService.get_model_for_task("unknown_task", settings) == "qwen2.5:14b"


def test_empty_settings_falls_back_to_safe_default(monkeypatch):
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    assert OllamaClientService.get_model_for_task("unknown_task", {}) == "qwen2.5:14b"


def test_env_var_used_when_setting_missing(monkeypatch):
    monkeypatch.setenv("OLLAMA_QUICK_MODEL", "env-quick-model")
    settings = {"ollama_model": "default-model"}
    assert OllamaClientService.get_model_for_task("quick", settings) == "env-quick-model"


def test_get_llm_settings_exposes_task_models(monkeypatch):
    monkeypatch.setenv("OLLAMA_SCRIPT_ANALYSIS_MODEL", "test-script")
    monkeypatch.setenv("OLLAMA_STORYBOARD_PROMPT_MODEL", "test-storyboard")
    monkeypatch.setenv("OLLAMA_QUICK_MODEL", "test-quick")
    monkeypatch.setenv("OLLAMA_FALLBACK_MODEL", "test-fallback")

    settings = get_llm_settings()

    assert settings["script_analysis_model"] == "test-script"
    assert settings["storyboard_prompt_model"] == "test-storyboard"
    assert settings["quick_model"] == "test-quick"
    assert settings["fallback_model"] == "test-fallback"
