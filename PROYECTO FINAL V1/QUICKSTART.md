# Quickstart - CID + CINE_AI_PLATFORM Integrado

## Requisitos previos

- **Docker Desktop** instalado y corriendo
- **ComfyUI** corriendo en `http://127.0.0.1:8188` (opcional, para renders)
- **Proyecto Supabase** creado en https://supabase.com

---

## Paso 1: Configurar credenciales Supabase

### 1.1 Obtener credenciales

1. Ve a https://supabase.com y crea un proyecto
2. Ve a **Project Settings > API**
3. Copia:
   - **Project URL** → `NEXT_PUBLIC_SUPABASE_URL`
   - **anon public** key → `NEXT_PUBLIC_SUPABASE_ANON_KEY`
   - **service_role** secret → `SUPABASE_SERVICE_ROLE_KEY`

### 1.2 Editar archivos .env

**`PROYECTO FINAL V1/.env`:**
```
NEXT_PUBLIC_SUPABASE_URL=https://tu-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
CINEMA_API_URL=http://localhost:8080/api/cine
AUTOMATION_ENGINE_URL=http://automation-engine:8000
```

**`PROYECTO FINAL V1/env/cid.env`:**
```
NEXT_PUBLIC_SUPABASE_URL=https://tu-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGci...
```

---

## Paso 2: Ejecutar setup

### Windows (PowerShell)
```powershell
cd "D:\SERVICIOS_CINE\PROYECTO FINAL V1"
.\setup.ps1
```

### Linux / Mac
```bash
chmod +x setup.sh
./setup.sh
```

### Manual
```bash
cd "D:\SERVICIOS_CINE\PROYECTO FINAL V1"
docker compose up -d --build
docker compose logs -f
```

---

## Paso 3: Verificar que todo funciona

| Servicio | URL | Esperado |
|---|---|---|
| CID Web App | http://localhost:8080 | Página de login |
| CINE API | http://localhost:8080/api/cine/health | `{"status":"ok"...}` |
| Automation Engine | http://localhost:8000/health | `{"status":"ok"...}` |

---

## URLs de acceso

```
CID App (Next.js):     http://localhost:8080
CINE API (FastAPI):    http://localhost:8080/api/cine
CINE API directa:      http://localhost:3000  (solo si mapeado)
Automation Engine:     http://localhost:8000
ComfyUI (render):     http://127.0.0.1:8188
```

---

## Credenciales de prueba

### CINE_AI_PLATFORM (propio auth SQLite)
```
admin@cine.local / CHANGE_ME     (admin)
editor@cine.local / editor1234   (editor)
viewer@cine.local / viewer1234    (viewer)
```

### Supabase Auth (usuarios reales)
```
Crea tu cuenta desde /registro en la app CID
```

---

## Comandos frecuentes

```bash
# Ver todos los logs
docker compose logs -f

# Ver logs de un servicio especifico
docker compose logs -f cid-web
docker compose logs -f cine-api
docker compose logs -f automation-engine

# Reiniciar un servicio
docker compose restart automation-engine

# Detener todo
docker compose down

# Reconstruir y reiniciar
docker compose down && docker compose up -d --build

# Ver estado de contenedores
docker compose ps

# Acceder a un contenedor
docker exec -it cid-web /bin/sh
docker exec -it cine-api /bin/bash
```

---

## Estructura del compose

```
Caddy (:8080)
  /api/cine/*   -->  cine-api:3000   (CINE_AI_PLATFORM)
  /*            -->  cid-web:3000    (Next.js CID App)

automation-engine:8000
  - Clasifica leads y rutea eventos
  - Conexion a CID, CINE_AI_PLATFORM, Web

ComfyUI (host:8188)
  - Generacion de imagenes
  - Accesible desde cine-api via host.docker.internal
```

---

## Configurar ComfyUI

Si ComfyUI esta en Docker (alternativa a ejecutarlo en el host):

Agregar al `docker-compose.yml`:

```yaml
  comfyui:
    image: ghcr.io/comfyanonymous/comfyui:latest
    container_name: comfyui
    restart: unless-stopped
    ports:
      - "8188:8188"
    volumes:
      - comfyui_models:/root/comfyui/models
    extra_hosts:
      - "host.docker.internal:host-gateway"

volumes:
  comfyui_models:
```

Y cambiar en `env/cine.env`:
```
COMFYUI_BASE_URL=http://comfyui:8188
```

---

## Solucion de problemas

### "CID Web no carga"
```bash
docker compose logs cid-web
docker exec -it cid-web ls -la
```

### "CINE API devuelve 500"
```bash
docker compose logs cine-api
docker exec -it cine-api python -c "from src.app import app; print('OK')"
```

### "Automation Engine no conecta a CID"
Verifica que `DRY_RUN=true` en `CID_SERVER/automation-engine/.env`.
El engine solo hace logging cuando `DRY_RUN=true` (modo desarrollo).

### "ComfyUI timeout"
```bash
# Verificar que ComfyUI corre
curl http://127.0.0.1:8188/system_stats

# Aumentar timeout en env/cine.env
COMFYUI_TIMEOUT_SECONDS=30
```

### "Next.js build falla"
```bash
cd "D:\SERVICIOS_CINE\Web Ailink_Cinema"
npm install
npm run build
```
