from __future__ import annotations

import json
from pathlib import Path

import pytest

import scripts.windows.build_beta_package as B


MODULES = [
    "editorial_collaboration_launcher.py",
    "editorial_collaboration_server.py",
    "editorial_selection_cli.py",
    "editorial_selection.py",
    "editorial_collaboration_surface.py",
]


def _invocation_lines(text: str) -> str:
    """Return only executable (non-rem/echo-header) lines of a .bat.

    Comment lines legitimately mention forbidden tool names (e.g. "no py.exe")
    to explain what the launcher does NOT use; only actual invocations matter.
    """
    kept = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(("rem", "@echo off", "echo", "setlocal", "endlocal", "goto")):
            continue
        if stripped.startswith("::"):
            continue
        kept.append(stripped)
    return "\n".join(kept)


@pytest.fixture()
def assembled_package(tmp_path: Path):
    """Controlled temp assembly fixture using the real builder helpers.

    Uses fake/minimal runtime placeholders (no full 500MB build). Runs only the
    editorial-relevant integration helpers with a minimal layout.
    """
    pkg = tmp_path / "CID-Local-Media-Agent-0.3.0-beta2"
    runtime = pkg / "runtime" / "python"
    runtime.mkdir(parents=True)
    runtime.joinpath("python.exe").write_bytes(b"x")
    runtime.joinpath("pythonw.exe").write_bytes(b"w")
    runtime.joinpath("python312._pth").write_text("..\\..\\app\n")
    (pkg / "runtime" / "ffmpeg" / "bin").mkdir(parents=True)
    (pkg / "models" / "faster-whisper-small").mkdir(parents=True)

    app = pkg / "app" / "scripts" / "local_media_agent"
    app.mkdir(parents=True)
    for mod in MODULES:
        app.joinpath(mod).write_text("# placeholder\n")

    site_packages = pkg / "runtime" / "python" / "Lib" / "site-packages"
    site_packages.mkdir(parents=True)

    B._copy_editorial_launcher(pkg)
    B._create_install_cmd(pkg)
    B._create_uninstall_cmd(pkg)
    B._create_producer_readme(pkg)
    B._create_package_manifest(pkg, 0, None, site_packages)
    return pkg


# ---------------- package layout / python authority ----------------

def test_builder_authoritative_runtime_path_is_runtime_python() -> None:
    assert B._copy_python_core.__name__ == "_copy_python_core"
    # main() creates python at package/runtime/python
    assert B.EDITORIAL_LAUNCHER_BASENAME == "CID Editorial.bat"
    assert B.EDITORIAL_INSTALL_RUNTIME == "runtime\\python\\pythonw.exe"


def test_package_python_core_includes_python_exe(assembled_package) -> None:
    assert (assembled_package / "runtime" / "python" / "python.exe").is_file()


def test_package_python_core_includes_pythonw_authority(assembled_package) -> None:
    assert (assembled_package / "runtime" / "python" / "pythonw.exe").is_file()


def test_python312_pth_contains_app_path(assembled_package) -> None:
    pth = (assembled_package / "runtime" / "python" / "python312._pth").read_text(encoding="utf-8")
    assert "..\\..\\app" in pth
    # the app dir is importable as scripts.local_media_agent.editorial_selection_cli
    assert "app" in pth


def test_cid_source_dirs_includes_local_media_agent() -> None:
    assert "scripts/local_media_agent" in B.CID_SOURCE_DIRS


# ---------------- launcher source / package -----------------

def test_editorial_launcher_source_exists() -> None:
    assert B.EDITORIAL_LAUNCHER_SOURCE.is_file()
    assert B.EDITORIAL_LAUNCHER_SOURCE.name == "cid_editorial_pilot_launcher.bat"


def test_package_assembly_copies_editorial_launcher(assembled_package) -> None:
    assert (assembled_package / "CID Editorial.bat").is_file()


def test_packaged_launcher_matches_source_authority(assembled_package) -> None:
    packaged = (assembled_package / "CID Editorial.bat").read_text(encoding="utf-8")
    assert packaged.rstrip("\r\n") == B._editorial_launcher_text().rstrip("\r\n")


