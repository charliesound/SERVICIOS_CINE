# AILinkCinema - Plataforma de Servicios Cinematográficos con IA

## 🚀 Inicio Rápido

### Opción 1: Deploy Completo (Primero uso)
```batch
deploy.bat
```

### Opción 2: Inicio Rápido (Si ya tienes dependencias)
```batch
iniciar.bat
```

---

## 📋 Requisitos

| Software | Versión | Enlace |
|----------|---------|--------|
| Python | 3.10+ | [python.org](https://python.org) |
| Node.js | 18+ | [nodejs.org](https://nodejs.org) |
| Git | - | [git-scm.com](https://git-scm.com) |

---

## 🖥️ Acceso

| Entorno | URL |
|---------|-----|
| Local | http://localhost |
| Tailscale IP | http://100.104.219.15 |
| Dominio personalizado | http://ailinkcinema |

**Nota**: Para dominio personalizado, agregar al archivo `hosts`:
```
100.104.219.15    ailinkcinema
```

---

## 👤 Credenciales Demo

| Rol | Email | Contraseña |
|-----|-------|------------|
| Admin | admin@servicios-cine.com | admin123 |
| Free | demo_free@servicios-cine.com | demo123 |
| Studio | demo_studio@servicios-cine.com | demo123 |

---

## 🔧 Scripts Disponibles

| Script | Función |
|--------|---------|
| `deploy.bat` | Instala todo y prepara el proyecto |
| `iniciar.bat` | Inicia backend y frontend |
| `start_backend.bat` | Solo backend |
| `start_frontend.bat` | Solo frontend |
| `health_check.ps1` | Verifica estado de servicios |
| `backup.ps1` | Realiza backup |
| `restart.ps1` | Reinicia servicios |
| `preflight_check.ps1` | Verifica pre-requisitos |

---

## 🐳 Docker (Opcional)

```batch
docker-compose up -d
```

### Servicios principales

| Servicio | URL local | URL Tailscale |
|----------|-----------|---------------|
| App principal | http://localhost | http://100.104.219.15 |
| Backend API | http://localhost:8000 | http://100.104.219.15:8000 |
| API Docs | http://localhost:8000/docs | http://100.104.219.15:8000/docs |
| CINE Web | http://localhost/cine/ | http://100.104.219.15/cine/ |
| CINE API | http://localhost/cine/api/ | http://100.104.219.15/cine/api/ |
| Automation Engine | http://localhost/automation/health | http://100.104.219.15/automation/health |
| n8n | http://localhost/n8n/ | http://100.104.219.15/n8n/ |
| Qdrant | http://localhost/qdrant/collections | http://100.104.219.15/qdrant/collections |

### HTTP y HTTPS

- Usa `http://` como opcion recomendada para el uso diario en red local y Tailscale.
- `https://` tambien funciona por Caddy, pero usa certificado autofirmado y el navegador puede mostrar advertencias.
- Si el navegador te fuerza a HTTPS, acepta la excepcion del certificado o vuelve a entrar con `http://`.

---

## 🌐 ComfyUI Backends

Para funcionalidad completa, iniciar 4 instancias ComfyUI:

| Backend | Puerto | Función |
|---------|--------|---------|
| still | 8188 | Generación de imágenes |
| video | 8189 | Generación de video |
| dubbing | 8190 | Doblaje y voz |
| lab | 8191 | Experimental |

---

## 📁 Estructura del Proyecto

```
SERVICIOS_CINE/
├── src/                    # Backend (FastAPI)
│   ├── routes/             # Endpoints API
│   ├── services/            # Lógica de negocio
│   ├── schemas/            # Modelos de datos
│   └── config/             # Configuración YAML
├── src_frontend/           # Frontend (React+Vite)
├── docs/                   # Documentación
├── scripts/                # Scripts auxiliares
├── Caddyfile               # Configuración proxy
├── docker-compose.yml      # Contenedores
└── *.bat / *.ps1          # Scripts de utilidad
```

---

## 📖 Documentación

- [Guía de Despliegue](docs/GUIA_DESPLIEGUE_SERVIDOR.md)
- [Mapa del Sistema](docs/MAPA_DEL_SISTEMA.md)
- [Acceso Tailscale](README_TAILSCALE.md)
- [Guía WSL2](README_WSL2.md)
- [Documentación Vigente](docs/DOCUMENTACION_VIGENTE.md)

---

## 🔧 Desarrollo

### Backend
```bash
cd src
pip install -r requirements.txt
python -m uvicorn app:app --reload --port 8000
```

### Frontend
```bash
cd src_frontend
npm install
npm run dev
```

### API Docs
```
http://localhost:8000/docs
```

### CINE Platform
```
http://localhost/cine/
```

### n8n
```
http://localhost/n8n/
```

---

## 📊 Endpoints Principales

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/auth/register` | POST | Registrar usuario |
| `/api/auth/login` | POST | Iniciar sesión |
| `/api/render/jobs` | POST | Crear job |
| `/api/render/jobs/{id}` | GET | Ver job |
| `/api/queue/status` | GET | Estado de cola |
| `/api/workflows/catalog` | GET | Catálogo workflows |
| `/api/metrics` | GET | Métricas del sistema |
| `/health` | GET | Health check |

---

## ⚙️ Configuración

Editar `src/config/config.yaml` para:
- Modo producción/desarrollo
- CORS orígenes permitidos
- Configuración de queue
- Features habilitadas

---

## 🔒 Seguridad

- Rate limiting implementado (100 req/min)
- Logging de requests
- Métricas de sistema
- JWT para autenticación

---

## 📝 Licencia

Privado - AILinkCinema 2024
