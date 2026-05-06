from typing import Dict, List, Optional, Any
from dataclasses import dataclass
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
    _health_timeout_seconds = 5
    _discovery_timeout_seconds = 5
    _model_endpoints = {
        "checkpoints": "/models/checkpoints",
        "loras": "/models/loras",
        "vae": "/models/vae",
        "controlnet": "/models/controlnet",
        "upscale_models": "/models/upscale_models",
        "embeddings": "/models/embeddings",
    }

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

        start_time = asyncio.get_running_loop().time()

        async with aiohttp.ClientSession() as session:
            base_url = backend.base_url.rstrip("/")
            health_data = await self._check_basic_health(
                session,
                base_url,
                capabilities,
            )
            if health_data is not None:
                model_result = await self._discover_models(session, base_url)
                node_result = await self._discover_nodes(session, base_url)
                capabilities.models = model_result["models"]
                capabilities.nodes = node_result["nodes"]
                capabilities.warnings.extend(model_result["warnings"])
                capabilities.warnings.extend(node_result["warnings"])

        end_time = asyncio.get_running_loop().time()
        capabilities.response_time_ms = (end_time - start_time) * 1000
        capabilities.detected_capabilities = self._merge_capabilities(
            backend.capabilities,
            self._infer_capabilities(capabilities),
        )

        self._cache[backend_key] = capabilities
        return capabilities

    async def _check_basic_health(
        self,
        session: aiohttp.ClientSession,
        base_url: str,
        capabilities: BackendCapabilities,
    ) -> Optional[Dict[str, Any]]:
        try:
            async with session.get(
                f"{base_url}/system_stats",
                timeout=self._health_timeout_seconds,
            ) as resp:
                if resp.status != 200:
                    capabilities.warnings.append(f"system_stats http {resp.status}")
                    return None
                data = await resp.json(content_type=None)
        except asyncio.TimeoutError:
            capabilities.warnings.append("system_stats timeout")
            return None
        except aiohttp.ClientError:
            capabilities.warnings.append("system_stats connection error")
            return None
        except Exception as exc:
            capabilities.warnings.append(f"system_stats error: {str(exc)}")
            return None

        capabilities.healthy = True
        capabilities.comfyui_version = self._extract_comfyui_version(data)
        return data

    async def _discover_models(
        self,
        session: aiohttp.ClientSession,
        base_url: str,
    ) -> Dict[str, Any]:
        models: List[ModelInfo] = []
        warnings: List[str] = []
        seen: set[tuple[str, str]] = set()
        for model_type, path in self._model_endpoints.items():
            result = await self._fetch_model_endpoint(session, base_url, model_type, path)
            warnings.extend(result["warnings"])
            for model in result["models"]:
                key = (model.model_type, model.model_name)
                if key in seen:
                    continue
                seen.add(key)
                models.append(model)
        return {"models": models, "warnings": warnings}

    async def _fetch_model_endpoint(
        self,
        session: aiohttp.ClientSession,
        base_url: str,
        model_type: str,
        path: str,
    ) -> Dict[str, Any]:
        endpoint_name = path.rsplit("/", 1)[-1]
        try:
            async with session.get(
                f"{base_url}{path}",
                timeout=self._discovery_timeout_seconds,
            ) as resp:
                if resp.status != 200:
                    return {
                        "models": [],
                        "warnings": [f"{endpoint_name} discovery http {resp.status}"],
                    }
                data = await resp.json(content_type=None)
        except asyncio.TimeoutError:
            return {
                "models": [],
                "warnings": [f"{endpoint_name} discovery timeout"],
            }
        except aiohttp.ClientError:
            return {
                "models": [],
                "warnings": [f"{endpoint_name} discovery connection error"],
            }
        except Exception as exc:
            return {
                "models": [],
                "warnings": [f"{endpoint_name} discovery error: {str(exc)}"],
            }

        models = [
            ModelInfo(
                model_name=item.get("name") or item.get("model_name") or "unknown",
                model_type=model_type,
                loaded=bool(item.get("loaded", False)),
                size_mb=self._coerce_size_mb(item.get("size_mb") or item.get("size")),
            )
            for item in self._normalize_model_entries(data)
        ]
        return {"models": models, "warnings": []}

    async def _discover_nodes(
        self,
        session: aiohttp.ClientSession,
        base_url: str,
    ) -> Dict[str, Any]:
        try:
            async with session.get(
                f"{base_url}/object_info",
                timeout=self._discovery_timeout_seconds,
            ) as resp:
                if resp.status != 200:
                    return {
                        "nodes": [],
                        "warnings": [f"object_info discovery http {resp.status}"],
                    }
                data = await resp.json(content_type=None)
        except asyncio.TimeoutError:
            return {"nodes": [], "warnings": ["object_info discovery timeout"]}
        except aiohttp.ClientError:
            return {"nodes": [], "warnings": ["object_info discovery connection error"]}
        except Exception as exc:
            return {
                "nodes": [],
                "warnings": [f"object_info discovery error: {str(exc)}"],
            }

        nodes, _models = self._parse_object_info(data)
        return {"nodes": nodes, "warnings": []}

    def _extract_comfyui_version(self, data: Dict[str, Any]) -> Optional[str]:
        system = data.get("system") if isinstance(data, dict) else None
        if isinstance(system, dict):
            version = system.get("comfyui_version")
            if version:
                return str(version)
        version = data.get("version") if isinstance(data, dict) else None
        return str(version) if version else None

    def _normalize_model_entries(self, data: Any) -> List[Dict[str, Any]]:
        if isinstance(data, list):
            return [self._normalize_model_entry(item) for item in data]
        if isinstance(data, dict):
            if isinstance(data.get("models"), list):
                return [self._normalize_model_entry(item) for item in data["models"]]
            normalized: List[Dict[str, Any]] = []
            for key, value in data.items():
                if isinstance(value, dict):
                    normalized.append({"name": key, **value})
                elif isinstance(value, list):
                    normalized.extend(self._normalize_model_entries(value))
                else:
                    normalized.append({"name": str(value or key)})
            return normalized
        if data is None:
            return []
        return [{"name": str(data)}]

    def _normalize_model_entry(self, item: Any) -> Dict[str, Any]:
        if isinstance(item, dict):
            if any(key in item for key in ("name", "model_name", "filename", "title")):
                return {
                    "name": item.get("name")
                    or item.get("model_name")
                    or item.get("filename")
                    or item.get("title"),
                    "loaded": item.get("loaded", False),
                    "size_mb": item.get("size_mb") or item.get("size"),
                }
            if len(item) == 1:
                key, value = next(iter(item.items()))
                if isinstance(value, dict):
                    return {"name": key, **value}
                return {"name": value or key}
            return {"name": str(item)}
        return {"name": str(item)}

    def _coerce_size_mb(self, value: Any) -> Optional[float]:
        if value is None:
            return None
        try:
            return round(float(value), 2)
        except (TypeError, ValueError):
            return None

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

    def _merge_capabilities(
        self,
        configured_capabilities: List[str],
        inferred_capabilities: List[str],
    ) -> List[str]:
        merged: List[str] = []
        for capability in [*(configured_capabilities or []), *inferred_capabilities]:
            if capability and capability not in merged:
                merged.append(capability)
        return merged

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
