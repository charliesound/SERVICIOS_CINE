from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import aiohttp
import asyncio

from .instance_registry import registry


@dataclass
class NodeInfo:
    node_type: str
    input_types: List[str]
    output_types: List[str]
    category: str


@dataclass
class ModelInfo:
    model_name: str
    model_type: str
    loaded: bool
    size_mb: Optional[float] = None


@dataclass
class BackendCapabilities:
    backend: str
    healthy: bool
    response_time_ms: float
    nodes: List[NodeInfo]
    models: List[ModelInfo]
    detected_capabilities: List[str]
    warnings: List[str]
    last_check: datetime
    comfyui_version: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "backend": self.backend,
            "healthy": self.healthy,
            "response_time_ms": round(self.response_time_ms, 2),
            "comfyui_version": self.comfyui_version,
            "nodes_count": len(self.nodes),
            "models_count": len(self.models),
            "nodes": [
                {
                    "type": n.node_type,
                    "category": n.category,
                    "inputs": n.input_types,
                    "outputs": n.output_types
                }
                for n in self.nodes
            ],
            "models": [
                {
                    "name": m.model_name,
                    "type": m.model_type,
                    "loaded": m.loaded,
                    "size_mb": m.size_mb
                }
                for m in self.models
            ],
            "detected_capabilities": self.detected_capabilities,
            "warnings": self.warnings,
            "last_check": self.last_check.isoformat()
        }


class NodeCategoryMapper:
    CATEGORY_MAP = {
        "CheckpointLoader": "model_loading",
        "CheckpointLoaderSimple": "model_loading",
        "CheckpointLoaderSDXL": "model_loading",
        "LoadImage": "io",
        "LoadAudio": "io",
        "SaveImage": "io",
        "SaveAnimatedWEBP": "io",
        "SaveAudio": "io",
        "CLIPTextEncode": "text",
        "CLIPTextDecode": "text",
        "CLIPVisionEncode": "vision",
        "KSampler": "sampling",
        "KSamplerAdvanced": "sampling",
        "EmptyLatentImage": "latent",
        "EmptyLatentVideo": "latent",
        "VAEEncode": "latent",
        "VAEDecode": "latent",
        "VAEEncodeForInpaint": "inpaint",
        "ImageUpscaleWithModel": "upscaling",
        "AnimateDiffLoader": "animation",
        "InterpolateLatents": "animation",
        "TextToSpeechNode": "audio",
        "VoiceCloneNode": "audio",
        "SpeechToText": "audio",
        "TranslateText": "text",
        "MergeAudio": "audio",
        "LoadAudio": "audio",
        "DialogueParser": "dubbing",
        "NodeProbe": "debug",
        "DynamicAssembler": "experimental",
        "IntentClassifier": "ai",
        "ModuleSelector": "ai",
        "ApplySdxlConditioning": "conditioning",
    }

    @classmethod
    def get_category(cls, node_type: str) -> str:
        for key, category in cls.CATEGORY_MAP.items():
            if key in node_type:
                return category
        return "other"


