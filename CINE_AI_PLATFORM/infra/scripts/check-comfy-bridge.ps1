param(
  [string]$EnvFile = "",
  [string]$ComposeFile = "",
  [string]$HostProbeUrl = "",
  [int]$TimeoutSeconds = 5,
  [switch]$SkipContainerCheck,
  [switch]$RequireSuccess
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path

if ([string]::IsNullOrWhiteSpace($EnvFile)) {
  $privateEnvFile = Join-Path $repoRoot ".env.private"
  $exampleEnvFile = Join-Path $repoRoot ".env.private.example"

  if (Test-Path -Path $privateEnvFile) {
    $EnvFile = $privateEnvFile
  }
  elseif (Test-Path -Path $exampleEnvFile) {
    $EnvFile = $exampleEnvFile
  }
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

function Get-SystemStatsUrl {
  param([string]$BaseUrl)

  $normalized = [string]$BaseUrl
  $normalized = $normalized.Trim().TrimEnd("/")
  if ([string]::IsNullOrWhiteSpace($normalized)) {
    return ""
  }

  $builder = [System.UriBuilder]::new($normalized)
  $path = $builder.Path
  if ([string]::IsNullOrWhiteSpace($path) -or $path -eq "/") {
    $builder.Path = "/system_stats"
  }
  else {
    $builder.Path = ($path.TrimEnd("/") + "/system_stats")
  }

  return $builder.Uri.AbsoluteUri
}

function Invoke-HostProbe {
  param(
    [string]$Url,
    [int]$TimeoutSec
  )

  $result = [ordered]@{
    ok = $false
    url = $Url
    status_code = $null
    error = $null
  }

  try {
    $response = Invoke-WebRequest -Method Get -Uri $Url -TimeoutSec $TimeoutSec -UseBasicParsing
    $result.ok = ($response.StatusCode -ge 200 -and $response.StatusCode -lt 300)
    $result.status_code = [int]$response.StatusCode
  }
  catch {
    if ($_.Exception.Response) {
      $result.status_code = [int]$_.Exception.Response.StatusCode.value__
      $result.error = "HTTP $($result.status_code)"
    }
    else {
      $result.error = $_.Exception.Message
    }
  }

  return [pscustomobject]$result
}

function Invoke-ContainerProbe {
  param(
    [string]$EnvPath,
    [string]$ComposePath,
    [int]$TimeoutSec
  )

  $result = [ordered]@{
    ok = $false
    url = $null
    status_code = $null
    error = $null
  }

  $pythonScript = @"
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

url = os.environ["COMFYUI_BASE_URL"].rstrip("/") + "/system_stats"
result = {"ok": False, "url": url, "status_code": None, "error": None}

try:
    with urlopen(url, timeout=$TimeoutSec) as response:
        result["status_code"] = int(response.status)
        result["ok"] = 200 <= int(response.status) < 300
except HTTPError as error:
    result["status_code"] = int(error.code)
    result["error"] = f"HTTP {error.code}"
except URLError as error:
    result["error"] = str(getattr(error, "reason", error))
except Exception as error:
    result["error"] = str(error)

print(json.dumps(result))
raise SystemExit(0 if result["ok"] else 1)
"@

  $encodedScript = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($pythonScript))

  Push-Location $repoRoot
  try {
    $output = docker compose --env-file "$EnvPath" -f "$ComposePath" exec -T api python -c "import base64; exec(base64.b64decode('$encodedScript'))" 2>&1
    $exitCode = $LASTEXITCODE
  }
  finally {
    Pop-Location
  }

  $lines = @($output | ForEach-Object { [string]$_ } | Where-Object { -not [string]::IsNullOrWhiteSpace($_) })
  $lastLine = if ($lines.Count -gt 0) { $lines[-1] } else { "" }

  try {
    if (-not [string]::IsNullOrWhiteSpace($lastLine)) {
      $parsed = $lastLine | ConvertFrom-Json
      $result.ok = [bool]$parsed.ok
      $result.url = [string]$parsed.url
      if ($null -ne $parsed.status_code) {
        $result.status_code = [int]$parsed.status_code
      }
      $result.error = [string]$parsed.error
    }
  }
  catch {
    $result.error = ($lines -join "`n").Trim()
  }

  if ($exitCode -ne 0 -and [string]::IsNullOrWhiteSpace($result.error)) {
    $result.error = ($lines -join "`n").Trim()
  }

  if ([string]::IsNullOrWhiteSpace($result.url)) {
    $result.url = "container:api -> COMFYUI_BASE_URL/system_stats"
  }

  return [pscustomobject]$result
}

if ([string]::IsNullOrWhiteSpace($EnvFile) -or -not (Test-Path -Path $EnvFile)) {
  throw "Missing env file: $EnvFile"
}

if (-not (Test-Path -Path $ComposeFile)) {
  throw "Missing compose file: $ComposeFile"
}

$envMap = Read-EnvFile -Path $EnvFile
$comfyuiBaseUrl = $envMap["COMFYUI_BASE_URL"]
if ([string]::IsNullOrWhiteSpace($comfyuiBaseUrl)) {
  $comfyuiBaseUrl = "http://host.docker.internal:8188"
}

if ([string]::IsNullOrWhiteSpace($HostProbeUrl)) {
  $HostProbeUrl = $envMap["COMFYUI_HOST_PROBE_URL"]
}

if ([string]::IsNullOrWhiteSpace($HostProbeUrl)) {
  $HostProbeUrl = Get-SystemStatsUrl -BaseUrl ($comfyuiBaseUrl -replace "host\.docker\.internal", "127.0.0.1")
}

$hostProbe = Invoke-HostProbe -Url $HostProbeUrl -TimeoutSec $TimeoutSeconds

if ($SkipContainerCheck) {
  $containerProbe = [pscustomobject]@{
    ok = $false
    url = Get-SystemStatsUrl -BaseUrl $comfyuiBaseUrl
    status_code = $null
    error = "skipped"
  }
}
else {
  $containerProbe = Invoke-ContainerProbe -EnvPath $EnvFile -ComposePath $ComposeFile -TimeoutSec $TimeoutSeconds
}

$result = [pscustomobject]@{
  comfyui_base_url = $comfyuiBaseUrl
  host_probe = $hostProbe
  container_probe = $containerProbe
}

if ($RequireSuccess) {
  if (-not $hostProbe.ok) {
    throw "ComfyUI host probe failed: $($hostProbe.error) [$($hostProbe.url)]"
  }

  if (-not $SkipContainerCheck -and -not $containerProbe.ok) {
    throw "ComfyUI container probe failed: $($containerProbe.error) [$($containerProbe.url)]"
  }
}

$result
