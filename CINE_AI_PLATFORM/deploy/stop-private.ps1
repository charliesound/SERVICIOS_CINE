param(
  [string]$EnvFile = "",
  [string]$ComposeFile = ""
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if ([string]::IsNullOrWhiteSpace($EnvFile)) {
  $EnvFile = Join-Path $repoRoot ".env.private"
}

if ([string]::IsNullOrWhiteSpace($ComposeFile)) {
  $ComposeFile = Join-Path $repoRoot "docker-compose.private.yml"
}

if (-not (Test-Path -Path $EnvFile)) {
  throw "Missing env file: $EnvFile"
}

if (-not (Test-Path -Path $ComposeFile)) {
  throw "Missing compose file: $ComposeFile"
}

Push-Location $repoRoot
try {
  docker compose --env-file "$EnvFile" -f "$ComposeFile" down
}
finally {
  Pop-Location
}
