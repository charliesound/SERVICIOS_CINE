# Directiva — MVP Productor Lean / AILinkCinema

## Objetivo

Construir el MVP Lean de la solución para productores dentro de AILinkCinema, tomando como referencia la landing/solución del Director ya implementada.

El MVP debe ayudar a un productor a entender rápidamente la propuesta de valor de AILinkCinema/CID para producción, financiación, presupuesto, planificación, documentación, seguimiento y distribución.

## Contexto

Ya existe una solución o landing para Director.

El Productor debe ser una solución separada, con su propia propuesta, copy, secciones y CTA, pero integrada dentro de la arquitectura de AILinkCinema/CID.

## Archivos afectados previstos

Antes de editar, inspeccionar:

- src_frontend/src/pages/
- src_frontend/src/components/landing/
- src_frontend/src/data/landingContent.ts
- src_frontend/src/App.tsx
- router frontend equivalente
- src/routes/solutions_routes.py
- src/services/solutions_service.py

## Reglas

- No tocar backend salvo que sea necesario registrar la nueva solución.
- No tocar lógica de Director salvo para reutilizar patrón.
- No mezclar refactors cosméticos globales.
- Mantener copy claro, premium y orientado a negocio.
- No crear funcionalidades falsas como si estuvieran completas.
- Separar MVP visible de integraciones futuras.
- No commitear cambios ajenos como src/routes/render_routes.py si no pertenecen a esta tarea.
- No ejecutar renders reales ni llamar a ComfyUI /prompt salvo autorización explícita.

## MVP mínimo

Debe incluir:

1. Landing específica de Productor.
2. Hero claro.
3. Problemas del productor.
4. Solución AILinkCinema/CID para producción.
5. Módulos iniciales:
   - análisis de proyecto
   - presupuesto
   - financiación y subvenciones
   - planificación
   - documentación
   - seguimiento de producción
   - distribución y ventas
6. CTA hacia demo o contacto.
7. Registro en navegación o soluciones si aplica.
8. Validación con build frontend.
9. Smoke backend solo si se toca backend.

## Validaciones

Frontend:

- cd /opt/SERVICIOS_CINE/src_frontend
- npm run build

Backend, solo si se toca backend:

- cd /opt/SERVICIOS_CINE
- source .venv/bin/activate
- export PYTHONPATH="$PWD/src"
- python -m py_compile archivos_modificados_reales
- ./scripts/smoke_cid_dev.sh

Git:

- bash scripts/guard_no_db_commit.sh
- git status --short
- git diff --cached --name-only
- no usar git add -A

## Errores aprendidos

- No ejecutar literalmente python -m py_compile <archivos_modificados>; es un marcador.
- Antes de commitear documentación Markdown, comprobar que los bloques de código estén cerrados.
- Si aparece un cambio ajeno en git status, dejarlo fuera del commit.
- Evitar bloques Markdown innecesarios en directivas para reducir errores de pegado.

## Criterio de terminado

El MVP Productor se considera terminado cuando:

- existe una página o landing clara para Productor
- está integrada en la navegación o sistema de soluciones
- el build frontend pasa
- el smoke backend pasa si se toca backend
- no hay archivos sensibles staged
- el commit es quirúrgico
- la CI pasa después del push
