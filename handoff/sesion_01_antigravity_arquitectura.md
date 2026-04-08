PROYECTO: SERVICIOS_CINE
RUTA RAÍZ DEL REPO: SERVICIOS_CINE
ROL: Principal systems architect

OBJETIVO
Diseñar la arquitectura final del producto SERVICIOS_CINE sin romper los componentes ya construidos previamente.

CONTEXTO
SERVICIOS_CINE será la plataforma principal donde se integrarán varias piezas:
- web comercial / captación de leads
- backend con autenticación y jobs
- integración con motores IA audiovisuales
- generación de imágenes fijas
- generación de vídeo
- doblaje / audio / TTS / voice clone
- workflows automáticos tipo planner/builder/validator
- colas, prioridades y planes comerciales
- panel admin
- demo comercial para productoras

BACKENDS REALES DISPONIBLES
- still images -> http://127.0.0.1:8188
- video -> http://127.0.0.1:8189
- dubbing/audio -> http://127.0.0.1:8190
- lab/experimental -> http://127.0.0.1:8191

OBJETIVO DEL PRODUCTO
SERVICIOS_CINE no debe ser solo una web que llama a ComfyUI.
Debe convertirse en:
- una plataforma de servicios audiovisuales con IA
- un orquestador multi-backend
- un sistema de workflows reutilizables
- una base comercial escalable por planes
- una demo vendible para productoras, creadores y estudios

OBJETIVOS TÉCNICOS
1. Unificar frontend y backend bajo SERVICIOS_CINE
2. Implementar orquestación multi-backend
3. Añadir colas y límites de concurrencia
4. Añadir planes comerciales y prioridades
5. Integrar auto-creación de workflows
6. Preparar estructura para despliegue doméstico y escalado futuro
7. Mantener compatibilidad incremental con lo ya construido anteriormente

NECESITO
1. arquitectura objetivo
2. módulos principales
3. árbol recomendado de carpetas
4. plan por fases
5. riesgos técnicos
6. estrategia de integración sin rehacer desde cero

IMPORTANTE
No quiero teoría genérica. Quiero una propuesta concreta para SERVICIOS_CINE.
Si detectas que conviene usar una estructura tipo:
- apps/api
- apps/web
- deploy
- handoff
- docs
indícalo explícitamente.
