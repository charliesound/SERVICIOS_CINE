# CID Landing vs CID SaaS: Boundary Policy v1

## Objective
Define the separation between **AILinkCinema Landing** (public commercial
layer) and **CID SaaS** (integrated production platform), establishing clear
boundaries for routing, content, and sales messaging.

## Current state

AILinkCinema Landing and CID SaaS share the same repository and Vite build:
- Landing routes: `/`, `/solutions/*`, `/pricing`, `/demo-cid`, `/legal/*`
- CID internal routes: `/cid/*`, `/dashboard`, `/projects/*`, `/queue`, etc.
- Both use the same `App.tsx` routing tree
- Landing CTAs link to CID internal pages
- SEO metadata applies the same defaults to all routes

## Policy

### 1. AILinkCinema Landing (public commercial layer)
Landing sells standalone services and leads to CID:
- Script analysis (service)
- Storyboard (service)
- Video production (service)
- Editing/post (service)
- Dossier/pitch (service)
- Distribution packs (service)
- AI consulting (service)
- **CID demo** (leads into full SaaS)

Landing pages are **public**. No authentication required.

### 2. CID SaaS (integrated platform)
CID is a **full production SaaS** organized in six interdependent layers:
1. **Producción / Productor** — funding, budget, breakdown, pitch
2. **Arte / Desarrollo / Preproducción** — script, storyboard, character/visual bible
3. **Rodaje / Ejecución** — shooting plan, ingest, reports, storage
4. **Postproducción** — editorial assembly, NLE bridge, VFX, color, audio
5. **Delivery / Entrega** — deliverables formats, QC, reviews
6. **Promoción / Distribución** — CRM, distribution packs, sales targets

CID routes are **authenticated** and **plan-gated**.

### 3. Separation rules
- Landing MUST NOT expose CID internal routes in its navigation
- CID MUST NOT be presented as a collection of standalone modules
- Each CID layer depends on data from previous layers
- Landing can sell modules as isolated services, CID cannot
- Public routes should be logically separated from internal routes
- Future phase: separate builds (landing SPA + CID SPA) or strict route isolation

### 4. What NOT to do yet
- Do NOT modify route structure in `src_frontend/src/App.tsx`
- Do NOT create separate Vite builds
- Do NOT move files between directories
- Do NOT change SEO configuration

### 5. Future separation criteria
Before separation:
- [ ] CID core is stable (Command Center real, permissions real, credits real)
- [ ] Landing and CID have independent marketing/SEO needs
- [ ] Bundle size or build complexity becomes a problem
- [ ] Stakeholder decision on separate deployments

## References
- `src_frontend/src/App.tsx` — current route tree
- `CID.REPOSITORY.INTELLIGENCE.AUDIT.1` sections 2, 4
- `CID.BASELINE.SAFETY.CANONICALIZATION.1` section 3 risk 7
