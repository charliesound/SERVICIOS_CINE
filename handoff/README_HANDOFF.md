# README_HANDOFF - Documentacion de Handoff SERVICIOS_CINE

> Estado: documentacion historica de desarrollo.
> Util para contexto de sesiones anteriores, pero no para operar el despliegue actual.
> Para operar el MVP actual usa primero `README.md` y `directivas/MVP_V1_IMPLEMENTATION_REFERENCE.md`.
> Para la documentacion vigente del sistema usa `README_WSL2.md`, `README_TAILSCALE.md` y `docs/DOCUMENTACION_VIGENTE.md`.

## Que es esto?
Coleccion de sesiones de handoff para el proyecto SERVICIOS_CINE.
Cada archivo es un prompt autonomeo para usar con Antigravity o OpenCode.

## Estructura de Archivos

| Archivo | Herramienta | Descripcion |
|---------|-------------|-------------|
| sesion_00_mapa_real_del_repo.md | Referencia | Mapa del repositorio |
| sesion_01_antigravity_arquitectura.md | Antigravity | Diseno arquitectonico |
| sesion_02_antigravity_auditoria_integracion.md | Antigravity | Auditoria proyectos heredados |
| sesion_03_opencode_backend_base_src.md | OpenCode | Verificar backend base |
| sesion_04_opencode_frontend_base_src_frontend.md | OpenCode | Verificar frontend base |
| sesion_05_opencode_multibackend.md | OpenCode | Routing multi-backend |
| sesion_06_opencode_queue_scheduler.md | OpenCode | Cola y scheduler |
| sesion_07_opencode_planes_y_limites.md | OpenCode | Sistema de planes |
| sesion_08_opencode_workflows_v1.md | OpenCode | Workflows base |
| sesion_09_opencode_backend_capabilities.md | OpenCode | Detectar capacidades |
| sesion_10_antigravity_producto_tarifas.md | Antigravity | Producto y pricing |
| sesion_11_antigravity_demo_comercial.md | Antigravity | Diseno demo comercial |
| sesion_12_opencode_demo_mode.md | OpenCode | Modo demo |
| sesion_13_antigravity_deploy_domestico.md | Antigravity | Deploy on-premise |
| sesion_14_opencode_ops_monitoring.md | OpenCode | Monitoreo operativo |
| sesion_99_reglas_entrega.md | Referencia | Reglas de entrega |
| crear_handoff_con_opencode.md | Referencia | Prompt para regenerar |

## Orden de Ejecucion

### Fase 1: Diseno (Antigravity)
1. sesion_01_antigravity_arquitectura.md
2. sesion_02_antigravity_auditoria_integracion.md
3. sesion_10_antigravity_producto_tarifas.md
4. sesion_11_antigravity_demo_comercial.md
5. sesion_13_antigravity_deploy_domestico.md

### Fase 2: Implementacion Backend (OpenCode)
6. sesion_03_opencode_backend_base_src.md
7. sesion_05_opencode_multibackend.md
8. sesion_06_opencode_queue_scheduler.md
9. sesion_07_opencode_planes_y_limites.md
10. sesion_08_opencode_workflows_v1.md
11. sesion_09_opencode_backend_capabilities.md
12. sesion_12_opencode_demo_mode.md
13. sesion_14_opencode_ops_monitoring.md

### Fase 3: Implementacion Frontend (OpenCode)
14. sesion_04_opencode_frontend_base_src_frontend.md

## Carpeta de Trabajo por Sesion

| Sesion | Carpeta Principal |
|--------|-------------------|
| 01-02, 10-11, 13 | D:\SERVICIOS_CINE (general) |
| 03, 05-09, 12, 14 | D:\SERVICIOS_CINE\src |
| 04 | D:\SERVICIOS_CINE\src_frontend |

## Como Usar

### Con OpenCode
1. Copiar contenido del archivo .md
2. Pegar en OpenCode
3. Verificar que la ruta de trabajo es la correcta
4. Ejecutar

### Con Antigravity
1. Copiar contenido del archivo .md
2. Pegar en Antigravity
3. Dejar que generé la respuesta
4. Copiar la respuesta al archivo correspondiente

## Reglas de Uso

1. **No mezclar fases**: Terminar Fase 1 antes de empezar Fase 2
2. **Verificar antes de continuar**: Cada sesion incluye smoke tests
3. **Documentar cambios**: Actualizar sesion_00 si cambia la estructura
4. **Conservar el orden**: Algunas sesiones dependen de anteriores

## Smoke Test Global

```bash
# Backend
cd D:\SERVICIOS_CINE\src
python -m uvicorn app:app --reload --port 8000

# Frontend
cd D:\SERVICIOS_CINE\src_frontend
npm run dev

# Demo
curl -X POST http://localhost:8000/api/demo/quick-start
```

## Verificacion de Entrega

Despues de todas las sesiones:
```bash
# Verificar estructura
Get-ChildItem -Path D:\SERVICIOS_CINE\src -Recurse -Name

# Verificar frontend
Get-ChildItem -Path D:\SERVICIOS_CINE\src_frontend\src -Recurse -Name

# Tests de integracion
curl http://localhost:8000/health
curl http://localhost:8000/api/plans/catalog
curl http://localhost:8000/api/workflows/catalog
curl http://localhost:8000/api/ops/status
```

## Contacto
Para dudas sobre el proyecto, revisar sesion_00 primero.
