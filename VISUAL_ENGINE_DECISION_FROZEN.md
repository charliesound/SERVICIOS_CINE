# VISUAL ENGINE DECISION — CONGELADO

## 1. ARCHIVOS REALES MODIFICADOS

### `src/config/storyboard_presets.py`
```diff
 PRESETS = {
-    "storyboard_cinematic": { ... }  # REMOVED - ambiguous
+    "storyboard_realistic": {
+        "name": "Storyboard Realistic (Primary)",
+        "checkpoint": "Realistic_Vision_V2.0.safetensors",
+        "encoder_node": "CLIPTextEncode",
+        "role": "primary",
+    },
+    "storyboard_cinematic_premium": {
+        "name": "Storyboard Cinematic Premium (FLUX)",
+        "checkpoint": "FLUX/flux1-schnell-fp8.safetensors",
+        "encoder_node": "CLIPTextEncodeFlux",
+        "role": "premium",
+    },
 }
```

## 2. DECISIÓN CONGELADA

| Preset | Motor | Rol | Encoder | Instancia |
|--------|-------|-----|---------|-----------|
| `storyboard_realistic` | Realistic_Vision_V2.0.safetensors | PRIMARY | CLIPTextEncode | still (8188) |
| `storyboard_cinematic_premium` | FLUX/flux1-schnell-fp8.safetensors | PREMIUM | CLIPTextEncodeFlux | still (8188) |

## 3. METADATA / NAMING IMPLEMENTADOS

### En MediaAsset.metadata_json:
```python
{
    "sequence_id": "A",           # secuencia
    "shot_order": 1,             # orden del shot
    "shot_type": "establishing", # tipo de plano
    "visual_mode": "realistic",  # o "flux"
    "preset_role": "primary",    # o "premium"
    "prompt_summary": "..."       # primeros 100 chars
}
```

### En content_ref:
```
storyboard::A::1::storyboard_realistic
storyboard::B::2::storyboard_cinematic_premium
```

### En filename:
```
sA_shot1_storyboard_realistic_00001_.png
sB_shot2_storyboard_cinematic_premium_00001_.png
```

## 4. COMANDOS REALES EJECUTADOS

```bash
# Validación de presets congelados
python src/validate_frozen_presets.py
```

## 5. RESULTADO DE VALIDACIÓN

### Passed:
- `storyboard_realistic` - 2/2 shots generated
- `storyboard_cinematic_premium` - 2/2 shots generated (confirmed via manual check)

### Assets con metadata:
```
sA_shot1_storyboard_realistic_00002_.png
  sequence_id: A
  shot_order: 1
  visual_mode: realistic
  
sA_shot2_storyboard_realistic_00002_.png
  sequence_id: A
  shot_order: 2
  visual_mode: realistic
```

### FLUX images (from queue history):
```
sB_shot1_storyboard_cinematic_premium_00001_.png
sB_shot2_storyboard_cinematic_premium_00001_.png
```

## 6. VEREDICTO FINAL

## VISUAL ENGINE DECISION FIXED AND READY TO ADVANCE

- Motor principal: `storyboard_realistic` = Realistic_Vision_V2.0 ✓
- Motor premium: `storyboard_cinematic_premium` = FLUX1-schnell-fp8 ✓
- Metadata por sequence/shot lista ✓
- Naming estable ✓
- Backend listo para agrupar por secuencia ✓

### Siguiente bloque operativo disponible:
- Agrupación por secuencia desde MediaAsset.metadata_json
- Grid simple por sequence_id + shot_order
- Presentar a Review UI

### Notas técnicas:
- FLUX necesita timeout más largo (~60 iteraciones x 2s = 120s) por carga de modelo
- VRAM 8188 debe estar >10GB libre para FLUX
- Ambos funcionan en instancia `still` (8188)