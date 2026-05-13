# Producción — AI Dubbing Legal Studio

## Despliegue completo

```bash
# 1. Configurar variables
cp .env.production.example .env
# Editar .env con valores seguros

# 2. Generar SSL (Let's Encrypt o autofirmado)
mkdir -p infra/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout infra/nginx/ssl/key.pem \
  -out infra/nginx/ssl/cert.pem \
  -subj "/CN=tudominio.com"

# 3. Desplegar
chmod +x infra/scripts/deploy.sh
./infra/scripts/deploy.sh

# 4. Verificar
curl https://localhost/health -k
```

## Backups

```bash
# Backup manual
./infra/scripts/backup.sh

# Restore
./infra/scripts/restore.sh infra/backups/db_20260101_120000.sql

# Cron diario (crontab -e)
0 2 * * * /path/to/infra/scripts/backup.sh
```

## Monitoreo

- Health: `GET /health`
- Logs: `docker compose logs -f backend worker`

## Checklist

- [ ] HTTPS configurado
- [ ] JWT secret generado
- [ ] DB password segura
- [ ] CORS limitado a dominio real
- [ ] Backups automáticos activos
- [ ] Rate limiting configurado
- [ ] Logs sin exposición de secretos
- [ ] Contratos y consentimientos verificados
