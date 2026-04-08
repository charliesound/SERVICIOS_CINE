# SERVICIOS_CINE - Copiar al Servidor
# Este script copia el proyecto del disco externo al disco interno del servidor

param(
    [string]$Origen = "",
    [string]$Destino = "",
    [switch]$Auto
)

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SERVICIOS_CINE - Copiar al Servidor" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Detectar discos disponibles
Write-Host "[INFO] Discos disponibles:" -ForegroundColor Yellow
Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Used -gt 0 } | ForEach-Object {
    Write-Host "  $($_.Name):\  ($($_.Used / 1GB -split '\.')[0] GB usados)" -ForegroundColor Gray
}
Write-Host ""

# Si no se proporcionan parametros, preguntar
if (-not $Origen) {
    $discos = @()
    Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Used -gt 0 } | ForEach-Object { $discos += $_.Name }

    Write-Host "Introduce la letra del disco de ORIGEN (ej: E):" -ForegroundColor White
    $letraOrigen = Read-Host

    if ($letraOrigen -notmatch '^[A-Za-z]$') {
        Write-Host "[ERROR] Letra de disco no valida" -ForegroundColor Red
        exit 1
    }

    $Origen = "${letraOrigen}:\SERVICIOS_CINE"

    if (-not (Test-Path $Origen)) {
        Write-Host "[ERROR] No se encontro $Origen" -ForegroundColor Red
        Write-Host "Asegurate de que el disco externo esta conectado" -ForegroundColor Yellow
        exit 1
    }
}

if (-not $Destino) {
    Write-Host "Introduce la ruta de DESTINO en disco interno (ej: D:\SERVICIOS_CINE):" -ForegroundColor White
    $Destino = Read-Host

    if (-not $Destino) {
        Write-Host "[ERROR] Destino no especificado" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuracion:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Origen:   $Origen" -ForegroundColor White
Write-Host "  Destino:  $Destino" -ForegroundColor White
Write-Host ""

# Verificar origen
if (-not (Test-Path $Origen)) {
    Write-Host "[ERROR] Origen no encontrado: $Origen" -ForegroundColor Red
    exit 1
}

# Verificar que src y src_frontend existen
if (-not (Test-Path "$Origen\src")) {
    Write-Host "[ERROR] No se encontro carpeta src en el origen" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "$Origen\src_frontend")) {
    Write-Host "[ERROR] No se encontro carpeta src_frontend en el origen" -ForegroundColor Red
    exit 1
}

# Crear directorio destino si no existe
$destinoDir = Split-Path $Destino -Parent
if (-not (Test-Path $destinoDir)) {
    Write-Host "[INFO] Creando directorio destino..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $destinoDir -Force | Out-Null
}

# Confirmar si el destino ya existe
if (Test-Path $Destino) {
    Write-Host "[AVISO] El directorio destino ya existe" -ForegroundColor Yellow
    Write-Host "Los archivos existentes seran sobreescritos" -ForegroundColor Yellow
    if (-not $Auto) {
        Write-Host ""
        Write-Host "Continuar? (S/N): " -NoNewline -ForegroundColor White
        $confirm = Read-Host
        if ($confirm -ne "S" -and $confirm -ne "s") {
            Write-Host "[CANCELADO] Operacion cancelada por el usuario" -ForegroundColor Red
            exit 0
        }
    }
}

Write-Host ""
Write-Host "[INFO] Copiando archivos..." -ForegroundColor Yellow
Write-Host ""

# Archivos/carpetas a excluir de la copia
$excludePatterns = @(
    '__pycache__',
    '*.pyc',
    'node_modules',
    '.git',
    '.venv',
    'venv',
    '*.log',
    'tmp_*.log',
    '*.tmp'
)

# Construir parametros para Copy-Item
$copyParams = @{
    Path = $Origen
    Destination = $Destino
    Recurse = $true
    Force = $true
}

# Filtrar archivos a excluir
$filesToCopy = Get-ChildItem -Path $Origen -Recurse -File | Where-Object {
    $relativePath = $_.FullName.Substring($Origen.Length + 1)
    foreach ($pattern in $excludePatterns) {
        if ($pattern.StartsWith('*') -and $relativePath -like $pattern) {
            return $false
        }
        if ($relativePath -eq $pattern -or $relativePath.StartsWith($pattern + '\')) {
            return $false
        }
    }
    return $true
}

# Copiar archivos
$totalFiles = $filesToCopy.Count
$copiedFiles = 0
$errors = 0

foreach ($file in $filesToCopy) {
    $relativePath = $file.FullName.Substring($Origen.Length + 1)
    $destPath = Join-Path $Destino $relativePath
    $destDir = Split-Path $destPath -Parent

    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }

    try {
        Copy-Item -Path $file.FullName -Destination $destPath -Force
        $copiedFiles++

        # Mostrar progreso cada 50 archivos
        if ($copiedFiles % 50 -eq 0) {
            $percent = [math]::Round(($copiedFiles / $totalFiles) * 100)
            Write-Host "  Progreso: $copiedFiles / $totalFiles ($percent%)" -ForegroundColor Gray
        }
    }
    catch {
        $errors++
        Write-Host "  [ERROR] $relativePath" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Resultado de la copia:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Archivos copiados: $copiedFiles" -ForegroundColor Green
if ($errors -gt 0) {
    Write-Host "  Errores: $errors" -ForegroundColor Red
}
Write-Host ""

# Verificar estructura copiada
Write-Host "[INFO] Verificando estructura..." -ForegroundColor Yellow
$estructuraOk = $true

$carpetasRequeridas = @(
    "src",
    "src_frontend",
    "docs",
    "handoff"
)

foreach ($carpeta in $carpetasRequeridas) {
    $path = Join-Path $Destino $carpeta
    if (Test-Path $path) {
        Write-Host "  [OK] $carpeta" -ForegroundColor Green
    }
    else {
        Write-Host "  [FALTA] $carpeta" -ForegroundColor Red
        $estructuraOk = $false
    }
}

# Verificar archivos clave
$archivosClave = @(
    "src\app.py",
    "src\requirements.txt",
    "src_frontend\package.json",
    "setup.bat",
    "start_backend.bat",
    "start_frontend.bat"
)

Write-Host ""
Write-Host "[INFO] Verificando archivos clave..." -ForegroundColor Yellow
foreach ($archivo in $archivosClave) {
    $path = Join-Path $Destino $archivo
    if (Test-Path $path) {
        Write-Host "  [OK] $archivo" -ForegroundColor Green
    }
    else {
        Write-Host "  [FALTA] $archivo" -ForegroundColor Red
        $estructuraOk = $false
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

if ($estructuraOk) {
    Write-Host "Copia completada exitosamente!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Proximo paso:" -ForegroundColor Cyan
    Write-Host "  1. Ejecutar setup.bat en el servidor" -ForegroundColor White
    Write-Host "  2. Arrancar ComfyUI backends" -ForegroundColor White
    Write-Host "  3. Ejecutar start_backend.bat" -ForegroundColor White
    Write-Host "  4. Ejecutar start_frontend.bat" -ForegroundColor White
    Write-Host ""
    Write-Host "Ver documentacion: docs\GUIA_DESPLIEGUE_SERVIDOR.md" -ForegroundColor Gray
}
else {
    Write-Host "La copia tuvo problemas. Revisa los errores arriba." -ForegroundColor Red
}

Write-Host "========================================" -ForegroundColor Cyan
