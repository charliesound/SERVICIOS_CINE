# SESION 13: Antigravity - Deploy Domestico

## Rol
Senior DevOps Engineer

## Contexto
Disenar el despliegue en servidor domestico para SERVICIOS_CINE.

## Restricciones del Entorno
- Hardware domestico (no datacenter)
- Conexion domestica
- Un solo servidor (idealmente)
- multiplexting de GPUs si hay varias
- Control de ruido/calor

## Componentes a Desplegar

### Backend (src)
- FastAPI en puerto 8000
- 4 instancias ComfyUI (8188-8191)
- Redis (opcional para V1)
- SQLite (para V1)

### Frontend (src_frontend)
- Build de produccion
- Nginx o serve estatico
- Puerto 3000 o 80

## Arquitectura Propuesta

```
                    Internet
                       |
                    [Nginx]
                    :80/:443
                       |
        +-------------+-------------+
        |             |             |
    [Frontend]   [Backend]    [ComfyUI]
     :3000         :8000        8188-8191
                                    |
                                 [GPU(s)]
```

## Requisitos Minimos
- CPU: 8 cores
- RAM: 32GB
- GPU: RTX 3080+ o equivalente
- Storage: 500GB SSD
- OS: Ubuntu 22.04 LTS

##/docker-compose.yml Propuesto
```yaml
version: '3.8'
services:
  backend:
    build: ./src
    ports:
      - "8000:8000"
    depends_on:
      - redis
    volumes:
      - ./data:/app/data

  frontend:
    build: ./src_frontend
    ports:
      - "3000:80"

  comfyui_still:
    image: comfyanonymous/comfyui
    ports:
      - "8188:8188"
    volumes:
      - ./models:/models

  comfyui_video:
    image: comfyanonymous/comfyui
    ports:
      - "8189:8189"
    volumes:
      - ./models:/models

  # ... dubbing y lab

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

## Monitoreo
- Health checks en cada componente
- Logs centralizados
- Alertas por email para errores

## Backup
- DB backups diarios
- Modelos en storage externo
- Config en git
