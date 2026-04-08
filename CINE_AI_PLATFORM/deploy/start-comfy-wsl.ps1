param(
  [string]$EnvFile = "",
  [string]$Distro = "",
  [string]$ComfyPath = "",
  [string]$PythonCommand = "python",
  [string]$LaunchCommand = "",
  [int]$Port = 8188,
  [int]$WaitSeconds = 30
)

$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

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

function Convert-ToBashDoubleQuoted {
  param([string]$Value)

  $escapedValue = $Value.Replace('"', '\"')
  return '"' + $escapedValue + '"'
}

if ([string]::IsNullOrWhiteSpace($LaunchCommand)) {
  if ([string]::IsNullOrWhiteSpace($ComfyPath)) {
    throw "ComfyPath is required when LaunchCommand is not provided."
  }

  $quotedPath = Convert-ToBashDoubleQuoted -Value $ComfyPath
  $LaunchCommand = "cd $quotedPath && nohup $PythonCommand main.py --listen 0.0.0.0 --port $Port > comfyui.private.log 2>&1 &"
}

$wslArgs = @()
if (-not [string]::IsNullOrWhiteSpace($Distro)) {
  $wslArgs += "-d"
  $wslArgs += $Distro
}
$wslArgs += "bash"
$wslArgs += "-lc"
$wslArgs += $LaunchCommand

& wsl.exe @wslArgs | Out-Null

$bridgeScript = Join-Path $repoRoot "infra\scripts\check-comfy-bridge.ps1"
if (-not (Test-Path -Path $bridgeScript)) {
  throw "Missing bridge check script: $bridgeScript"
}

$deadline = (Get-Date).AddSeconds($WaitSeconds)
$bridge = $null

do {
  Start-Sleep -Seconds 2
  $bridge = & $bridgeScript -EnvFile $EnvFile -SkipContainerCheck
  if ($bridge.host_probe.ok) {
    $bridge
    exit 0
  }
} while ((Get-Date) -lt $deadline)

$bridge
throw "ComfyUI did not become reachable from Windows host within $WaitSeconds seconds."
