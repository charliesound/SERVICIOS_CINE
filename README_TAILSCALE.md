# ==========================================
# GUÍA DE DESPLIEGUE - AILinkCinema
# ==========================================

## Acceso desde Laptop (via Tailscale)

### Opción 1: Por nombre recomendado
```
http://ailinkcinema
```

### Opción 2: Por IP de Tailscale

```
http://100.104.219.15
```

### Opción 3: Con hosts en Windows (si no resuelve el nombre)

1. **En el LAPTOP (Windows)**:
   - Abrir `C:\Windows\System32\drivers\etc\hosts` como administrador
   - Agregar línea:
     ```
     100.104.219.15    ailinkcinema
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
| Landing principal | 80 | http://localhost | http://ailinkcinema |
| Backend API | 8000 | http://localhost:8000 | http://ailinkcinema:8000 |
| API Docs | Caddy | http://localhost/docs | http://ailinkcinema/docs |
| CINE API | Caddy | http://localhost/cine/api/ | http://ailinkcinema/cine/api/ |
| CINE Web | Caddy | http://localhost/cine/ | http://ailinkcinema/cine/ |
| Automation Engine | Caddy | http://localhost/automation/health | http://ailinkcinema/automation/health |
| n8n | Caddy | http://localhost/n8n/ | http://ailinkcinema/n8n/ |
| Qdrant | Caddy | http://localhost/qdrant/collections | http://ailinkcinema/qdrant/collections |

## Rutas recomendadas

```text
App:        http://ailinkcinema/
CINE:       http://ailinkcinema/cine/
n8n:        http://ailinkcinema/n8n/
Qdrant:     http://ailinkcinema/qdrant/collections
Automation: http://ailinkcinema/automation/health
```

- `/` es publico como landing.
- `/cine/`, `/app`, `/n8n/`, `/qdrant/`, `/automation/` y la documentacion tecnica requieren autenticacion basica.
- La contrasena no se guarda en la documentacion; se gestiona en `.env`.

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
