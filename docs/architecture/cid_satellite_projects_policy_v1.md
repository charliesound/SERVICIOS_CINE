# CID Satellite Projects Policy v1

## Objective
Define the status and future of standalone satellite projects
(`cid-budget/`, `comfysearch/`, `ai-dubbing-legal-studio/`) that
duplicate or extend functionality already present in CID core.

## Current state

| Project | Stack | Connected to CID | Solapamiento with src/ |
|---|---|---|---|
| `cid-budget/` | FastAPI + React + Alembic | NO | Budget + Estimator already in `src/` |
| `comfysearch/` | FastAPI API + Web UI | NO | ComfySearch route in `src/routes/comfysearch_routes.py` |
| `ai-dubbing-legal-studio/` | FastAPI + React + Nginx + Alembic | Partial | `dubbing_bridge_routes.py` in `src/` |

## Policy

### 1. Freeze immediately
- All three satellite projects are **frozen**
- No new development in these projects
- No bug fixes, no dependency updates, no refactors
- Existing code remains in place

### 2. Do NOT touch
- Do NOT move, delete, or rename project directories
- Do NOT integrate into CID core at this phase
- Do NOT port features from satellites into `src/`
- Do NOT remove satellite-specific `.gitignore` entries

### 3. CID core is canonical
- CID core lives exclusively in `src/` (backend) and `src_frontend/` (frontend)
- Any functionality needed by CID SaaS must be implemented in CID core
- Satellite projects served as prototypes/experiments only

### 4. Future integration criteria
Before any satellite is integrated:
- [ ] CID core is stable and feature-complete for the relevant layer
- [ ] Integration audit performed
- [ ] Migration plan documented and approved
- [ ] No functionality regression from the satellite's current state
- [ ] Pricing/licensing model aligned with CID SaaS

### 5. Evaluation per project

| Project | Verdict | Rationale |
|---|---|---|
| `cid-budget/` | **Archive** | Everything exists in `src/` |
| `comfysearch/` | **Archive** | Route exists in `src/routes/` |
| `ai-dubbing-legal-studio/` | **Evaluate later** | Has legal/compliance requirements that may justify standalone deployment |

## References
- `CID.BASELINE.SAFETY.CANONICALIZATION.1` section 7
- `CID.REPOSITORY.INTELLIGENCE.AUDIT.1` sections 3, 15
