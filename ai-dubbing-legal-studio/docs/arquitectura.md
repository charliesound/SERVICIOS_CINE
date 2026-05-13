# Arquitectura de AI Dubbing Legal Studio

## Visión general

Sistema SaaS/local para gestión de doblaje con trazabilidad legal.
Arquitectura en capas con frontend React, backend FastAPI, workers asíncronos y almacenamiento S3.

## Diagrama de componentes

```
[Browser] → [Nginx] → [Frontend React]
                   → [Backend FastAPI] → [PostgreSQL]
                                        → [Redis] → [Worker Python]
                                        → [MinIO/S3]
                                        → [Qdrant opcional]
```

## Capas

### Frontend (React + TypeScript + Tailwind)
- Login
- Dashboard
- Proyectos y jobs
- Contratos y validación legal
- Auditoría

### Backend (FastAPI)
- REST API con JWT auth
- SQLAlchemy async + PostgreSQL
- Servicios: auth, contracts, audit, legal report
- Providers: TTS, LipSync (interfaces abstractas)

### Workers (Python)
- Cola Redis/RQ
- Steps: transcribe → translate → generate_voice → lipsync → mix → export
- Validación legal antes de procesar

### Storage (MinIO/S3)
- Media assets (vídeo/audio original)
- Generated assets (voces, lipsync)
- Exports (informes PDF, entregables)

## Flujo de datos

1. Usuario crea proyecto y sube media
2. Crea dubbing job con modo y parámetros
3. Si modo IA → valida contrato
4. Si validación falla → job blocked_legal
5. Si válido → worker pipeline
6. Cada paso actualiza JobStep + AuditLog
7. Al finalizar → awaiting_approval
8. Usuario aprueba/rechaza
9. Exporta entregables + informe legal PDF

## Seguridad

- JWT tokens con expiry
- Roles y permisos
- Contraseñas hasheadas con bcrypt
- CORS configurable
- Rate limiting
- Audit logging obligatorio
- Contratos con validación multi-check