def test_packaged_launcher_no_carlos(assembled_package) -> None:
    text = (assembled_package / "CID Editorial.bat").read_text(encoding="utf-8")
    assert "Carlos" not in text


def test_packaged_launcher_no_wsl_localhost(assembled_package) -> None:
    text = (assembled_package / "CID Editorial.bat").read_text(encoding="utf-8")
    assert "wsl.localhost" not in text
    assert "wsl$" not in text


def test_packaged_launcher_no_mnt_slash(assembled_package) -> None:
    text = (assembled_package / "CID Editorial.bat").read_text(encoding="utf-8")
    assert "/mnt/" not in text


def test_packaged_launcher_no_py_exe(assembled_package) -> None:
    text = (assembled_package / "CID Editorial.bat").read_text(encoding="utf-8")
    # no invocation of py.exe / where python / system python
    assert not any(line.strip().startswith(("py.exe", "where python")) for line in text.splitlines() if not line.strip().startswith(("rem", "@echo", "echo")))
    # no system Python absolute path reference
    assert "\\Python" not in text.replace("python\\pythonw", "")


def test_packaged_launcher_no_system_python_absolute_path(assembled_package) -> None:
    text = (assembled_package / "CID Editorial.bat").read_text(encoding="utf-8")
    assert "C:\\Python" not in text
    assert "C:/Python" not in text


def test_packaged_launcher_prefers_pythonw(assembled_package) -> None:
    text = (assembled_package / "CID Editorial.bat").read_text(encoding="utf-8")
    # pythonw must be resolved before (and independently present) python.exe
    assert text.index("pythonw.exe") < text.index("python.exe")


def test_packaged_launcher_falls_back_to_python_exe(assembled_package) -> None:
    text = (assembled_package / "CID Editorial.bat").read_text(encoding="utf-8")
    assert "runtime\\python\\python.exe" in text


def test_packaged_launcher_invokes_selection_cli_launch(assembled_package) -> None:
    text = (assembled_package / "CID Editorial.bat").read_text(encoding="utf-8")
    assert "scripts.local_media_agent.editorial_selection_cli launch" in text


# ---------------- cmd paren escape defect (WINDOWS_CMD_UNESCAPED_CLOSING_PAREN) ----------------

def test_released_launcher_escapes_if_set_parentheses() -> None:
    # The refusal block lives inside `if not defined PYTHON_EXE ( ... )`. An
    # unescaped ")" inside the block bytes prematurely closes it in cmd.exe,
    # making the following lines unconditional. The literal must be CMD-escaped.
    text = B._editorial_launcher_text()
    assert "echo     CID_PYTHONW environment variable ^(if set^)" in text


def test_released_launcher_has_no_unsafe_unclosed_paren_literal() -> None:
    text = B._editorial_launcher_text()
    assert "CID_PYTHONW environment variable (if set)" not in text.replace("CID_PYTHONW environment variable ^(if set^)", "")


def test_packaged_launcher_contains_escaped_form(assembled_package) -> None:
    text = (assembled_package / "CID Editorial.bat").read_text(encoding="utf-8")
    assert "echo     CID_PYTHONW environment variable ^(if set^)" in text


def test_packaged_launcher_has_no_unsafe_unclosed_paren_literal(assembled_package) -> None:
    text = (assembled_package / "CID Editorial.bat").read_text(encoding="utf-8")
    safe = "CID_PYTHONW environment variable ^(if set^)"
    assert "CID_PYTHONW environment variable (if set)" not in text.replace(safe, "")


def test_packaged_launcher_refusal_block_stays_parenthesized(assembled_package) -> None:
    # The refusal branch must remain a single cmd `(...)` block closed by the
    # structural `)` on its own line, guarded by `if not defined PYTHON_EXE`.
    # The refusal must terminate (exit /b 1) before the launch command, and the
    # escaped diagnostic must sit inside that block (before its closing `)`).
    text = (assembled_package / "CID Editorial.bat").read_text(encoding="utf-8")
    refusal_open = text.index("if not defined PYTHON_EXE (")
    launch_at = text.index("scripts.local_media_agent.editorial_selection_cli launch")
    block = text[refusal_open:launch_at]
    assert "CID Editorial Pilot: packaged Python runtime not found." in block
    assert "CID_PYTHONW environment variable ^(if set^)" in block
    assert "exit /b 1" in block
    # resolve pythonw.exe before resolving python.exe (structure is preserved)
    assert block.index("pythonw.exe") < block.index("python.exe")


