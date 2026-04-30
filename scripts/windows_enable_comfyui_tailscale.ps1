$ErrorActionPreference = 'Stop'

$tailscaleIp = '100.121.83.126'
$wslIp = '172.24.174.31'
$port = 8188
$ruleName = 'ComfyUI Tailscale 8188'

Write-Host 'Configuring ComfyUI access via Tailscale only...' -ForegroundColor Cyan

Start-Process -FilePath 'netsh.exe' -ArgumentList @(
  'interface', 'portproxy', 'delete', 'v4tov4',
  "listenaddress=$tailscaleIp", "listenport=$port"
) -Verb RunAs -Wait

Start-Process -FilePath 'netsh.exe' -ArgumentList @(
  'interface', 'portproxy', 'add', 'v4tov4',
  "listenaddress=$tailscaleIp", "listenport=$port",
  "connectaddress=$wslIp", "connectport=$port"
) -Verb RunAs -Wait

Start-Process -FilePath 'powershell.exe' -ArgumentList @(
  '-NoProfile', '-Command',
  "if (-not (Get-NetFirewallRule -DisplayName '$ruleName' -ErrorAction SilentlyContinue)) { New-NetFirewallRule -DisplayName '$ruleName' -Direction Inbound -Protocol TCP -LocalPort $port -RemoteAddress 100.64.0.0/10 -Action Allow } else { Set-NetFirewallRule -DisplayName '$ruleName' -Enabled True -Action Allow }"
) -Verb RunAs -Wait

Write-Host ''
Write-Host 'ComfyUI should now be available on:' -ForegroundColor Green
Write-Host "  http://$tailscaleIp:$port/system_stats"
