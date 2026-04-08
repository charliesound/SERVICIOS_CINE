# Misión 08 — Operativización real de Antigravity y OpenCode

## Objetivo exacto
Convertir las carpetas existentes de Antigravity y OpenCode en un sistema operativo real de trabajo para el proyecto.

## Problema actual
Existen carpetas como:
- `antigravity/missions`
- `.opencode/agents`
- `.opencode/skills`

Pero aún no funcionan como sistema de ejecución real guiado por misiones y perfiles especializados.

## Alcance exacto
Esta misión debe:
1. definir estructura estándar de misiones
2. definir agentes de OpenCode
3. definir skills de OpenCode
4. documentar el flujo de trabajo entre ambos
5. establecer convención de nombres y orden de ejecución

## Entregables obligatorios
### En Antigravity
- convención oficial para misiones
- índice de misiones

### En OpenCode
Crear al menos estos perfiles:
- `backend_api_engineer.md`
- `frontend_migration_engineer.md`
- `storage_contract_engineer.md`
- `comfyui_integration_engineer.md`
- `repo_hardening_engineer.md`

Y estas skills:
- `read_repo_state.md`
- `edit_routes_and_services.md`
- `migrate_frontend_fetches.md`
- `normalize_api_contracts.md`
- `prepare_manual_tests.md`

## Documento obligatorio
- `docs/automation/antigravity_opencode_workflow.md`

## Contenido mínimo del documento
- qué decide Antigravity
- qué implementa OpenCode
- cómo se pasa una misión de uno a otro
- formato estándar de input
- formato estándar de output
- checklist de cierre por misión

## Criterios de aceptación
- Antigravity deja de ser una carpeta vacía
- OpenCode deja de ser una carpeta vacía
- existe un método reproducible de trabajo
- cada nueva fase puede ejecutarse de forma consistente

## Riesgos a vigilar
- usar Antigravity para microedición
- usar OpenCode sin spec claro
- generar prompts ambiguos o demasiado genéricos

## Siguiente misión encadenada
- la siguiente fase concreta de producto según roadmap técnico