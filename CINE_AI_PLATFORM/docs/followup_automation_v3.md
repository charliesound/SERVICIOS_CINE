# Follow-up Automation V3 — Cola, Reintentos, Prioridades y Secuencias

## Resumen

La V3 convierte el sistema de follow-ups en una automatización comercial operativa con:
- **Cola de envío** con procesamiento por prioridad (hot > warm > cold)
- **Reintentos controlados** con backoff exponencial y clasificación de errores
- **Secuencias de follow-up** para campañas CID Storyboard IA
- **Motor de elegibilidad** que evita duplicación y respeta ventanas temporales
- **Visibilidad operativa** desde endpoints y frontend

## Arquitectura

```
Lead captado → Genera follow-up → Encolado → Procesador de cola → Envío SMTP/Simulado
                                        ↓
                              ¿Éxito? → Sí: marca sent, programa siguiente step
                                      → No: ¿reintentable? → Sí: reencola con backoff
                                                              → No: marca failed/terminal
```

## Endpoints

### Cola y procesamiento
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/followups/queue` | Lista cola con filtros y resumen |
| POST | `/api/followups/process-queue` | Procesa lote de la cola (batch_size configurable) |
| POST | `/api/followups/{id}/enqueue` | Encola un follow-up individual |
| POST | `/api/followups/{id}/retry` | Reintenta un follow-up fallido |
| POST | `/api/followups/{id}/send` | Envía un follow-up individual |
| GET | `/api/followups/automation-status` | Estado de automatización y resumen de cola |

### Secuencias
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/leads/{lead_id}/followups` | Todos los follow-ups de un lead |
| GET | `/api/leads/{lead_id}/sequences` | Secuencias y pasos de un lead |
| POST | `/api/leads/{lead_id}/sequences/generate` | Genera secuencia inicial para un lead |

### Testing
| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/followups/test-email` | Envía email de prueba real |
| POST | `/api/followups/system/test-smtp` | Test de conectividad SMTP |

## Estados de cola

| Estado | Significado |
|---|---|
| `queued` | Listo para procesar |
| `processing` | Siendo procesado (lock activo) |
| `sent` | Enviado correctamente |
| `failed` | Error de envío (reintentable) |
| `skipped` | Saltado definitivamente |
| `cancelled` | Cancelado manualmente |

## Secuencia CID Storyboard IA

| Step | Delay | Descripción |
|---|---|---|
| 1 | 0 min | Autorespuesta inicial |
| 2 | 3 días | Recordatorio suave |
| 3 | 7 días | Cierre amable / invitación final |

## Variables de entorno

| Variable | Default | Descripción |
|---|---|---|
| `FOLLOWUP_SEND_MODE` | `simulated` | `disabled` \| `simulated` \| `smtp` |
| `FOLLOWUP_AUTO_SEND_ENABLED` | `false` | Autoenvío al generar follow-up |
| `FOLLOWUP_FROM_NAME` | `CID` | Nombre del remitente |
| `FOLLOWUP_FROM_EMAIL` | `noreply@cid.example.com` | Email del remitente |
| `FOLLOWUP_REPLY_TO` | `` | Reply-To |
| `FOLLOWUP_TEST_RECIPIENT` | `` | Email para testing |
| `FOLLOWUP_SQLITE_FILE` | `data/followups.db` | Ruta SQLite |
| `SMTP_HOST` | `` | Host SMTP |
| `SMTP_PORT` | `587` | Puerto SMTP |
| `SMTP_USERNAME` | `` | Usuario SMTP |
| `SMTP_PASSWORD` | `` | Password SMTP |
| `SMTP_USE_TLS` | `true` | Usar STARTTLS |
| `SMTP_USE_SSL` | `false` | Usar SSL directo |
| `SMTP_TIMEOUT_SECONDS` | `30` | Timeout conexión |
| `SMTP_ALLOW_SELF_SIGNED` | `false` | Permitir certs autofirmados |

## Cómo probar

### 1. Crear un follow-up
```bash
curl -X POST http://127.0.0.1:3000/api/followups \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": "test-lead-001",
    "template_key": "cid_storyboard_ia_initial",
    "recipient_email": "test@example.com",
    "priority": "hot",
    "auto_send": true
  }'
```

### 2. Ver la cola
```bash
curl http://127.0.0.1:3000/api/followups/queue
```

### 3. Procesar la cola
```bash
curl -X POST http://127.0.0.1:3000/api/followups/process-queue?batch_size=10
```

### 4. Generar secuencia para un lead
```bash
curl -X POST http://127.0.0.1:3000/api/leads/test-lead-001/sequences/generate \
  -H "Content-Type: application/json" \
  -d '{"campaign_key": "cid_storyboard_ia"}'
```

### 5. Ver secuencias de un lead
```bash
curl http://127.0.0.1:3000/api/leads/test-lead-001/sequences
```

### 6. Reintentar un follow-up fallido
```bash
curl -X POST http://127.0.0.1:3000/api/followups/{followup_id}/retry
```

## Limitaciones V3

- No hay cron automático — el procesamiento se activa manualmente vía endpoint
- No hay tracking de aperturas/clics
- No hay respuesta del lead ni stop automático de secuencia
- Las secuencias solo tienen 1 plantilla reutilizada (personalizar en V4)
- No hay cola externa (Redis, Celery) — todo en SQLite

## Siguientes pasos V4

- Cron/worker separado para procesamiento automático
- Tracking de aperturas y clics
- Detección de respuesta del lead → stop de secuencia
- Plantillas personalizadas por step
- Integración con CRM (HubSpot, Pipedrive)
- Dashboard con métricas de conversión
- Cola externa (Redis) para mayor throughput
