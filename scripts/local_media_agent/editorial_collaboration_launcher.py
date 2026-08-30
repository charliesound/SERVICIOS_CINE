"""CID local pilot launch experience for EDITORIAL_SELECTION (launch).

Turns the operator board into a one-click local experience: double-click a
Windows launcher -> a loopback-only server starts on an ephemeral port -> the
default browser opens on the clean localhost URL -> the operator uses the board
and closes it via a clean ``POST /shutdown``.

Binary/external-launch policy: only the stdlib ``webbrowser`` module is used.
No ``os.system``/``subprocess``/``start``/``cmd /c``/``powershell``. The browser
opener is injectable so tests can verify the URL without opening a browser.

Security contract: bind ``127.0.0.1`` (never LAN), ephemeral port ``0``, URL
carries no token/selection/filesystem path, request-token-protected shutdown,
no selection mutation on shutdown.
"""

from __future__ import annotations

import os
import threading
import webbrowser
from pathlib import Path
from typing import Any, Callable

from scripts.local_media_agent.editorial_collaboration_server import (
    create_server,
)

DEFAULT_ROLE = "PRODUCER"
HOST = "127.0.0.1"

DEFAULT_STORE_UNAVAILABLE = "CID_EDITORIAL_DEFAULT_STORE_UNAVAILABLE"
STORE_UNAVAILABLE = "CID_EDITORIAL_STORE_UNAVAILABLE"
BROWSER_OPEN_FAILED = "CID_EDITORIAL_BROWSER_OPEN_FAILED"
LAUNCH_ARGUMENTS_REJECTED = "CID_EDITORIAL_LAUNCH_ARGUMENTS_REJECTED"
LAUNCH_INTERNAL_FAILURE = "CID_EDITORIAL_LAUNCH_INTERNAL_FAILURE"


