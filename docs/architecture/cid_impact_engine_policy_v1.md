# CID Impact Engine Policy v1

## Objective
Define the requirements for an Impact Engine that tracks and propagates
changes across the six interdependent CID production layers. A change in
one layer can require actions in upstream or downstream layers.

## The six CID layers (interdependent)

```
Layer 1: Producción / Productor
    ↑↓
Layer 2: Arte / Desarrollo / Preproducción
    ↑↓
Layer 3: Rodaje / Ejecución
    ↑↓
Layer 4: Postproducción
    ↑↓
Layer 5: Delivery / Entrega
    ↑↓
Layer 6: Promoción / Distribución
```

Changes flow both directions. A script change (L2) affects budget (L1),
storyboard (L2), shooting plan (L3), and post (L4). A delivery
requirement (L5) affects post (L4) and distribution (L6).

## Current state
- `ChangeGovernance` exists (models, routes, frontend) for controlled changes
- Branch Impact section in Command Center is a **placeholder**
  (conceptual states: pending, evaluating, approved, rejected)
- No automated impact propagation

## Policy

### 1. Impact Engine must record

| Field | Description | Required |
|---|---|---|
| `source_event` | What happened (script change, budget approval, etc.) | Yes |
| `source_layer` | Which layer originated the change (1-6) | Yes |
| `affected_entities` | Specific entities (ScriptVersion, Budget, etc.) | Yes |
| `affected_layers` | Which layers are affected (1-6) | Yes |
| `action_required` | What action is needed (review, re-estimate, re-render) | Yes |
| `responsible_role` | Which role must act | Yes |
| `affected_version` | Version/tag of the affected baseline | Yes |
| `credit_cost` | Estimated credit impact (if applicable) | Optional |
| `status` | pending / evaluating / approved / rejected / completed | Yes |
| `created_at` | Timestamp | Yes |
| `resolved_at` | Timestamp | Optional |

### 2. Mandatory impact scenarios to support

| Scenario | Source Layer | Affected Layers | Required Actions |
|---|---|---|---|
| Script change | L2 | L1, L2, L3, L4 | Re-estimate budget, update storyboard, revise shooting plan |
| Budget approval | L1 | L1, L2 | Unlock preproduction phases, release funding |
| Storyboard revision | L2 | L2, L3 | Update shot list, revise shooting plan |
| Director feedback | L2 | L2 | Regenerate/revise specific shots |
| Editorial cut | L4 | L4, L5, L6 | Review, QC, delivery prep, distribution planning |
| Sound incident | L3 | L3, L4, L5, L6 | ADR, M&E remix, subtitle sync, delivery delay |
| Shooting date change | L3 | L1, L2, L3 | Rebook crew, equipment, locations; revise budget |
| New platform requirement | L5 | L4, L5, L6 | Re-export formats, new QC, subtitle conform |
| CRM opportunity | L6 | L1, L6 | Update commercial dossier, prepare deliverables |
| Credit shortage | All | All | Block non-critical jobs, alert project owner |

### 3. What NOT to do yet
- Do NOT implement Impact Engine backend
- Do NOT create models
- Do NOT modify ChangeGovernance
- Do NOT change Command Center placeholders

## References
- `src_frontend/src/pages/ProjectDashboardPage.tsx` — Branch Impact placeholder
- `src/models/change_governance.py` — existing ChangeGovernance
- `src/routes/change_governance_routes.py` — ChangeGovernance routes
- `docs/product/cid_project_command_center_branches_v1.md` — branch architecture
- `CID.REPOSITORY.INTELLIGENCE.AUDIT.1` sections 10, 13
