param(
  [string]$EnvFile = "",
  [string]$ComposeFile = "",
  [string[]]$Services = @(),
  [int]$Tail = 200,
  [switch]$Follow
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if ([string]::IsNullOrWhiteSpace($EnvFile)) {
  $privateEnvFile = Join-Path $repoRoot ".env.private"
  if (Test-Path -Path $privateEnvFile) {
    $EnvFile = $privateEnvFile
  }
  else {
    $EnvFile = Join-Path $repoRoot ".env.private.example"
  }
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

$allowedServices = @("nginx", "api", "web", "n8n", "qdrant")
$selectedServices = @()
foreach ($service in $Services) {
  $normalized = [string]$service
  $normalized = $normalized.Trim().ToLowerInvariant()
  if ([string]::IsNullOrWhiteSpace($normalized)) {
    continue
  }
  if ($allowedServices -notcontains $normalized) {
    throw "Unsupported service: $normalized"
  }
  $selectedServices += $normalized
}

$commandArgs = @(
  "compose",
  "--env-file", $EnvFile,
  "-f", $ComposeFile,
  "logs",
  "--tail", [string]$Tail
)

if ($Follow) {
  $commandArgs += "-f"
}

if ($selectedServices.Count -gt 0) {
  $commandArgs += $selectedServices
}

Push-Location $repoRoot
try {
  & docker @commandArgs
}
finally {
  Pop-Location
}
