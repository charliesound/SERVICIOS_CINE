"""CID Local Media Agent — Windows Self-Contained Beta Package Assembler.

Builds a self-contained beta directory that includes:
- Python runtime (embedded, no system dependency)
- Required packages (pip install --target)
- BtbN FFmpeg DLLs and binaries
- faster-whisper model
- CID Local Media Agent source scripts
- install.cmd / uninstall.cmd / launcher

Usage:
    python scripts/windows/build_beta_package.py [--output-dir PATH]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import sysconfig
from datetime import datetime, timezone
from pathlib import Path

VERSION = "0.3.0-beta1"
PACKAGE_NAME = f"CID-Local-Media-Agent-{VERSION}"

REPO_ROOT = Path(__file__).resolve().parents[2]

# When running from a temp copy on Windows, resolve the WSL repo path
if not (REPO_ROOT / "pyproject.toml").is_file():
    # Try the WSL UNC path
    wsl_candidates = [
        Path(r"\\wsl.localhost\Ubuntu-24.04-CID\opt\SERVICIOS_CINE"),
        Path(r"\\wsl$\Ubuntu-24.04-CID\opt\SERVICIOS_CINE"),
    ]
    for candidate in wsl_candidates:
        if candidate.is_dir() and (candidate / "pyproject.toml").is_file():
            REPO_ROOT = candidate
            break

PYTHON_EXE = sys.executable
PYTHON_DIR = Path(sys.prefix)

REQUIRED_PACKAGES = [
    "ctranslate2",
    "faster-whisper",
    "av",
    "numpy",
    "tokenizers",
    "huggingface-hub",
    "tqdm",
    "colorama",
    "regex",
    "onnxruntime",
    "packaging",
    "filelock",
    "fsspec",
    "requests",
    "pyyaml",
    "typing_extensions",
    "platformdirs",
    "jinja2",
    "MarkupSafe",
    "click",
    "six",
    "certifi",
    "charset-normalizer",
    "idna",
    "urllib3",
    "mpmath",
    "networkx",
    "yaml",
]

BtbN_DLLS = [
    "avcodec-61.dll",
    "avformat-61.dll",
    "avutil-59.dll",
    "avdevice-61.dll",
    "avfilter-10.dll",
    "swscale-8.dll",
    "swresample-5.dll",
]

PYTHON_CORE_FILES = [
    "python.exe",
    "python3.dll",
    "python312.dll",
    "pythonw.exe",
    "vcruntime140.dll",
    "vcruntime140_1.dll",
]

CID_SOURCE_DIRS = [
    "scripts/local_media_agent",
    "scripts/editorial_intelligence/transcription",
]


def _copy_python_core(target_python: Path) -> None:
    """Copy Python executable, core DLLs and stdlib C-extension modules."""
    target_python.mkdir(parents=True, exist_ok=True)
    for name in PYTHON_CORE_FILES:
        src = PYTHON_DIR / name
        if src.is_file():
            shutil.copy2(src, target_python / name)
            print(f"  {name}")
    # Copy BtbN DLLs alongside python.exe (PyAV loads from here)
    for dll in BtbN_DLLS:
        src = PYTHON_DIR / dll
        if src.is_file():
            shutil.copy2(src, target_python / dll)
            print(f"  {dll}")
    # Stdlib C-extension modules (.pyd) and their dependent DLLs
    dlls_src = PYTHON_DIR / "DLLs"
    if dlls_src.is_dir():
        dlls_dest = target_python / "DLLs"
        dlls_dest.mkdir(parents=True, exist_ok=True)
        excluded = {
            "_ctypes_test.pyd", "_msi.pyd", "_testbuffer.pyd",
            "_testcapi.pyd", "_testclinic.pyd", "_testconsole.pyd",
            "_testimportmultiple.pyd", "_testinternalcapi.pyd",
            "_testmultiphase.pyd", "_wmi.pyd", "winsound.pyd",
        }
        for entry in dlls_src.iterdir():
            if entry.is_file() and entry.name not in excluded:
                shutil.copy2(entry, dlls_dest / entry.name)
        print(f"  DLLs/ ({len(list(dlls_dest.iterdir()))} files)")

    # Tcl/Tk runtime assets for the tkinter producer GUI (offline, from the
    # validated local Python installation).
    tcl_src = PYTHON_DIR / "tcl"
    if tcl_src.is_dir():
        tcl_dest = target_python / "tcl"
        shutil.copytree(
            tcl_src,
            tcl_dest,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "nmake", "*.lib"),
        )
        print(f"  tcl/ (Tcl/Tk runtime)")


def _copy_site_packages(target_site_packages: Path) -> None:
    """Copy the validated packages from the system Python site-packages.

    The system Python hosts the accepted, validated runtime stack
    (custom av 16.0.0 + BtbN FFmpeg, custom ctranslate2 4.8.1, etc.).
    Copying those exact packages guarantees the packaged product matches
    the validated runtime without pip resolution or version drift.
    """
    target_site_packages.mkdir(parents=True, exist_ok=True)
    for stale in target_site_packages.iterdir():
        shutil.rmtree(stale) if stale.is_dir() else stale.unlink()
    src_sp = PYTHON_DIR / "Lib" / "site-packages"

    def _norm(name: str) -> str:
        return re.sub(r"[-_.]", "", name).lower()

    required = {_norm(p) for p in REQUIRED_PACKAGES}
    version_re = re.compile(r"-\d[\w.\-+]*$")

    def _copy_entry(src: Path, dest: Path) -> None:
        if src.is_dir():
            shutil.copytree(
                src,
                dest,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
        else:
            shutil.copy2(src, dest)

    copied = 0
    for entry in src_sp.iterdir():
        name = entry.name
        if name.endswith(".dist-info"):
            base = name[: -len(".dist-info")]
            m = version_re.search(base)
            pkg = base[: m.start()] if m else base
            if _norm(pkg) in required:
                _copy_entry(entry, target_site_packages / name)
                copied += 1
        else:
            base = name[: -3] if name.endswith(".py") else name
            n = _norm(base)
            if n in required or (n.endswith("libs") and n[:-4] in required):
                _copy_entry(entry, target_site_packages / name)
                copied += 1
    print(f"  Copied {copied} site-packages entries")


def _copy_stdlib(target_lib: Path) -> None:
    """Copy the full stdlib tree, minus heavy/dev-only directories."""
    stdlib_src = Path(sysconfig.get_path("stdlib"))
    target_lib.mkdir(parents=True, exist_ok=True)

    # Directories not needed at runtime: dev tests, demos, tooling, or
    # components whose native dependencies are not shipped.
    exclude_dirs = {
        "__pycache__",
        "test",
        "turtledemo",
        "ensurepip",
        "lib2to3",
        "msilib",
        "curses",
    }

    for entry in stdlib_src.iterdir():
        if entry.is_dir():
            if entry.name in exclude_dirs:
                continue
            shutil.copytree(
                entry,
                target_lib / entry.name,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "test", "tests"),
            )
        elif entry.is_file() and entry.suffix in {".py", ".pyi"}:
            dest = target_lib / entry.name
            if not dest.exists():
                shutil.copy2(entry, dest)

    print(f"  Stdlib modules copied")


def _copy_cid_source(target_app: Path) -> None:
    """Copy CID Local Media Agent source scripts."""
    for rel_dir in CID_SOURCE_DIRS:
        src = REPO_ROOT / rel_dir
        if src.is_dir():
            dest = target_app / rel_dir
            shutil.copytree(src, dest, dirs_exist_ok=True,
                          ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            print(f"  {rel_dir}")
    # Copy pyproject.toml for version info
    pyproject = REPO_ROOT / "pyproject.toml"
    if pyproject.is_file():
        shutil.copy2(pyproject, target_app / "pyproject.toml")


def _copy_ffmpeg(target_ffmpeg: Path) -> None:
    """Copy BtbN FFmpeg binaries."""
    sdk_bin = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "cid_build" / "ffmpeg-btbn-shared-7.1" / "bin"
    if not sdk_bin.exists():
        print(f"  WARNING: FFmpeg SDK not found at {sdk_bin}")
        return
    target_ffmpeg.mkdir(parents=True, exist_ok=True)
    for exe in ("ffmpeg.exe", "ffprobe.exe"):
        src = sdk_bin / exe
        if src.is_file():
            shutil.copy2(src, target_ffmpeg / exe)
            print(f"  {exe}")
    # Copy BtbN DLLs to ffmpeg/bin too (redundant with python dir, but ensures availability)
    for dll in BtbN_DLLS:
        src = sdk_bin / dll
        if src.is_file():
            shutil.copy2(src, target_ffmpeg / dll)


def _copy_model(target_models: Path) -> None:
    """Copy faster-whisper model."""
    model_src = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "cid_lma_models" / "faster-whisper-small"
    if not model_src.exists():
        print(f"  WARNING: Model not found at {model_src}")
        return
    model_dest = target_models / "faster-whisper-small"
    shutil.copytree(model_src, model_dest,
                   ignore=shutil.ignore_patterns(".git", "__pycache__"))
    total = sum(f.stat().st_size for f in model_dest.rglob("*") if f.is_file())
    print(f"  faster-whisper-small ({total / 1024 / 1024:.0f} MB)")


def _create_python_pth(target_python: Path, target_lib: Path, target_site_packages: Path) -> None:
    """Create python312._pth for embedded Python path isolation.

    When a ._pth file exists, PYTHONPATH is ignored, so the CID app dir
    must be listed here explicitly (relative to the runtime/python dir).
    """
    pth_content = "\n".join([
        "python312.zip",
        ".",
        "DLLs",
        "Lib",
        "Lib/site-packages",
        "..\\..\\app",
        "",
    ])
    pth_path = target_python / "python312._pth"
    pth_path.write_text(pth_content, encoding="utf-8")
    print(f"  python312._pth")


def _create_launcher(package_dir: Path) -> None:
    """Create the CLI support launcher CMD (for support/development only)."""
    launcher = package_dir / "CID Local Media Agent (CLI).cmd"
    launcher_content = f"""@echo off
