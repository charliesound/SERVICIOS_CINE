# SERVICIOS_CINE - Documentacion Maestra

## Que es SERVICIOS_CINE?

SERVICIOS_CINE es una plataforma orquestadora de servicios audiovisuales con IA, diseñada para estudios cinematográficos que necesitan:

- **Generacion de imagenes** con IA (backend still)
- **Creacion de video** con IA (backend video)
- **Doblaje y sintesis de voz** (backend dubbing)
- **Experimentacion** con nuevas tecnicas (backend lab)

## Objetivo del Producto

Reducir costos en pre-produccion cinematografica mediante:
- Prototipado rapido de escenas
- Consistencia de personajes
- Iteracion agil
- Control total sobre el proceso

## Estructura Real del Repositorio

```
D:\SERVICIOS_CINE
|
|-- src                          # BACKEND PRINCIPAL (FastAPI)
|   |-- routes/                  # Endpoints API
|   |-- services/                # Logica de negocio
|   |-- schemas/                 # Modelos Pydantic
|   |-- config/                  # Configuracion YAML
|   |-- tests/                   # Tests
|   |-- app.py                   # Entry point
|   |-- requirements.txt         # Dependencias Python
|
|-- src_frontend                # FRONTEND PRINCIPAL (React+TS+Vite)
|   |-- src/
|       |-- api/                # Servicios API
|       |-- components/          # Componentes React
|       |-- pages/               # Vistas
|       |-- hooks/               # React Query hooks
|       |-- store/               # Zustand stores
|       |-- types/               # TypeScript types
|
|-- CID_SERVER                   # PROYECTO HEREDADO - Auditar
|-- CINE_AI_PLATFORM             # PROYECTO HEREDADO - Auditar
|-- PROYECTO FINAL V1            # PROYECTO HEREDADO - Auditar
|-- Web Ailink_Cinema            # FRONTEND HEREDADO - Auditar
|
|-- handoff/                     # SESIONES PARA Antigravity/OpenCode
|-- docs/                        # DOCUMENTACION MAESTRA
```

## Papel de Cada Carpeta

| Carpeta | Rol | Estado |
|---------|-----|--------|
| src | Backend principal | En desarrollo |
| src_frontend | Frontend principal | En desarrollo |
| CID_SERVER | Fuente/Integracion | Por auditar |
| CINE_AI_PLATFORM | Fuente/Integracion | Por auditar |
| PROYECTO FINAL V1 | Fuente/Integracion | Por auditar |
| Web Ailink_Cinema | Frontend heredado | Por auditar |
| handoff | Sesiones de desarrollo | Activo |
| docs | Documentacion | Activo |

## Vision Tecnica

### Backend (src)
- Framework: FastAPI
- Puertos de backends ComfyUI:
  - still: 8188
  - video: 8189
  - dubbing: 8190
  - lab: 8191
- Puerto API: 8000
- Puerto Frontend: 3000

### Frontend (src_frontend)
- Framework: React 18 + TypeScript
- Build: Vite
- Estado: Zustand
- API calls: Axios + React Query
- Estilos: Tailwind CSS

## Vision Comercial

### Planes
| Plan | Precio | Jobs Activos | Jobs Cola | Servicios |
|------|--------|-------------|-----------|-----------|
| Free | $0 | 1 | 2 | still |
| Creator | $9.99 | 2 | 5 | still, dubbing |
| Studio | $29.99 | 3 | 10 | still, video, dubbing |
| Enterprise | $99.99 | 5 | 20 | all |

## Como Empezar

- Despliegue en WSL2: `README_WSL2.md`
- Acceso por Tailscale: `README_TAILSCALE.md`
- Documentacion vigente: `docs/DOCUMENTACION_VIGENTE.md`

### 1. Backend
```bash
cd /opt/SERVICIOS_CINE/src
pip install -r requirements.txt
python -m uvicorn app:app --reload --port 8000
```

### 2. Frontend
```bash
cd /opt/SERVICIOS_CINE/src_frontend
npm install
npm run dev
```

### 3. Inicializar Demo
```bash
curl -X POST http://localhost:8000/api/demo/quick-start
```

## Orden Recomendado para Trabajar

1. Leer este README
2. Revisar MAPA_DEL_SISTEMA.md
3. Consultar ROADMAP.md para contexto
4. Usar sesiones en handoff/ para desarrollo

## Referencias

- Documentacion: `docs/`
- Sesiones de desarrollo: `handoff/`
- API Docs: http://localhost:8000/docs
- Frontend dev: http://localhost:3000
- Frontend principal docker: http://localhost
- WSL2: `README_WSL2.md`
