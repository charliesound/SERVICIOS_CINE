# Demo Comercial Controlada V1

## Que es este producto
CINE AI PLATFORM lee un guion cinematografico, lo desglosa en escenas y elementos visuales, planifica una cobertura de planos coherente y genera storyboard/render a partir de esa planificacion.

No es un generador de imagenes generico. Es un sistema que entiende la estructura narrativa y propone una cobertura visual razonable para preproduccion.

## Que entra
- Un fragmento de guion en texto plano (formato screenplay basico).
- Ejemplo real incluido en el repo:
  - `examples/demo_screenplay_01.txt`

## Que sale
- Escenas parseadas con headings, localizacion y tiempo del dia
- Desglose por escena: personajes, acciones, props, elementos visuales, candidatos de movimiento
- Planificacion cinematografica: beats con tipo, shot_intent y motivacion
- Grounding visual por shot: sujetos primarios/secundarios, composicion, props, accion
- Continuidad formal en escenas conversacionales: eje, direccion de mirada, posicion en pantalla
- Shots con prompts enriquecidos listos para render
- Si ComfyUI esta disponible: imagenes generadas por shot

## Flujo end-to-end

### Paso 1: Preparar el entorno
```powershell
# En el ordenador de casa (servidor)
powershell -ExecutionPolicy Bypass -File .\deploy\start-private.ps1
```

### Paso 2: Validar conectividad
```powershell
powershell -ExecutionPolicy Bypass -File .\infra\scripts\smoke-private.ps1
```

### Paso 3: Cargar el caso de demo
```powershell
$demoScript = Get-Content -Raw -Path .\examples\demo_screenplay_01.txt
```

### Paso 4: Ejecutar el planner
```powershell
$baseUrl = "http://127.0.0.1"  # o tu hostname Tailscale
$token = "TU_TOKEN_DEMO"  # bootstrap user token

$headers = @{ Authorization = "Bearer $token" }
$body = @{ script_text = $demoScript; sequence_id = "demo_001" } | ConvertTo-Json

$response = Invoke-RestMethod -Method Post -Uri "$baseUrl/api/sequence/plan-and-render" -ContentType "application/json" -Headers $headers -Body $body
```

### Paso 5: Inspeccionar resultados
```powershell
# Escenas parseadas
$response.parsed_scenes | ConvertTo-Json -Depth 4

# Breakdown por escena
$response.scene_breakdowns | ConvertTo-Json -Depth 4

# Planificacion con beat_type, shot_intent, motivation
$response.beats | ConvertTo-Json -Depth 4

# Shots con grounding y continuity_formal
$response.shots | ConvertTo-Json -Depth 4
```

### Paso 6: Render (si ComfyUI esta disponible)
El endpoint `plan-and-render` ya lanza los jobs automaticamente.
Los resultados se consultan via:
```powershell
Invoke-RestMethod -Method Get -Uri "$baseUrl/api/render/jobs" -Headers $headers
```

### Paso 7: Presentar
- Mostrar parsed_scenes → el sistema entiende el guion
- Mostrar scene_breakdowns → desglose cinematografico automatico
- Mostrar beats con shot_intent → planificacion visual coherente
- Mostrar grounding → decisiones visuales justificadas
- Mostrar continuity_formal → coherencia conversacional
- Mostrar renders → storyboard visual resultante

## Pre-demo checklist

### Infraestructura
- [ ] Ordenador de casa encendido y accesible
- [ ] Docker Desktop corriendo
- [ ] WSL2 disponible
- [ ] ComfyUI arrancado en WSL2 (`deploy/start-comfy-wsl.ps1`)
- [ ] Tailscale conectado en laptop y servidor
- [ ] Stack privado arriba (`deploy/start-private.ps1`)

### Validacion tecnica
- [ ] `smoke-private.ps1` pasa sin errores
- [ ] `check-comfy-bridge.ps1` reporta host y container OK
- [ ] Endpoint `/api/health` responde 200
- [ ] Endpoint `/api/health/details` reporta ComfyUI reachable
- [ ] Token de demo valido (bootstrap user)

