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
import shutil
import subprocess
import sys
import sysconfig
from datetime import datetime, timezone
from pathlib import Path

VERSION = "0.2.0-beta1"
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
            "_testmultiphase.pyd", "_tkinter.pyd", "_wmi.pyd",
            "tcl86t.dll", "tk86t.dll", "winsound.pyd",
        }
        for entry in dlls_src.iterdir():
            if entry.is_file() and entry.name not in excluded:
                shutil.copy2(entry, dlls_dest / entry.name)
        print(f"  DLLs/ ({len(list(dlls_dest.iterdir()))} files)")


def _install_packages(target_site_packages: Path) -> None:
    """Install required packages into target using pip --target."""
    target_site_packages.mkdir(parents=True, exist_ok=True)
    cmd = [
        PYTHON_EXE, "-m", "pip", "install",
        "--target", str(target_site_packages),
        "--no-deps",
        "--quiet",
    ] + REQUIRED_PACKAGES
    print(f"  Installing {len(REQUIRED_PACKAGES)} packages...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        # Retry with deps for packages that need them
        cmd_full = [
            PYTHON_EXE, "-m", "pip", "install",
            "--target", str(target_site_packages),
            "--quiet",
        ] + REQUIRED_PACKAGES
        result = subprocess.run(cmd_full, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  WARNING: pip install had issues: {result.stderr[:500]}")
    # Count installed
    pkg_count = sum(1 for _ in target_site_packages.iterdir() if _.is_dir() or _.suffix == ".dist-info")
    print(f"  Installed {pkg_count} packages")


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
        "tkinter",
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
    """Create python312._pth for embedded Python path isolation."""
    pth_content = "\n".join([
        "python312.zip",
        ".",
        "DLLs",
        "Lib",
        "Lib/site-packages",
        "",
    ])
    pth_path = target_python / "python312._pth"
    pth_path.write_text(pth_content, encoding="utf-8")
    print(f"  python312._pth")


def _create_launcher(package_dir: Path) -> None:
    """Create the CID Local Media Agent launcher CMD."""
    launcher = package_dir / "CID Local Media Agent.cmd"
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
    print(f"  CID Local Media Agent.cmd")


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

echo   [3/5] Copying Python runtime...
if exist "%INSTALL_TARGET%\\runtime\\python" rmdir /s /q "%INSTALL_TARGET%\\runtime\\python"
xcopy /s /e /q /y "%PACKAGE_DIR%\\runtime\\python\\*" "%INSTALL_TARGET%\\runtime\\python\\" >nul

echo   [4/5] Copying FFmpeg...
if not exist "%INSTALL_TARGET%\\runtime\\ffmpeg\\bin" mkdir "%INSTALL_TARGET%\\runtime\\ffmpeg\\bin"
xcopy /s /e /q /y "%PACKAGE_DIR%\\runtime\\ffmpeg\\bin\\*" "%INSTALL_TARGET%\\runtime\\ffmpeg\\bin\\" >nul

echo   [5/5] Copying model (this may take a moment)...
if exist "%INSTALL_TARGET%\\models" rmdir /s /q "%INSTALL_TARGET%\\models"
xcopy /s /e /q /y "%PACKAGE_DIR%\\models\\*" "%INSTALL_TARGET%\\models\\" >nul

echo.
echo   [6/6] Creating launcher...
echo @echo off > "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent.cmd"
echo title CID Local Media Agent {VERSION} >> "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent.cmd"
echo. >> "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent.cmd"
echo set CID_PACKAGE_DIR=%INSTALL_TARGET% >> "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent.cmd"
echo set PYTHON=%INSTALL_TARGET%\\runtime\\python\\python.exe >> "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent.cmd"
echo set APP_DIR=%INSTALL_TARGET%\\app >> "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent.cmd"
echo set PYTHONNOUSERSITE=1 >> "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent.cmd"
echo set PYTHONPATH=%INSTALL_TARGET%\\app >> "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent.cmd"
echo set CID_FFMPEG_PATH=%INSTALL_TARGET%\\runtime\\ffmpeg\\bin\\ffmpeg.exe >> "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent.cmd"
echo set CID_FFPROBE_PATH=%INSTALL_TARGET%\\runtime\\ffmpeg\\bin\\ffprobe.exe >> "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent.cmd"
echo. >> "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent.cmd"
echo "%INSTALL_TARGET%\\runtime\\python\\python.exe" -m scripts.local_media_agent.cid_local_media_agent_operator %%* >> "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent.cmd"
echo if errorlevel 1 pause >> "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent.cmd"

echo.
echo   ======================================================
echo   Installation complete.
echo.
echo   Launch:  %LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent.cmd
echo   Target:  %INSTALL_TARGET%
echo   Results: %LOCALAPPDATA%\\CID\\LocalMediaAgent\\results\\
echo   ======================================================
echo.
pause
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
set LAUNCHER=%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Local Media Agent.cmd

echo   This will remove the installed CID Local Media Agent application.
echo   User results in %%LOCALAPPDATA%%\\CID\\LocalMediaAgent\\results\\
echo   will be PRESERVED.
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

echo   [2/3] Removing launcher...
if exist "%LAUNCHER%" del /f "%LAUNCHER%"

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
echo   %%LOCALAPPDATA%%\\CID\\LocalMediaAgent\\results\\
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
) -> None:
    """Create package_manifest.json."""
    manifest = {
        "package_name": PACKAGE_NAME,
        "version": VERSION,
        "package_type": "windows_self_contained_beta",
        "build_timestamp": datetime.now(timezone.utc).isoformat(),
        "target_os": "windows",
        "target_arch": "win_amd64",
        "product_commit_sha": _get_git_commit(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "ctranslate2_version": "4.8.1",
        "pyav_version": "16.0.0",
        "ffmpeg_identity": "BtbN n7.1.5-12-g1fdbca85aa win64-lgpl-shared-7.1",
        "faster_whisper_version": "1.2.1",
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
            "CID Local Media Agent.cmd": "Launcher",
            "licenses/": "Third-party license files",
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
        f"2. FFmpeg (BtbN build) - LGPL v2.1\n"
        f"   See FFMPEG_LICENSE.txt\n\n"
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
        f"10. Various Python packages under BSD/MIT/Apache licenses\n",
        encoding="utf-8",
    )
    print(f"  licenses/")


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

    print("[3/9] Required packages...")
    _install_packages(target_sp)
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
    _create_install_cmd(package_dir)
    _create_uninstall_cmd(package_dir)
    print()

    print("[9/9] Licenses and manifest...")
    _create_licenses(package_dir)
    pkg_size = _dir_size(package_dir)
    _create_package_manifest(package_dir, pkg_size, None)
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
    _create_package_manifest(package_dir, pkg_size, zip_size)

    print(f"\n{'=' * 60}")
    print(f"BUILD COMPLETE")
    print(f"  Package: {package_dir}")
    print(f"  ZIP:     {zip_path}")
    print(f"{'=' * 60}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