title CID Local Media Agent {VERSION}
echo.
echo   ======================================================
echo    CID  Local Media Agent  {VERSION}
echo    Scan + Metadata + Batch Transcription + Subtitles
echo   ======================================================
echo.

set CID_PACKAGE_DIR=%~dp0
set CID_PACKAGE_DIR=%CID_PACKAGE_DIR:~0,-1%

set PYTHON=%CID_PACKAGE_DIR%\\runtime\\python\\python.exe
set APP_DIR=%CID_PACKAGE_DIR%\\app

if not exist "%PYTHON%" (
    echo   ERROR: Packaged Python not found at:
    echo   %PYTHON%
    echo.
    pause
    exit /b 1
)

if not exist "%APP_DIR%" (
    echo   ERROR: CID application not found at:
    echo   %APP_DIR%
    echo.
    pause
    exit /b 1
)

set PYTHONNOUSERSITE=1
set PYTHONPATH=%APP_DIR%
set CID_FFMPEG_PATH=%CID_PACKAGE_DIR%\\runtime\\ffmpeg\\bin\\ffmpeg.exe
set CID_FFPROBE_PATH=%CID_PACKAGE_DIR%\\runtime\\ffmpeg\\bin\\ffprobe.exe

"%PYTHON%" -m scripts.local_media_agent.cid_local_media_agent_operator %*
if errorlevel 1 (
    echo.
    echo   CID Local Media Agent exited with errors.
    pause
)
"""
    launcher.write_text(launcher_content, encoding="utf-8")
    print(f"  CID Local Media Agent (CLI).cmd")


def _create_gui_launcher(package_dir: Path) -> None:
    """Create the producer GUI launcher (no console, pythonw hidden).

    Uses only standard Windows mechanisms (WSH/VBScript) and packaged
    assets. The VBS derives its install location at runtime, so the same
    file works from the package dir and from the install target.
    """
    launcher = package_dir / "CID Local Media Agent.vbs"
    content = (
        "Set shell = CreateObject(\"WScript.Shell\")\n"
        "Set fso = CreateObject(\"Scripting.FileSystemObject\")\n"
        "base = fso.GetParentFolderName(WScript.ScriptFullName)\n"
        "appDir = base & \"\\app\"\n"
        "pythonw = appDir & \"\\runtime\\python\\pythonw.exe\"\n"
        "If Not fso.FileExists(pythonw) Then\n"
        "    MsgBox \"CID Local Media Agent: runtime no encontrado.\", vbCritical, \"CID Local Media Agent\"\n"
        "    WScript.Quit 1\n"
        "End If\n"
        "shell.CurrentDirectory = appDir\n"
        "shell.Environment(\"PROCESS\")(\"PYTHONNOUSERSITE\") = \"1\"\n"
        "shell.Environment(\"PROCESS\")(\"PYTHONPATH\") = appDir\n"
        "shell.Environment(\"PROCESS\")(\"CID_FFMPEG_PATH\") = appDir & \"\\runtime\\ffmpeg\\bin\\ffmpeg.exe\"\n"
        "shell.Environment(\"PROCESS\")(\"CID_FFPROBE_PATH\") = appDir & \"\\runtime\\ffmpeg\\bin\\ffprobe.exe\"\n"
        "shell.Run \"\"\"\" & pythonw & \"\"\" -m scripts.local_media_agent.cid_gui\", 0, False\n"
    )
    launcher.write_text(content, encoding="utf-8")
    print(f"  CID Local Media Agent.vbs")


def _create_install_cmd(package_dir: Path) -> None:
    """Create install.cmd."""
    install_cmd = package_dir / "install.cmd"
    content = f"""@echo off
