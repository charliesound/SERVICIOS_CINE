# CID Credits Accounting Policy v1

## Objective
Define the requirements for implementing a production-grade credit accounting
system in CID. Credits are the primary monetization mechanism — they cannot
remain as frontend-only placeholders.

## Current state (verified)

### Documentation (exists)
- `docs/business/cid_credits_business_model_v1.md`
- `docs/business/cid_ai_gpu_credit_cost_model_v1.md`
- `docs/business/cid_credit_purchase_flow_v1.md`

### Backend (partial)
- `storyboard_credit_estimator_service.py` — estimates credits for storyboard
- `POST /{project_id}/storyboard/estimate-credits` — estimation endpoint
- **NO** `CreditTransaction`, `CreditPool`, `BillingRecord` models
- **NO** credit consumption/deduction endpoints
- **NO** Stripe/PayPal integration

### Frontend (placeholder)
- Command Center: hardcoded mock values (2000 included, 420 used, 1580 remaining)
- Visible disclaimer: "No real data yet"
- AI Status credit card: mock estimate range "35–90"

## Policy

### 1. Credit operations required
The credit system MUST support these operations, in order:

| # | Operation | Description |
|---|---|---|
| 1 | Credit Pool | Per-organization or per-project balance |
| 2 | Reservation | Reserve credits before job execution |
| 3 | Consumption | Deduct credits on job completion/success |
| 4 | Rollback | Return reserved credits on job failure |
| 5 | History | Full audit trail of all credit movements |
| 6 | Alerts | Warning at configurable thresholds |
| 7 | Blocking | Block new jobs when balance is insufficient |

### 2. Every credit transaction MUST track
- `organization_id`
- `project_id`
- `user_id`
- `job_id` (if applicable)
- `module` (storyboard, script_analysis, concept_art, etc.)
- `amount` (positive = consumption, negative = top-up)
- `transaction_type` (reservation, consumption, rollback, top-up, admin_adjustment)
- `timestamp`
- `description` / `reference`

### 3. Actions that SHOULD consume credits

| Action | Module | Priority |
|---|---|---|
| Storyboard render (per shot) | storyboard | High |
| Script analysis (per analysis) | script_intelligence | High |
| Concept art generation | concept_art | High |
| Document analysis / OCR | document | Medium |
| RAG embedding generation | memory | Medium |
| Qdrant vector search | retrieval | Medium |
| ComfyUI job execution | pipeline_builder | High |
| Ollama job (model inference) | pipeline_builder | High |
| Editorial export (advanced) | editorial | Low |

### 4. Credit pool structure
```
OrganizationCreditPool:
  - organization_id (PK)
  - total_credits (lifetime purchased/allocated)
  - consumed_credits (lifetime consumed)
  - reserved_credits (currently reserved by running jobs)
  - available = total - consumed - reserved

CreditTransaction:
  - id (PK)
  - organization_id
  - project_id (optional)
  - user_id
  - job_id (optional)
  - module (string)
  - amount (integer, negative for consumption)
  - balance_before
  - balance_after
  - type (enum)
  - description
  - created_at
```

### 5. What NOT to do yet
- Do NOT create the credit models now
- Do NOT modify any existing endpoints
- Do NOT change the frontend placeholders
- Do NOT add Stripe/PayPal credentials
- Do NOT modify `src/config/plans.yml` credit values

## References
- `src/services/storyboard_credit_estimator_service.py` — existing estimator
- `src/routes/storyboard_routes.py` — existing estimate endpoint
- `src_frontend/src/pages/ProjectDashboardPage.tsx` — mock credit display
- `docs/business/cid_credits_business_model_v1.md` — business model
- `docs/business/cid_ai_gpu_credit_cost_model_v1.md` — GPU cost formulas
- `CID.BASELINE.SAFETY.CANONICALIZATION.1` section 9
