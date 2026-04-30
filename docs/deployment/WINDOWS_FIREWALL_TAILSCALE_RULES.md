# Windows Firewall + Tailscale Rules

Ejecutar en PowerShell como administrador:

```powershell
New-NetFirewallRule -DisplayName "AILinkCinema CID HTTP Tailscale 80" -Direction Inbound -Protocol TCP -LocalPort 80 -RemoteAddress 100.64.0.0/10 -Action Allow

New-NetFirewallRule -DisplayName "AILinkCinema CID Frontend Tailscale 3000" -Direction Inbound -Protocol TCP -LocalPort 3000 -RemoteAddress 100.64.0.0/10 -Action Allow

New-NetFirewallRule -DisplayName "AILinkCinema CID Backend Tailscale 8000" -Direction Inbound -Protocol TCP -LocalPort 8000 -RemoteAddress 100.64.0.0/10 -Action Allow

New-NetFirewallRule -DisplayName "ComfyUI Tailscale 8188" -Direction Inbound -Protocol TCP -LocalPort 8188 -RemoteAddress 100.64.0.0/10 -Action Allow
```

Notas:

- No hace falta abrir puertos en el router.
- Las reglas limitan el acceso al rango CGNAT de Tailscale.
- Si Docker Desktop o el firewall ya tienen reglas previas, revisar duplicados antes de crear nuevas.

## Exponer ComfyUI de WSL solo por Tailscale

Si ComfyUI corre dentro de WSL y responde en `172.24.174.31:8188`, pero no en la IP Tailscale del PC, crear un `portproxy` de Windows limitado a la IP Tailscale:

```powershell
netsh interface portproxy delete v4tov4 listenaddress=100.121.83.126 listenport=8188
netsh interface portproxy add v4tov4 listenaddress=100.121.83.126 listenport=8188 connectaddress=172.24.174.31 connectport=8188
```

Comprobar despues:

```powershell
netsh interface portproxy show all
```

Tambien se puede ejecutar el helper:

```powershell
powershell -ExecutionPolicy Bypass -File C:\opt\SERVICIOS_CINE\scripts\windows_enable_comfyui_tailscale.ps1
```
