param(
  [string]$EnvFile = "",
  [string]$ComposeFile = "",
  [string]$BaseUrl = "",
  [string]$AdminEmail = "admin@cine.local",
  [string]$AdminPassword = "admin1234"
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

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
  throw "Missing env file: $EnvFile"
}

$envMap = Read-EnvFile -Path $EnvFile

if ([string]::IsNullOrWhiteSpace($BaseUrl)) {
  $privateBaseUrl = $envMap["PRIVATE_BASE_URL"]
  if (-not [string]::IsNullOrWhiteSpace($privateBaseUrl)) {
    $BaseUrl = $privateBaseUrl.TrimEnd("/")
  }
  else {
    $port = $envMap["NGINX_PORT_BIND"]
    if ([string]::IsNullOrWhiteSpace($port)) {
      $port = "80"
    }

    if ($port -eq "80") {
      $BaseUrl = "http://127.0.0.1"
    }
    else {
      $BaseUrl = "http://127.0.0.1:$port"
    }
  }
}

$health = Invoke-RestMethod `
  -Method Get `
  -Uri "$BaseUrl/api/health"

$healthDetails = Invoke-RestMethod `
  -Method Get `
  -Uri "$BaseUrl/api/health/details"

$loginBody = @{
  email = $AdminEmail
  password = $AdminPassword
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod `
  -Method Post `
  -Uri "$BaseUrl/api/auth/login" `
  -ContentType "application/json" `
  -Body $loginBody

$headers = @{
  Authorization = "Bearer $($loginResponse.access_token)"
}

$authMe = Invoke-RestMethod `
  -Method Get `
  -Uri "$BaseUrl/api/auth/me" `
  -Headers $headers

$storageInfo = Invoke-RestMethod `
  -Method Get `
  -Uri "$BaseUrl/api/storage/info" `
  -Headers $headers

$n8nStatusCode = 0
try {
  $n8nResponse = Invoke-WebRequest `
    -Method Get `
    -Uri "$BaseUrl/n8n/" `
    -MaximumRedirection 0
  $n8nStatusCode = [int]$n8nResponse.StatusCode
}
catch {
  if ($_.Exception.Response) {
    $n8nStatusCode = [int]$_.Exception.Response.StatusCode.value__
  }
  else {
    throw
  }
}

$bridgeScript = Join-Path $repoRoot "infra\scripts\check-comfy-bridge.ps1"
if (-not (Test-Path -Path $bridgeScript)) {
  throw "Missing bridge check script: $bridgeScript"
}

$bridge = & $bridgeScript -EnvFile $EnvFile -ComposeFile $ComposeFile

if (-not $bridge.host_probe.ok) {
  throw "ComfyUI host bridge failed: $($bridge.host_probe.error) [$($bridge.host_probe.url)]"
}

if (-not $bridge.container_probe.ok) {
  throw "ComfyUI container bridge failed: $($bridge.container_probe.error) [$($bridge.container_probe.url)]"
}

[pscustomobject]@{
  base_url = $BaseUrl
  private_base_url = $envMap["PRIVATE_BASE_URL"]
  api_health_ok = $health.ok
  api_health_details_ok = $healthDetails.ok
  comfyui_health_reachable = $healthDetails.health.integrations.comfyui.reachable
  auth_user = $authMe.user.email
  storage_backend = $storageInfo.storage.active_backend
  n8n_status_code = $n8nStatusCode
  comfyui_base_url = $bridge.comfyui_base_url
  comfyui_host_probe_ok = $bridge.host_probe.ok
  comfyui_host_probe_url = $bridge.host_probe.url
  comfyui_host_probe_status_code = $bridge.host_probe.status_code
  comfyui_container_probe_ok = $bridge.container_probe.ok
  comfyui_container_probe_url = $bridge.container_probe.url
  comfyui_container_probe_status_code = $bridge.container_probe.status_code
}
