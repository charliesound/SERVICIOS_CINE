from __future__ import annotations


STORYBOARD_WORKFLOW_PRESET_MAP: dict[str, str] = {
    "clean_4_panel_pitch": "storyboard_cinematic_pitch",
    "clean_6_panel_review": "storyboard_clean_review",
    "grid_8_panel_vertical": "storyboard_clean_review",
    "grid_8_panel_landscape": "storyboard_clean_review",
    "production_12_panel_vertical": "storyboard_technical",
    "production_12_panel_landscape": "storyboard_technical",
    "client_review_with_notes": "storyboard_client_notes",
    "technical_storyboard_sheet": "storyboard_technical",
}

ALLOWED_STORYBOARD_WORKFLOW_PROFILES: set[str] = {
    "storyboard_clean_review",
    "storyboard_client_notes",
    "storyboard_technical",
    "storyboard_cinematic_pitch",
    "storyboard_wan22_motion_ready",
    "storyboard_flux_fast",
    "storyboard_image_edit_consistency",
}

DEFAULT_STORYBOARD_WORKFLOW_PROFILE = "storyboard_safe"


class StoryboardWorkflowPresetService:
    def resolve_profile(self, sheet_template: str | None, requested_profile: str | None) -> dict[str, object]:
        normalized_template = sheet_template.strip() if isinstance(sheet_template, str) and sheet_template.strip() else None
        normalized_requested = requested_profile.strip() if isinstance(requested_profile, str) and requested_profile.strip() else None

        if normalized_requested:
            if normalized_requested in ALLOWED_STORYBOARD_WORKFLOW_PROFILES:
                return {
                    "workflow_profile_requested": normalized_requested,
                    "source": "explicit",
                    "sheet_template": normalized_template,
                    "requested_profile": normalized_requested,
                    "fallback_applied": False,
                    "reason": "explicit_profile_accepted",
                }
            return {
                "workflow_profile_requested": DEFAULT_STORYBOARD_WORKFLOW_PROFILE,
                "source": "explicit",
                "sheet_template": normalized_template,
                "requested_profile": normalized_requested,
                "fallback_applied": True,
                "reason": f"unknown_requested_profile:{normalized_requested}",
            }

        if normalized_template:
            mapped_profile = STORYBOARD_WORKFLOW_PRESET_MAP.get(normalized_template)
            if mapped_profile:
                return {
                    "workflow_profile_requested": mapped_profile,
                    "source": "sheet_template",
                    "sheet_template": normalized_template,
                    "requested_profile": None,
                    "fallback_applied": False,
                    "reason": "sheet_template_mapped",
                }
            return {
                "workflow_profile_requested": DEFAULT_STORYBOARD_WORKFLOW_PROFILE,
                "source": "default",
                "sheet_template": normalized_template,
                "requested_profile": None,
                "fallback_applied": True,
                "reason": f"unknown_sheet_template:{normalized_template}",
            }

        return {
            "workflow_profile_requested": DEFAULT_STORYBOARD_WORKFLOW_PROFILE,
            "source": "default",
            "sheet_template": None,
            "requested_profile": None,
            "fallback_applied": False,
            "reason": "default_storyboard_safe",
        }


storyboard_workflow_preset_service = StoryboardWorkflowPresetService()
