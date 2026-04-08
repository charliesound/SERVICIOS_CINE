# Checklist de primera prueba integrada

## A. Preparación
- [ ] Docker Desktop funcionando
- [ ] Web Ailink_Cinema disponible en `../Web Ailink_Cinema` (Next.js CID app)
- [ ] CINE_AI_PLATFORM disponible en `../CINE_AI_PLATFORM`
- [ ] CID_SERVER/automation-engine disponible en `../CID_SERVER/automation-engine`
- [ ] ComfyUI arrancado en el host y respondiendo en `http://127.0.0.1:8188/system_stats`
- [ ] `.env` completado (NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY)
- [ ] `env/cid.env` completado
- [ ] `env/cine.env` completado
- [ ] `CID_SERVER/automation-engine/.env` completado

## B. Levantar servicios
```bash
docker compose up -d --build
docker compose ps
```

## C. Probar conectividad
### CID
- [ ] Abrir `http://TU_IP_LOCAL:8080`
- [ ] Login correcto
- [ ] Dashboard carga

### CINE_AI_PLATFORM
- [ ] Abrir `http://TU_IP_LOCAL:8080/api/cine/health`
- [ ] Responde 200

### ComfyUI
- [ ] `http://127.0.0.1:8188/system_stats` responde
- [ ] El contenedor `cine-api` puede alcanzar `host.docker.internal:8188`

## D. Demo comercial
- [ ] Crear tu usuario admin
- [ ] Crear demo.viewer y demo.operator
- [ ] Ejecutar seed demo de CID
- [ ] Crear lead nuevo desde formulario o panel
- [ ] Aplicar campaña
- [ ] Procesar cola
- [ ] Simular reply

## E. Demo de producción / storyboard
- [ ] Pegar fragmento de guion
- [ ] Ejecutar extract
- [ ] Ejecutar sequence plan
- [ ] Ejecutar storyboard render
- [ ] Ver imágenes generadas

## F. Cierre
- [ ] Export CSV desde CID
- [ ] Capturas o PDF de storyboard
- [ ] Material listo para enseñar a productoras
