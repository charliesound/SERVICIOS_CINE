param(
  [string]$EnvFile = "",
  [string]$ComposeFile = "",
  [switch]$SkipBridgeCheck
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if ([string]::IsNullOrWhiteSpace($EnvFile)) {
  $EnvFile = Join-Path $repoRoot ".env.private"
}

if ([string]::IsNullOrWhiteSpace($ComposeFile)) {
  $ComposeFile = Join-Path $repoRoot "docker-compose.private.yml"
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

if (-not (Test-Path -Path $EnvFile)) {
  throw "Missing env file: $EnvFile`nCreate it from .env.private.example before starting the stack."
}

if (-not (Test-Path -Path $ComposeFile)) {
  throw "Missing compose file: $ComposeFile"
}

$envMap = Read-EnvFile -Path $EnvFile
$pathsToCreate = @(
  $envMap["API_DATA_PATH"],
  $envMap["N8N_DATA_PATH"],
  $envMap["QDRANT_STORAGE_PATH"],
  $envMap["NGINX_LOG_PATH"]
)

foreach ($path in $pathsToCreate) {
  if ([string]::IsNullOrWhiteSpace($path)) {
    continue
  }
  if (-not (Test-Path -Path $path)) {
    New-Item -ItemType Directory -Path $path -Force | Out-Null
  }
}

Push-Location $repoRoot
try {
  docker compose --env-file "$EnvFile" -f "$ComposeFile" config | Out-Null
  docker compose --env-file "$EnvFile" -f "$ComposeFile" up -d --build
  docker compose --env-file "$EnvFile" -f "$ComposeFile" ps

  if (-not $SkipBridgeCheck) {
    $bridgeScript = Join-Path $repoRoot "infra\scripts\check-comfy-bridge.ps1"
    if (Test-Path -Path $bridgeScript) {
      $bridgeStatus = & $bridgeScript -EnvFile $EnvFile -ComposeFile $ComposeFile
      $bridgeStatus | Format-List

      if (-not $bridgeStatus.host_probe.ok -or -not $bridgeStatus.container_probe.ok) {
        Write-Warning "ComfyUI bridge is not fully reachable yet. Review host_probe/container_probe in the output above."
      }
    }
  }
}
finally {
  Pop-Location
}
