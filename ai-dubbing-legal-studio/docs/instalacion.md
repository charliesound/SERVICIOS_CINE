# Instalación — AI Dubbing Legal Studio

## Requisitos

- Docker y Docker Compose v2
- Python 3.12+
- Node.js 20+
- FFmpeg

## Pasos

### 1. Preparar entorno

```bash
git clone <repo>
cd ai-dubbing-legal-studio
cp .env.example .env
# Editar .env con tus valores
```

### 2. Infraestructura

```bash
docker compose up -d postgres redis minio
```

### 3. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 5. Verificar

```bash
curl http://localhost:8000/health
# {"status":"ok","app":"AI Dubbing Legal Studio","version":"1.0.0"}
```

## Seed data

```bash
# Registrar usuario admin
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123","name":"Admin","role":"admin"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'
```