class LaunchError(Exception):
    """Base for controlled launcher failures."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class LaunchArgumentError(LaunchError):
    pass


class LaunchDefaultStoreUnavailable(LaunchError):
    pass


class LaunchStoreUnavailable(LaunchError):
    pass


class BrowserOpenFailed(LaunchError):
    pass


def default_store_path() -> Path:
    """Resolve the default pilot store from LOCALAPPDATA.

    Contract: only ``%LOCALAPPDATA%\\CID\\editorial_selections``. Missing
    LOCALAPPDATA (without an explicit store) is a controlled refusal. The
    directory may be empty; the launcher creates ONLY that empty directory.
    No fallback to repo/cwd/WSL/temp/home.
    """
    localappdata = os.environ.get("LOCALAPPDATA")
    if not localappdata or not localappdata.strip():
        raise LaunchDefaultStoreUnavailable(DEFAULT_STORE_UNAVAILABLE)
    return Path(localappdata) / "CID" / "editorial_selections"


def prepare_default_store(store: str | Path) -> Path:
    """Ensure the product default store directory exists (first-run support).

    Contract: resolve/store only ``%LOCALAPPDATA%\\CID\\editorial_selections``.
    Creates ONLY that directory tree when absent; never deletes/overwrites or
    modifies existing selection JSON. A path that exists but is not a directory,
    or an OS failure creating the tree, is a controlled refusal (no server).
    """
    store_path = Path(store)
    if store_path.exists():
        if not store_path.is_dir():
            raise LaunchStoreUnavailable(STORE_UNAVAILABLE)
        return store_path
    try:
        store_path.mkdir(parents=True, exist_ok=True)
    except OSError:
        raise LaunchStoreUnavailable(STORE_UNAVAILABLE) from None
    if not store_path.is_dir():
        raise LaunchStoreUnavailable(STORE_UNAVAILABLE)
    return store_path


def validate_explicit_store(store: str | Path) -> Path:
    """Validate a caller-supplied explicit store without creating it.

    Explicit stores are caller-controlled and must already exist as a
    directory. Missing or non-directory paths are a controlled refusal raised
    BEFORE any server is created. Never created implicitly, never falls back to
    ``LOCALAPPDATA``.
    """
    store_path = Path(store)
    if not store_path.exists() or not store_path.is_dir():
        raise LaunchStoreUnavailable(STORE_UNAVAILABLE)
    return store_path


def build_local_url(port: int) -> str:
    """Return the clean loopback launch URL (no token/selection/fs path)."""
    return f"http://127.0.0.1:{port}/"


def open_local_browser(url: str, opener: Callable[[str], bool] | None = None) -> None:
    """Open ``url`` in the default browser; controlled failure on refusal.

    ``opener`` is injectable for tests; defaults to ``webbrowser.open``. On a
    ``False`` return or an exception, raise ``BrowserOpenFailed`` (caller prints
    the safe URL, never a token/traceback).
    """
    if url is None or not str(url).startswith("http://127.0.0.1:"):
        raise BrowserOpenFailed(BROWSER_OPEN_FAILED)
    do_open = opener if opener is not None else webbrowser.open
    try:
        ok = do_open(url)
    except Exception as exc:
        raise BrowserOpenFailed(BROWSER_OPEN_FAILED) from exc
    if not ok:
        raise BrowserOpenFailed(BROWSER_OPEN_FAILED)


def launch_editorial_board(
    store: str | Path | None,
    role: str | None = None,
    *,
    open_browser: bool = True,
    opener: Callable[[str], bool] | None = None,
    store_env: str = "LOCALAPPDATA",
) -> dict[str, Any]:
    """Start the launch experience and block until a clean shutdown.

    Resolves the store (explicit or default), creates a loopback ephemeral
    server, opens the browser on the clean localhost URL, then serves until a
    valid ``POST /shutdown`` triggers a clean stop. Returns a result dict.
    """
    if role is None:
        role = DEFAULT_ROLE
    if not isinstance(role, str) or not role.strip():
        raise LaunchArgumentError(LAUNCH_ARGUMENTS_REJECTED)

    if store is None:
        try:
            default = default_store_path()
        except LaunchDefaultStoreUnavailable as exc:
            raise exc
        store_path = prepare_default_store(default)
    else:
        store_path = validate_explicit_store(Path(store))

    actual_store = str(store_path)

    stop = threading.Event()

    def _on_shutdown() -> None:
        # Runs on the handler thread after the shutdown response is flushed;
        # stop serve_forever from another thread so it returns cleanly.
        stop.set()
        server.shutdown()

    server = create_server(
        actual_store,
        role,
        host=HOST,
        port=0,
        shutdown_handler=_on_shutdown,
    )
    actual_port = server.server_address[1]
    url = build_local_url(actual_port)

    if open_browser:
        try:
            open_local_browser(url, opener=opener)
        except BrowserOpenFailed:
            pass  # caller prints browser-open-failed + safe URL, no traceback

    server_thread = threading.Thread(
        target=_serve_forever_until,
        args=(server, stop),
        name="cid-editorial-pilot",
        daemon=True,
    )
    server_thread.start()

    try:
        server_thread.join()
    finally:
        server.server_close()

    return {
        "store": actual_store,
        "role": role,
        "host": HOST,
        "port": actual_port,
        "url": url,
    }


def _serve_forever_until(server, stop: threading.Event) -> None:
    while not stop.is_set():
        # serve_forever(poll_interval) returns on shutdown()/close; we stop at
        # the next poll so the thread cannot block forever.
        server.serve_forever(poll_interval=0.2)


__all__ = [
    "DEFAULT_ROLE",
    "HOST",
    "DEFAULT_STORE_UNAVAILABLE",
    "STORE_UNAVAILABLE",
    "BROWSER_OPEN_FAILED",
    "LAUNCH_ARGUMENTS_REJECTED",
    "LAUNCH_INTERNAL_FAILURE",
    "LaunchError",
    "LaunchArgumentError",
    "LaunchDefaultStoreUnavailable",
    "LaunchStoreUnavailable",
    "BrowserOpenFailed",
    "default_store_path",
    "prepare_default_store",
    "validate_explicit_store",
    "build_local_url",
    "open_local_browser",
    "launch_editorial_board",
]
