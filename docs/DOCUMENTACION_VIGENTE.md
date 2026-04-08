# DOCUMENTACION VIGENTE

Este indice separa la documentacion operativa actual de la documentacion historica del repositorio.

## Documentacion vigente

- `README.md` -> vision general y accesos principales
- `README_WSL2.md` -> despliegue actual en Ubuntu/WSL2 con Docker
- `README_TAILSCALE.md` -> acceso remoto por Tailscale
- `DOCKER.md` -> stack Docker actual
- `docs/README_MASTER.md` -> mapa general del repositorio
- `docs/MAPA_DEL_SISTEMA.md` -> arquitectura funcional

## Documentacion historica o de contexto

Estas carpetas contienen material util como referencia, pero no deben usarse como fuente principal para operar el stack actual:

- `handoff/` -> sesiones historicas de desarrollo
- `scripts/README.md` -> flujo antiguo centrado en Windows y scripts manuales
- `docs/ARRANQUE_EN_SERVIDOR.md` -> arranque manual antiguo
- `docs/GUIA_DESPLIEGUE_SERVIDOR.md` -> despliegue antiguo en Windows/disco local
- `PROYECTO FINAL V1/` -> propuesta/integracion legacy
- `Web Ailink_Cinema/` -> frontend heredado

## Ruta recomendada de lectura

1. `README.md`
2. `README_WSL2.md`
3. `README_TAILSCALE.md`
4. `DOCKER.md`
5. `docs/MAPA_DEL_SISTEMA.md`

## Regla practica

Si un documento menciona rutas como `D:\SERVICIOS_CINE`, despliegues manuales en Windows, o puertos distintos de las rutas unificadas por Caddy, tratalo como historico salvo que se indique lo contrario.
