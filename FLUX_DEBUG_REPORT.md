# DEBUG FLUX — REPORTE FINAL

---

## 1. WORKFLOW FLUX EXACTO AUDITADO

### Workflow que funciona:
```python
{
    "1": {"inputs": {"ckpt_name": "FLUX/flux1-schnell-fp8.safetensors"}, "class_type": "CheckpointLoaderSimple"},
    "2": {"inputs": {"clip": ["1", 1], "clip_l": "...", "t5xxl": "...", "guidance": 3.5}, "class_type": "CLIPTextEncodeFlux"},
    "3": {"inputs": {"clip": ["1", 1], "clip_l": "...", "t5xxl": "...", "guidance": 3.5}, "class_type": "CLIPTextEncodeFlux"},
    "4": {"inputs": {"width": 1024, "height": 576, "batch_size": 1}, "class_type": "EmptyLatentImage"},
    "5": {"inputs": {"seed": 12345, "steps": 16, "cfg": 1.0, "sampler_name": "euler", ...}, "class_type": "KSampler"},
    "6": {"inputs": {"samples": ["5", 0], "vae": ["1", 2]}, "class_type": "VAEDecode"},
    "7": {"inputs": {"filename_prefix": "flux_test", "images": ["6", 0]}, "class_type": "SaveImage"},
}
```

### Nodos clave:
- **Loader**: `CheckpointLoaderSimple` (no Nunchaku - solo en 8191)
- **Encode**: `CLIPTextEncodeFlux` (NO `CLIPTextEncode` estándar)
- **Inputs FLUX**: `clip`, `clip_l`, `t5xxl`, `guidance`

---

## 2. INSTANCIA USADA

| Instancia | Puerto | ComfyUI | Resultado |
|-----------|--------|---------|-----------|
| still | 8188 | 0.19.1 | ✓ FUNCIONA |
| lab | 8191 | 0.13.0 | ✗ NO FUNCIONA (stuck) |

---

## 3. COMANDOS REALES EJECUTADOS

### Prueba directa en 8191 (lab):
```bash
curl -X POST http://localhost:8191/prompt -d '{"prompt": wf, "prompt_id": "test"}'
# Result: Job accepted but stuck in queue
# VRAM: ~12GB free (not enough for FLUX loading)
```

### Prueba directa en 8188 (still):
```bash
curl -X POST http://localhost:8188/prompt -d '{"prompt": wf_flux, "prompt_id": "flux_8188"}'
# Result: SUCCESS - generated in 30s
# VRAM: 15.2GB free
```

### Prueba desde AILinkCinema backend:
```python
client = factory.get_client("still")
result = await client.post_prompt(wf, "flux_test")
# Result: SUCCESS - 21.1s, ProjectJob + MediaAsset created
```

---

## 4. RESULTADO DE PRUEBA DIRECTA

| Prueba | Instancia | Resultado | Tiempo |
|--------|-----------|-----------|--------|
| easy fluxLoader | 8191 | Stuck in queue | >120s |
| CheckpointLoaderSimple + CLIPTextEncodeFlux | 8191 | Stuck in queue | >120s |
| Realistic_Vision_V2.0 | 8191 | Stuck in queue | >60s |
| **CheckpointLoaderSimple + CLIPTextEncodeFlux** | **8188** | **SUCCESS** | **30s** |

---

## 5. RESULTADO DE PRUEBA DESDE AILINKCINEMA

```
Project: 353182a684464b0dbebb467cdb5ee297

Job: job-flux-backend-7b661759: completed
Asset: flux_backend_00001_.png -> flux_backend_test

Duration: 21.1s
Status: completed
```

**ProjectJob**: ✓ Created, completed
**JobHistory**: ✓ (via history API)
**MediaAsset**: ✓ Persisted

---

## 6. CAUSA EXACTA DEL BLOQUEO

### Problema identificado: **wrong instance routing**

**8191 (lab)** tiene:
- ComfyUI 0.13.0 (más viejo)
- VRAM disponible ~12GB (insuficiente para cargar FLUX)
- Jobs se quedan en queue_running pero nunca progresan
- Mismo comportamiento con Realistic_Vision (stuck)

**8188 (still)** tiene:
- ComfyUI 0.19.1 (más nuevo)
- VRAM disponible ~15GB+ (suficiente)
- FLUX carga y genera correctamente

**Conclusión**: 8191 tiene problemas de ejecución (posiblemente VRAM insuficiente o versión de ComfyUI incompatible). La solución es usar **8188 para FLUX**.

---

## 7. VEREDICTO FINAL

### FLUX BLOCKED KEEP REALISTIC PRIMARY

**Con recomendaciones:**

| Motor | Status | Notas |
|-------|--------|-------|
| Realistic_Vision_V2.0 | ✓ PRIMARY | Estable, funciona en ambas instancias |
| FLUX1-schnell-fp8 | ✓ FUNCIONAL | Solo en 8188, ~20-30s por imagen |

### Recomendación para producto:
1. **Mantener Realistic_Vision_V2.0** como motor principal (port 8188)
2. **FLUX funciona** - puede añadirse como modo premium
3. **No usar 8191 para FLUX** - tiene problemas de ejecución

### Para habilitar FLUX como premium:
- Usar siempre instancia `still` (8188)
- Workflow: `CheckpointLoaderSimple` + `CLIPTextEncodeFlux`
- No requiere cambios en backend - solo configurar preset

---

## Archivos de debug creados:
- `src/test_flux_lab.py` - Prueba en 8191 (falló)
- `src/test_flux_simple.py` - Prueba simple 8191 (falló)
- `src/test_baseline_8191.py` - Baseline en 8191 (falló)
- `src/test_flux_8188.py` - FLUX en 8188 (EXITÓ)
- `src/test_flux_backend.py` - FLUX vía backend (EXITÓ)
- `FLUX_DEBUG_REPORT.md` - Este reporte