### Caso de demo
- [ ] `examples/demo_screenplay_01.txt` existe y es legible
- [ ] El guion se carga correctamente en la variable de demo
- [ ] Se ha probado una ejecucion completa antes de la demo real

### Presentacion
- [ ] Navegador abierto en el panel web
- [ ] Secuencia de presentacion preparada:
  1. Mostrar el guion
  2. Ejecutar planner
  3. Mostrar escenas parseadas
  4. Mostrar breakdown
  5. Mostrar planificacion visual
  6. Mostrar grounding y continuidad
  7. Mostrar renders (si disponibles)
- [ ] Explicacion comercial breve preparada (ver seccion narrativa)

## Recovery checklist

### Backend no responde
1. Verificar Docker Desktop
2. `docker compose --env-file .env.private -f docker-compose.private.yml ps`
3. `deploy/start-private.ps1` si necesario
4. Revisar logs: `deploy/logs-private.ps1 -Services api`

### ComfyUI no responde
1. Verificar WSL2: `wsl --list --running`
2. `check-comfy-bridge.ps1 -SkipContainerCheck`
3. Si ComfyUI cayo: `deploy/start-comfy-wsl.ps1 -ComfyPath "/home/<user>/ComfyUI"`
4. Re-validar bridge completo

### Tailscale no conecta
1. Verificar Tailscale en ambos extremos
2. Probar ping entre laptop y servidor
3. Fallback a local: usar `http://127.0.0.1` en el servidor
4. Si no hay alternativa, hacer demo solo con planner (sin render)

### Render tarda demasiado
1. Mostrar planificacion y grounding como resultado intermedio valido
2. Explicar que el render es asincrono
3. Mostrar resultados de una ejecucion previa si existen
4. No bloquear la demo esperando renders

### No llegan imagenes
1. Verificar jobs: `GET /api/render/jobs`
2. Revisar estado: failed/running/queued
3. Si todos failed: revisar ComfyUI y logs
4. Fallback: mostrar planificacion visual como storyboard textual

## Narrativa comercial breve

### Problema
La preproduccion cinematografica requiere desglosar guiones, planificar cobertura visual y generar storyboard. Hoy esto se hace manualmente con horas de trabajo especializado.

### Solucion
CINE AI PLATFORM lee un guion, lo entiende cinematicamente y propone una cobertura visual coherente con continuidad de eje, grounding por intencion de plano y desglose automatico de elementos visuales.

### Que entra
Un guion en texto plano.

### Que sale
- Escenas estructuradas
- Desglose de personajes, props, accion y elementos visuales
- Planificacion de planos con intencion cinematografica
- Continuidad conversacional coherente
- Prompts enriquecidos listos para generacion
- Storyboard visual (con ComfyUI)

### Valor diferencial
No es un generador de imagenes generico. Es un sistema que entiende la estructura narrativa y propone una cobertura visual razonable, con continuidad de eje, grounding por intencion de plano y desglose cinematografico automatico.

### Para quien
- Directores y directores de fotografia en fase de preproduccion
- Productores que necesitan estimar cobertura visual rapidamente
- Equipos de storyboard que buscan un punto de partida estructurado

## Estado de automatizacion

### Automatizado
- Parsing de guion (V1)
- Breakdown cinematografico (V2)
- Planificacion visual (V3)
- Grounding por shot (V1)
- Continuidad formal conversacional (V1)
- Plan-and-render end-to-end
- Smoke tests operativos

### Operativo/manual
- Arranque de ComfyUI en WSL2 (script disponible pero requiere ejecucion)
- Configuracion de Tailscale entre laptop y servidor
- Validacion de conectividad antes de demo
- Presentacion y narrativa comercial (preparada pero manual)

### No disponible todavia
- Parser Fountain/FDX
- Evaluacion visual automatica de renders
- Ranking de imagenes
- Frontend comercial definitivo
- Despliegue multiusuario
- Observabilidad compleja
