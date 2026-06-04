# CID Pricing Canonicalization — Estado y Pasos Pendientes v1

## Objective
Document the current pricing discrepancy between commercial documentation
and actual code configuration, and define the alignment required before
monetization can proceed.

## Current state (verified)

### Documentation pricing (commercial target)
| Plan | Price (€/month) | Users | Credits/month |
|---|---|---|---|
| Starter | 99 | Up to 9 | 500 |
| Pro | 299 | Up to 15 | 2,000 |
| Studio | 799 | Up to 30 | 8,000 |
| Premium | 1,490 | Up to 50 | 20,000 |
| Enterprise | 3,500+ | Custom | Custom |

Source: `docs/business/cid_pricing_competitive_baseline_v1.md`

### Code pricing (actual in plans.yml)
| Plan | Price (€/month) |
|---|---|
| Demo | 0 |
| Free | 0 |
| Creator | 9.99 |
| Producer | 19.99 |
| Studio | 29.99 |
| Enterprise | 99.99 |

Source: `src/config/plans.yml` — this is what the frontend `PlanRoute`
and backend `plan_limits_service` actually use.

### Discrepancy
- 5 plans in docs vs 6 plans in code
- Prices differ by orders of magnitude (99€ vs 9.99€ for entry-level)
- Plan names differ (Starter/Pro/Premium vs Demo/Free/Creator/Producer)
- Docs mention 5 tiers, code has 6 tiers
- No validation exists on which pricing is the "real" one

## Policy

### 1. Do NOT correct yet
- Do NOT modify `src/config/plans.yml`
- Do NOT modify documentation pricing
- Do NOT validate or gate by pricing at this phase

### 2. Future alignment criteria (separate phase)
Before any monetization launch:
- [ ] Stakeholder decision on final pricing model
- [ ] `plans.yml` updated to match commercial target
- [ ] Frontend `PlanRoute` updated for new plan names
- [ ] Backend gating implemented per plan (see `cid_backend_gating_policy_v1.md`)
- [ ] Backend credit accounting implemented (see `cid_credits_accounting_policy_v1.md`)
- [ ] Stripe/PayPal integration ready
- [ ] Pricing page matches actual enforced limits

## References
- `src/config/plans.yml` — actual code configuration
- `docs/business/cid_pricing_competitive_baseline_v1.md` — commercial docs
- `docs/business/cid_credits_business_model_v1.md` — credit model per plan
- `CID.BASELINE.SAFETY.CANONICALIZATION.1` section 3 risk 8