echo.
echo   CID Local Media Agent {VERSION} - Installer
echo   ======================================================
echo.

set INSTALL_TARGET=%LOCALAPPDATA%\\CID\\LocalMediaAgent\\app
set PACKAGE_DIR=%~dp0
set PACKAGE_DIR=%PACKAGE_DIR:~0,-1%

echo   Source:   %PACKAGE_DIR%
echo   Target:   %INSTALL_TARGET%
echo.

if not exist "%PACKAGE_DIR%\\runtime\\python\\python.exe" (
    echo   ERROR: Packaged Python not found in this package.
    echo   Ensure the full package was extracted correctly.
    pause
    exit /b 1
)

echo   [1/5] Creating target directory...
if not exist "%INSTALL_TARGET%" mkdir "%INSTALL_TARGET%"
if not exist "%INSTALL_TARGET%\\runtime" mkdir "%INSTALL_TARGET%\\runtime"

echo   [2/5] Copying application source...
if exist "%INSTALL_TARGET%\\app" rmdir /s /q "%INSTALL_TARGET%\\app"
xcopy /s /e /q /y "%PACKAGE_DIR%\\app\\*" "%INSTALL_TARGET%\\app\\" >nul
if errorlevel 1 goto :fail

echo   [3/5] Copying Python runtime...
if exist "%INSTALL_TARGET%\\runtime\\python" rmdir /s /q "%INSTALL_TARGET%\\runtime\\python"
xcopy /s /e /q /y "%PACKAGE_DIR%\\runtime\\python\\*" "%INSTALL_TARGET%\\runtime\\python\\" >nul
if errorlevel 1 goto :fail

echo   [4/5] Copying FFmpeg...
if not exist "%INSTALL_TARGET%\\runtime\\ffmpeg\\bin" mkdir "%INSTALL_TARGET%\\runtime\\ffmpeg\\bin"
xcopy /s /e /q /y "%PACKAGE_DIR%\\runtime\\ffmpeg\\bin\\*" "%INSTALL_TARGET%\\runtime\\ffmpeg\\bin\\" >nul
if errorlevel 1 goto :fail

echo   [5/5] Copying model (this may take a moment)...
if exist "%INSTALL_TARGET%\\models" rmdir /s /q "%INSTALL_TARGET%\\models"
xcopy /s /e /q /y "%PACKAGE_DIR%\\models\\*" "%INSTALL_TARGET%\\models\\" >nul
if errorlevel 1 goto :fail