class BackendCapabilityService:
    _instance = None
    _cache: Dict[str, BackendCapabilities] = {}
    _cache_ttl = 60

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

    def _is_cache_valid(self, backend: str) -> bool:
        if backend not in self._cache:
            return False
        cached = self._cache[backend]
        age = (datetime.utcnow() - cached.last_check).total_seconds()
        return age < self._cache_ttl

    async def detect_capabilities(self, backend_key: str, force: bool = False) -> Optional[BackendCapabilities]:
        if not force and self._is_cache_valid(backend_key):
            return self._cache[backend_key]

        backend = registry.get_backend(backend_key)
        if not backend:
            return None

        capabilities = BackendCapabilities(
            backend=backend_key,
            healthy=False,
            response_time_ms=0,
            nodes=[],
            models=[],
            detected_capabilities=[],
            warnings=[],
            last_check=datetime.utcnow()
        )

        start_time = asyncio.get_event_loop().time()

        try:
            async with aiohttp.ClientSession() as session:
                base_url = backend.base_url

                async with session.get(f"{base_url}/system_stats", timeout=5) as resp:
                    if resp.status == 200:
                        capabilities.healthy = True
                        data = await resp.json()
                        capabilities.comfyui_version = data.get("version")

                async with session.get(f"{base_url}/api/object_info", timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        nodes, models = self._parse_object_info(data)
                        capabilities.nodes = nodes
                        capabilities.models = models

        except asyncio.TimeoutError:
            capabilities.warnings.append("Timeout connecting to backend")
        except Exception as e:
            capabilities.warnings.append(f"Connection error: {str(e)}")

        end_time = asyncio.get_event_loop().time()
        capabilities.response_time_ms = (end_time - start_time) * 1000

        capabilities.detected_capabilities = self._infer_capabilities(capabilities)

        self._cache[backend_key] = capabilities
        return capabilities

    def _parse_object_info(self, data: Dict) -> tuple[List[NodeInfo], List[ModelInfo]]:
        nodes = []
        models = []

        for node_type, node_data in data.items():
            if isinstance(node_data, dict):
                input_types = []
                output_types = []

                if "input" in node_data:
                    input_config = node_data.get("input", {})
                    if "required" in input_config:
                        input_types.extend(input_config["required"].keys())
                    if "optional" in input_config:
                        input_types.extend(input_config["optional"].keys())

                if "output" in node_data:
                    output_types = node_data.get("output", [])

                nodes.append(NodeInfo(
                    node_type=node_type,
                    input_types=input_types,
                    output_types=output_types,
                    category=NodeCategoryMapper.get_category(node_type)
                ))

                if "CheckpointLoader" in node_type or "Loader" in node_type:
                    models.append(ModelInfo(
                        model_name="detected",
                        model_type="checkpoint",
                        loaded=False
                    ))

        return nodes, models

    def _infer_capabilities(self, caps: BackendCapabilities) -> List[str]:
        capabilities = []
        node_types = {n.node_type for n in caps.nodes}

        if any("CheckpointLoader" in n for n in node_types):
            capabilities.append("image_generation")
        if any("KSampler" in n for n in node_types):
            capabilities.append("sampling")
        if any("VAEDecode" in n for n in node_types):
            capabilities.append("image_decoding")
        if any("SaveImage" in n for n in node_types):
            capabilities.append("image_output")
        if any("SaveAnimatedWEBP" in n for n in node_types):
            capabilities.append("video_output")
        if any("EmptyLatentVideo" in n or "AnimateDiff" in n for n in node_types):
            capabilities.append("video_generation")
        if any("LoadAudio" in n or "SaveAudio" in n or "TTS" in n for n in node_types):
            capabilities.append("audio_processing")
        if any("VoiceClone" in n for n in node_types):
            capabilities.append("voice_cloning")
        if any("Inpaint" in n for n in node_types):
            capabilities.append("inpainting")
        if any("Upscale" in n for n in node_types):
            capabilities.append("upscaling")
        if any("CLIPVision" in n for n in node_types):
            capabilities.append("vision_conditioning")
        if any("Translate" in n for n in node_types):
            capabilities.append("translation")
        if any("SpeechToText" in n for n in node_types):
            capabilities.append("speech_to_text")

        return capabilities

    async def detect_all_capabilities(self, force: bool = False) -> Dict[str, Any]:
        backends = ["still", "video", "dubbing", "lab"]
        results = {}

        tasks = [self.detect_capabilities(b, force) for b in backends]
        detected = await asyncio.gather(*tasks, return_exceptions=True)

        for backend, caps in zip(backends, detected):
            if isinstance(caps, Exception):
                results[backend] = {
                    "backend": backend,
                    "healthy": False,
                    "error": str(caps),
                    "response_time_ms": 0,
                    "detected_capabilities": []
                }
            else:
                results[backend] = caps.to_dict() if caps else {
                    "backend": backend,
                    "healthy": False,
                    "error": "Backend not found"
                }

        return results

    def get_cached_capabilities(self, backend_key: str) -> Optional[BackendCapabilities]:
        return self._cache.get(backend_key)

    def can_workflow_run(self, backend_key: str, required_capabilities: List[str]) -> tuple[bool, List[str]]:
        caps = self._cache.get(backend_key)
        if not caps:
            return True, []

        missing = [cap for cap in required_capabilities if cap not in caps.detected_capabilities]
        
        if missing:
            return False, missing
        return True, []

    def invalidate_cache(self, backend_key: Optional[str] = None):
        if backend_key:
            self._cache.pop(backend_key, None)
        else:
            self._cache.clear()


capability_service = BackendCapabilityService()
