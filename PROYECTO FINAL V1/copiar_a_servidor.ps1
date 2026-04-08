# ================================================
# COPIAR PROYECTO A SERVIDOR (desde laptop)
# ================================================
# Ejecutar en TU LAPTOP (PowerShell como Administrador)
# Destino: Servidor Windows via red

param(
    [string]$ServidorIP = "",      # IP del servidor (ej: 192.168.1.100)
    [string]$Origen = "",          # Unidad del disco externo (ej: F:\)
    [switch]$SoloPreparar          # Solo genera el comando sin ejecutar
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  COPIAR PROYECTO AL SERVIDOR" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ─── Detectar disco externo ───
if (-not $Origen) {
    Write-Host "[1/4] Detectando disco externo..." -ForegroundColor Cyan
    
    $discos = Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Used -gt 0 -and $_.Free -gt 0 }
    $discoExt = $discos | Where-Object { 
        $_.Name -ne "C" -and $_.Name -ne "D" -and $_.Name -ne "X" -and $_.Name -ne "Y" -and $_.Name -ne "Z"
    } | Select-Object -First 1
    
    if ($discoExt) {
        $Origen = "$($discoExt.Name):\SERVICIOS_CINE"
        Write-Host "    Disco detectado: $($discoExt.Name):\" -ForegroundColor Green
        Write-Host "    Buscando proyecto..." -ForegroundColor Gray
        
        # Buscar la carpeta correcta
        $unidades = Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Name -eq $discoExt.Name }
        foreach ($u in $unidades) {
            $ruta = Join-Path "$($u.Name):\" "SERVICIOS_CINE"
            if (Test-Path $ruta) {
                $Origen = $ruta
                Write-Host "    Proyecto encontrado: $ruta" -ForegroundColor Green
                break
            }
        }
        
        # Si no existe, buscar en subcarpetas
        if (-not (Test-Path $Origen)) {
            $buscar = Get-ChildItem "$($discoExt.Name):\" -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -like "*CINE*" -or $_.Name -like "*SERVICIO*" }
            if ($buscar) {
                $Origen = $buscar[0].FullName
                Write-Host "    Proyecto encontrado: $Origen" -ForegroundColor Green
            }
        }
    }
    
    if (-not (Test-Path $Origen)) {
        Write-Host "    No se encontro automaticamente. Buscando en todas las unidades..." -ForegroundColor Yellow
        Get-PSDrive -PSProvider FileSystem | ForEach-Object {
            $ruta = Join-Path "$($_.Name):\" "SERVICIOS_CINE"
            if (Test-Path $ruta) {
                $Origen = $ruta
                Write-Host "    ENCONTRADO: $Origen" -ForegroundColor Green
            }
        }
    }
    
    if (-not $Origen -or -not (Test-Path $Origen)) {
        Write-Host ""
        Write-Host "[ERROR] No se encontro el proyecto en el disco externo" -ForegroundColor Red
        Write-Host "Indica la ruta manualmente con -Origen F:\CARPETA" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Unidades disponibles:" -ForegroundColor White
        Get-PSDrive -PSProvider FileSystem | Format-Table Name, Used, Free -AutoSize
        exit 1
    }
}

# ─── IP del servidor ───
if (-not $ServidorIP) {
    Write-Host ""
    Write-Host "[2/4] Indica la IP del servidor" -ForegroundColor Cyan
    Write-Host "    (ej: 192.168.1.100)" -ForegroundColor Gray
    $ServidorIP = Read-Host "    IP del servidor"
    
    if (-not $ServidorIP) {
        Write-Host "[ERROR] IP requerida" -ForegroundColor Red
        exit 1
    }
}

# ─── Calcular tamanos ───
Write-Host ""
Write-Host "[3/4] Calculando tamanos..." -ForegroundColor Cyan

