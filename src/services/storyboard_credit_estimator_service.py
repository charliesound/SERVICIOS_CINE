from __future__ import annotations

from typing import Any


class StoryboardCreditEstimatorService:
    CREDIT_COSTS = {
        "script_analysis": 1,
        "prompt_generation_per_shot": 1,
        "image_render_per_shot": 1,
    }

    COVERAGE_SHOTS_PER_SCENE = 2

    def estimate_credits(
        self,
        *,
        mode: str,
        estimated_scenes: int,
        shots_per_scene: int,
        include_coverage_shots: bool = False,
        sequence_ids: list[str] | None = None,
        scene_start: int | None = None,
        scene_end: int | None = None,
    ) -> dict[str, Any]:
        base_shots = max(0, estimated_scenes) * max(1, shots_per_scene)

        coverage_shots = 0
        if include_coverage_shots and estimated_scenes > 0:
            coverage_shots = estimated_scenes * self.COVERAGE_SHOTS_PER_SCENE

        total_estimated_shots = base_shots + coverage_shots

        script_analysis_cost = self.CREDIT_COSTS["script_analysis"] if estimated_scenes > 0 else 0
        prompt_generation_cost = max(0, estimated_scenes) * self.CREDIT_COSTS["prompt_generation_per_shot"]
        image_render_cost = total_estimated_shots * self.CREDIT_COSTS["image_render_per_shot"]
        total_credits = script_analysis_cost + prompt_generation_cost + image_render_cost

        notes: list[str] = [
            "La estimación puede variar si la IA añade o elimina cobertura narrativa.",
        ]
        if include_coverage_shots:
            notes.append(
                "Los planos de cobertura se estiman como hasta 2 planos extra por escena según intensidad narrativa."
            )

        plan_warning = None
        if total_estimated_shots > 20:
            plan_warning = (
                f"Estimación alta ({total_estimated_shots} planos). "
                "Verifica que tu plan permita este volumen de renders."
            )

        return {
            "mode": mode,
            "estimated_scenes": estimated_scenes,
            "base_shots": base_shots,
            "coverage_shots": coverage_shots,
            "total_estimated_shots": total_estimated_shots,
            "credits": {
                "script_analysis": script_analysis_cost,
                "prompt_generation": prompt_generation_cost,
                "image_render": image_render_cost,
                "total": total_credits,
            },
            "plan_warning": plan_warning,
            "notes": notes,
        }


storyboard_credit_estimator_service = StoryboardCreditEstimatorService()