echo.
echo   [6/6] Creating launchers...
echo @echo off > "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent (CLI).cmd"
echo title CID Local Media Agent {VERSION} (CLI) >> "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent (CLI).cmd"
echo. >> "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent (CLI).cmd"
echo set CID_PACKAGE_DIR=%INSTALL_TARGET% >> "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent (CLI).cmd"
echo set PYTHON=%INSTALL_TARGET%\\runtime\\python\\python.exe >> "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent (CLI).cmd"
echo set APP_DIR=%INSTALL_TARGET%\\app >> "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent (CLI).cmd"
echo set PYTHONNOUSERSITE=1 >> "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent (CLI).cmd"
echo set PYTHONPATH=%INSTALL_TARGET%\\app >> "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent (CLI).cmd"
echo set CID_FFMPEG_PATH=%INSTALL_TARGET%\\runtime\\ffmpeg\\bin\\ffmpeg.exe >> "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent (CLI).cmd"
echo set CID_FFPROBE_PATH=%INSTALL_TARGET%\\runtime\\ffmpeg\\bin\\ffprobe.exe >> "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent (CLI).cmd"
echo. >> "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent (CLI).cmd"
echo "%INSTALL_TARGET%\\runtime\\python\\python.exe" -m scripts.local_media_agent.cid_local_media_agent_operator %%* >> "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent (CLI).cmd"
echo if errorlevel 1 pause >> "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent (CLI).cmd"
copy /y "%PACKAGE_DIR%\\CID Local Media Agent.vbs" "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent.vbs" >nul
if errorlevel 1 goto :fail

echo.
echo   ======================================================
echo   Installation complete.
echo.
echo   Launch:  %LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent.vbs
echo   Target:  %INSTALL_TARGET%
echo   Results: %USERPROFILE%\\Documents\\CID Local Media Agent\\Resultados\\
echo   ======================================================
echo.
pause
exit /b 0

:fail
echo.
echo   ERROR: Installation failed. Re-check the source package and retry.
echo.
pause
exit /b 1
"""
    install_cmd.write_text(content, encoding="utf-8")
    print(f"  install.cmd")


def _create_uninstall_cmd(package_dir: Path) -> None:
    """Create uninstall.cmd."""
    uninstall_cmd = package_dir / "uninstall.cmd"
    content = f"""@echo off
echo.
echo   CID Local Media Agent {VERSION} - Uninstaller
echo   ======================================================
echo.

set INSTALL_TARGET=%LOCALAPPDATA%\\CID\\LocalMediaAgent\\app
set GUI_LAUNCHER=%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent.vbs
set CLI_LAUNCHER=%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent (CLI).cmd

echo   This will remove the installed CID Local Media Agent application.
echo   User results in %%USERPROFILE%%\\Documents\\CID Local Media Agent\\Resultados
echo   (and any custom results location) will be PRESERVED.
echo.

set /p CONFIRM="  Continue? [y/N]: "
if /i not "%CONFIRM%"=="y" (
    echo   Uninstall cancelled.
    pause
    exit /b 0
)

echo.
echo   [1/3] Removing application and runtime...
if exist "%INSTALL_TARGET%" rmdir /s /q "%INSTALL_TARGET%"

echo   [2/3] Removing launchers...
if exist "%GUI_LAUNCHER%" del /f "%GUI_LAUNCHER%"
if exist "%CLI_LAUNCHER%" del /f "%CLI_LAUNCHER%"

echo   [3/3] Removing empty directories...
if exist "%LOCALAPPDATA%\\CID\\LocalMediaAgent" (
    dir /b "%LOCALAPPDATA%\\CID\\LocalMediaAgent" 2>nul | findstr /r ".">nul
    if errorlevel 1 (
        rmdir "%LOCALAPPDATA%\\CID\\LocalMediaAgent"
    )
)

