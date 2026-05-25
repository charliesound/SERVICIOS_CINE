# Frontend Static Metadata Scope - PRODUCT.2B

**Date:** 2026-05-21
**Workspace:** `/opt/SERVICIOS_CINE`
**Scope:** Frontend static metadata and public static copy only
**Status:** GO

## Objective

Align base frontend metadata with the CID Core scope after PRODUCT.2A: CID Core is now focused on cinematic preproduction, not dubbing, sound post, postproduction or delivery as part of the main customer-facing promise.

## Files Modified

- `src_frontend/index.html`
- `src_frontend/src/utils/seo.ts`
- `src_frontend/src/pages/LandingPage.tsx`
- `src_frontend/src/data/landingContent.ts`
- `src_frontend/src/data/landingVisualBible.ts`
- `src_frontend/src/data/solutionsContent.ts`
- `src_frontend/src/components/landing/LandingHeroCinematic.tsx`
- `src_frontend/src/components/landing/LandingProblemSolution.tsx`
- `src_frontend/src/components/landing/LandingDiferencial.tsx`
- `src_frontend/src/components/landing/LandingAudienceB2B.tsx`
- `src_frontend/src/components/landing/LandingShowcasePlaceholder.tsx`
- `src_frontend/src/pages/ModulesCatalogPage.tsx`
- `src_frontend/src/pages/PricingPage.tsx`
- `src_frontend/src/pages/ProducerSolutionPage.tsx`

Reviewed and left unchanged:

- `src_frontend/public/robots.txt`
- static public image assets under `src_frontend/public/`

## Previous Metadata

Base `index.html`, `og:description`, `twitter:description` and SEO fallback used:

```text
Software y soluciones de inteligencia artificial para cine, television y publicidad: guion, storyboard, produccion, doblaje, postproduccion y delivery.
```

Base title used:

```text
AILinkCinema | IA para cine y produccion audiovisual
```

## New Metadata

Base `index.html`, `og:description`, `twitter:description` and SEO fallback now use:

```text
Software de inteligencia artificial para preproduccion cinematografica: guion, analisis, storyboard, visual bible, presupuesto, pitch y planificacion.
```

Base title now uses:

```text
AILinkCinema | IA para preproduccion cinematografica
```

## Public Copy Cleanup

- Updated home SEO copy and structured data to CID Core preproduction.
- Updated landing public content that previously promised dubbing, sound post and delivery as part of the main CID flow.
- Removed DubbingTake and Sound Post from the static home solutions grid.
- Reframed public wording toward guion, analisis, storyboard, visual bible, presupuesto, pitch and planificacion.
- Kept lab/future product references where they explicitly describe non-core products as outside CID Core.

## Search Validation

Targeted checks found no old global metadata/copy in:

- `src_frontend/index.html`
- `src_frontend/src/utils/seo.ts`
- `src_frontend/src/pages/LandingPage.tsx`
- `src_frontend/src/data/landingContent.ts`
- `src_frontend/src/components/landing/`
- built `src_frontend/dist/index.html`

Remaining occurrences of terms such as `delivery` or `doblaje` are limited to internal route/code names, retained lab/future-product pages, module keys, or visual-generation reference assets, not the global static metadata.

## Local Build Validation

Command:

```bash
cd /opt/SERVICIOS_CINE/src_frontend
npm run build
```

Result: PASS.

Notes:

- Vite emitted existing dynamic-import/chunk-size warnings.
- Built asset: `dist/assets/index-BljAO7NR.js`.

## Docker Build Validation

Command:

```bash
cd /opt/SERVICIOS_CINE
docker compose -f compose.base.yml -f compose.home.yml build --no-cache frontend
```

Result: PASS.

Notes:

- Docker build completed and produced `servicios_cine-frontend:latest`.
- `npm ci` reported existing package audit notices: 5 vulnerabilities, 4 moderate and 1 high.
- Vite emitted the same existing dynamic-import/chunk-size warnings.

## Docker Up Validation

Command:

```bash
cd /opt/SERVICIOS_CINE
docker compose -f compose.base.yml -f compose.home.yml up -d frontend
```

Result: PASS.

Notes:

- `ailinkcinema_frontend` was recreated and started.
- Compose reported existing orphan containers but no failure.

## Curl Validation

Command:

```bash
curl -sS http://127.0.0.1/ | sed -n '1,80p'
```

Result: PASS.

Confirmed served metadata:

```html
<meta name="description" content="Software de inteligencia artificial para preproduccion cinematografica: guion, analisis, storyboard, visual bible, presupuesto, pitch y planificacion." />
<meta property="og:title" content="AILinkCinema | IA para preproduccion cinematografica" />
<meta property="og:description" content="Software de inteligencia artificial para preproduccion cinematografica: guion, analisis, storyboard, visual bible, presupuesto, pitch y planificacion." />
<meta name="twitter:title" content="AILinkCinema | IA para preproduccion cinematografica" />
<meta name="twitter:description" content="Software de inteligencia artificial para preproduccion cinematografica: guion, analisis, storyboard, visual bible, presupuesto, pitch y planificacion." />
<title>AILinkCinema | IA para preproduccion cinematografica</title>
```

## GO / NO-GO

GO for commit after review.

Rationale:

- Static base metadata now matches CID Core preproduction scope.
- Docker-served HTML confirms the new metadata.
- Frontend build and Docker frontend rebuild both pass.
- No backend, feature flags, modules, routes or Docker compose files were modified.
- No commit was created.
