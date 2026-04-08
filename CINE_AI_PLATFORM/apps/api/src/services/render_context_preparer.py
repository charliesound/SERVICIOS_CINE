import copy
import logging
from typing import Any, Dict, Optional, Tuple

from src.services.storage_service import StorageService
from src.settings import settings

logger = logging.getLogger(__name__)

class RenderContextPreparer:
    def __init__(self, storage_service: StorageService):
        self.storage_service = storage_service

    def prepare_payload(self, raw_payload: Dict[str, Any], context_flags: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enriquece el payload original con contexto cinematográfico si la flag está activa.
        """
        if not settings.enable_render_context_flags:
            return raw_payload

        # Trabajamos sobre una copia profunda para no mutar el original
        payload = copy.deepcopy(raw_payload)
        
        try:
            character_id = context_flags.get("character_id")
            if character_id:
                payload = self._inject_character_context(payload, character_id)
            
            # Aquí se podrían añadir más inyecciones (scene_id, lighting, etc.)
            
            return payload
        except Exception as e:
            logger.error(f"Error during render context enrichment: {str(e)}", exc_info=True)
            # Fallback: devolver el original si algo falla en el enriquecimiento
            return raw_payload

    def _inject_character_context(self, payload: Dict[str, Any], character_id: str) -> Dict[str, Any]:
        character = self.storage_service.get_active_storage_character(
            backend=settings.shots_store_backend, 
            character_id=character_id
        )
        
        if not character:
            logger.warning(f"Character {character_id} not found in storage. Skipping context injection.")
            return payload

        reference_images = character.get("reference_images", [])
        if not reference_images:
            return payload

        # Por ahora tomamos la primera imagen de referencia para IP-Adapter
        image_name = reference_images[0]
        return self._inject_ip_adapter(payload, image_name)

    def _inject_ip_adapter(self, payload: Dict[str, Any], image_name: str) -> Dict[str, Any]:
        """
        Injects IP-Adapter nodes into the ComfyUI graph.
        This is a conservative implementation that looks for a KSampler or similar and 
        applies the adapter to the MODEL input.
        """
        # 1. Encontrar el nodo KSampler (o equivalente) para saber dónde inyectar el MODEL
        target_node_id, target_node = self._find_node_by_class(payload, ["KSampler", "KSamplerAdvanced"])
        if not target_node_id:
            logger.warning("Could not find KSampler node for IP-Adapter injection. Skipping.")
            return payload

        # 2. Generar IDs para los nuevos nodos
        next_id = self._get_next_node_id(payload)
        load_img_id = str(next_id)
        clip_vision_id = str(next_id + 1)
        ip_adapter_model_id = str(next_id + 2)
        ip_adapter_apply_id = str(next_id + 3)

        # 3. Definir los nuevos nodos
        # Nota: Los nombres de los modelos vienen de settings
        new_nodes = {
            load_img_id: {
                "class_type": "LoadImage",
                "inputs": {
                    "image": image_name,
                    "upload": "image"
                },
                "_meta": {"title": f"CAI_LoadChar_{image_name[:8]}"}
            },
            clip_vision_id: {
                "class_type": "CLIPVisionLoader",
                "inputs": {
                    "clip_name": settings.clip_vision_model
                },
                "_meta": {"title": "CAI_CLIPVision"}
            },
            ip_adapter_model_id: {
                "class_type": "IPAdapterModelLoader",
                "inputs": {
                    "ipadapter_file": settings.ipadapter_sdxl_model
                },
                "_meta": {"title": "CAI_IPAdapterModel"}
            },
            ip_adapter_apply_id: {
                "class_type": "IPAdapter",
                "inputs": {
                    "model": target_node["inputs"]["model"], # Interceptamos la conexión original
                    "ipadapter": [ip_adapter_model_id, 0],
                    "image": [load_img_id, 0],
                    "clip_vision": [clip_vision_id, 0],
                    "weight": 0.8,
                    "noise": 0.0
                },
                "_meta": {"title": "CAI_ApplyIPAdapter"}
            }
        }

        # 4. Actualizar el KSampler para que use el modelo adaptado
        payload.update(new_nodes)
        target_node["inputs"]["model"] = [ip_adapter_apply_id, 0]

        return payload

    def _find_node_by_class(self, payload: Dict[str, Any], class_types: list[str]) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        for node_id, node in payload.items():
            if node.get("class_type") in class_types:
                return node_id, node
        return None, None

    def _get_next_node_id(self, payload: Dict[str, Any]) -> int:
        numeric_ids = [int(nid) for nid in payload.keys() if nid.isdigit()]
        return max(numeric_ids) + 1 if numeric_ids else 1
