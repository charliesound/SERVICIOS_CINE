param(
  [string]$EnvFile = "",
  [string]$BackupPath = "",
  [string[]]$Components = @("api", "n8n", "qdrant", "nginx"),
  [switch]$IncludeEnvFile,
  [switch]$Force
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

function Clear-DirectoryContents {
  param([string]$Path)

  if (-not (Test-Path -Path $Path)) {
    New-Item -ItemType Directory -Path $Path -Force | Out-Null
    return
  }

  $items = @(Get-ChildItem -Force -LiteralPath $Path)
  foreach ($item in $items) {
    Remove-Item -LiteralPath $item.FullName -Recurse -Force
  }
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

if ([string]::IsNullOrWhiteSpace($BackupPath)) {
  throw "BackupPath is required."
}

if (-not $Force) {
  throw "Restore is destructive. Re-run with -Force after stopping the stack."
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
  throw "No components selected for restore."
}

$temporaryExtractPath = $null
$backupRoot = $null

if ((Test-Path -Path $BackupPath -PathType Leaf) -and ([System.IO.Path]::GetExtension($BackupPath).ToLowerInvariant() -eq ".zip")) {
  $temporaryExtractPath = Join-Path ([System.IO.Path]::GetTempPath()) ("cine-private-restore-" + [guid]::NewGuid().ToString("N"))
  New-Item -ItemType Directory -Path $temporaryExtractPath -Force | Out-Null
  Expand-Archive -Path $BackupPath -DestinationPath $temporaryExtractPath -Force
  $candidates = @(Get-ChildItem -Path $temporaryExtractPath -Directory)
  if ($candidates.Count -eq 0) {
    throw "Backup archive does not contain a backup directory: $BackupPath"
  }
  $backupRoot = $candidates[0].FullName
}
elseif (Test-Path -Path $BackupPath -PathType Container) {
  $backupRoot = (Resolve-Path $BackupPath).Path
}
else {
  throw "Backup path not found: $BackupPath"
}

try {
  $restoredComponents = @()
  foreach ($component in $selectedComponents) {
    if ($component -eq "env") {
      $sourceEnvFile = Join-Path $backupRoot "env\.env.private"
      if (-not (Test-Path -Path $sourceEnvFile)) {
        throw "Backup does not contain env file: $sourceEnvFile"
      }

      $targetEnvFile = Join-Path $repoRoot ".env.private"
      Copy-Item -Path $sourceEnvFile -Destination $targetEnvFile -Force
      $restoredComponents += "env"
      continue
    }

    $sourceDir = Join-Path $backupRoot (Join-Path "components" $component)
    if (-not (Test-Path -Path $sourceDir -PathType Container)) {
      throw "Backup does not contain component directory: $sourceDir"
    }

    $targetDir = $componentPaths[$component]
    if ([string]::IsNullOrWhiteSpace($targetDir)) {
      throw "Missing target path for component: $component"
    }

    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    Clear-DirectoryContents -Path $targetDir
    Copy-DirectoryContents -SourcePath $sourceDir -DestinationPath $targetDir
    $restoredComponents += $component
  }

  [pscustomobject]@{
    env_file = $resolvedEnvFile
    backup_path = $BackupPath
    backup_root = $backupRoot
    restored_components = $restoredComponents
  }
}
finally {
  if ($null -ne $temporaryExtractPath -and (Test-Path -Path $temporaryExtractPath)) {
    Remove-Item -Path $temporaryExtractPath -Recurse -Force
  }
}
