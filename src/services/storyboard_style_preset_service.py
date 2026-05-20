from __future__ import annotations


DEFAULT_NEGATIVE = (
    "blurry, low quality, bad anatomy, deformed hands, extra fingers, duplicate, "
    "cropped, watermark, text, logo, oversaturated, cartoon, anime, plastic skin"
)


NON_REALISTIC_NEGATIVE = (
    "photograph, photorealistic, hyperreal, hyper realistic, ultra realistic, realistic face, realistic skin, "
    "natural skin texture, detailed skin, DSLR, RAW photo, cinematic still, cinematic photography, movie frame, "
    "final frame, final movie frame, concept art render, 3d render, octane render, unreal engine, glossy"
)


REALISTIC_CLIENT_REVIEW_POSITIVE = (
    "realistic storyboard frame for a client-facing commercial or film pitch, clean professional visual style, "
    "cinematic but readable composition, consistent characters, realistic lighting, clear body language, modern production design, "
    "polished presentation look, easy-to-understand action, storyboard frame suitable for review by director, producer and client"
)

REALISTIC_CLIENT_REVIEW_NEGATIVE = (
    "low quality, messy composition, deformed hands, inconsistent characters, distorted faces, unreadable action, "
    "cluttered background, chaotic framing, oversaturated colors, bad anatomy, broken perspective, random text, watermark, logo, UI elements"
)


class StoryboardStylePresetService:
    def __init__(self) -> None:
        self._presets = {
            "hand_drawn_storyboard": {
                "positive_style_prompt": "rough hand drawn storyboard, pencil line art, unfinished production sketch, loose construction lines, storyboard thumbnails, black and white, monochrome, no color, director blocking sketch, rough pencil sketch, expressive loose strokes, previsualization drawing",
                "negative_style_prompt": NON_REALISTIC_NEGATIVE,
                "normalized_style_preset": "hand_drawn_storyboard",
                "preset_key": "storyboard_sketch",
                "checkpoint": "",
                "legacy_realistic": False,
            },
            "rough_pencil_storyboard": {
                "positive_style_prompt": "rough pencil storyboard drawing, hand-sketched cinematic panel, monochrome graphite lines, production storyboard rough pass, gesture-driven linework",
                "negative_style_prompt": NON_REALISTIC_NEGATIVE,
                "normalized_style_preset": "rough_pencil_storyboard",
                "preset_key": "storyboard_sketch",
                "checkpoint": "",
                "legacy_realistic": False,
            },
            "ink_storyboard": {
                "positive_style_prompt": "ink storyboard line art, strong black contours, monochrome storyboard frame, cinematic blocking illustration, clean directional hatching",
                "negative_style_prompt": NON_REALISTIC_NEGATIVE,
                "normalized_style_preset": "ink_storyboard",
                "preset_key": "storyboard_sketch",
                "checkpoint": "",
                "legacy_realistic": False,
            },
            "charcoal_storyboard": {
                "positive_style_prompt": "charcoal storyboard concept frame, expressive dark tonal sketch, cinematic silhouette planning, monochrome textured strokes",
                "negative_style_prompt": NON_REALISTIC_NEGATIVE,
                "normalized_style_preset": "charcoal_storyboard",
                "preset_key": "storyboard_sketch",
                "checkpoint": "",
                "legacy_realistic": False,
            },
            "graphic_novel_storyboard": {
                "positive_style_prompt": "graphic novel storyboard panel, dramatic line art, stylized monochrome shading, cinematic framing and action readability",
                "negative_style_prompt": NON_REALISTIC_NEGATIVE,
                "normalized_style_preset": "graphic_novel_storyboard",
                "preset_key": "storyboard_sketch",
                "checkpoint": "",
                "legacy_realistic": False,
            },
            "cinematic_realistic": {
                "positive_style_prompt": "cinematic realistic storyboard frame",
                "negative_style_prompt": "",
                "normalized_style_preset": "cinematic_realistic",
                "preset_key": "storyboard_realistic",
                "checkpoint": "Realistic_Vision_V2.0.safetensors",
                "legacy_realistic": True,
            },
            "moody_noir": {
                "positive_style_prompt": "moody noir storyboard frame",
                "negative_style_prompt": "",
                "normalized_style_preset": "moody_noir",
                "preset_key": "storyboard_realistic",
                "checkpoint": "Realistic_Vision_V2.0.safetensors",
                "legacy_realistic": True,
            },
            "commercial_pitch": {
                "positive_style_prompt": "commercial pitch storyboard frame",
                "negative_style_prompt": "",
                "normalized_style_preset": "commercial_pitch",
                "preset_key": "storyboard_realistic",
                "checkpoint": "Realistic_Vision_V2.0.safetensors",
                "legacy_realistic": True,
            },
            "realistic_client_review": {
                "positive_style_prompt": REALISTIC_CLIENT_REVIEW_POSITIVE,
                "negative_style_prompt": REALISTIC_CLIENT_REVIEW_NEGATIVE,
                "normalized_style_preset": "realistic_client_review",
                "preset_key": "storyboard_realistic",
                "checkpoint": "Realistic_Vision_V2.0.safetensors",
                "legacy_realistic": True,
            },
        }
        self._aliases = {
            "graphic_novel": "graphic_novel_storyboard",
        }

    def get_storyboard_style_preset(self, name: str) -> dict[str, str | bool]:
        preset = (name or "hand_drawn_storyboard").strip().lower()
        normalized = self._aliases.get(preset, preset)
        if normalized not in self._presets:
            normalized = "hand_drawn_storyboard"
        return dict(self._presets[normalized])

    def enrich_prompt_with_storyboard_style(self, base_prompt: str, preset: str) -> str:
        payload = self.get_storyboard_style_preset(preset)
        style_block = str(payload["positive_style_prompt"]).strip()
        base = (base_prompt or "").strip()
        if not style_block:
            return base
        if style_block.lower() in base.lower():
            return base
        if not base:
            return style_block
        return f"{base}, {style_block}"

    def get_negative_prompt_for_storyboard_style(self, preset: str) -> str:
        payload = self.get_storyboard_style_preset(preset)
        return str(payload["negative_style_prompt"] or "").strip()


storyboard_style_preset_service = StoryboardStylePresetService()