def test_packaged_launcher_resolution_order_preserved(assembled_package) -> None:
    text = (assembled_package / "CID Editorial.bat").read_text(encoding="utf-8")
    pos_cid = text.index("if defined CID_PYTHONW")
    pos_pyw = text.index("if exist \"%BASE%\\runtime\\python\\pythonw.exe\"")
    pos_py = text.index("if exist \"%BASE%\\runtime\\python\\python.exe\"")
    # CID_PYTHONW -> pythonw.exe -> python.exe
    assert pos_cid < pos_pyw < pos_py


def test_packaged_launcher_missing_runtime_refusal_kept(assembled_package) -> None:
    text = (assembled_package / "CID Editorial.bat").read_text(encoding="utf-8")
    assert "CID Editorial Pilot: packaged Python runtime not found." in text
    assert "exit /b 1" in text
    assert "Expected one of:" in text


# ---------------- CID source modules included -----------------

@pytest.mark.parametrize("module", MODULES)
def test_package_contains_editorial_module(assembled_package, module) -> None:
    assert (assembled_package / "app" / "scripts" / "local_media_agent" / module).is_file()


def test_modules_covered_by_directory_copy_not_duplicated() -> None:
    # directory copy of scripts/local_media_agent already covers them; we must
    # not add individual duplicate copies.
    assert "scripts/local_media_agent" in B.CID_SOURCE_DIRS


def test_recursive_copy_includes_project_video_profile_modules(tmp_path) -> None:
    app = tmp_path / "app"
    app.mkdir()
    B._copy_cid_source(app)
    module_root = app / "scripts" / "local_media_agent"
    for module in (
        "local_project.py",
        "project_video_profile.py",
        "source_video_profile.py",
    ):
        assert (module_root / module).is_file()


# ---------------- manifest -----------------

def test_manifest_includes_editorial_launcher(assembled_package) -> None:
    manifest = json.loads((assembled_package / "package_manifest.json").read_text(encoding="utf-8"))
    assert manifest["contents"]["CID Editorial.bat"] == "CID Editorial one-click local collaboration launcher"


def test_manifest_keeps_runtime_python_authority(assembled_package) -> None:
    manifest = json.loads((assembled_package / "package_manifest.json").read_text(encoding="utf-8"))
    assert "runtime/python" in manifest["contents"]


def test_manifest_keeps_ffmpeg_authority(assembled_package) -> None:
    manifest = json.loads((assembled_package / "package_manifest.json").read_text(encoding="utf-8"))
    assert "runtime/ffmpeg/bin" in manifest["contents"]


# ---------------- installer -----------------

def test_install_creates_installed_editorial_launcher(assembled_package) -> None:
    install = (assembled_package / "install.cmd").read_text(encoding="utf-8")
    assert 'copy /y "%PACKAGE_DIR%\\CID Editorial.bat" "%INSTALL_TARGET%\\CID Editorial.bat"' in install
    assert "%LOCALAPPDATA%\\CID\\LocalMediaAgent\\CID Editorial.bat" in install


def test_installed_launcher_resolves_installed_runtime(assembled_package) -> None:
    install = (assembled_package / "install.cmd").read_text(encoding="utf-8")
    # installed-root launcher is copied into INSTALL_TARGET (app), so its
    # relative runtime\\python\\pythonw.exe resolves to installed runtime.
    assert 'copy /y "%PACKAGE_DIR%\\CID Editorial.bat" "%INSTALL_TARGET%\\CID Editorial.bat"' in install
    # wrapper delegates to INSTALL_TARGET launcher, which uses ~dp0 runtime
    assert 'call "%INSTALL_TARGET%\\CID Editorial.bat"' in install


def test_installed_launcher_never_uses_system_python(assembled_package) -> None:
    launcher = (assembled_package / "CID Editorial.bat").read_text(encoding="utf-8")
    exec_lines = _invocation_lines(launcher)
    assert "where python" not in exec_lines
    assert "py.exe" not in exec_lines
    assert "C:\\Python" not in exec_lines


