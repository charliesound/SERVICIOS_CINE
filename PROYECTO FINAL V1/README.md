# Integración local: CID + CINE_AI_PLATFORM + ComfyUI

> Estado: propuesta/integracion legacy.
> Este material se conserva como referencia historica y no describe el stack operativo actual de `SERVICIOS_CINE`.
> Para despliegue vigente usa `README_WSL2.md`, `DOCKER.md` y `docs/DOCUMENTACION_VIGENTE.md`.
> Los archivos runtime locales de esta carpeta como `.env`, `env/` y `*.zip` no forman parte del versionado operativo.

Este paquete prepara una **primera prueba real** en un solo PC, con separación clara de servicios.

## Arquitectura

- **Caddy**: reverse proxy y punto único de entrada
- **CID**: CRM / campañas / leads / follow-ups
- **CINE_AI_PLATFORM**: API para extracción, planificación y storyboard
- **ComfyUI**: motor de generación de imágenes (corriendo fuera de este compose o como servicio aparte)

## URLs sugeridas en LAN
- CID: `http://tu-ip:8080`
- CINE API: `http://tu-ip:8080/api/cine/*`
- Health CID: `http://tu-ip:8080/api/health`
- Health CINE: `http://tu-ip:8080/api/cine/health`

## Estructura esperada en tu ordenador

```text
D:\SERVICIOS_CINE\
  ├─ PROYECTO FINAL V1\
  │   ├─ docker-compose.yml
  │   ├─ Dockerfile.cine          <- build para CINE_AI_PLATFORM API
  │   ├─ Dockerfile.cid           <- build para Next.js CID app
  │   ├─ Caddyfile                <- reverse proxy
  │   ├─ .env                     <- vars para compose (Supabase, etc.)
  │   └─ env\
  │       ├─ cid.env              <- vars runtime CID
  │       └─ cine.env             <- vars runtime CINE_AI_PLATFORM
  ├─ Web Ailink_Cinema\           <- Next.js app (con Dockerfile)
  ├─ CINE_AI_PLATFORM\            <- Python API (con Dockerfile.cine)
  ├─ CID_SERVER\automation-engine\ <- Python FastAPI (con Dockerfile)
  └─ COMFYUI\                    <- tu instalación actual
```

## Flujo recomendado de primera prueba

1. Levantar `cid-web` y `cine-api` con Docker.
2. Mantener ComfyUI corriendo en tu entorno actual en el puerto `8188`.
3. Verificar health checks.
4. Entrar en CID con tu usuario admin.
5. Crear / sembrar cuentas demo.
6. Probar caso comercial:
   - alta de lead demo
   - aplicar campaña
   - procesar cola
7. Probar caso de producción:
   - meter fragmento de guion en CINE_AI_PLATFORM
   - extraer / planificar / renderizar storyboard
8. Enseñar ambos como sistema conectado.

## Importante

Para esta primera prueba:
- deja el **admin privado**
- usa acceso local o Tailscale
- no abras todavía el panel admin al público

## Siguiente ajuste que tendrás que hacer

En el repo CID añade una variable para apuntar al backend de CINE_AI_PLATFORM, por ejemplo:

- `CINE_PLATFORM_BASE_URL=http://cine-api:3000`

Y en la UI o en tus procesos internos puedes enlazar ambos mundos:
- CID gestiona cliente y seguimiento
- CINE_AI_PLATFORM genera storyboard e imágenes
