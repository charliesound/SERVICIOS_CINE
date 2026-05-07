from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

from config import get_llm_settings
from services.llm.base import BaseLLMProvider, LLMRequest, LLMStatus
from services.llm.json_utils import LLMJSONError, parse_model
from services.llm.ollama_provider import OllamaProvider
from services.llm.prompts import (
    build_pipeline_recommendation_system_prompt,
    build_pipeline_recommendation_user_prompt,
    build_script_analysis_system_prompt,
    build_script_analysis_user_prompt,
    build_storyboard_prompt_system_prompt,
    build_storyboard_prompt_user_prompt,
)


class LLMSceneDialogueBlock(BaseModel):
    character: str
    text: str = ""


class LLMSceneAnalysis(BaseModel):
    scene_number: int
    scene_id: str
    heading: str
    int_ext: str
    location: str
    time_of_day: str
    action_blocks: list[str] = Field(default_factory=list)
    dialogue_blocks: list[LLMSceneDialogueBlock] = Field(default_factory=list)
    characters_detected: list[str] = Field(default_factory=list)
    production_needs: list[str] = Field(default_factory=list)
    storyboard_suggestions: list[str] = Field(default_factory=list)


class LLMSequenceSuggestion(BaseModel):
    sequence_id: str
    sequence_number: int
    title: str
    summary: str
    included_scenes: list[int] = Field(default_factory=list)
    characters: list[str] = Field(default_factory=list)
    location: Optional[str] = None
    emotional_arc: Optional[str] = None
    estimated_duration: Optional[int] = None
    estimated_shots: int = 0


class ScriptAnalysisLLMOutput(BaseModel):
    tone: str = ""
    summary: str = ""
    production_needs: list[str] = Field(default_factory=list)
    storyboard_suggestions: list[str] = Field(default_factory=list)
    sequences: list[LLMSequenceSuggestion] = Field(default_factory=list)
    scenes: list[LLMSceneAnalysis] = Field(default_factory=list)


class StoryboardPromptShotLLMOutput(BaseModel):
    shot_number: int
    shot_type: str
    description: str
    prompt: str
    negative_prompt: str
    visual_style: str = ""
    lens: str = ""
    lighting: str = ""
    composition: str = ""
    continuity_notes: str = ""


class StoryboardPromptLLMOutput(BaseModel):
    shots: list[StoryboardPromptShotLLMOutput] = Field(default_factory=list)


class PipelineRecommendationLLMOutput(BaseModel):
    preset_key: str
    workflow_key: Optional[str] = None
    backend: Optional[str] = None
    suggested_params: dict[str, Any] = Field(default_factory=dict)
    missing_inputs: list[str] = Field(default_factory=list)
    reasoning: str = ""


class LLMService:
    def __init__(self) -> None:
        self._provider: BaseLLMProvider | None = None

    def _settings(self) -> dict[str, Any]:
        return get_llm_settings()

    def _provider_name(self) -> str:
        return str(self._settings().get("provider", "ollama")).strip().lower()

    def _fallback_enabled(self) -> bool:
        return bool(self._settings().get("enable_fallback", True))

    def _get_provider(self) -> BaseLLMProvider:
        if self._provider is None:
            provider_name = self._provider_name()
            if provider_name == "ollama":
                self._provider = OllamaProvider()
            else:
                raise RuntimeError(f"Unsupported LLM provider: {provider_name}")
        return self._provider

    async def get_status(self) -> LLMStatus:
        try:
            return await self._get_provider().get_status()
        except Exception as exc:
            settings = self._settings()
            return LLMStatus(
                provider=str(settings.get("provider", "ollama")),
                model=str(settings.get("ollama_model", "unknown")),
                base_url=str(settings.get("ollama_base_url", "")),
                available=False,
                error_message=str(exc),
            )

    async def analyze_script(self, script_text: str) -> ScriptAnalysisLLMOutput:
        request = LLMRequest(
            system_prompt=build_script_analysis_system_prompt(),
            user_prompt=build_script_analysis_user_prompt(script_text),
            temperature=float(self._settings().get("temperature", 0.2)),
            timeout_seconds=int(self._settings().get("timeout_seconds", 120)),
            json_mode=True,
        )
        response = await self._get_provider().chat(request)
        return parse_model(response.content, ScriptAnalysisLLMOutput)

    async def generate_storyboard_prompts(
        self,
        *,
        project_name: str,
        project_description: str | None,
        scene: dict[str, Any],
        style_preset: str,
        shots_per_scene: int,
    ) -> StoryboardPromptLLMOutput:
        request = LLMRequest(
            system_prompt=build_storyboard_prompt_system_prompt(),
            user_prompt=build_storyboard_prompt_user_prompt(
                project_name=project_name,
                project_description=project_description,
                scene=scene,
                style_preset=style_preset,
                shots_per_scene=shots_per_scene,
            ),
            temperature=float(self._settings().get("temperature", 0.2)),
            timeout_seconds=int(self._settings().get("timeout_seconds", 120)),
            json_mode=True,
        )
        response = await self._get_provider().chat(request)
        return parse_model(response.content, StoryboardPromptLLMOutput)

    async def recommend_pipeline_preset(
        self,
        *,
        intent: str,
        context: dict[str, Any],
        presets: list[dict[str, Any]],
    ) -> PipelineRecommendationLLMOutput:
        request = LLMRequest(
            system_prompt=build_pipeline_recommendation_system_prompt(),
            user_prompt=build_pipeline_recommendation_user_prompt(intent=intent, context=context, presets=presets),
            temperature=float(self._settings().get("temperature", 0.2)),
            timeout_seconds=int(self._settings().get("timeout_seconds", 120)),
            json_mode=True,
        )
        response = await self._get_provider().chat(request)
        return parse_model(response.content, PipelineRecommendationLLMOutput)

    def is_enabled_for(self, feature_key: str) -> bool:
        settings = self._settings()
        return str(settings.get(feature_key, settings.get("provider", "ollama"))).strip().lower() == "ollama"

    def should_fallback(self, exc: Exception) -> bool:
        del exc
        return self._fallback_enabled()


llm_service = LLMService()
