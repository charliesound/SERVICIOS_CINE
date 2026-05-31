# AGENTS.md - SERVICIOS_CINE Operating Guide for AI Agents

Scope: mandatory guidance for agents working in `/opt/SERVICIOS_CINE`.

## 1) Mission and non-negotiables
- Prioritize security, reproducibility, traceability, and minimal diffs.
- Implement only what the task asks; avoid opportunistic refactors.
- Validate with real commands; do not claim checks you did not run.
- Never expose, generate, or commit secrets or private runtime artifacts.

## 2) Project scope map
- `src/`: main FastAPI backend.
- `src_frontend/`: main React + TypeScript + Vite frontend.
- `tests/`: root pytest suite (unit + integration).
- `scripts/`: smoke/validation and operational scripts.
- `docs/`: release/deploy references.
- `directivas/`: living technical directives (high-priority context).

This repo includes legacy/sibling folders; do not touch them unless the task explicitly requires it.

## 3) Flujo obligatorio antes de tocar código
Before editing any file, do all of the following:
1. Inspect current workspace and task scope.
2. Run `git status --short`.
3. Read this `AGENTS.md`.
4. Review relevant `directivas/` documents.
5. Read impacted files end-to-end before editing.
6. Infer conventions from nearby code/tests first.
7. Define a minimal change plan and matching validations.

After changes:
1. Run targeted validation commands first.
2. Run broader checks if risk is medium/high.
3. Report exact commands and real outcomes.

## 4) directivas/ policy (living source of truth)
- Treat `directivas/` as operational memory for architecture and critical flows.
- If a relevant directive exists, follow it.
- If task changes architecture/security/CI-critical flow and no directive exists, propose adding one.
- If constraints change, update corresponding directive in same task (when requested).

A good directive should document: objective, context, affected files, workflow, validations, edge cases, and known constraints.

Never store in directives: secrets, tokens, API keys, credential dumps, raw `.env` values, or sensitive private payloads.

## 5) Environment baseline
- Python `3.10+`
- Node `18+`
- Backend import root: `PYTHONPATH=/opt/SERVICIOS_CINE/src`

Backend setup:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Frontend setup:
```bash
npm --prefix src_frontend install
```

## 6) Validaciones backend/frontend
Run from repo root unless noted.

Backend syntax check for edited files:
```bash
python -m py_compile src/path/to/file.py
```

Backend full tests:
```bash
PYTHONPATH=src pytest -q
```

Run one test file:
```bash
PYTHONPATH=src pytest tests/unit/test_security_jwt.py -q
```

Run one test function:
```bash
PYTHONPATH=src pytest tests/unit/test_security_jwt.py::test_token_expiration -q
```

Keyword-filtered run:
```bash
PYTHONPATH=src pytest -k "security and not integration" -q
```

Frontend lint:
```bash
npm --prefix src_frontend run lint
```

Frontend build (includes TS compile):
```bash
npm --prefix src_frontend run build
```

Frontend dev server (local dev):
```bash
npm --prefix src_frontend run dev
```

Project smoke/validation scripts:
```bash
./scripts/smoke_cid_dev.sh
./scripts/validate_cid_dev.sh
```

## 7) Code style and architecture conventions

Python/FastAPI:
- Follow PEP 8 and existing module patterns.
- Use explicit typing (`dict[str, X]`, `list[X]`, `X | None`).
- Import order: stdlib, third-party, local.
- Keep route logic scoped in `src/routes/` and domain logic in `src/services/`.
- Use dependency injection (`Depends`) for auth/tenant/context.
- Prefer explicit `response_model` on routes.
- Raise `HTTPException` for expected API errors; map unexpected failures clearly.
- Preserve multitenancy checks and authorization boundaries.

TypeScript/React:
- Respect strict TS; avoid `any` unless unavoidable and justified.
- Preserve current formatting conventions (single quotes, no semicolons).
- Group imports coherently (external first, internal second).
- Keep route declarations centralized in `src_frontend/src/App.tsx`.
- Prefer shared hooks/utilities/components over duplication.
- Handle loading/error states explicitly in async flows.

Naming:
- Python files/functions/vars: `snake_case`.
- Python classes/types: `PascalCase`.
- TS functions/vars: `camelCase`.
- React components/pages: `PascalCase.tsx`.
- Constants: `UPPER_SNAKE_CASE`.
- Tests: `tests/**/test_*.py`.

