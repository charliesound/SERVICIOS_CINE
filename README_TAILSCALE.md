# ==========================================
# GUÍA DE DESPLIEGUE - AILinkCinema
# ==========================================

## Acceso desde Laptop (via Tailscale)

### Opción 1: Por IP de Tailscale
```
http://100.105.161.84
```

### Opción 2: Con dominio personalizado (RECOMENDADO)

1. **En el LAPTOP (Windows)**:
   - Abrir `C:\Windows\System32\drivers\etc\hosts` como administrador
   - Agregar línea:
     ```
     100.105.161.84    ailinkcinema
     ```
   - Guardar

2. **Acceder desde navegador**:
   ```
   http://ailinkcinema
   ```

---

## Servicios

| Servicio | Puerto | URL Local | URL Tailscale |
|----------|--------|-----------|---------------|
| Frontend principal | 80 | http://localhost | http://100.105.161.84 |
| Backend API | 8000 | http://localhost:8000 | http://100.105.161.84:8000 |
| API Docs | 8000 | http://localhost:8000/docs | http://100.105.161.84:8000/docs |
| CINE API | Caddy | http://localhost/cine/api/ | http://100.105.161.84/cine/api/ |
| CINE Web | Caddy | http://localhost/cine/ | http://100.105.161.84/cine/ |
| Automation Engine | Caddy | http://localhost/automation/health | http://100.105.161.84/automation/health |
| n8n | Caddy | http://localhost/n8n/ | http://100.105.161.84/n8n/ |
| Qdrant | Caddy | http://localhost/qdrant/collections | http://100.105.161.84/qdrant/collections |

## Rutas recomendadas

```text
App:        http://100.105.161.84/
CINE:       http://100.105.161.84/cine/
n8n:        http://100.105.161.84/n8n/
Qdrant:     http://100.105.161.84/qdrant/collections
Automation: http://100.105.161.84/automation/health
```

Para Tailscale, usa `http://` como opcion recomendada. `https://` funciona con certificado autofirmado y puede mostrar advertencias del navegador.

---

## Credenciales Demo

- **Admin**: admin@servicios-cine.com / admin123
- **Free**: demo_free@servicios-cine.com / demo123
- **Studio**: demo_studio@servicios-cine.com / demo123

---

## Arranque Manual

```batch
:: Arrancar backend
start_backend.bat

:: Arrancar frontend
start_frontend.bat
```

## Docker (alternativo)

```batch
docker-compose up -d
```

---

## Notas

- Los backends ComfyUI (8188-8191) deben estar corriendo para renderizado
- Caddy sirve como reverse proxy para app principal, CINE, n8n, Qdrant y Automation
- Para cambiar IP de Tailscale, editar `.env`
