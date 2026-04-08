param(
  [string]$EnvFile = "",
  [string]$BackupDir = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

if ([string]::IsNullOrWhiteSpace($EnvFile)) {
  $EnvFile = Join-Path $repoRoot ".env.private"
}
if ([string]::IsNullOrWhiteSpace($BackupDir)) {
  $BackupDir = Join-Path $repoRoot "backups"
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

if (-not (Test-Path -Path $BackupDir)) {
  New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$archiveName = "stack-private-backup-$timestamp.zip"
$archivePath = Join-Path $BackupDir $archiveName

$backupMap = @{
  "api_data" = $envMap["API_DATA_PATH"]
  "n8n_data" = $envMap["N8N_DATA_PATH"]
  "qdrant_storage" = $envMap["QDRANT_STORAGE_PATH"]
  "nginx_logs" = $envMap["NGINX_LOG_PATH"]
  "env_file" = $EnvFile
}

$tempDir = Join-Path $env:TEMP "cine_back_$timestamp"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

Write-Host "Creando backup completo en: $archivePath"
try {
  foreach ($key in $backupMap.Keys) {
    $src = $backupMap[$key]
    if ([string]::IsNullOrWhiteSpace($src)) { continue }
    if (Test-Path -Path $src) {
      $dest = Join-Path $tempDir $key
      New-Item -ItemType Directory -Path $dest -Force | Out-Null
      
      if (Test-Path -Path $src -PathType Container) {
        Copy-Item -Path "$src\*" -Destination $dest -Recurse -Force -ErrorAction SilentlyContinue
      } else {
        Copy-Item -Path $src -Destination $dest -Force -ErrorAction SilentlyContinue
      }
      Write-Host "Anexado $key -> $src"
    } else {
      Write-Host "Omitido $key -> $src (No encontrado)" -ForegroundColor Yellow
    }
  }

  Compress-Archive -Path "$tempDir\*" -DestinationPath $archivePath -Force
  Write-Host "Backup de $archiveName finalizado exitosamente." -ForegroundColor Green
} finally {
  Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
}
