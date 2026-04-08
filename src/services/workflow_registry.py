from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class TaskCategory(Enum):
    STILL = "still"
    VIDEO = "video"
    DUBBING = "dubbing"
    LAB = "lab"


@dataclass
class WorkflowNode:
    node_id: str
    class_type: str
    inputs: Dict[str, Any]
    required_inputs: List[str]
    optional_inputs: List[str]


@dataclass
class WorkflowTemplate:
    key: str
    name: str
    category: TaskCategory
    backend: str
    description: str
    required_inputs: List[str]
    optional_inputs: List[str]
    nodes: List[WorkflowNode]
    output_node_id: str
    tags: List[str]


class WorkflowRegistry:
    _instance = None
    _workflows: Dict[str, WorkflowTemplate] = {}
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if WorkflowRegistry._initialized:
            return
        WorkflowRegistry._initialized = True
        self._load_presets()

    def _load_presets(self):
        self._workflows = {
            "still_text_to_image_pro": WorkflowTemplate(
                key="still_text_to_image_pro",
                name="Text to Image Pro",
                category=TaskCategory.STILL,
                backend="still",
                description="Generación de imagen desde texto con SDXL",
                required_inputs=["prompt"],
                optional_inputs=["negative_prompt", "width", "height", "steps", "cfg_scale", "seed"],
                nodes=[
                    WorkflowNode("1", "CheckpointLoaderSimple", {"ckpt_name": "sdxl_base.safetensors"}, ["ckpt_name"], []),
                    WorkflowNode("2", "CLIPTextEncode", {"text": "", "clip": ["1", 0]}, ["text", "clip"], []),
                    WorkflowNode("3", "CLIPTextEncode", {"text": "", "clip": ["1", 0]}, ["text", "clip"], []),
                    WorkflowNode("4", "KSampler", {"model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "seed": 0, "steps": 30, "cfg": 8.0, "sampler_name": "euler", "scheduler": "normal"}, ["model", "positive", "negative", "seed", "steps", "cfg", "sampler_name", "scheduler"], []),
                    WorkflowNode("5", "KSampler", {"model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "seed": 0, "steps": 30, "cfg": 8.0, "sampler_name": "euler", "scheduler": "normal"}, ["model", "positive", "negative", "seed", "steps", "cfg", "sampler_name", "scheduler"], ["model", "positive", "negative", "seed", "steps", "cfg", "sampler_name", "scheduler"]),
                    WorkflowNode("6", "EmptyLatentImage", {"width": 1024, "height": 1024, "batch_size": 1}, ["width", "height", "batch_size"], []),
                    WorkflowNode("7", "VAEDecode", {"samples": ["5", 0], "vae": ["1", 1]}, ["samples", "vae"], []),
                    WorkflowNode("8", "SaveImage", {"images": ["7", 0], "filename_prefix": "text_to_image"}, ["images", "filename_prefix"], [])
                ],
                output_node_id="8",
                tags=["text_to_image", "sdxl", "production"]
            ),
            "still_img2img_cinematic": WorkflowTemplate(
                key="still_img2img_cinematic",
                name="Image to Image Cinematic",
                category=TaskCategory.STILL,
                backend="still",
                description="Transformación de imagen con estilo cinematográfico",
                required_inputs=["prompt", "source_image"],
                optional_inputs=["strength", "negative_prompt", "seed"],
                nodes=[
                    WorkflowNode("1", "CheckpointLoaderSimple", {"ckpt_name": "sdxl_base.safetensors"}, ["ckpt_name"], []),
                    WorkflowNode("2", "LoadImage", {"image": ""}, ["image"], []),
                    WorkflowNode("3", "CLIPTextEncode", {"text": "", "clip": ["1", 0]}, ["text", "clip"], []),
                    WorkflowNode("4", "CLIPTextEncode", {"text": "low quality, blurry", "clip": ["1", 0]}, ["text", "clip"], []),
                    WorkflowNode("5", "VAEEncode", {"pixels": ["2", 0], "vae": ["1", 2]}, ["pixels", "vae"], []),
                    WorkflowNode("6", "KSampler", {"seed": 0, "steps": 30, "cfg": 7.5}, ["seed", "steps", "cfg"], ["model", "positive", "negative", "sampler_name", "scheduler"]),
                    WorkflowNode("7", "VAEDecode", {}, ["samples", "vae"], []),
                    WorkflowNode("8", "SaveImage", {}, ["images", "filename_prefix"], [])
                ],
                output_node_id="8",
                tags=["img2img", "cinematic", "style_transfer"]
            ),
            "still_inpaint_production": WorkflowTemplate(
                key="still_inpaint_production",
                name="Inpainting Production",
                category=TaskCategory.STILL,
                backend="still",
                description="Inpainting con máscara para edición局部",
                required_inputs=["prompt", "source_image", "mask"],
                optional_inputs=["strength", "seed"],
                nodes=[
                    WorkflowNode("1", "CheckpointLoaderSimple", {}, ["ckpt_name"], []),
                    WorkflowNode("2", "LoadImage", {}, ["image"], []),
                    WorkflowNode("3", "LoadImage", {}, ["image"], []),
                    WorkflowNode("4", "CLIPTextEncode", {}, ["text", "clip"], []),
                    WorkflowNode("5", "VAEEncodeForInpaint", {}, ["pixels", "vae", "mask"], []),
                    WorkflowNode("6", "KSampler", {}, ["seed", "steps", "cfg"], []),
                    WorkflowNode("7", "VAEDecode", {}, ["samples", "vae"], []),
                    WorkflowNode("8", "SaveImage", {}, ["images", "filename_prefix"], [])
                ],
                output_node_id="8",
                tags=["inpaint", "mask", "editing"]
            ),
            "still_storyboard_frame": WorkflowTemplate(
                key="still_storyboard_frame",
                name="Storyboard Frame",
                category=TaskCategory.STILL,
                backend="still",
                description="Generación de frame para storyboard",
                required_inputs=["prompt"],
                optional_inputs=["aspect_ratio", "shot_type", "lighting"],
                nodes=[
                    WorkflowNode("1", "CheckpointLoaderSimple", {}, ["ckpt_name"], []),
                    WorkflowNode("2", "CLIPTextEncode", {}, ["text", "clip"], []),
                    WorkflowNode("3", "CLIPTextEncode", {}, ["text", "clip"], []),
                    WorkflowNode("4", "EmptyLatentImage", {"width": 1920, "height": 1080}, ["width", "height", "batch_size"], []),
                    WorkflowNode("5", "KSampler", {}, ["seed", "steps", "cfg"], []),
                    WorkflowNode("6", "VAEDecode", {}, ["samples", "vae"], []),
                    WorkflowNode("7", "SaveImage", {"filename_prefix": "storyboard"}, ["images", "filename_prefix"], [])
                ],
                output_node_id="7",
                tags=["storyboard", "frame", "cinematic"]
            ),
            "still_character_consistency": WorkflowTemplate(
                key="still_character_consistency",
                name="Character Consistency",
                category=TaskCategory.STILL,
                backend="still",
                description="Mantener consistencia de personaje entre generaciones",
                required_inputs=["prompt", "reference_image"],
                optional_inputs=["strength", "seed"],
                nodes=[
                    WorkflowNode("1", "CheckpointLoaderSimple", {}, ["ckpt_name"], []),
                    WorkflowNode("2", "LoadImage", {}, ["image"], []),
                    WorkflowNode("3", "CLIPVisionEncode", {}, ["clip_vision", "image"], []),
                    WorkflowNode("4", "CLIPTextEncode", {}, ["text", "clip"], []),
                    WorkflowNode("5", "ApplySdxlConditioning", {}, ["positive", "clip_vision_output"], []),
                    WorkflowNode("6", "KSampler", {}, ["seed", "steps", "cfg"], []),
                    WorkflowNode("7", "VAEDecode", {}, ["samples", "vae"], []),
                    WorkflowNode("8", "SaveImage", {}, ["images", "filename_prefix"], [])
                ],
                output_node_id="8",
                tags=["character", "consistency", "reference"]
            ),
            "still_upscale_master": WorkflowTemplate(
                key="still_upscale_master",
                name="Upscale Master",
                category=TaskCategory.STILL,
                backend="still",
                description="Upscale de imagen con detalles mejorados",
                required_inputs=["source_image"],
                optional_inputs=["scale", "denoise"],
                nodes=[
                    WorkflowNode("1", "LoadImage", {}, ["image"], []),
                    WorkflowNode("2", "ImageUpscaleWithModel", {}, ["image", "upscale_model"], []),
                    WorkflowNode("3", "VAEEncode", {}, ["pixels", "vae"], []),
                    WorkflowNode("4", "KSampler", {}, ["seed", "steps", "cfg"], []),
                    WorkflowNode("5", "VAEDecode", {}, ["samples", "vae"], []),
                    WorkflowNode("6", "SaveImage", {"filename_prefix": "upscaled"}, ["images", "filename_prefix"], [])
                ],
                output_node_id="6",
                tags=["upscale", "enhance", "quality"]
            ),
            "video_text_to_video_base": WorkflowTemplate(
                key="video_text_to_video_base",
                name="Text to Video Base",
                category=TaskCategory.VIDEO,
                backend="video",
                description="Generación de video desde texto",
                required_inputs=["prompt"],
                optional_inputs=["duration", "fps", "seed", "motion_strength"],
                nodes=[
                    WorkflowNode("1", "CheckpointLoaderSimple", {}, ["ckpt_name"], []),
                    WorkflowNode("2", "CLIPTextEncode", {}, ["text", "clip"], []),
                    WorkflowNode("3", "EmptyLatentVideo", {"width": 512, "height": 512, "frames": 24}, ["width", "height", "frames", "fps"], []),
                    WorkflowNode("4", "KSampler", {}, ["seed", "steps", "cfg"], []),
                    WorkflowNode("5", "VAEDecode", {}, ["samples", "vae"], []),
                    WorkflowNode("6", "SaveAnimatedWEBP", {"filename_prefix": "text_to_video"}, ["images", "filename_prefix"], [])
                ],
                output_node_id="6",
                tags=["text_to_video", "base", "animation"]
            ),
            "video_image_to_video_base": WorkflowTemplate(
                key="video_image_to_video_base",
                name="Image to Video Base",
                category=TaskCategory.VIDEO,
                backend="video",
                description="Animar imagen existente",
                required_inputs=["source_image", "prompt"],
                optional_inputs=["duration", "motion_strength"],
                nodes=[
                    WorkflowNode("1", "LoadImage", {}, ["image"], []),
                    WorkflowNode("2", "CLIPTextEncode", {}, ["text", "clip"], []),
                    WorkflowNode("3", "ImageEncodeToLatent", {}, ["image", "vae"], []),
                    WorkflowNode("4", "AnimateDiffLoader", {}, ["model", "ad_model"], []),
                    WorkflowNode("5", "KSampler", {}, ["seed", "steps", "cfg"], []),
                    WorkflowNode("6", "VAEDecode", {}, ["samples", "vae"], []),
                    WorkflowNode("7", "SaveAnimatedWEBP", {}, ["images", "filename_prefix"], [])
                ],
                output_node_id="7",
                tags=["image_to_video", "animation", "motion"]
            ),
            "video_first_last_frame": WorkflowTemplate(
                key="video_first_last_frame",
                name="First Last Frame Video",
                category=TaskCategory.VIDEO,
                backend="video",
                description="Video interpolado entre primer y último frame",
                required_inputs=["first_frame", "last_frame", "prompt"],
                optional_inputs=["frames", "interpolation_mode"],
                nodes=[
                    WorkflowNode("1", "LoadImage", {}, ["image"], []),
                    WorkflowNode("2", "LoadImage", {}, ["image"], []),
                    WorkflowNode("3", "InterpolateLatents", {}, ["samples1", "samples2", "frames"], []),
                    WorkflowNode("4", "VAEDecode", {}, ["samples", "vae"], []),
                    WorkflowNode("5", "SaveAnimatedWEBP", {}, ["images", "filename_prefix"], [])
                ],
                output_node_id="5",
                tags=["interpolation", "keyframes", "morph"]
            ),
            "dubbing_tts_es_es": WorkflowTemplate(
                key="dubbing_tts_es_es",
                name="TTS Español",
                category=TaskCategory.DUBBING,
                backend="dubbing",
                description="Texto a voz en español",
                required_inputs=["text"],
                optional_inputs=["voice", "speed", "pitch"],
                nodes=[
                    WorkflowNode("1", "TextToSpeechNode", {"language": "es-ES"}, ["text", "language", "voice"], ["speed", "pitch"]),
                    WorkflowNode("2", "SaveAudio", {"filename_prefix": "tts_es"}, ["audio", "filename_prefix"], [])
                ],
                output_node_id="2",
                tags=["tts", "spanish", "voice"]
            ),
            "dubbing_voice_clone_single": WorkflowTemplate(
                key="dubbing_voice_clone_single",
                name="Voice Clone Single",
                category=TaskCategory.DUBBING,
                backend="dubbing",
                description="Clonación de voz desde audio de referencia",
                required_inputs=["text", "reference_audio"],
                optional_inputs=["similarity", "stability"],
                nodes=[
                    WorkflowNode("1", "LoadAudio", {}, ["audio"], []),
                    WorkflowNode("2", "VoiceCloneNode", {}, ["reference_audio", "text"], ["similarity", "stability"]),
                    WorkflowNode("3", "SaveAudio", {}, ["audio", "filename_prefix"], [])
                ],
                output_node_id="3",
                tags=["voice_clone", "tts", "reference"]
            ),
            "dubbing_multi_character_dialog": WorkflowTemplate(
                key="dubbing_multi_character_dialog",
                name="Multi Character Dialog",
                category=TaskCategory.DUBBING,
                backend="dubbing",
                description="Diálogos multi-personaje con voces distintas",
                required_inputs=["script"],
                optional_inputs=["character_voices"],
                nodes=[
                    WorkflowNode("1", "DialogueParser", {}, ["script"], ["character_voices"]),
                    WorkflowNode("2", "VoiceCloneNode", {}, ["reference_audio", "text"], []),
                    WorkflowNode("3", "VoiceCloneNode", {}, ["reference_audio", "text"], []),
                    WorkflowNode("4", "MergeAudio", {}, ["audio1", "audio2"], []),
                    WorkflowNode("5", "SaveAudio", {}, ["audio", "filename_prefix"], [])
                ],
                output_node_id="5",
                tags=["dialog", "multi_character", "dubbing"]
            ),
            "dubbing_translate_stt_tts": WorkflowTemplate(
                key="dubbing_translate_stt_tts",
                name="Translate STT TTS",
                category=TaskCategory.DUBBING,
                backend="dubbing",
                description="Transcripción, traducción y síntesis de voz",
                required_inputs=["source_audio", "target_language"],
                optional_inputs=["source_language", "voice_style"],
                nodes=[
                    WorkflowNode("1", "LoadAudio", {}, ["audio"], []),
                    WorkflowNode("2", "SpeechToText", {}, ["audio"], ["language"]),
                    WorkflowNode("3", "TranslateText", {}, ["text", "target_language"], ["source_language"]),
                    WorkflowNode("4", "TextToSpeechNode", {}, ["text", "language"], ["voice_style"]),
                    WorkflowNode("5", "SaveAudio", {}, ["audio", "filename_prefix"], [])
                ],
                output_node_id="5",
                tags=["translate", "stt", "tts", "dubbing"]
            ),
            "lab_probe_nodes": WorkflowTemplate(
                key="lab_probe_nodes",
                name="Probe Nodes",
                category=TaskCategory.LAB,
                backend="lab",
                description="Exploración de nodos disponibles",
                required_inputs=[],
                optional_inputs=["node_filter"],
                nodes=[
                    WorkflowNode("1", "NodeProbe", {}, [], ["node_filter"]),
                ],
                output_node_id="1",
                tags=["probe", "debug", "nodes"]
            ),
            "lab_auto_assemble_test": WorkflowTemplate(
                key="lab_auto_assemble_test",
                name="Auto Assemble Test",
                category=TaskCategory.LAB,
                backend="lab",
                description="Ensamblaje automático para testing",
                required_inputs=["intent"],
                optional_inputs=["modules"],
                nodes=[
                    WorkflowNode("1", "IntentClassifier", {}, ["intent"], []),
                    WorkflowNode("2", "ModuleSelector", {}, ["intent"], ["modules"]),
                    WorkflowNode("3", "DynamicAssembler", {}, ["modules"], []),
                ],
                output_node_id="3",
                tags=["auto", "assemble", "experimental"]
            ),
        }

    def get_workflow(self, key: str) -> Optional[WorkflowTemplate]:
        return self._workflows.get(key)

    def get_workflows_by_category(self, category: TaskCategory) -> List[WorkflowTemplate]:
        return [w for w in self._workflows.values() if w.category == category]

    def get_workflows_by_backend(self, backend: str) -> List[WorkflowTemplate]:
        return [w for w in self._workflows.values() if w.backend == backend]

    def get_all_workflows(self) -> List[WorkflowTemplate]:
        return list(self._workflows.values())

    def get_catalog(self) -> List[Dict[str, Any]]:
        return [
            {
                "key": w.key,
                "name": w.name,
                "category": w.category.value,
                "backend": w.backend,
                "description": w.description,
                "required_inputs": w.required_inputs,
                "optional_inputs": w.optional_inputs,
                "tags": w.tags
            }
            for w in self._workflows.values()
        ]

    def search_workflows(self, query: str) -> List[WorkflowTemplate]:
        query_lower = query.lower()
        results = []
        for w in self._workflows.values():
            if (query_lower in w.name.lower() or 
                query_lower in w.description.lower() or
                any(query_lower in tag for tag in w.tags)):
                results.append(w)
        return results


workflow_registry = WorkflowRegistry()
