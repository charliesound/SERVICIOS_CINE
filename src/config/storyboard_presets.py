# Storyboard Cinematic Preset Configuration
# Official preset for AILinkCinema storyboard generation
# Decision frozen: Realistic_Vision as primary, FLUX as premium

PRESETS = {
    "storyboard_realistic": {
        "name": "Storyboard Realistic (Primary)",
        "description": "Primary stable storyboard engine - cinematic film still using Realistic Vision",
        "checkpoint": "Realistic_Vision_V2.0.safetensors",
        "encoder_node": "CLIPTextEncode",
        "settings": {
            "width": 1024,
            "height": 576,
            "steps": 20,
            "cfg": 7.0,
            "sampler_name": "euler",
            "scheduler": "normal",
            "denoise": 1.0,
        },
        "workflow": [
            "CheckpointLoaderSimple",
            "CLIPTextEncode",
            "EmptyLatentImage",
            "KSampler",
            "VAEDecode",
            "SaveImage",
        ],
        "target_instance": "still",
        "role": "primary",
    },
    "storyboard_cinematic_premium": {
        "name": "Storyboard Cinematic Premium (FLUX)",
        "description": "Premium cinematic mode - FLUX1-schnell for higher visual quality",
        "checkpoint": "FLUX/flux1-schnell-fp8.safetensors",
        "encoder_node": "CLIPTextEncodeFlux",
        "settings": {
            "width": 1024,
            "height": 576,
            "steps": 16,
            "cfg": 1.0,
            "guidance": 3.5,
            "sampler_name": "euler",
            "scheduler": "normal",
            "denoise": 1.0,
        },
        "workflow": [
            "CheckpointLoaderSimple",
            "CLIPTextEncodeFlux",
            "EmptyLatentImage",
            "KSampler",
            "VAEDecode",
            "SaveImage",
        ],
        "target_instance": "still",
        "role": "premium",
    },
}

# Negative prompts for storyboard
NEGATIVE_PROMPTS = {
    "cinematic": "blurry, low quality, bad anatomy, deformed hands, extra fingers, duplicate, cropped, watermark, text, logo, oversaturated, cartoon, anime, plastic skin, stock photo, flat lighting",
    "sketch": "blurry, oversaturated, cartoon, anime style, flat color, fully rendered, photorealistic, digital art, 3d render",
    "flux": "blurry, low quality, bad anatomy, watermark, text, cartoon, anime",
}

# Prompt templates
PROMPT_TEMPLATES = {
    "establishing": "cinematic wide shot, {description}, establishing shot, film still",
    "medium": "cinematic medium shot, {description}, cinematic composition, film still",
    "closeup": "cinematic close-up, {description}, character-driven detail, film still",
    "movement": "cinematic medium shot, {description}, action moment, film still",
}

# Sequence/Shot metadata defaults
DEFAULT_METADATA = {
    "sequence_id": None,
    "shot_order": None,
    "shot_type": "unknown",
    "visual_mode": "realistic",
}
