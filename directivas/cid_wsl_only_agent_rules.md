# Directiva WSL-Only para OpenCode y Antigravity

## Objetivo

Garantizar que toda edición, auditoría y validación del repositorio
`/opt/SERVICIOS_CINE` se ejecute exclusivamente dentro de WSL Ubuntu,
eliminando riesgos de contaminación entre sistemas de archivos Windows y WSL.

## Alcance

Aplica a todos los agentes (OpenCode, Antigravity y cualquier agente auxiliar)
que interactúen con este repositorio.

## Reglas obligatorias

1. **Directorio único de trabajo**: `/opt/SERVICIOS_CINE`
2. **Shell**: bash dentro de WSL Ubuntu
3. **Virtualenv**: activar `.venv` antes de cualquier operación Python
4. **Prohibiciones absolutas**:
   - No usar rutas `C:\` ni ninguna letra de unidad Windows
   - No usar `/mnt/c` ni ningún `mnt/` mount
   - No usar `\\wsl.localhost` ni ninguna ruta UNC Windows
   - No usar PowerShell, cmd.exe ni ningún shell de Windows
   - No usar herramientas Windows (Windows Python, pip de Windows, etc.)
   - No guardar informes en `C:\tmp` ni en ninguna ruta Windows

## Preflight obligatorio antes de tocar código

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate
echo "PWD=$(pwd)"
test "$(pwd)" = "/opt/SERVICIOS_CINE" && echo "OK repo path"
test ! -d /opt/SERVICIOS_CINE/opt && echo "OK no nested copy"
git status --short --untracked-files=all
```

## Cierre obligatorio después de cada operación

```bash
git status --short --untracked-files=all
git diff --stat
test ! -d /opt/SERVICIOS_CINE/opt && echo "OK no nested copy"
```

## Invalidación de auditorías externas

Toda auditoría o informe generado desde fuera de WSL (PowerShell, Windows
Python, rutas Windows) queda automáticamente invalidado hasta ser verificado
y reproducido desde WSL.