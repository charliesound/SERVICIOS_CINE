# Roadmap SERVICIOS_CINE (DEPRECATED)
> [!CAUTION]
> This document is **DEPRECATED**. It does not reflect the current SEED/FLOW/IMPACT architecture.
> Please refer to: [MASTER_TECHNICAL_ROADMAP.md](file:///wsl.localhost/Ubuntu/opt/SERVICIOS_CINE/docs/MASTER_TECHNICAL_ROADMAP.md) for the official development path.


## Fase 0: Auditoria e Integracion

**Objetivo:** Identificar valor en proyectos heredados.

**Entregables:**
- Matriz de integracion CID_SERVER, CINE_AI_PLATFORM, PROYECTO FINAL V1, Web Ailink_Cinema
- Lista de componentes a reutilizar
- Lista de componentes a descartar

**Riesgos:**
- Codigo heredado desactualizado
- Dependencias faltantes
- Licencias no compatibles

**Criterio de Validacion:**
- Matriz completa con prioridades
- Proof-of-concept de integracion de al menos 1 componente

---

## Fase 1: Backend Base y Frontend Base

**Objetivo:** Verificar que src y src_frontend funcionan de forma independiente.

**Entregables:**
- [x] Backend levanta en puerto 8000
- [x] Frontend levanta en puerto 3000
- [x] API docs disponible en /docs
- [x] Login basico funciona
- [x] Health check funciona

**Riesgos:**
- Dependencias faltantes en Windows
- Conflictos de puertos

**Criterio de Validacion:**
```bash
curl http://localhost:8000/health  # {"status": "healthy"}
curl http://localhost:3000        # Frontend carga
```

---

## Fase 2: Multi-Backend

**Objetivo:** Implementar routing a backends ComfyUI.

**Entregables:**
- [x] instance_registry.py con 4 backends
- [x] comfyui_client_factory.py
- [x] job_router.py con logica de seleccion
- [x] Configuracion en instances.yml

**Riesgos:**
- Backends ComfyUI no levantan
- Latencia alta entre backends

**Criterio de Validacion:**
```bash
curl -X POST http://localhost:8000/api/render/jobs \
  -d '{"task_type":"still",...}'  # Devuelve backend=still
```

---

## Fase 3: Cola y Concurrencia

**Objetivo:** Controlar carga en servidor domestico.

**Entregables:**
- [x] queue_service.py (en memoria)
- [x] job_scheduler.py (asyncio loop)
- [x] Reglas de concurrencia por backend
- [x] Estados: queued, running, succeeded, failed, timeout

**Riesgos:**
- Scheduler consume muchos recursos
- Jobs se quedan en running para siempre

**Criterio de Validacion:**
```bash
curl http://localhost:8000/api/queue/status
# Muestra jobs por backend con saturacion
```

---

## Fase 4: Planes y Prioridades

**Objetivo:** Limitar usuarios free y reservar capacidad para premium.

**Entregables:**
- [x] plans.yml con 4 planes
- [x] plan_limits_service.py
- [x] UserPlanTracker para limites activos
- [x] Ordenamiento por priority_score DESC

**Riesgos:**
- Contadores se desincronizan
- Plan no se valida en todas las rutas

**Criterio de Validacion:**
```bash
curl http://localhost:8000/api/plans/free/can-run/video  # false
curl http://localhost:8000/api/plans/studio/can-run/video  # true
```

---

## Fase 5: Workflows Automaticos V1

**Objetivo:** Permitir creacion de workflows desde intenciones.

**Entregables:**
- [x] workflow_registry.py (15 templates)
- [x] workflow_planner.py (analisis de intencion)
- [x] workflow_builder.py (construccion JSON)
- [x] workflow_validator.py (validacion)
- [x] workflow_preset_service.py (presets de usuario)

**Riesgos:**
- Intenciones no se clasifican bien
- Workflows no son compatibles con todos los backends

**Criterio de Validacion:**
```bash
curl -X POST http://localhost:8000/api/workflows/plan \
  -d '{"intent":"robot en atardecer"}'
# Devuelve task_type=still, workflow=still_text_to_image_pro
```

---

## Fase 6: Deteccion de Capacidades

**Objetivo:** Detectar que puede hacer cada backend en tiempo real.

**Entregables:**
- [x] backend_capability_service.py
- [x] Deteccion de nodos disponibles
- [x] Deteccion de modelos cargados
- [x] Inferencia de capacidades

**Riesgos:**
- Backends no responden al health check
- Deteccion lenta

**Criterio de Validacion:**
```bash
curl http://localhost:8000/api/ops/capabilities/still
# Devuelve nodes_count, models_count, detected_capabilities
```

---

## Fase 7: Demo Comercial

**Objetivo:** Permitir mostrar el producto sin preparacion.

**Entregables:**
- [x] demo_service.py
- [x] demo_routes.py
- [x] 5 usuarios demo preconfigurados
- [x] Presets demo
- [x] Jobs demo simulados

**Riesgos:**
- Demo no se reinicia correctamente
- Datos demo persisten en produccion

**Criterio de Validacion:**
```bash
curl -X POST http://localhost:8000/api/demo/quick-start
# Crea usuarios demo, devuelve credenciales
```

---

## Fase 8: Despliegue Domestico

**Objetivo:** Servicio estable en servidor propio.

**Entregables:**
- [ ] Docker compose para todos los servicios
- [ ] Health checks configurados
- [ ] Logs centralizados
- [ ] Backup de configuracion
- [ ] Guia de instalacion

**Riesgos:**
- HW insuficiente (sin GPU dedicada)
- Problemas de red/seguridad
- Overheating

**Criterio de Validacion:**
- docker-compose up levanta todo
- Frontend accesible desde red local
- Backends ComfyUI responden

---

## Fase 9: Escalado Futuro

**Objetivo:** Preparar arquitectura para mas usuarios.

**Consideraciones:**
- Redis para cola persistente
- PostgreSQL para datos
- CDN para assets
- Kubernetes para orquestacion
- Metrics con Prometheus/Grafana

**No priorizado para V1.**

---

## Resumen de Progreso

| Fase | Estado | Entregables |
|------|--------|-------------|
| 0. Auditoria | PENDIENTE | Matriz de integracion |
| 1. Base | COMPLETO | Backend + Frontend funcionando |
| 2. Multi-backend | COMPLETO | Routing a 8188-8191 |
| 3. Cola | COMPLETO | Queue + Scheduler |
| 4. Planes | COMPLETO | 4 planes + limites |
| 5. Workflows | COMPLETO | 15 templates + planner |
| 6. Capabilities | COMPLETO | Deteccion de capacidades |
| 7. Demo | COMPLETO | Usuarios demo |
| 8. Deploy | PENDIENTE | Docker + guia |
| 9. Escalado | BACKLOG | Redis, K8s, etc |

## Proxima Accion

Continuar con Fase 8 (Despliegue Domestico) o回过头审计 proyectos heredados (Fase 0).
