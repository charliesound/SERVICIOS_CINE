from __future__ import annotations

from typing import Any


def build_script_analysis_system_prompt() -> str:
    return (
        "You are a senior script analyst for film and television. "
        "Return ONLY valid JSON. Extract structured screenplay information with production awareness. "
        "Preserve scene order and keep descriptions concise."
    )


def build_script_analysis_user_prompt(script_text: str) -> str:
    return f"""
Analyze this screenplay excerpt and return JSON with this shape:
{{
  "tone": "string",
  "summary": "string",
  "production_needs": ["string"],
  "storyboard_suggestions": ["string"],
  "sequences": [
    {{
      "sequence_id": "seq_01",
      "sequence_number": 1,
      "title": "string",
      "summary": "string",
      "included_scenes": [1,2],
      "characters": ["string"],
      "location": "string|null",
      "emotional_arc": "string|null",
      "estimated_duration": 120,
      "estimated_shots": 4
    }}
  ],
  "scenes": [
    {{
      "scene_number": 1,
      "scene_id": "scene_001",
      "heading": "INT. LOCATION - DAY",
      "int_ext": "INT|EXT|INT/EXT",
      "location": "string",
      "time_of_day": "string",
      "action_blocks": ["string"],
      "dialogue_blocks": [{{"character": "string", "text": "string"}}],
      "characters_detected": ["string"],
      "production_needs": ["string"],
      "storyboard_suggestions": ["string"]
    }}
  ]
}}

Rules:
- Keep every scene in order.
- Detect scene headings even if numbering is inconsistent.
- Characters_detected should contain unique character names per scene.
- production_needs should mention notable props, VFX, stunts, vehicles, crowd, animals, night exterior, special makeup, etc.
- storyboard_suggestions should suggest visually useful coverage ideas.
- Do not include markdown, commentary or extra prose.

Script:
{script_text}
""".strip()


def build_storyboard_prompt_system_prompt() -> str:
    return (
        "You are a cinematic storyboard prompt designer for generative image workflows. "
        "Return ONLY valid JSON. Write concise but visually rich prompts that are production ready for ComfyUI."
    )


def build_storyboard_prompt_user_prompt(
    *,
    project_name: str,
    project_description: str | None,
    scene: dict[str, Any],
    style_preset: str,
    shots_per_scene: int,
) -> str:
    return f"""
Create storyboard prompt JSON for one scene.
Return this shape:
{{
  "shots": [
    {{
      "shot_number": 1,
      "shot_type": "WS|MS|CU|ECU|OTS|TRACKING|POV",
      "description": "short cinematic description",
      "prompt": "full positive prompt",
      "negative_prompt": "negative prompt",
      "visual_style": "string",
      "lens": "string",
      "lighting": "string",
      "composition": "string",
      "continuity_notes": "string"
    }}
  ]
}}

Constraints:
- Generate exactly {shots_per_scene} shots.
- Use style preset: {style_preset}.
- Preserve character continuity and setting continuity.
- Prefer cinematic realism unless the scene demands otherwise.
- Keep prompts optimized for still-frame generation.
- No markdown.

Project name: {project_name}
Project description: {project_description or ''}
Scene JSON:
{scene}
""".strip()


def build_pipeline_recommendation_system_prompt() -> str:
    return (
        "You are an AI workflow architect for audiovisual pipelines. "
        "Choose the best preset/workflow from the provided catalog. Return ONLY valid JSON. "
        "Do not invent new workflow keys."
    )


def build_pipeline_recommendation_user_prompt(
    *,
    intent: str,
    context: dict[str, Any],
    presets: list[dict[str, Any]],
) -> str:
    return f"""
Recommend the best preset and workflow for this pipeline request.
Return JSON with this shape:
{{
  "preset_key": "string",
  "workflow_key": "string|null",
  "backend": "string|null",
  "suggested_params": {{"key": "value"}},
  "missing_inputs": ["string"],
  "reasoning": "string"
}}

Rules:
- Use only preset keys and workflow keys that exist in the provided presets.
- suggested_params should help the caller prefill the workflow.
- missing_inputs should contain required values not present in context.
- Keep reasoning short and actionable.

Intent: {intent}
Context: {context}
Available presets: {presets}
""".strip()
