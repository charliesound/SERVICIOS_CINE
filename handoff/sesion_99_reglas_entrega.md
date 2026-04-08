# SESION 99: Reglas de Entrega para SERVICIOS_CINE

## Reglas Fundamentales

### Antes de Entregar
1. Verificar que el codigo compila/ejecuta
2. Probar endpoints con curl
3. Verificar que no rompe funcionalidad existente
4. Documentar todos los cambios

### Criterios de Entrega
- Codigo listo para integrar
- Sin errores de import
- Tests pasando (si existen)
- Documentacion actualizada

### Formato de Entrega Estandar

```markdown
## Archivos Modificados
- archivo1.py
- archivo2.py

## Archivos Creados
- nuevo_archivo.py

## Comandos de Prueba
[comandos curl o npm]

## Payload JSON
[ejes]
```

## Restricciones

### NO Hacer
- No rehacer el proyecto entero
- No romper compatibilidad si no es imprescindible
- No crear archivos innecesarios
- No usar paths absolutos hardcodeados
- No exponer secrets en codigo
- No mover proyectos heredados (CID_SERVER, CINE_AI_PLATFORM, etc) sin autorizacion
- No asumir que existen 15 workflows reales sin verificar

### SI Hacer
- Mantener estructura existente en src/
- Usar config.yaml para settings
- Exportar en __init__.py
- Incluir tree de archivos
- Incluir smoke tests
- Incluir payloads JSON
- Trabajar de forma incremental
- Preservar contratos de API existentes

## Verificacion Rapida

```bash
# Backend
cd D:\SERVICIOS_CINE\src
pip install -r requirements.txt
python -c "from config import config; print('config OK')"
python -m uvicorn app:app --reload --port 8000

# Frontend
cd D:\SERVICIOS_CINE\src_frontend
npm install
npm run dev
```

## Smoke Tests Obligatorios

```bash
# Health
curl http://localhost:8000/health

# Plans
curl http://localhost:8000/api/plans/catalog

# Workflows
curl http://localhost:8000/api/workflows/catalog

# Instances
curl http://localhost:8000/api/ops/instances

# Queue
curl http://localhost:8000/api/queue/status

# Demo
curl -X POST http://localhost:8000/api/demo/quick-start
```

## Checklist de Entrega

- [ ] Archivos modificados documentados
- [ ] Archivos creados documentados
- [ ] Comandos de prueba incluidos
- [ ] Payloads JSON de ejemplo
- [ ] Breaking changes documentados (si los hay)
- [ ] Dependencias nuevas documentadas
- [ ] No se rompio nada existente

## Prioridades

1. **CRITICO:** No romper el backend que ya funciona
2. **ALTO:** Mantener la estructura de src/ intacta
3. **MEDIO:** Agregar funcionalidad de forma incremental
4. **BAJO:** Refactorizaciones optativas

## Proyectos Heredados

No modificar sin verificacion previa:
- `D:\SERVICIOS_CINE\CID_SERVER`
- `D:\SERVICIOS_CINE\CINE_AI_PLATFORM`
- `D:\SERVICIOS_CINE\PROYECTO FINAL V1`
- `D:\SERVICIOS_CINE\Web Ailink_Cinema`

Solo extraer componentes si hay ganancia clara.

## NuCLEO DEL PRODUCTO

Priorizar siempre:
1. Multi-backend (8188-8191)
2. Queue + Scheduler
3. Planes y limites
4. Workflows automaticos
