# COMPARATIVA CONTROLADA: MOTORES DE STORYBOARD CINEMÁTICO

## FASE 0 — INSPECCIÓN

### baseline actual
- **Workflow**: SD15 standard con `Realistic_Vision_V2.0.safetensors`
- **API**: `CLIPTextEncode` (clip: ["1", 1])
- **Instancia**: port 8188 (still)
- **Resolución**: 1344x768

### FLUX2 (flux1-schnell-fp8)
- **Workflow attempted**: SD15 con clip_name1/clip_name2 → FALLA VALIDACIÓN
- **Workflow corregido**: CLIPTextEncodeFlux → ACEPTADO PERO STUCK
- **API real**: `CLIPTextEncodeFlux` (clip, clip_l, t5xxl, guidance)
- **Problema**: El job queda en queue_running pero no avanza (posiblemente cargando modelo)
- **Instancia**: port 8188 (still)

### FLUX Krea Dev (flux1-dev-fp8)
- Mismo problema que FLUX2

---

## FASE 1 — RESULTADOS EJECUTADOS

### Comandos ejecutados:
```bash
python src/ab_storyboard_comparison.py
```

### Settings finales usados:
| Motor | Checkpoint | Steps | CFG | Sampler | Resolution |
|-------|------------|-------|-----|---------|------------|
| baseline | Realistic_Vision_V2.0.safetensors | 20 | 7.0 | euler | 1344x768 |
| flux2 | FLUX/flux1-schnell-fp8.safetensors | 16 | 1.0 | euler | 1344x768 |
| krea | FLUX/flux1-dev-fp8.safetensors | 16 | 1.0 | euler | 1344x768 |

---

## RESULTADO POR MOTOR

### baseline (Realistic_Vision_V2.0)
- **A1 (cafe establishing)**: TIMEOUT (120s) - no image
- **A2 (cafe interaction)**: SUCCESS - 4.7s
- **B1 (street establishing)**: SUCCESS - 4.1s
- **B2 (street movement)**: SUCCESS - 4.1s

### FLUX2 (flux1-schnell-fp8)
- **A1**: ERROR - No prompt_id (validation failed initially)
- **A2**: ERROR - No prompt_id
- **B1**: ERROR - No prompt_id
- **B2**: ERROR - No prompt_id
- Workflow corregido con CLIPTextEncodeFlux → Aceptado pero job stuck en queue

### Krea (flux1-dev-fp8)
- Mismos errores que FLUX2

---

## JOBS Y MEDIAASSETS CREADOS

```
Project: 899433bc23844989920656545ffa6907

JOBS:
  job-baseline-A1-c56564: failed
  job-baseline-A2-458dd2: completed
  job-baseline-B1-997cd1: completed
  job-baseline-B2-7c58b4: completed
  job-flux2-A1-5eb1a7: failed
  job-flux2-A2-7b7434: failed
  job-flux2-B1-99ed1d: failed
  job-flux2-B2-c10bc9: failed
  job-krea-A1-185367: failed
  job-krea-A2-381f76: failed
  job-krea-B1-e552cb: failed
  job-krea-A2-9a837b: failed

ASSETS (3):
  ab_baseline_seqA_shotinteraction_00001_.png
  ab_baseline_seqB_shotestablishing_00001_.png
  ab_baseline_seqB_shotmovement_00001_.png
```

---

## VEREDICTO FINAL

### BEST FOR MAIN STORYBOARD: **baseline (Realistic_Vision_V2.0)**
- Funciona consistentemente
- Tiempos rápidos (4-5s por imagen)
- 3/4 success en primera ejecución

### BEST FOR PREMIUM LOOK: **DESCARTADO - No funcional**
- FLUX workflow requiere adaptación API específica
- Jobs se quedan stuck (posiblemente carga de modelo muy lenta o fallida)
- No produce imágenes en ambiente actual

### DISCARD / KEEP AS SECONDARY:
- **FLUX2**: DISCARD por ahora - requiere debugging de carga de modelo
- **Krea**: DISCARD por ahora - mismo problema

---

## NOTAS TÉCNICAS

1. **FLUX requiere workflow específico**:
   - No usa `CLIPTextEncode` estándar
   - Usa `CLIPTextEncodeFlux` con inputs: clip, clip_l, t5xxl, guidance
   - El workflow fue aceptado pero el job no avanza (stuck)

2. **Posible causa del stuck**:
   - VRAM disponible: ~20GB en 8188
   - FLUX1-schnell-fp8 requiere ~10-12GB
   - Puede haber conflicto con modelo ya cargado (Realistic Vision ~4GB)

3. **Recomendación**:
   - Mantener Realistic_Vision_V2.0 como motor principal
   - Investigar FLUX en instancia dedicada (sin otros modelos cargados)
   - Considerar port 8191 para FLUX si tiene VRAM disponible