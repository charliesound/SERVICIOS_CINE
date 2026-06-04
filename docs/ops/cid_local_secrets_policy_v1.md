# CID Local Secrets Policy v1

## Objective
Define how secrets are handled in the CID repository to prevent credential
leakage in git history, logs, chat transcripts, and audit reports.

## Rules

### 1. `.env` file
- `.env` MAY exist locally with real credentials for development/demo
- `.env` MUST NEVER be tracked by git (already in `.gitignore`)
- `.env.example` MUST contain only placeholder values like `your-secret-here`
- Verify before any commit: `.env` is NOT staged

### 2. Secret variables known in `.env`
- `AUTH_SECRET_KEY`
- `POSTGRES_PASSWORD`
- `GOOGLE_DRIVE_CLIENT_ID`
- `GOOGLE_DRIVE_CLIENT_SECRET`
- `N8N_ENCRYPTION_KEY`
- `DATABASE_URL` (contains password)

### 3. Audit and report rules
- Never print secret values in audit reports
- Use `[REDACTED]` in place of values
- Report only: variable name, file path, risk severity
- If a secret value appears in chat, logs or commit by accident,
  it MUST be rotated immediately

### 4. No history rewrite
- DO NOT rewrite git history unless explicitly instructed
- Rotate the compromised secret instead

### 5. Rotation checklist (future phase)
When rotating secrets:
- Generate new `AUTH_SECRET_KEY` (openssl rand -hex 32)
- Generate new `POSTGRES_PASSWORD`
- Revoke old `GOOGLE_DRIVE_CLIENT_SECRET` in Google Cloud Console
- Update `.env` on all environments (local, VPS, CI)
- Verify all services restart and reconnect
- Remove old `.env` backups if any

### 6. Additional watch targets
Also monitor for secrets in:
- n8n workflow exports (`*.json` with webhook/auth data)
- ComfyUI workflow exports (`*.json` with API keys)
- Inventory/export files (`*inventory*.json`, `*export*.json`)
- CI/CD environment files
- Test fixtures containing real credentials
- Shell history files (`.bash_history`, `.zsh_history`)

### 7. Pre-commit guard
Run `scripts/dev/guard_wsl_repo.sh` before any commit to detect:
- `.env` staged
- `*credentials*.json` staged
- `*secret*.json` staged
- Sensitive patterns in staged diff

## References
- `.gitignore` lines 2-5: `.env` protection rules
- `scripts/dev/guard_wsl_repo.sh`: staged diff scanning
