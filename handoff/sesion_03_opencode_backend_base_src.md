# SESION 03: OpenCode - Backend Base en src

## Rol
Senior Backend Engineer

## Ruta de Trabajo
`D:\SERVICIOS_CINE\src`

## Contexto
Backend FastAPI existente con estructura basica. No crear apps/api o subdirectorios innecesarios.

## Objetivo
Verificar y enhancer el backend base:
1. Estructura de carpetas correcta
2. Rutas basicas funcionando
3. Configuracion centralizada
4. Health checks
5. CORS configurado

## Archivos Existentes a Verificar
```
src/
├── app.py
├── config.py
├── config/
│   ├── config.yaml
│   ├── instances.yml
│   └── plans.yml
├── routes/
├── services/
├── schemas/
├── middleware/
├── models/
├── utils/
├── backends/
├── tests/
├── requirements.txt
└── README.md
```

## Tareas
1. Verificar que app.py carga correctamente
2. Verificar que config.py lee config.yaml
3. Verificar que todas las rutas estan registradas
4. Probar endpoints basicos:
   - GET /
   - GET /health
   - GET /api/plans/catalog
   - GET /api/workflows/catalog

## Reglas
- NO crear apps/ o subdirectorios innecesarios
- Mantener estructura plana
- Usar imports relativos

## Smoke Test
```bash
cd D:\SERVICIOS_CINE\src
python -m uvicorn app:app --reload --port 8000

# En otra terminal:
curl http://localhost:8000/health
curl http://localhost:8000/api/plans/catalog
```