def test_installed_launcher_invokes_selection_cli_launch(assembled_package) -> None:
    launcher = (assembled_package / "CID Editorial.bat").read_text(encoding="utf-8")
    assert "scripts.local_media_agent.editorial_selection_cli launch" in launcher


def test_installed_launcher_defaults_producer_via_released_launch(assembled_package) -> None:
    # the released launch command omits --role, so PRODUCER default is used
    launcher = (assembled_package / "CID Editorial.bat").read_text(encoding="utf-8")
    assert " launch" in launcher
    assert "--role" not in launcher


# ---------------- uninstaller -----------------

def test_uninstall_removes_installed_editorial_launcher(assembled_package) -> None:
    uninstall = (assembled_package / "uninstall.cmd").read_text(encoding="utf-8")
    assert "CID Editorial.bat" in uninstall
    assert "del /f" in uninstall


def test_uninstall_does_not_delete_editorial_selections(assembled_package) -> None:
    uninstall = (assembled_package / "uninstall.cmd").read_text(encoding="utf-8")
    # the only recursive delete is INSTALL_TARGET (app), not the store
    assert uninstall.count("rmdir /s /q \"%INSTALL_TARGET%\"") == 1
    assert "editorial_selections" in uninstall
    assert "/s /q \"%LOCALAPPDATA%\\CID\"" not in uninstall


def test_uninstall_success_exits_zero_and_preserves_editorial_state(assembled_package) -> None:
    uninstall = (assembled_package / "uninstall.cmd").read_text(encoding="utf-8")
    assert uninstall.rstrip().endswith("pause\nexit /b 0")
    assert uninstall.count('rmdir /s /q "%INSTALL_TARGET%"') == 1
    assert 'rmdir /s /q "%LOCALAPPDATA%\\CID"' not in uninstall
    assert "editorial_selections" in uninstall
    assert 'del /f "%EDITORIAL_LAUNCHER%"' in uninstall
    assert 'del /f "%EDITORIAL_LAUNCHER_INSTALLED%"' in uninstall
    assert 'rmdir /s /q "%LOCALAPPDATA%\\CID\\projects"' not in uninstall
    assert 'del /f "%LOCALAPPDATA%\\CID\\active_project.json"' not in uninstall


def test_install_reinstall_does_not_delete_editorial_selections(assembled_package) -> None:
    install = (assembled_package / "install.cmd").read_text(encoding="utf-8")
    # install never rmdir the editorial store
    assert "editorial_selections" not in install
    assert "/s /q \"%LOCALAPPDATA%\\CID\"" not in install
    assert 'rmdir /s /q "%LOCALAPPDATA%\\CID\\projects"' not in install
    assert 'del /f "%LOCALAPPDATA%\\CID\\active_project.json"' not in install


def test_package_build_does_not_create_editorial_selections(assembled_package) -> None:
    store = assembled_package / "editorial_selections"
    assert not store.exists()
    assert not (assembled_package / "CID" / "editorial_selections").exists()


# ---------------- readme -----------------

def test_readme_documents_cid_editorial(assembled_package) -> None:
    readme = (assembled_package / "LEEME_PRIMERO.txt").read_text(encoding="utf-8")
    assert "CID EDITORIAL" in readme.upper()


def test_readme_states_local_127_0_0_1_behavior(assembled_package) -> None:
    readme = (assembled_package / "LEEME_PRIMERO.txt").read_text(encoding="utf-8")
    assert "127.0.0.1" in readme


def test_readme_explains_browser_shutdown(assembled_package) -> None:
    readme = (assembled_package / "LEEME_PRIMERO.txt").read_text(encoding="utf-8")
    assert "Close CID Editorial" in readme
    assert "navegador" in readme


def test_readme_no_wsl_for_user_flow(assembled_package) -> None:
    readme = (assembled_package / "LEEME_PRIMERO.txt").read_text(encoding="utf-8")
    assert "wsl" not in readme.lower()


# ---------------- dependency / license / personal paths -----------------

def test_no_new_dependency_introduced() -> None:
    # no new third-party package identity added
    text = Path(B.__file__).read_text(encoding="utf-8")
    assert "REQUIRED_PACKAGES" in text


