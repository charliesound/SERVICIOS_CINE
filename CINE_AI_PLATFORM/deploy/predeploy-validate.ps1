param(
  [string]$EnvFile = "",
  [string]$ComposeFile = ""
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

if ([string]::IsNullOrWhiteSpace($EnvFile)) {
  $EnvFile = Join-Path $repoRoot ".env.private.example"
}

if ([string]::IsNullOrWhiteSpace($ComposeFile)) {
  $ComposeFile = Join-Path $repoRoot "docker-compose.private.yml"
}

$requiredFiles = @(
  ".env.private.example",
  "docker-compose.private.yml",
  "infra/nginx/default.private.conf",
  "deploy/start-private.ps1",
  "deploy/stop-private.ps1",
  "deploy/start-comfy-wsl.ps1",
  "deploy/predeploy-validate.ps1",
  "infra/scripts/check-comfy-bridge.ps1",
  "infra/scripts/smoke-private.ps1",
  "deploy/README.private.md",
  "docs/COMFYUI_BRIDGE_PRIVATE.md"
)

$scriptFiles = @(
  "deploy/start-private.ps1",
  "deploy/stop-private.ps1",
  "deploy/start-comfy-wsl.ps1",
  "deploy/predeploy-validate.ps1",
  "infra/scripts/check-comfy-bridge.ps1",
  "infra/scripts/smoke-private.ps1"
)

$requiredEnvKeys = @(
  "PRIVATE_BASE_URL",
  "PRIVATE_BROWSER_ORIGINS",
  "COMFYUI_BASE_URL",
  "COMFYUI_HOST_PROBE_URL",
  "COMFYUI_TIMEOUT_SECONDS",
  "API_DATA_PATH",
  "N8N_DATA_PATH",
  "QDRANT_STORAGE_PATH",
  "NGINX_LOG_PATH"
)

function Test-PowerShellSyntax {
  param([string]$Path)

  $parseErrors = $null
  [void][System.Management.Automation.Language.Parser]::ParseFile($Path, [ref]$null, [ref]$parseErrors)

  return [pscustomobject]@{
    ok = ($parseErrors.Count -eq 0)
    errors = @($parseErrors | ForEach-Object { $_.Message })
  }
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
      throw "Invalid env line in ${Path}: $line"
    }

    $key = $pair[0].Trim()
    $value = $pair[1].Trim()

    if ([string]::IsNullOrWhiteSpace($key)) {
      throw "Invalid empty env key in $Path"
    }

    $values[$key] = $value
  }

  return $values
}

$filesReport = foreach ($relativePath in $requiredFiles) {
  $absolutePath = Join-Path $repoRoot $relativePath
  [pscustomobject]@{
    path = $relativePath
    exists = (Test-Path -Path $absolutePath)
  }
}

$missingFiles = @($filesReport | Where-Object { -not $_.exists })
if ($missingFiles.Count -gt 0) {
  $missingList = ($missingFiles | ForEach-Object { $_.path }) -join ", "
  throw "Missing required files: $missingList"
}

$syntaxReport = foreach ($relativePath in $scriptFiles) {
  $absolutePath = Join-Path $repoRoot $relativePath
  $syntax = Test-PowerShellSyntax -Path $absolutePath
  [pscustomobject]@{
    path = $relativePath
    ok = $syntax.ok
    errors = $syntax.errors
  }
}

$syntaxFailures = @($syntaxReport | Where-Object { -not $_.ok })
if ($syntaxFailures.Count -gt 0) {
  $details = $syntaxFailures | ForEach-Object {
    "$($_.path): $($_.errors -join ' | ')"
  }
  throw "PowerShell syntax validation failed:`n$($details -join "`n")"
}

$envValues = Read-EnvFile -Path $EnvFile
$missingEnvKeys = @($requiredEnvKeys | Where-Object { -not $envValues.ContainsKey($_) })
if ($missingEnvKeys.Count -gt 0) {
  throw "Missing required env keys in ${EnvFile}: $($missingEnvKeys -join ', ')"
}

Push-Location $repoRoot
try {
  docker compose --env-file "$EnvFile" -f "$ComposeFile" config | Out-Null
}
finally {
  Pop-Location
}

[pscustomobject]@{
  mode = "predeploy"
  env_file = $EnvFile
  compose_file = $ComposeFile
  files_ok = $true
  powershell_ok = $true
  env_example_ok = $true
  compose_config_ok = $true
  runtime_bridge_validated = $false
  tailscale_validated = $false
  note = "Portable package validated. Runtime bridge and smoke must be executed later on the home machine."
}
