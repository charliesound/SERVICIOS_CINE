# SERVICIOS_CINE Demo Mode

## Quick Start

### 1. Start Backend
```bash
cd src
pip install -r requirements.txt
python -m uvicorn app:app --reload --port 8000
```

### 2. Initialize Demo
```bash
# Windows
.\demo_init.bat

# Linux/Mac
chmod +x demo_init.sh
./demo_init.sh

# Or manually:
curl -X POST http://localhost:8000/api/demo/quick-start
```

### 3. Access Frontend
```bash
cd src_frontend
npm install
npm run dev
```

Open http://localhost:3000 and login with demo credentials.

## Demo Users

| Plan | Email | Password |
|------|-------|----------|
| Free | demo_free@servicios-cine.com | demo123 |
| Creator | demo_creator@servicios-cine.com | demo123 |
| Studio | demo_studio@servicios-cine.com | demo123 |
| Enterprise | demo_enterprise@servicios-cine.com | demo123 |
| Admin | admin@servicios-cine.com | admin123 |

## Demo API Endpoints

### Initialize Demo
```bash
# Quick start - initializes everything
curl -X POST http://localhost:8000/api/demo/quick-start

# Just seed data
curl -X POST http://localhost:8000/api/demo/seed

# Reset and reseed
curl -X POST http://localhost:8000/api/demo/reset
```

### Check Status
```bash
curl http://localhost:8000/api/demo/status
```

### Get Demo Users
```bash
curl http://localhost:8000/api/demo/users
```

### Get Demo Jobs for User
```bash
curl http://localhost:8000/api/demo/jobs/demo_studio
```

### Get Demo Projects
```bash
curl http://localhost:8000/api/demo/projects
```

### Get Demo Presets
```bash
curl http://localhost:8000/api/demo/presets
```

## What Gets Seeded

### Users
- 5 demo users with different plans
- Pre-configured passwords

### Presets
- Cinematic Portrait
- Fast Storyboard
- Voice Clone Basic

### Projects
- Cine: Robot en Atardecer
- Storyboard: Escena de Accion
- Video: Transicion Paisaje
- Doblaje: Narracion Documental
- Consistencia de Personaje

### Jobs
- 5 demo jobs per demo user
- Various statuses: succeeded, running, queued

## Testing Workflows

### Login as Studio User
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo_studio@servicios-cine.com","password":"demo123"}'
```

### Create a Job
```bash
curl -X POST http://localhost:8000/api/render/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "still",
    "workflow_key": "still_text_to_image_pro",
    "prompt": {"positive": "cinematic robot"},
    "user_id": "demo_studio",
    "user_plan": "studio"
  }'
```

### Check Queue
```bash
curl http://localhost:8000/api/queue/status
```

## Demo Frontend

The frontend includes demo mode indicators:

### Components
- `DemoBanner` - Shows when in demo mode
- `PlanBadge` - Shows current plan limits

### Pages
- `/demo` - Demo landing page (if created)

## Reset Demo

To reset all demo data:
```bash
curl -X POST http://localhost:8000/api/demo/reset
```

This clears all demo jobs and reseeds everything.

## Production Note

Production candidate deployments should keep demo routes disabled by default:

1. Set `APP_ENV=production`
2. Set `ENABLE_DEMO_ROUTES=0`
3. Only enable `ENABLE_DEMO_ROUTES=1` for controlled commercial demo environments
