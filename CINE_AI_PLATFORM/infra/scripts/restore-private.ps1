param(
  [string]$EnvFile = "",
  [string]$BackupZip = "",
  [switch]$FullRestore
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

if ([string]::IsNullOrWhiteSpace($EnvFile)) {
  $EnvFile = Join-Path $repoRoot ".env.private"
}
if ([string]::IsNullOrWhiteSpace($BackupZip)) {
  throw "Debe proporcionar -BackupZip con la ruta al archivo .zip generado por backup-private.ps1."
}
if (-not (Test-Path -Path $BackupZip)) {
  throw "Archivo backup no encontrado: $BackupZip"
}

function Read-EnvFile {
  param([string]$Path)
  $values = @{}
  foreach ($line in Get-Content -Path $Path) {
    if ([string]::IsNullOrWhiteSpace($line) -or $line.Trim().StartsWith("#")) { continue }
    $pair = $line.Split("=", 2)
    if ($pair.Count -eq 2) { $values[$pair[0].Trim()] = $pair[1].Trim() }
  }
  return $values
}

if (-not (Test-Path -Path $EnvFile)) { throw "Falta env file: $EnvFile" }
$envMap = Read-EnvFile -Path $EnvFile

$restoreMap = @{
  "api_data" = $envMap["API_DATA_PATH"]
}

if ($FullRestore) {
  $restoreMap["n8n_data"] = $envMap["N8N_DATA_PATH"]
  $restoreMap["qdrant_storage"] = $envMap["QDRANT_STORAGE_PATH"]
  $restoreMap["env_file"] = $EnvFile
}

$tempDir = Join-Path $env:TEMP "cine_rest_$(Get-Date -Format 'yyyyMMddHHmmss')"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

Write-Host "Descomprimiendo y restaurando backup $BackupZip ..."
try {
  Expand-Archive -Path $BackupZip -DestinationPath $tempDir -Force
  
  foreach ($key in $restoreMap.Keys) {
    $dest = $restoreMap[$key]
    $src = Join-Path $tempDir $key
    
    if (-not [string]::IsNullOrWhiteSpace($dest) -and (Test-Path -Path $src)) {
      Write-Host "Restaurando capa $key hacia $dest"
      if ($key -eq "env_file") {
        Copy-Item -Path "$src\*" -Destination (Split-Path $dest -Parent) -Force
      } else {
        if (-not (Test-Path -Path $dest)) { New-Item -ItemType Directory -Path $dest -Force | Out-Null }
        Copy-Item -Path "$src\*" -Destination $dest -Recurse -Force
      }
    } else {
       Write-Host "Omitiendo $key (no existe en backup seleccionado o variables vacías)" -ForegroundColor Yellow
    }
  }
  Write-Host "Restore completado íntegramente." -ForegroundColor Green
  Write-Host "Reinicia los contenedores con .\deploy\start-private.ps1 para montar los nuevos datos."
} finally {
  Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}