echo.
echo   ======================================================
echo   Uninstall complete.
echo   Results directory preserved at:
echo   %%USERPROFILE%%\\Documents\\CID Local Media Agent\\Resultados\\
echo   ======================================================
echo.
pause
"""
    uninstall_cmd.write_text(content, encoding="utf-8")
    print(f"  uninstall.cmd")


def _create_package_manifest(
    package_dir: Path,
    package_size: int,
    zip_size: int | None,
    site_packages: Path,
) -> None:
    """Create package_manifest.json."""
    def _pkg_version(pkg_name: str) -> str:
        for entry in site_packages.iterdir():
            if entry.is_dir() and entry.name.endswith(".dist-info"):
                base = entry.name[: -len(".dist-info")]
                if base.lower().startswith(pkg_name.lower() + "-"):
                    return base[len(pkg_name) + 1:]
        return "unknown"

    manifest = {
        "package_name": PACKAGE_NAME,
        "version": VERSION,
        "package_type": "windows_self_contained_beta",
        "build_timestamp": datetime.now(timezone.utc).isoformat(),
        "target_os": "windows",
        "target_arch": "win_amd64",
        "product_commit_sha": _get_git_commit(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "ctranslate2_version": _pkg_version("ctranslate2"),
        "pyav_version": _pkg_version("av"),
        "ffmpeg_identity": "BtbN n7.1.5-12-g1fdbca85aa win64-lgpl-shared-7.1",
        "faster_whisper_version": _pkg_version("faster_whisper"),
        "onnxruntime_version": _pkg_version("onnxruntime"),
        "model": {
            "name": "Systran/faster-whisper-small",
            "revision": "536b0662742c02347bc0e980a01041f333bce120",
        },
        "contents": {
            "runtime/python": "Embedded Python 3.12 runtime",
            "runtime/ffmpeg/bin": "BtbN FFmpeg 7.1 binaries and DLLs",
            "models/faster-whisper-small": "Whisper model (local/offline)",
            "app/scripts": "CID Local Media Agent source scripts",
            "install.cmd": "Installer",
            "uninstall.cmd": "Uninstaller",
            "CID Local Media Agent.vbs": "Producer GUI launcher (no console)",
            "CID Local Media Agent (CLI).cmd": "CLI support launcher",
            "licenses/": "Third-party license files",
            "NOTAS_BETA.txt": "Producer-facing beta limitations note",
            "LEEME_PRIMERO.txt": "Producer-facing first-read guide",
        },
        "package_bytes": package_size,
        "zip_bytes": zip_size,
    }
    manifest_path = package_dir / "package_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  package_manifest.json")


def _create_licenses(package_dir: Path) -> None:
    """Copy license files for packaged components."""
    licenses_dir = package_dir / "licenses"
    licenses_dir.mkdir(exist_ok=True)

    # Python license
    py_license = PYTHON_DIR / "LICENSE.txt"
    if py_license.is_file():
        shutil.copy2(py_license, licenses_dir / "PYTHON_LICENSE.txt")

    # faster-whisper-small model MIT license
    model_license = licenses_dir / "MODEL_LICENSE.txt"
    model_license.write_text(
        "MIT License\n\n"
        "Copyright (c) 2023 SYSTRAN\n\n"
        "Permission is hereby granted, free of charge, to any person obtaining a copy\n"
        "of this software and associated documentation files (the \"Software\"), to deal\n"
        "in the Software without restriction, including without limitation the rights\n"
        "to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n"
        "copies of the Software, and to permit persons to whom the Software is\n"
        "furnished to do so, subject to the following conditions:\n\n"
        "The above copyright notice and this permission notice shall be included in\n"
        "all copies or substantial portions of the Software.\n\n"
        "THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n"
        "IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n"
        "FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n"
        "AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n"
        "LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n"
        "OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN\n"
        "THE SOFTWARE.\n",
        encoding="utf-8",
    )
    print(f"  MODEL_LICENSE.txt")

    # Apache License 2.0 text for embedded/shipped Apache-2.0 components
    apache_license = licenses_dir / "APACHE-2.0_LICENSE.txt"
    apache_license.write_text(
        "Apache License\n"
        "Version 2.0, January 2004\n"
        "http://www.apache.org/licenses/\n\n"
        "TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION\n\n"
        "1. Definitions.\n\n"
        "\"License\" shall mean the terms and conditions for use, reproduction,\n"
        "and distribution as defined by Sections 1 through 9 of this document.\n\n"
        "\"Licensor\" shall mean the copyright owner or entity authorized by\n"
        "the copyright owner that is granting the License.\n\n"
        "\"Legal Entity\" shall mean the union of the acting entity and all\n"
        "other entities that control, are controlled by, or are under common\n"
        "control with that entity. For the purposes of this definition,\n"
        "\"control\" means (i) the power, direct or indirect, to cause the\n"
        "direction or management of such entity, whether by contract or\n"
        "otherwise, or (ii) ownership of fifty percent (50%) or more of the\n"
        "outstanding shares, or (iii) beneficial ownership of such entity.\n\n"
        "\"You\" (or \"Your\") shall mean an individual or Legal Entity\n"
        "exercising permissions granted by this License.\n\n"
        "\"Source\" form shall mean the preferred form for making modifications,\n"
        "including but not limited to software source code, documentation\n"
        "source, and configuration files.\n\n"
        "\"Object\" form shall mean any form resulting from mechanical\n"
        "transformation or translation of a Source form, including but\n"
        "not limited to compiled object code, generated documentation,\n"
        "and conversions to other media types.\n\n"
        "\"Work\" shall mean the work of authorship, whether in Source or\n"
        "Object form, made available under the License, as indicated by a\n"
        "copyright notice that is included in or attached to the work\n"
        "(an example is provided in the Appendix below).\n\n"
        "\"Derivative Works\" shall mean any work, whether in Source or Object\n"
        "form, that is based on (or derived from) the Work and for which the\n"
        "editorial revisions, annotations, elaborations, or other modifications\n"
        "represent, as a whole, an original work of authorship. For the purposes\n"
        "of this License, Derivative Works shall not include works that remain\n"
        "separable from, or merely link (or bind by name) to the interfaces of,\n"
        "the Work and Derivative Works thereof.\n\n"
        "\"Contribution\" shall mean any work of authorship, including\n"
        "the original version of the Work and any modifications or additions\n"
        "to that Work or Derivative Works thereof, that is intentionally\n"
        "submitted to Licensor for inclusion in the Work by the copyright owner\n"
        "or by an individual or Legal Entity authorized to submit on behalf of\n"
        "the copyright owner. For the purposes of this definition, \"submitted\"\n"
        "means any form of electronic, verbal, or written communication sent\n"
        "to the Licensor or its representatives, including but not limited to\n"
        "communication on electronic mailing lists, source code control systems,\n"
        "and issue tracking systems that are managed by, or on behalf of, the\n"
        "Licensor for the purpose of discussing and improving the Work, but\n"
        "excluding communication that is conspicuously marked or otherwise\n"
        "designated in writing by the copyright owner as \"Not a Contribution.\"\n\n"
        "\"Contributor\" shall mean Licensor and any individual or Legal Entity\n"
        "on behalf of whom a Contribution has been received by Licensor and\n"
        "subsequently incorporated within the Work.\n\n"
        "2. Grant of Copyright License. Subject to the terms and conditions of\n"
        "this License, each Contributor hereby grants to You a perpetual,\n"
        "worldwide, non-exclusive, no-charge, royalty-free, irrevocable\n"
        "copyright license to reproduce, prepare Derivative Works of,\n"
        "publicly display, publicly perform, sublicense, and distribute the\n"
        "Work and such Derivative Works in Source or Object form.\n\n"
        "3. Grant of Patent License. Subject to the terms and conditions of\n"
        "this License, each Contributor hereby grants to You a perpetual,\n"
        "worldwide, non-exclusive, no-charge, royalty-free, irrevocable\n"
        "(except as stated in this section) patent license to make, have made,\n"
        "use, offer to sell, sell, import, and otherwise transfer the Work,\n"
        "where such license applies only to those patent claims licensable\n"
        "by such Contributor that are necessarily infringed by their\n"
        "Contribution(s) alone or by combination of their Contribution(s)\n"
        "with the Work to which such Contribution(s) was submitted. If You\n"
        "institute patent litigation against any entity (including a\n"
        "cross-claim or counterclaim in a lawsuit) alleging that the Work\n"
        "or a Contribution incorporated within the Work constitutes direct\n"
        "or contributory patent infringement, then any patent licenses\n"
        "granted to You under this License for that Work shall terminate\n"
        "as of the date such litigation is filed.\n\n"
        "4. Redistribution. You may reproduce and distribute copies of the\n"
        "Work or Derivative Works thereof in any medium, with or without\n"
        "modifications, and in Source or Object form, provided that You\n"
        "meet the following conditions:\n\n"
        "(a) You must give any other recipients of the Work or\n"
        "Derivative Works a copy of this License; and\n\n"
        "(b) You must cause any modified files to carry prominent notices\n"
        "stating that You changed the files; and\n\n"
        "(c) You must retain, in the Source form of any Derivative Works\n"
        "that You distribute, all copyright, patent, trademark, and\n"
        "attribution notices from the Source form of the Work,\n"
        "excluding those notices that do not pertain to any part of\n"
        "the Derivative Works; and\n\n"
        "(d) If the Work includes a \"NOTICE\" text file as part of its\n"
        "distribution, then any Derivative Works that You distribute must\n"
        "include a readable copy of the attribution notices contained\n"
        "within such NOTICE file, excluding those notices that do not\n"
        "pertain to any part of the Derivative Works, in at least one\n"
        "of the following places: within a NOTICE text file distributed\n"
        "as part of the Derivative Works; within the Source form or\n"
        "documentation, if provided along with the Derivative Works; or,\n"
        "within a display generated by the Derivative Works, if and\n"
        "wherever such third-party notices normally appear. The contents\n"
        "of the NOTICE file are for informational purposes only and\n"
        "do not modify the License. You may add Your own attribution\n"
        "notices within Derivative Works that You distribute, alongside\n"
        "or as an addendum to the NOTICE text from the Work, provided\n"
        "that such additional attribution notices cannot be construed\n"
        "as modifying the License.\n\n"
        "You may add Your own copyright statement to Your modifications and\n"
        "may provide additional or different license terms and conditions\n"
        "for use, reproduction, or distribution of Your modifications, or\n"
        "for any such Derivative Works as a whole, provided Your use,\n"
        "reproduction, and distribution of the Work otherwise complies with\n"
        "the conditions stated in this License.\n\n"
        "5. Submission of Contributions. Unless You explicitly state otherwise,\n"
        "any Contribution intentionally submitted for inclusion in the Work\n"
        "by You to the Licensor shall be under the terms and conditions of\n"
        "this License, without any additional terms or conditions.\n"
        "Notwithstanding the above, nothing herein shall supersede or modify\n"
        "the terms of any separate license agreement you may have executed\n"
        "with Licensor regarding such Contributions.\n\n"
        "6. Trademarks. This License does not grant permission to use the trade\n"
        "names, trademarks, service marks, or product names of the Licensor,\n"
        "except as required for reasonable and customary use in describing the\n"
        "origin of the Work and reproducing the content of the NOTICE file.\n\n"
        "7. Disclaimer of Warranty. Unless required by applicable law or\n"
        "agreed to in writing, Licensor provides the Work (and each\n"
        "Contributor provides its Contributions) on an \"AS IS\" BASIS,\n"
        "WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or\n"
        "implied, including, without limitation, any warranties or conditions\n"
        "of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A\n"
        "PARTICULAR PURPOSE. You are solely responsible for determining the\n"
        "appropriateness of using or redistributing the Work and assume any\n"
        "risks associated with Your exercise of permissions under this License.\n\n"
        "8. Limitation of Liability. In no event and under no legal theory,\n"
        "whether in tort (including negligence), contract, or otherwise,\n"
        "unless required by applicable law (such as deliberate and grossly\n"
        "negligent acts) or agreed to in writing, shall any Contributor be\n"
        "liable to You for damages, including any direct, indirect, special,\n"
        "incidental, or consequential damages of any character arising as a\n"
        "result of this License or out of the use or inability to use the\n"
        "Work (including but not limited to damages for loss of goodwill,\n"
        "work stoppage, computer failure or malfunction, or any and all\n"
        "other commercial damages or losses), even if such Contributor\n"
        "has been advised of the possibility of such damages.\n\n"
        "9. Accepting Warranty or Additional Liability. While redistributing\n"
        "the Work or Derivative Works thereof, You may choose to offer,\n"
        "and charge a fee for, acceptance of support, warranty, indemnity,\n"
        "or other liability obligations and/or rights consistent with this\n"
        "License. However, in accepting such obligations, You may act only\n"
        "on Your own behalf and on Your sole responsibility, not on behalf\n"
        "of any other Contributor, and only if You agree to indemnify,\n"
        "defend, and hold each Contributor harmless for any liability\n"
        "incurred by, or claims asserted against, such Contributor by reason\n"
        "of your accepting any such warranty or additional liability.\n\n"
        "END OF TERMS AND CONDITIONS\n\n"
        "APPENDIX: How to apply the Apache License to your work.\n\n"
        "To apply the Apache License to your work, attach the following\n"
        "boilerplate notice, with the fields enclosed by brackets \"[]\"\n"
        "replaced with your own identifying information. (Don't include\n"
        "the brackets!)  The text should be enclosed in the appropriate\n"
        "comment syntax for the file format. We also recommend that a\n"
        "file or class name and description of purpose be included on the\n"
        "same \"printed page\" as the copyright notice for easier\n"
        "identification within third-party archives.\n\n"
        "   Copyright [yyyy] [name of copyright owner]\n\n"
        "   Licensed under the Apache License, Version 2.0 (the \"License\");\n"
        "   you may not use this file except in compliance with the License.\n"
        "   You may obtain a copy of the License at\n\n"
        "       http://www.apache.org/licenses/LICENSE-2.0\n\n"
        "   Unless required by applicable law or agreed to in writing, software\n"
        "   distributed under the License is distributed on an \"AS IS\" BASIS,\n"
        "   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n"
        "   See the License for the specific language governing permissions and\n"
        "   limitations under the License.\n",
        encoding="utf-8",
    )
    print(f"  APACHE-2.0_LICENSE.txt")

    # BtbN FFmpeg license (LGPL)
    sdk_root = Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "cid_build" / "ffmpeg-btbn-shared-7.1"
    for name in ("LICENSE", "LGPL", "COPYING"):
        for ext in ("", ".txt", ".md"):
            src = sdk_root / f"{name}{ext}"
            if src.is_file():
                shutil.copy2(src, licenses_dir / f"FFMPEG_{name}{ext}")
                break

    # Create notice for other components
    notice = licenses_dir / "THIRD_PARTY_NOTICES.txt"
    notice.write_text(
        f"CID Local Media Agent {VERSION} - Third-Party Notices\n"
        f"{'=' * 60}\n\n"
        f"This package includes the following third-party components:\n\n"
        f"1. Python 3.12 - PSF License\n"
        f"   See PYTHON_LICENSE.txt\n\n"
        f"2. FFmpeg (BtbN build n7.1.5) - GNU LGPL v3\n"
        f"   See FFMPEG_LICENSE.txt\n"
        f"   FFmpeg is dynamically linked. Corresponding source and build\n"
        f"   configuration for this BtbN build are available from the BtbN\n"
        f"   FFmpeg-Builds project; relinking is possible with the shared\n"
        f"   libraries shipped in runtime/ffmpeg/bin. Written source offer:\n"
        f"   contact the CID distributor on request.\n\n"
        f"3. CTranslate2 4.8.1 - MIT License\n"
        f"   Copyright 2020 OpenNMT. All rights reserved.\n\n"
        f"4. faster-whisper 1.2.1 - MIT License\n"
        f"   Copyright 2023 SYSTRAN. All rights reserved.\n\n"
        f"5. PyAV 16.0.0 - BSD License\n"
        f"   Copyright 2013-2024 PyAV contributors\n\n"
        f"6. NumPy - BSD License\n"
        f"   Copyright 2005-2024 NumPy Developers\n\n"
        f"7. tokenizers - Apache License 2.0\n"
        f"   Copyright  Hugging Face, Inc.\n\n"
        f"8. huggingface_hub - Apache License 2.0\n"
        f"   Copyright  Hugging Face, Inc.\n\n"
        f"9. onnxruntime - MIT License\n"
        f"   Copyright Microsoft Corporation\n\n"
        f"10. oneDNN - Apache License 2.0\n"
        f"    oneDNN (formerly DNNL) is statically linked into the CTranslate2\n"
        f"    binary distributed in this package. See APACHE-2.0_LICENSE.txt.\n\n"
        f"11. Systran/faster-whisper-small model - MIT License\n"
        f"    Copyright SYSTRAN. See MODEL_LICENSE.txt and the model README\n"
        f"    shipped in models/faster-whisper-small.\n\n"
        f"12. Various Python packages under BSD/MIT/Apache licenses\n"
        f"    Individual license texts are preserved in their installed\n"
        f"    package metadata under runtime/python/Lib/site-packages.\n",
        encoding="utf-8",
    )
    print(f"  licenses/")


def _create_release_notes(package_dir: Path) -> None:
    """Create a concise producer-facing beta limitations note."""
    note = package_dir / "NOTAS_BETA.txt"
    note.write_text(
        "CID Local Media Agent 0.3.0-beta1 - Notas de la versión beta\n"
        "============================================================\n\n"
        "Limitaciones conocidas de esta versión beta:\n\n"
        "1. La transcripción local en CPU puede tardar un tiempo\n"
        "   considerable en entrevistas largas.\n"
        "2. Los nombres propios pueden requerir corrección editorial\n"
        "   del transcripto.\n"
        "3. La sincronización de audio de cámara con grabadora externa\n"
        "   sigue pendiente de validación con una grabación real pareada.\n"
        "4. Esta versión beta es exclusiva para Windows.\n\n"
        "El producto funciona sin conexión y no sube ningún material.\n",
        encoding="utf-8",
    )
    print(f"  NOTAS_BETA.txt")


def _create_producer_readme(package_dir: Path) -> None:
    """Create a concise producer-facing first-read document."""
    readme = package_dir / "LEEME_PRIMERO.txt"
    readme.write_text(
        "CID Local Media Agent 0.3.0-beta1\n"
        "=================================\n\n"
        "Bienvenido. Esta es una versión beta para Windows.\n"
        "Todo el procesamiento es local y sin conexión.\n\n"
        "QUÉ HACE\n"
        "--------\n"
        "CID analiza el material de tu proyecto, identifica las grabaciones\n"
        "y recomienda qué audio transcribir. Genera subtítulos (SRT) que\n"
        "puedes importar en DaVinci Resolve.\n\n"
        "PRIVACIDAD\n"
        "----------\n"
        "- El análisis y la transcripción ocurren en tu equipo.\n"
        "- CID no sube ni envía tus archivos a ningún servicio.\n"
        "- La beta no necesita conexión a internet.\n"
        "- Tus archivos de origen no se modifican (solo lectura).\n"
        "- Los resultados se guardan localmente.\n\n"
        "CÓMO EMPEZAR\n"
        "------------\n"
        "1. Descomprime el archivo ZIP.\n"
        "2. Ejecuta install.cmd (o el instalador incluido).\n"
        "3. Abre \"CID Local Media Agent\" desde el menú Inicio.\n"
        "4. Selecciona la carpeta con el material del proyecto.\n"
        "5. Pulsa Analizar y sigue la recomendación de CID.\n"
        "6. Los resultados se guardan en tus Documentos y puedes abrirlos\n"
        "   desde la propia ventana de CID.\n\n"
        "DÓNDE SE GUARDAN LOS RESULTADOS\n"
        "-------------------------------\n"
        "Por defecto: C:\\Users\\<usuario>\\Documents\\CID Local Media Agent\\Resultados\n"
        "Puedes cambiar la ubicación desde CID y se recordará.\n\n"
        "CÓMO DESINSTALAR\n"
        "----------------\n"
        "Ejecuta uninstall.cmd de la carpeta instalada. Tus archivos de\n"
        "origen y tus resultados no se tocan.\n\n"
        "LIMITACIONES DE ESTA BETA\n"
        "--------------------------\n"
        "Ver NOTAS_BETA.txt en esta carpeta.\n\n"
        "SOPORTE\n"
        "-------\n"
        "Si algo falla, usa \"Exportar diagnóstico\" desde CID si está\n"
        "disponible, o recopila la carpeta de diagnósticos indicada por\n"
        "tu contacto de CID. No envíes material de tus entrevistas salvo\n"
        "que se te pida explícitamente.\n\n"
        "AVISO LEGAL\n"
        "-----------\n"
        "Los textos de licencia de terceros están en la carpeta licenses/.\n",
        encoding="utf-8",
    )
    print(f"  LEEME_PRIMERO.txt")


def _get_git_commit() -> str:
    """Get current git commit SHA (env override preferred, then git)."""
    env_commit = os.environ.get("CID_PRODUCT_COMMIT")
    if env_commit:
        return env_commit.strip()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def _dir_size(path: Path) -> int:
    """Calculate total size of a directory."""
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


def main() -> int:
    parser = argparse.ArgumentParser(description="Build CID LMA Windows beta package")
    parser.add_argument("--output-dir", type=str,
                       default=str(Path(os.environ.get("LOCALAPPDATA", "")) / "Temp" / "cid_release_build"),
                       help="Output directory for the package")
    args = parser.parse_args()

    output_base = Path(args.output_dir)
    package_dir = output_base / PACKAGE_NAME

    print(f"=" * 60)
    print(f"CID Local Media Agent {VERSION} - Package Builder")
    print(f"=" * 60)
    print(f"  Output: {package_dir}")
    print(f"  Python: {PYTHON_EXE}")
    print(f"  Repo:   {REPO_ROOT}")
    print(f"=" * 60)
    print()

    # Clean previous build
    if package_dir.exists():
        shutil.rmtree(package_dir)
        print("  Cleaned previous build")

    # Create directory structure
    target_python = package_dir / "runtime" / "python"
    target_lib = package_dir / "runtime" / "python" / "Lib"
    target_sp = package_dir / "runtime" / "python" / "Lib" / "site-packages"
    target_ffmpeg = package_dir / "runtime" / "ffmpeg" / "bin"
    target_models = package_dir / "models"
    target_app = package_dir / "app"

    print("[1/9] Python core + BtbN DLLs...")
    _copy_python_core(target_python)
    print()

    print("[2/9] Python stdlib...")
    _copy_stdlib(target_lib)
    print()

    print("[3/9] Validated site-packages...")
    _copy_site_packages(target_sp)
    print()

    print("[4/9] Python path isolation...")
    _create_python_pth(target_python, target_lib, target_sp)
    print()

    print("[5/9] FFmpeg binaries...")
    _copy_ffmpeg(target_ffmpeg)
    print()

    print("[6/9] Whisper model...")
    _copy_model(target_models)
    print()

    print("[7/9] CID source scripts...")
    _copy_cid_source(target_app)
    print()

    print("[8/9] Launcher, install, uninstall...")
    _create_launcher(package_dir)
    _create_gui_launcher(package_dir)
    _create_install_cmd(package_dir)
    _create_uninstall_cmd(package_dir)
    print()

    print("[9/9] Licenses, notes and manifest...")
    _create_licenses(package_dir)
    _create_release_notes(package_dir)
    _create_producer_readme(package_dir)
    pkg_size = _dir_size(package_dir)
    _create_package_manifest(package_dir, pkg_size, None, target_sp)
    print()

    print(f"=" * 60)
    print(f"Package built: {package_dir}")
    print(f"Package size:  {pkg_size / 1024 / 1024:.1f} MB")

    # Create ZIP
    zip_path = output_base / f"{PACKAGE_NAME}-win64.zip"
    print(f"\nCreating ZIP: {zip_path}")
    shutil.make_archive(
        str(zip_path.with_suffix("")),
        "zip",
        str(output_base),
        PACKAGE_NAME,
    )
    zip_size = zip_path.stat().st_size
    print(f"ZIP size: {zip_size / 1024 / 1024:.1f} MB")

    # Update manifest with ZIP size
    _create_package_manifest(package_dir, pkg_size, zip_size, target_sp)

    print(f"\n{'=' * 60}")
    print(f"BUILD COMPLETE")
    print(f"  Package: {package_dir}")
    print(f"  ZIP:     {zip_path}")
    print(f"{'=' * 60}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
