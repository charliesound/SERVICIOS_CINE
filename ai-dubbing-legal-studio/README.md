# AI Dubbing Legal Studio

Aplicación SaaS/local para gestionar doblaje con IA, doblaje humano asistido, clonación autorizada de voz, traducción, lipsync, mezcla, trazabilidad legal y control de contratos.

## Stack

- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Frontend**: React + TypeScript + Tailwind CSS
- **Cola**: Redis
- **Storage**: MinIO (S3-compatible)
- **Vector store**: Qdrant (opcional)
- **Procesamiento**: FFmpeg, Whisper, workers Python

## Requisitos

- Docker & Docker Compose
- Python 3.12+
- Node.js 20+
- FFmpeg (para workers)

## Inicio rápido

### 1. Clonar y entrar

```bash
cd ai-dubbing-legal-studio
```

### 2. Copiar entorno

```bash
cp .env.example .env
```

### 3. Levantar infraestructura

```bash
docker compose up -d postgres redis minio
```

### 4. Instalar backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 5. Iniciar backend

```bash
uvicorn app.main:app --reload --port 8000
```

### 6. Instalar frontend

```bash
cd frontend
npm install
npm run dev
```

### 7. Abrir

- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs
- MinIO Console: http://localhost:9001

## Estructura del proyecto

```
ai-dubbing-legal-studio/
├── backend/
│   ├── app/
│   │   ├── main.py              # Entry point FastAPI
│   │   ├── core/                # Config, seguridad, DB
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── api/                 # Routes: auth, projects, contracts, dubbing, audit
│   │   ├── services/            # Lógica de negocio
│   │   ├── workers/             # Procesamiento async
│   │   └── providers/           # Interfaces TTS, LipSync
│   ├── alembic/                 # Migraciones
│   ├── tests/
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/                 # Cliente Axios
│   │   ├── pages/               # Login, Dashboard, Proyectos, Contratos, Jobs, Auditoría
│   │   ├── components/          # Layout, UI components
│   │   ├── stores/              # Zustand store
│   │   └── types/               # TypeScript interfaces
│   └── Dockerfile
├── infra/
│   ├── nginx/                   # Config proxy producción
│   └── scripts/                 # deploy.sh, backup.sh, restore.sh
├── docs/
│   ├── arquitectura.md
│   ├── instalacion.md
│   ├── produccion.md
│   ├── legal.md
│   └── prompts/                 # Prompts para Antigravity/OpenCode
├── docker-compose.yml           # Desarrollo
├── docker-compose.prod.yml      # Producción
├── .env.example                 # Variables de entorno
└── README.md
```

## API Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | /api/auth/register | Registrar usuario |
| POST | /api/auth/login | Iniciar sesión |
| GET | /api/auth/me | Perfil actual |
| POST | /api/projects | Crear proyecto |
| GET | /api/projects | Listar proyectos |
| GET | /api/projects/{id} | Detalle proyecto |
| POST | /api/contracts | Crear contrato |
| GET | /api/contracts | Listar contratos |
| GET | /api/contracts/{id} | Detalle contrato |
| PATCH | /api/contracts/{id} | Actualizar contrato |
| POST | /api/contracts/{id}/validate | Validar contrato |
| POST | /api/actors | Crear actor |
| GET | /api/actors | Listar actores |
| POST | /api/dubbing-jobs/project/{id} | Crear job |
| GET | /api/dubbing-jobs/project/{id} | Listar jobs |
| GET | /api/dubbing-jobs/{id} | Detalle job |
| POST | /api/dubbing-jobs/{id}/start | Iniciar job |
| POST | /api/dubbing-jobs/{id}/approve | Aprobar job |
| POST | /api/dubbing-jobs/{id}/reject | Rechazar job |
| GET | /api/dubbing-jobs/{id}/export | Exportar job |
| GET | /api/audit/project/{id} | Auditoría proyecto |
| GET | /api/audit/job/{id} | Auditoría job |

## Roles

- **admin**: Administración completa
- **productor**: Gestiona proyectos y jobs
- **supervisor_legal**: Valida contratos y auditoría
- **tecnico_audio**: Opera workers de procesamiento
- **traductor**: Revisa traducciones
- **actor**: Visualiza contratos propios
- **cliente_viewer**: Solo lectura de proyectos

## Flujo de doblaje

1. Crear proyecto
2. Subir vídeo/audio
3. Seleccionar modo (humano asistido / IA autorizada)
4. Validar contrato (si modo IA)
5. Pipeline automático: transcribir → traducir → generar voz → lipsync → mezclar
6. Revisar y aprobar
7. Exportar entregables (vídeo, audio WAV, stems, subtítulos, informe legal PDF)

## Licencia

Uso interno / demostración comercial. AILinkCinema.
