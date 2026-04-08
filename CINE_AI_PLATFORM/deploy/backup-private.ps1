param(
  [string]$EnvFile = "",
  [string]$BackupRoot = "",
  [string[]]$Components = @("api", "n8n", "qdrant", "nginx"),
  [switch]$IncludeEnvFile
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

function Resolve-EnvFile {
  if (-not [string]::IsNullOrWhiteSpace($EnvFile)) {
    return $EnvFile
  }

  $privateEnvFile = Join-Path $repoRoot ".env.private"
  $exampleEnvFile = Join-Path $repoRoot ".env.private.example"

  if (Test-Path -Path $privateEnvFile) {
    return $privateEnvFile
  }

  return $exampleEnvFile
}

function Read-EnvFile {
  param([string]$Path)

  $values = @{}
  foreach ($line in Get-Content -Path $Path) {
    $trimmed = $line.Trim()
    if ([string]::IsNullOrWhiteSpace($trimmed)) {
      continue
    }
    if ($trimmed.StartsWith("#")) {
      continue
    }

    $pair = $trimmed.Split("=", 2)
    if ($pair.Count -ne 2) {
      continue
    }

    $values[$pair[0].Trim()] = $pair[1].Trim()
  }

  return $values
}

function Get-PlatformRoot {
  param([string]$StoragePath)

  $directory = [System.IO.DirectoryInfo]::new($StoragePath)
  if ($null -eq $directory.Parent -or $null -eq $directory.Parent.Parent -or $null -eq $directory.Parent.Parent.Parent) {
    throw "Cannot derive platform root from storage path: $StoragePath"
  }

  return $directory.Parent.Parent.Parent.FullName
}

function Copy-DirectoryContents {
  param(
    [string]$SourcePath,
    [string]$DestinationPath
  )

  New-Item -ItemType Directory -Path $DestinationPath -Force | Out-Null

  $items = @(Get-ChildItem -Force -LiteralPath $SourcePath)
  foreach ($item in $items) {
    Copy-Item -LiteralPath $item.FullName -Destination $DestinationPath -Recurse -Force
  }
}

$resolvedEnvFile = Resolve-EnvFile
if (-not (Test-Path -Path $resolvedEnvFile)) {
  throw "Missing env file: $resolvedEnvFile"
}

$envMap = Read-EnvFile -Path $resolvedEnvFile
$componentPaths = [ordered]@{
  api = $envMap["API_DATA_PATH"]
  n8n = $envMap["N8N_DATA_PATH"]
  qdrant = $envMap["QDRANT_STORAGE_PATH"]
  nginx = $envMap["NGINX_LOG_PATH"]
}

$selectedComponents = New-Object System.Collections.Generic.List[string]
foreach ($component in $Components) {
  $normalized = [string]$component
  $normalized = $normalized.Trim().ToLowerInvariant()
  if ([string]::IsNullOrWhiteSpace($normalized)) {
    continue
  }
  if (-not $componentPaths.Contains($normalized)) {
    throw "Unsupported component: $normalized"
  }
  if (-not $selectedComponents.Contains($normalized)) {
    $selectedComponents.Add($normalized)
  }
}

if ($IncludeEnvFile -and -not $selectedComponents.Contains("env")) {
  $selectedComponents.Add("env")
}

if ($selectedComponents.Count -eq 0) {
  throw "No components selected for backup."
}

if ([string]::IsNullOrWhiteSpace($BackupRoot)) {
  $platformRoot = Get-PlatformRoot -StoragePath $componentPaths["api"]
  $BackupRoot = Join-Path $platformRoot "backups\private"
}

New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupDir = Join-Path $BackupRoot "private-backup-$timestamp"
$componentsDir = Join-Path $backupDir "components"
$envDir = Join-Path $backupDir "env"

New-Item -ItemType Directory -Path $componentsDir -Force | Out-Null

$copiedComponents = @()
foreach ($component in $selectedComponents) {
  if ($component -eq "env") {
    if (Test-Path -Path $resolvedEnvFile) {
      New-Item -ItemType Directory -Path $envDir -Force | Out-Null
      Copy-Item -Path $resolvedEnvFile -Destination (Join-Path $envDir ".env.private") -Force
      $copiedComponents += "env"
    }
    continue
  }

  $sourcePath = $componentPaths[$component]
  if ([string]::IsNullOrWhiteSpace($sourcePath)) {
    throw "Missing source path for component: $component"
  }
  if (-not (Test-Path -Path $sourcePath)) {
    throw "Missing source path on disk for component ${component}: $sourcePath"
  }

  $destinationPath = Join-Path $componentsDir $component
  Copy-DirectoryContents -SourcePath $sourcePath -DestinationPath $destinationPath
  $copiedComponents += $component
}

$manifest = [pscustomobject]@{
  created_at = (Get-Date).ToString("s")
  env_file = $resolvedEnvFile
  backup_dir = $backupDir
  components = $copiedComponents
  component_paths = $componentPaths
}

$manifest | ConvertTo-Json -Depth 5 | Set-Content -Path (Join-Path $backupDir "manifest.json") -Encoding UTF8

$zipPath = "$backupDir.zip"
if (Test-Path -Path $zipPath) {
  Remove-Item -Path $zipPath -Force
}
Compress-Archive -Path $backupDir -DestinationPath $zipPath -Force

[pscustomobject]@{
  env_file = $resolvedEnvFile
  backup_dir = $backupDir
  backup_zip = $zipPath
  components = $copiedComponents
}
