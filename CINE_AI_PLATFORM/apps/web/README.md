# CINE AI PLATFORM Web

## Official frontend path
- Entrypoint: `apps/web/src/main.tsx`
- Main app: `apps/web/src/App.tsx`

## Local run

```bash
cd apps/web
npm install
cp .env.example .env
npm run dev
```

## Validation commands
- `npm run lint`
- `npm run build`

## Env variables
- `VITE_API_BASE_URL`
  - Dev example: `http://127.0.0.1:3000`
  - Compose/nginx example: `/api`

## Docker + nginx
- `apps/web/Dockerfile` builds static assets and serves them with nginx.
- `apps/web/nginx.conf` serves frontend and proxies `/api/*` to backend service `api:3000`.
