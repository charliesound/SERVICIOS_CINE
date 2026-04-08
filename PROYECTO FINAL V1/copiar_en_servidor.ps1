# ================================================
# COPIAR DESDE DISCO EXTERNO AL SERVIDOR
# ================================================
# Ejecutar en el SERVIDOR despues de conectar el disco

param(
    [switch]$Simular  # Usa -Simular para probar sin copiar
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  COPIAR PROYECTO AL SERVIDOR" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ─── Detectar disco externo ───
Write-Host "[1/5] Buscando disco externo..." -ForegroundColor Cyan

$discoExt = Get-PSDrive -PSProvider FileSystem | Where-Object { 
    $_.Used -gt 0 -and $_.Free -gt 0 -and 
    $_.Name -ne "C" -and $_.Name -ne "G"
}

if ($discoExt.Count -eq 0) {
    Write-Host "    [ERROR] No se encontro disco externo" -ForegroundColor Red
    Write-Host "    Verifica que el disco esta conectado y formateado" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Unidades disponibles:" -ForegroundColor White
    Get-PSDrive -PSProvider FileSystem | Format-Table Name, @{N="Tamano";E={"$([math]::Round($_.Used/1GB, 1)) GB"}}, Free -AutoSize
    exit 1
}

$letra = $discoExt[0].Name
$origen = "${letra}:\SERVICIOS_CINE"

if (-not (Test-Path $origen)) {
    $origen = "${letra}:\"
    $subcarpetas = Get-ChildItem "${letra}:\" -Directory -ErrorAction SilentlyContinue
    $encontrado = $subcarpetas | Where-Object { $_.Name -like "*CINE*" -or $_.Name -like "*SERVICIO*" }
    if ($encontrado) {
        $origen = $encontrado[0].FullName
    }
}

if (-not (Test-Path $origen)) {
    Write-Host "    [ERROR] No se encontro carpeta SERVICIOS_CINE en $letra":\" -ForegroundColor Red
    Write-Host "    Contenido del disco:" -ForegroundColor Yellow
    Get-ChildItem "${letra}:\" -Directory | Format-Table Name
    exit 1
}

Write-Host "    Disco encontrado: ${letra}:\" -ForegroundColor Green
Write-Host "    Proyecto: $origen" -ForegroundColor White

# ─── Crear destino ───
Write-Host ""
Write-Host "[2/5] Preparando destino G:\..." -ForegroundColor Cyan

$destino = "G:\SERVICIOS_CINE"

if (-not (Test-Path "G:\")) {
    Write-Host "    [ERROR] La unidad G: no existe" -ForegroundColor Red
    Write-Host "    Crea la unidad G: en Disk Management" -ForegroundColor Yellow
    Write-Host "    O cambia la letra del disco a G:" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $destino)) {
    New-Item -ItemType Directory -Path $destino -Force | Out-Null
    Write-Host "    Carpeta creada: $destino" -ForegroundColor Green
} else {
    Write-Host "    Carpeta ya existe: $destino" -ForegroundColor Green
}

# ─── Calcular tamanos ───
Write-Host ""
Write-Host "[3/5] Calculando tamanos..." -ForegroundColor Cyan

$sizeMain = [math]::Round((Get-ChildItem $origen -Recurse -Exclude node_modules,venv,.venv,__pycache__,.next,.git -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum / 1GB, 1)
Write-Host "    Proyecto principal: ~$sizeMain GB" -ForegroundColor White

$sizeTotal = $sizeMain

$nmPath = Join-Path $origen "Web Ailink_Cinema\node_modules"
if (Test-Path $nmPath) {
    $sz = [math]::Round((Get-ChildItem $nmPath -Recurse -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum / 1GB, 1)
    Write-Host "    Web Ailink_Cinema node_modules: ~$sz GB" -ForegroundColor Gray
    $sizeTotal += $sz
}

$venvPath = Join-Path $origen "CID_SERVER\automation-engine\venv"
if (Test-Path $venvPath) {
    $sz = [math]::Round((Get-ChildItem $venvPath -Recurse -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum / 1GB, 1)
    Write-Host "    Automation engine venv: ~$sz GB" -ForegroundColor Gray
    $sizeTotal += $sz
}

Write-Host "    TOTAL: ~$sizeTotal GB" -ForegroundColor Yellow

# ─── Copiar proyecto principal ───
Write-Host ""
Write-Host "[4/5] Copiando proyecto principal..." -ForegroundColor Cyan

$excluir = @(
    "\node_modules\","\venv\","\.venv\","\__pycache__\",
    "\.next\","\.cache\","\.git\","\dist\","\build\",
    "\*.pyc","\*.pyo","\.DS_Store","\Thumbs.db"
) -join " "

if ($Simular) {
    Write-Host "    [SIMULACION - no se copiara nada]" -ForegroundColor Yellow
    Write-Host "    robocopy $origen $destino /L /E /NP /NDL" -ForegroundColor Gray
} else {
    & robocopy $origen $destino /E /MIR /R:3 /W:2 /MT:32 /NP /NDL /XF $excluir
    $rc = $LASTEXITCODE
    if ($rc -lt 8) {
        Write-Host "    Proyecto principal copiado" -ForegroundColor Green
    } else {
        Write-Host "    Errores en robocopy (codigo: $rc)" -ForegroundColor Yellow
    }
}

# ─── Copiar node_modules y venv ───
Write-Host ""
Write-Host "[5/5] Copiando node_modules y venv..." -ForegroundColor Cyan

$copiar = @(
    @{Src="Web Ailink_Cinema\node_modules"; Tag="Web Ailink_Cinema node_modules"}
    @{Src="CID_SERVER\automation-engine\venv"; Tag="Automation engine venv"}
    @{Src="CINE_AI_PLATFORM\apps\web\node_modules"; Tag="CINE_AI_PLATFORM web node_modules"}
)

foreach ($item in $copiar) {
    $srcPath = Join-Path $origen $item.Src
    $dstPath = Join-Path $destino $item.Src
    
    if (Test-Path $srcPath) {
        $sz = [math]::Round((Get-ChildItem $srcPath -Recurse -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum / 1GB, 1)
        Write-Host "    $($item.Tag) (~${sz} GB)..." -ForegroundColor Gray -NoNewline
        
        if ($Simular) {
            Write-Host " [simularia]"
        } else {
            & robocopy $srcPath $dstPath /E /R:2 /W:1 /MT:16 /NP /NDL | Out-Null
            if ($LASTEXITCODE -lt 8) {
                Write-Host " OK" -ForegroundColor Green
            } else {
                Write-Host " Warning" -ForegroundColor Yellow
            }
        }
    }
}

# ─── Verificar ───
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  VERIFICACION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$carpetas = @(
    "PROYECTO FINAL V1",
    "Web Ailink_Cinema",
    "CINE_AI_PLATFORM",
    "CID_SERVER\automation-engine"
)

$ok = $true
foreach ($c in $carpetas) {
    $path = Join-Path $destino $c
    if (Test-Path $path) {
        Write-Host "    $c OK" -ForegroundColor Green
    } else {
        Write-Host "    $c FALTANTE" -ForegroundColor Red
        $ok = $false
    }
}

if ($ok) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  COPIA COMPLETADA" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Ejecuta el setup:" -ForegroundColor White
    Write-Host ""
    Write-Host "  cd G:\SERVICIOS_CINE\" -ForegroundColor Yellow
    Write-Host "  cd 'PROYECTO FINAL V1'" -ForegroundColor Yellow
    Write-Host "  .\setup.ps1" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "  [WARNING] Algunas carpetas faltan. Revisa la copia." -ForegroundColor Yellow
}

Write-Host ""