def test_license_identity_unchanged() -> None:
    text = Path(B.__file__).read_text(encoding="utf-8")
    assert "ffmpeg_identity" in text
    assert "BtbN" in text
    assert "PYTHON_LICENSE.txt" in text
    assert "MODEL_LICENSE.txt" in text
    # no new component identity introduced
    assert text.count("\"runtime/python\"") == 1


def test_no_source_media_paths_embedded(assembled_package) -> None:
    for f in ("CID Editorial.bat",):
        text = (assembled_package / f).read_text(encoding="utf-8")
        assert ".mp4" not in text
        assert "ffmpeg.exe" not in text


def test_no_username_embedded(assembled_package) -> None:
    text = (assembled_package / "CID Editorial.bat").read_text(encoding="utf-8")
    assert "\\Users\\" not in text
    assert "C:\\Users" not in text


def test_no_repo_absolute_path_in_launcher(assembled_package) -> None:
    text = (assembled_package / "CID Editorial.bat").read_text(encoding="utf-8")
    assert "/opt/SERVICIOS_CINE" not in text
    assert "\\opt\\SERVICIOS_CINE" not in text


def test_package_contract_from_root_with_spaces(tmp_path) -> None:
    root = tmp_path / "My Package Space" / "CID Editorial Dist"
    pkg = root / "PKG"
    runtime = pkg / "runtime" / "python"
    runtime.mkdir(parents=True)
    runtime.joinpath("python.exe").write_bytes(b"x")
    runtime.joinpath("pythonw.exe").write_bytes(b"w")
    runtime.joinpath("python312._pth").write_text("..\\..\\app\n")
    app = pkg / "app" / "scripts" / "local_media_agent"
    app.mkdir(parents=True)
    for mod in MODULES:
        app.joinpath(mod).write_text("#x\n")
    (pkg / "runtime" / "ffmpeg" / "bin").mkdir(parents=True)
    (pkg / "models" / "faster-whisper-small").mkdir(parents=True)
    sp = pkg / "runtime" / "python" / "Lib" / "site-packages"
    sp.mkdir(parents=True)
    B._copy_editorial_launcher(pkg)
    B._create_install_cmd(pkg)
    B._create_uninstall_cmd(pkg)
    B._create_producer_readme(pkg)
    B._create_package_manifest(pkg, 0, None, sp)
    contract = B._validate_editorial_package_contract(pkg)
    assert contract["launcher_present"] is True
    assert contract["launcher_identical_to_source"] is True


def test_installed_launcher_contract_from_localappdata_with_spaces(tmp_path) -> None:
    local = tmp_path / "CID Local Data with Spaces"
    install_target = local / "CID" / "LocalMediaAgent" / "app"
    runtime = install_target / "runtime" / "python"
    runtime.mkdir(parents=True)
    runtime.joinpath("pythonw.exe").write_bytes(b"w")
    runtime.joinpath("python.exe").write_bytes(b"x")
    runtime.joinpath("python312._pth").write_text("..\\..\\app\n")
    app = install_target / "app" / "scripts" / "local_media_agent"
    app.mkdir(parents=True)
    for mod in MODULES:
        app.joinpath(mod).write_text("#x\n")
    (install_target / "runtime" / "ffmpeg" / "bin").mkdir(parents=True)
    (install_target / "models" / "faster-whisper-small").mkdir(parents=True)
    sp = install_target / "runtime" / "python" / "Lib" / "site-packages"
    sp.mkdir(parents=True)
    # installed-root launcher derived from released source
    B._copy_editorial_launcher(install_target)
    contract = B._validate_editorial_package_contract(install_target)
    assert contract["launcher_present"] is True
    assert contract["runtime_authority_ok"] is True
    assert contract["launcher_identical_to_source"] is True


def test_only_authoritative_packaged_python_used(assembled_package) -> None:
    launcher = (assembled_package / "CID Editorial.bat").read_text(encoding="utf-8")
    assert "runtime\\python\\pythonw.exe" in launcher
    assert "runtime\\python\\python.exe" in launcher
    exec_lines = _invocation_lines(launcher)
    assert "where python" not in exec_lines
    assert "py.exe" not in exec_lines
    assert "sys.executable" not in exec_lines
