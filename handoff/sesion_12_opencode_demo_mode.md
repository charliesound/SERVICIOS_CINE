# SESION 12: OpenCode - Modo Demo

## Rol
Senior Backend Engineer

## Ruta de Trabajo
`D:\SERVICIOS_CINE\src`

## Objetivo
Implementar modo demo con usuarios y datos preconfigurados.

## Archivos a Crear/Verificar

### 1. services/demo_service.py (ya existe)
Verificar que incluye:
- DemoService singleton
- seed_demo_data()
- reset_demo_data()
- get_demo_users()
- get_demo_jobs()

### 2. routes/demo_routes.py (ya existe)
Verificar endpoints:
- POST /api/demo/seed
- POST /api/demo/reset
- POST /api/demo/quick-start
- GET /api/demo/status
- GET /api/demo/users
- GET /api/demo/jobs/{user_id}
- GET /api/demo/projects
- GET /api/demo/presets

### 3. app.py (modificado)
Verificar inclusion de demo_routes.router

## Usuarios Demo
| Plan | Email | Password |
|------|-------|----------|
| free | demo_free@servicios-cine.com | demo123 |
| creator | demo_creator@servicios-cine.com | demo123 |
| studio | demo_studio@servicios-cine.com | demo123 |
| enterprise | demo_enterprise@servicios-cine.com | demo123 |
| admin | admin@servicios-cine.com | admin123 |

## Datos Demo
- 5 usuarios preconfigurados
- 5 proyectos demo
- 3 presets demo (Cinematic Portrait, Fast Storyboard, Voice Clone)
- 5 jobs demo por usuario (estados variados)

## Smoke Test
```bash
# Inicializar demo
curl -X POST http://localhost:8000/api/demo/quick-start

# Ver usuarios demo
curl http://localhost:8000/api/demo/users

# Login demo
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo_studio@servicios-cine.com","password":"demo123"}'

# Reset demo
curl -X POST http://localhost:8000/api/demo/reset
```

## Response Example - Quick Start
```json
{
  "message": "Demo initialized successfully",
  "credentials": {
    "free": {"email": "demo_free@servicios-cine.com", "password": "demo123"},
    "studio": {"email": "demo_studio@servicios-cine.com", "password": "demo123"}
  },
  "status": {
    "seeded": true,
    "demo_users_count": 5
  }
}
```

## Uso
1. Ejecutar demo_init.bat/sh
2. O curl -X POST /api/demo/quick-start
3. Login con credenciales demo
