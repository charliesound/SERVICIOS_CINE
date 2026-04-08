param(
  [string]$EnvFile = "",
  [string]$ComposeFile = ""
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

$resolvedEnvFile = Resolve-EnvFile
if ([string]::IsNullOrWhiteSpace($ComposeFile)) {
  $ComposeFile = Join-Path $repoRoot "docker-compose.private.yml"
}

if (-not (Test-Path -Path $resolvedEnvFile)) {
  throw "Missing env file: $resolvedEnvFile"
}

if (-not (Test-Path -Path $ComposeFile)) {
  throw "Missing compose file: $ComposeFile"
}

$envMap = Read-EnvFile -Path $resolvedEnvFile
$storagePaths = @(
  [pscustomobject]@{ component = "api"; path = $envMap["API_DATA_PATH"] },
  [pscustomobject]@{ component = "n8n"; path = $envMap["N8N_DATA_PATH"] },
  [pscustomobject]@{ component = "qdrant"; path = $envMap["QDRANT_STORAGE_PATH"] },
  [pscustomobject]@{ component = "nginx"; path = $envMap["NGINX_LOG_PATH"] }
) | ForEach-Object {
  [pscustomobject]@{
    component = $_.component
    path = $_.path
    exists = (Test-Path -Path $_.path)
  }
}

$composePs = $null
$composeError = $null

Push-Location $repoRoot
try {
  try {
    $composePs = docker compose --env-file "$resolvedEnvFile" -f "$ComposeFile" ps 2>&1
    if ($LASTEXITCODE -ne 0) {
      $composeError = ($composePs | Out-String).Trim()
      $composePs = $null
    }
  }
  catch {
    $composeError = $_.Exception.Message
  }
}
finally {
  Pop-Location
}

[pscustomobject]@{
  env_file = $resolvedEnvFile
  compose_file = $ComposeFile
  private_base_url = $envMap["PRIVATE_BASE_URL"]
  comfyui_base_url = $envMap["COMFYUI_BASE_URL"]
  storage_paths = $storagePaths
  compose_ps = if ($null -eq $composePs) { $null } else { ($composePs | Out-String).Trim() }
  compose_error = $composeError
}
