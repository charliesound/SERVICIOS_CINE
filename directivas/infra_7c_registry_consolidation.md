## Objetivo

Consolidar el uso de registro de instancias ComfyUI en una sola fuente de verdad (`instance_registry` + `instances.yml`) sin romper compatibilidad del API legado `/api/v1/comfyui/*`.

## Contexto

Existian dos rutas de configuracion/registro en paralelo:

- Unificada: `src/services/instance_registry.py` + `src/config/instances.yml`.
- Legada: `src/services/comfyui_instance_registry_service.py` + `src/config/comfyui_instances.yml`.

La ruta legada mantenia endpoints publicos y tests propios, generando riesgo de desalineacion operativa y de routing por task type.

## Archivos afectados

- `src/routes/comfyui_instance_routes.py`
- `tests/unit/test_comfyui_instance_routes.py`

## Entradas

- Config unificada de backends en `src/config/instances.yml`.
- Reglas de routing `routing_rules.task_type_mapping`.

## Salidas

- Endpoints `/api/v1/comfyui/*` resueltos contra `instance_registry`.
- Compatibilidad de claves legadas en payload/path (`image`, `video_cine`, `dubbing_audio`, `three_d`).
- Compatibilidad de aliases de task type legado (`i2v`, `t2v`, `lipsync`, `upscale`, `mesh`, `scene`).

## Flujo de trabajo

1. Cargar configuracion con `registry.load_config()`.
2. Traducir `instance_key` legado -> backend key unificada.
3. Resolver datos/health en `instance_registry`.
4. Traducir backend key unificada -> key legada para respuesta del API legado.
5. Normalizar task type legado -> task type canonic de `instances.yml` antes de resolver.

## Validaciones

- `python -m py_compile src/routes/comfyui_instance_routes.py tests/unit/test_comfyui_instance_routes.py`
- `python -m pytest tests/unit/test_comfyui_instance_routes.py -q`

## Casos borde

- `task_type` desconocido en API legado debe mantener `404`.
- Backend definido pero no saludable: health devuelve `healthy=false` sin excepcion.
- Alias de instancia no mapeado: fallback a key original para no bloquear extensiones futuras.

## Restricciones conocidas

- El API legado conserva formato historico y alias, aunque internamente use la capa unificada.
- Mientras existan tests/consumidores legados, no eliminar `comfyui_instance_registry_service.py`.

## Errores aprendidos

- Permitir fallback implicito para task type desconocido (regla global) en API legado rompe contrato historico de `404`.
- Mantener dos esquemas de configuracion en runtime aumenta drift operativo.

## Comandos seguros

- `git status --short`
- `python -m py_compile src/routes/comfyui_instance_routes.py tests/unit/test_comfyui_instance_routes.py`
- `python -m pytest tests/unit/test_comfyui_instance_routes.py -q`
