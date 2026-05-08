# CID Visual Reference — Integración con ComfyUI

> FASE 9 — Preparación del pipeline de render para soportar referencia visual.

---

## Estado actual

El pipeline de ComfyUI actual usa:
- `flux_cine_2.template.json` — workflow FLUX sin soporte para IPAdapter, CLIPVision ni ControlNet
- `build_landing_comfyui_payloads_v4.py` — construye payloads con prompt + semillas
- `render_landing_comfyui_images_v4.py` — envía a `/prompt`

No hay integración de image-to-prompt, ni referencia visual directa.

---

## Campos preparados en payload

El payload de render puede incluir estos campos opcionales para referencia visual:

```python
{
    "image_key": "shot-001",
    "block_label": "Hero scene",
    "prompt": "...",
    "negative_prompt": "...",
    "compiled_workflow": {...},

    # Visual reference support (FASE 9)
    "visual_reference_profile_id": "ref_abc123",
    "reference_image_path": "/mnt/g/COMFYUI_HUB/input/cid_landing_v4_references/reference.webp",
    "reference_purpose": "scene_mood",
    "style_reference_strength": 0.35,
    "composition_reference_enabled": False,
    "palette_reference_enabled": True,
    "lighting_reference_enabled": True,
}
```

---

## Integración futura con nodos ComfyUI

Cuando el workflow de ComfyUI soporte nodos de referencia visual:

### IPAdapter
```python
# En el workflow JSON, añadir nodo IPAdapter:
{
    "class_type": "IPAdapterUnifiedLoader",
    "inputs": {
        "ipadapter": "IPAdapter",
        "model": ["model_node", 0],
    }
}
```

### CLIPVision + image interrogation
```python
# Nodo de interrogación de imagen:
{
    "class_type": "CLIPVisionLoader",
    "inputs": {"clip_name": "CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors"},
}
```

### ControlNet reference
```python
# ControlNet para composición:
{
    "class_type": "ControlNetLoader",
    "inputs": {"control_net_name": "control-lora-canny.safetensors"},
}
```

---

## Recomendación de implementación

1. **Corto plazo**: El perfil `StyleReferenceProfile` guía solo el prompt textual. La referencia visual se usa como dirección artística, no como entrada al modelo.
2. **Medio plazo**: Añadir nodo `IPAdapter` al workflow FLUX template cuando esté disponible en la instancia ComfyUI.
3. **Largo plazo**: Pipeline completo: imagen → CLIPVision → captioning → perfil → prompt → IPAdapter → generación controlada.

No implementar nodos inventados. Solo preparar el payload para que cuando el workflow lo soporte, los campos estén disponibles.
