param(
  [string]$EnvFile = "",
  [string]$ComposeFile = "",
  [string]$BaseUrl = "",
  [string]$DemoScriptPath = "",
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

if ([string]::IsNullOrWhiteSpace($DemoScriptPath)) {
  $DemoScriptPath = Join-Path $repoRoot "examples\demo_screenplay_01.txt"
}

function Read-EnvFile {
  param([string]$Path)
  $values = @{}
  foreach ($line in Get-Content -Path $Path) {
    $trimmed = $line.Trim()
    if ([string]::IsNullOrWhiteSpace($trimmed)) { continue }
    if ($trimmed.StartsWith("#")) { continue }
    $pair = $trimmed.Split("=", 2)
    if ($pair.Count -ne 2) { continue }
    $values[$pair[0].Trim()] = $pair[1].Trim()
  }
  return $values
}

if (-not (Test-Path -Path $EnvFile)) {
  throw "Missing env file: $EnvFile"
}

if (-not (Test-Path -Path $DemoScriptPath)) {
  throw "Missing demo script: $DemoScriptPath"
}

$envMap = Read-EnvFile -Path $EnvFile

if ([string]::IsNullOrWhiteSpace($BaseUrl)) {
  $privateBaseUrl = $envMap["PRIVATE_BASE_URL"]
  if (-not [string]::IsNullOrWhiteSpace($privateBaseUrl)) {
    $BaseUrl = $privateBaseUrl.TrimEnd("/")
  }
  else {
    $port = $envMap["NGINX_PORT_BIND"]
    if ([string]::IsNullOrWhiteSpace($port)) { $port = "80" }
    $BaseUrl = if ($port -eq "80") { "http://127.0.0.1" } else { "http://127.0.0.1:$port" }
  }
}

$demoScript = Get-Content -Raw -Path $DemoScriptPath
if ([string]::IsNullOrWhiteSpace($demoScript)) {
  throw "Demo script is empty: $DemoScriptPath"
}

$loginBody = @{ email = $AdminEmail; password = $AdminPassword } | ConvertTo-Json
$loginResponse = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/auth/login" -ContentType "application/json" -Body $loginBody
$headers = @{ Authorization = "Bearer $($loginResponse.access_token)" }

$planBody = @{ script_text = $demoScript; sequence_id = "demo_controlled_001" } | ConvertTo-Json -Depth 4
$planResponse = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/sequence/plan-and-render" -ContentType "application/json" -Headers $headers -Body $planBody

$results = [ordered]@{
  ok = $false
  base_url = $BaseUrl
  demo_script = $DemoScriptPath
  parsed_scenes_count = 0
  scene_breakdowns_count = 0
  beats_count = 0
  shots_count = 0
  has_grounding = $false
  has_continuity_formal = $false
  has_beat_type = $false
  has_shot_intent = $false
  has_motivation = $false
  render_jobs_created = 0
}

if ($planResponse.ok) {
  $results.parsed_scenes_count = @($planResponse.parsed_scenes).Count
  $results.scene_breakdowns_count = @($planResponse.scene_breakdowns).Count
  $results.beats_count = @($planResponse.beats).Count
  $results.shots_count = @($planResponse.shots).Count
  $results.has_grounding = @($planResponse.shots | Where-Object { $_.grounding }).Count -gt 0
  $results.has_continuity_formal = @($planResponse.shots | Where-Object { $_.continuity_formal }).Count -gt 0
  $results.has_beat_type = @($planResponse.beats | Where-Object { $_.beat_type }).Count -gt 0
  $results.has_shot_intent = @($planResponse.beats | Where-Object { $_.shot_intent }).Count -gt 0
  $results.has_motivation = @($planResponse.beats | Where-Object { $_.motivation }).Count -gt 0
  $results.render_jobs_created = @($planResponse.created_jobs).Count
  $results.ok = $true
}

[pscustomobject]$results