$sizeMain = [math]::Round((Get-ChildItem $Origen -Recurse -Exclude node_modules,venv,.venv,__pycache__,.next,.git -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum / 1GB, 1)
Write-Host "    Proyecto principal: ~$sizeMain GB" -ForegroundColor White

$sizeNodeModules = 0
$sizeVenv = 0

$nmPath = Join-Path $Origen "Web Ailink_Cinema\node_modules"
if (Test-Path $nmPath) {
    $sizeNodeModules = [math]::Round((Get-ChildItem $nmPath -Recurse -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum / 1GB, 1)
    Write-Host "    Web Ailink_Cinema node_modules: ~$sizeNodeModules GB" -ForegroundColor Gray
}

$venvPath = Join-Path $Origen "CID_SERVER\automation-engine\venv"
if (Test-Path $venvPath) {
    $sizeVenv = [math]::Round((Get-ChildItem $venvPath -Recurse -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum / 1GB, 1)
    Write-Host "    Automation engine venv: ~$sizeVenv GB" -ForegroundColor Gray
}

$total = $sizeMain + $sizeNodeModules + $sizeVenv
Write-Host ""
Write-Host "    TOTAL ESTIMADO: ~$total GB" -ForegroundColor Yellow

$destino = "\\$ServidorIP\G`$\SERVICIOS_CINE"

Write-Host ""
Write-Host "[4/4] Destino: $destino" -ForegroundColor Cyan
Write-Host ""

if ($SoloPreparar) {
    Write-Host "=== COMANDO A EJECUTAR EN EL SERVIDOR ===" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "En el servidor, ejecuta primero para permitir el acceso:" -ForegroundColor White
    Write-Host "    winrm quickconfig" -ForegroundColor Gray
    Write-Host "    Enable-PSRemoting -Force" -ForegroundColor Gray
    exit 0
}

# ─── Verificar conectividad ───
Write-Host "Verificando conexion al servidor..." -ForegroundColor Cyan
$ping = Test-Connection -ComputerName $ServidorIP -Count 1 -Quiet
if (-not $ping) {
    Write-Host "    [ERROR] No se puede hacer ping a $ServidorIP" -ForegroundColor Red
    Write-Host "    Verifica que el servidor esta encendido y la IP es correcta" -ForegroundColor Yellow
    exit 1
}
Write-Host "    Servidor accesible" -ForegroundColor Green

# ─── Verificar acceso a G$ ───
Write-Host "Verificando acceso a G$ en el servidor..." -ForegroundColor Cyan
try {
    $null = Get-ChildItem $destino -ErrorAction Stop
    Write-Host "    Acceso OK a $destino" -ForegroundColor Green
} catch {
    Write-Host "    Primer intento fallido, intentando crear..." -ForegroundColor Yellow
    try {
        New-Item -ItemType Directory -Path $destino -Force | Out-Null
        Write-Host "    Carpeta creada: $destino" -ForegroundColor Green
    } catch {
        Write-Host "    [ERROR] No se pudo acceder a $destino" -ForegroundColor Red
        Write-Host "    Asegurate de:" -ForegroundColor Yellow
        Write-Host "    1. Compartir la unidad G en el servidor (G$)" -ForegroundColor Gray
        Write-Host "    2. Tu usuario tiene permisos de administrador en el servidor" -ForegroundColor Gray
        Write-Host "    3. El firewall permite SMB (puerto 445)" -ForegroundColor Gray
        Write-Host ""
        Write-Host "    En el SERVIDOR, ejecuta PowerShell como Admin:" -ForegroundColor Yellow
        Write-Host "    Set-SmbServerConfiguration -AllowAuthenticationHosts $env:COMPUTERNAME -Force" -ForegroundColor Gray
        Write-Host "    New-SmbShare -Name 'G`'$ -Path 'G:\' -FullAccess 'Everyone'" -ForegroundColor Gray
        exit 1
    }
}

# ─── COPIA ───
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  INICIANDO COPIA" -ForegroundColor Cyan
Write-Host "  (Presiona Ctrl+C para cancelar)" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Copiar proyecto principal (sin temporales)
Write-Host "[1/2] Copiando proyecto principal (~${sizeMain} GB)..." -ForegroundColor Cyan
$excluirTemporal = @(
    "\node_modules\","\venv\","\.venv\","\__pycache__\",
    "\.next\","\.cache\","\.git\","\dist\","\build\",
    "\*.pyc","\*.pyo","\.DS_Store","\Thumbs.db"
) -join " "

& robocopy $Origen $destino /E /MIR /R:3 /W:3 /MT:16 /NP /NDL /XF $excluirTemporal

if ($LASTEXITCODE -lt 8) {
    Write-Host "    Proyecto principal copiado" -ForegroundColor Green
} else {
    Write-Host "    Errores en copia principal (codigo: $LASTEXITCODE)" -ForegroundColor Yellow
}

# 2. Copiar node_modules y venv
Write-Host ""
Write-Host "[2/2] Copiando node_modules y venv..." -ForegroundColor Cyan

$copiarAhora = @(
    @{Src="Web Ailink_Cinema\node_modules"; Tag="Web Ailink_Cinema node_modules"}
    @{Src="CID_SERVER\automation-engine\venv"; Tag="Automation engine venv"}
    @{Src="CINE_AI_PLATFORM\apps\web\node_modules"; Tag="CINE_AI_PLATFORM web node_modules"}
)

foreach ($item in $copiarAhora) {
    $srcPath = Join-Path $Origen $item.Src
    $dstPath = Join-Path $destino $item.Src
    if (Test-Path $srcPath) {
        $sz = [math]::Round((Get-ChildItem $srcPath -Recurse -ErrorAction SilentlyContinue | Measure-Object Length -Sum).Sum / 1GB, 1)
        Write-Host "    $($item.Tag) (~${sz} GB)..." -ForegroundColor Gray -NoNewline
        & robocopy $srcPath $dstPath /E /R:3 /W:3 /MT:8 /NP /NDL | Out-Null
        if ($LASTEXITCODE -lt 8) {
            Write-Host " OK" -ForegroundColor Green
        } else {
            Write-Host " Warning" -ForegroundColor Yellow
        }
    }
}

# ─── Resumen ───
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  COPIA COMPLETADA" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "  En el SERVIDOR, ejecuta:" -ForegroundColor White
Write-Host ""
Write-Host "  cd G:\SERVICIOS_CINE\" -ForegroundColor Yellow
Write-Host "  cd 'PROYECTO FINAL V1'" -ForegroundColor Yellow
Write-Host "  .\setup.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "  O manualmente:" -ForegroundColor White
Write-Host "  docker compose up -d --build" -ForegroundColor Gray
Write-Host ""