## 8) Reglas de seguridad
- Enforce least-privilege mindset in all changes.
- Do not leak internals in production error messages.
- Keep request correlation (`request_id`) where available.
- Guard DB/network/external calls with timeouts and failure handling.
- Validate payload shape/size before expensive operations.

## 9) Prohibición de secretos y artefactos runtime
Never commit:
- `.env`, credentials, access tokens, API keys, OAuth secrets.
- `*.db`, `*.sqlite`, `*.sqlite3`.
- `node_modules/`, `dist/`, `build/`, logs, local caches.
- Private user uploads, private exports, or sensitive generated outputs.

If found staged by mistake, unstage immediately and report it.

## 10) Reglas Git seguras
- Do not run destructive git operations (`reset --hard`, force push) unless explicitly requested.
- Do not amend commits unless explicitly requested.
- Use explicit staging (`git add <path>`), never broad indiscriminate staging.
- Keep commits surgical: one objective, coherent files, validated behavior.

Pre-commit safety checks:
```bash
bash scripts/guard_no_db_commit.sh
git status --short
git diff --cached --name-only
```

## 11) Manejo de incertidumbre
Si falta contexto:
- inspeccionar primero
- inferir desde código existente
- buscar patrones similares
- no inventar APIs
- no asumir schemas inexistentes

Si hay duda crítica:
- detener cambios destructivos
- pedir confirmación explícita

## 12) Reglas ComfyUI / n8n / workflows IA
- Do not trigger real ComfyUI production rendering (`/prompt` or equivalent) unless explicitly requested.
- Prefer mocks, dry-runs, or contract validations for workflow changes.
- Do not call external paid/critical APIs without explicit instruction.
- Preserve compatibility with existing workflow schemas and routing contracts.
- When editing workflow-related code, validate with the nearest smoke/test scripts in `scripts/` and `tests/`.
- Do not commit raw workflow dumps containing sensitive metadata.
- For n8n-related logic, keep configuration explicit, deterministic, and auditable.

## 13) Docker and runtime rules
Use official demo stack commands:
```bash
docker compose -f compose.base.yml -f compose.home.yml config
docker compose -f compose.base.yml -f compose.home.yml up -d --build
```

Operational guidance:
- Prefer official compose overlays (`compose.base.yml` + environment overlay).
- Validate config before `up`.
- Do not modify Docker/network/TLS posture unless the task requires it.

## 14) Cursor/Copilot local rules status
Checked paths requested by product process:
- `.cursor/rules/`: not present.
- `.cursorrules`: not present.
- `.github/copilot-instructions.md`: not present.

If these files appear later, merge their directives here and treat them as high-priority local rules.

## 15) Criterio de entrega
A task is complete only when:
1. Diff is minimal, coherent, and scoped.
2. Affected files were reviewed before editing.
3. Relevant validations were run and reported.
4. No secrets or runtime artifacts are staged.
5. Behavior and contracts remain consistent with existing architecture.
6. Any blocked validation is documented with exact repro commands.

## Regla obligatoria WSL para CID / OpenCode

Este repositorio debe editarse, probarse y validarse únicamente dentro de WSL Ubuntu.

Directorio obligatorio de trabajo:

/opt/SERVICIOS_CINE

Antes de cualquier acción, ejecutar:

cd /opt/SERVICIOS_CINE
source .venv/bin/activate
pwd
git status --short

No usar nunca:

- PowerShell
- Python de Windows
- C:\Python...
- C:\mnt\...
- /mnt/wsl.localhost/...
- rutas \\wsl.localhost\... como ruta de trabajo dentro de bash
- rutas que creen archivos fuera del repositorio real de WSL

Los archivos del repo deben crearse directamente bajo:

/opt/SERVICIOS_CINE

Nunca bajo:

/mnt/c/mnt
C:\mnt
/mnt/wsl.localhost

Los hostnames Docker como qdrant, ollama y ailinkcinema_postgres solo son válidos desde contenedores Docker, no desde Python de Windows.

Para comprobaciones dentro del backend Docker, usar:

docker exec -i ailinkcinema_backend python3 - <<'PYDOCKER'
# código Python aquí
PYDOCKER

Antes de cada commit, ejecutar desde WSL:

cd /opt/SERVICIOS_CINE
source .venv/bin/activate
git status --short
git diff --check

