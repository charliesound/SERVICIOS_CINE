# SECRETS PRIVATE

## Variables secretas
- `N8N_ENCRYPTION_KEY`
- `AUTH_BOOTSTRAP_USERS`

## Variables que deben cambiarse obligatoriamente
- `N8N_ENCRYPTION_KEY`
- la password incluida en `AUTH_BOOTSTRAP_USERS`

## Variables que deben revisarse antes de arrancar
- `PRIVATE_BASE_URL`
- `PRIVATE_BROWSER_ORIGINS`
- `N8N_HOST`
- `N8N_EDITOR_BASE_URL`
- `N8N_WEBHOOK_URL`
- `COMFYUI_BASE_URL`
- `COMFYUI_HOST_PROBE_URL`
- `API_DATA_PATH`
- `N8N_DATA_PATH`
- `QDRANT_STORAGE_PATH`
- `NGINX_LOG_PATH`

## Criterio recomendado

### N8N_ENCRYPTION_KEY
- minimo 32 caracteres
- recomendado 48-64 caracteres
- valor aleatorio
- sin espacios ni comillas

Formato esperado:

```text
CHANGE_ME_MIN_32_RANDOM_CHARS_PRIVATE_ONLY
```

### AUTH_BOOTSTRAP_USERS
Formato:

```text
email:password:role
```

Para este pack privado:
- mantener al menos un usuario `admin`
- password minima 20 caracteres
- recomendado mezclar mayusculas, minusculas, numeros y simbolos
- no reutilizar passwords conocidas o de demo

Formato esperado:

```text
admin@cine.local:CHANGE_ME_ADMIN_PASSWORD_USE_20PLUS_CHARS:admin
```

## Reglas operativas
- copiar `.env.private.example` a `.env.private`
- editar secretos solo en `.env.private`
- no commitear secretos reales
- no arrancar el stack si quedan valores `CHANGE_ME_*`
