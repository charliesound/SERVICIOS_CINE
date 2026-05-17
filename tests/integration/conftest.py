from __future__ import annotations

import importlib
import os
import sqlite3
import subprocess
import sys
import types
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "src"

# Default to memory queue for SQLite compatibility in tests
os.environ.setdefault("QUEUE_PERSISTENCE_MODE", "memory")

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


PROJECT_MODULE_PREFIXES = (
    "app",
    "config",
    "core",
    "database",
    "dependencies",
    "middleware",
    "models",
    "routes",
    "services",
)

SMOKE_ORG_A = "db4d7a5dadc9457ebaa2993a30d48201"
SMOKE_ORG_B = "54c10f417b714c558dc6da6015a96cc3"
SMOKE_ADMIN_USER_ID = "dd66db71cbe643eb9494abd8616d3f64"
SMOKE_TENANT_A_USER_ID = "4b153c715f76428b9e299698e5ab5561"
SMOKE_TENANT_B_USER_ID = "54c10f417b714c558dc6da6015a96cc2"
SMOKE_PROJECT_ID = "32fb858f66ef4569a7bc12db3b5ef2fd"
SMOKE_STORAGE_SOURCE_ID = "d7fac025-fa34-487d-a83a-d81ce2aadcac"
SMOKE_STORAGE_ROOT = REPO_ROOT / "data" / "smoke_tenant_A" / "project_alpha"

_MINIMAL_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR"
    b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
    b"\x90wS\xde"
    b"\x00\x00\x00\x0cIDATx\x9cc\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00"
    b"\xc9\xfe\x92\xef"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _placeholder_bytes(file_name: str, mime_type: str | None) -> bytes:
    name = file_name.lower()
    mime = (mime_type or "").lower()
    if mime == "image/png" or name.endswith(".png"):
        return _MINIMAL_PNG_BYTES
    if mime in {"application/pdf"} or name.endswith(".pdf"):
        return b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n"
    if mime.startswith("image/"):
        return _MINIMAL_PNG_BYTES
    return b"smoke placeholder\n"


def _ensure_shared_smoke_filesystem_fixture(db_path: Path) -> None:
    data_root = REPO_ROOT / "data"
    (data_root / "smoke_tenant_A").mkdir(parents=True, exist_ok=True)
    (data_root / "smoke_tenant_B").mkdir(parents=True, exist_ok=True)

    if not _sqlite_table_exists(db_path, "storage_sources"):
        return

    connection = sqlite3.connect(str(db_path))
    try:
        cursor = connection.cursor()
        storage_rows = cursor.execute(
            """
            SELECT id, mount_path
            FROM storage_sources
            WHERE organization_id IN (?, ?)
            """,
            (SMOKE_ORG_A, SMOKE_ORG_B),
        ).fetchall()

        storage_roots_by_id: dict[str, Path] = {}
        for storage_id, mount_path in storage_rows:
            mount_text = (mount_path or "").strip()
            if not mount_text:
                continue
            root_path = Path(mount_text)
            if not root_path.is_absolute():
                root_path = (REPO_ROOT / root_path).resolve()
            else:
                root_path = root_path.resolve()
            root_path.mkdir(parents=True, exist_ok=True)
            storage_roots_by_id[str(storage_id)] = root_path

        if not _sqlite_table_exists(db_path, "media_assets"):
            return

        asset_rows = cursor.execute(
            """
            SELECT storage_source_id, file_name, relative_path, canonical_path, mime_type
            FROM media_assets
            WHERE project_id = ? AND organization_id IN (?, ?)
            """,
            (SMOKE_PROJECT_ID, SMOKE_ORG_A, SMOKE_ORG_B),
        ).fetchall()

        for storage_source_id, file_name, relative_path, canonical_path, mime_type in asset_rows:
            storage_root = storage_roots_by_id.get(str(storage_source_id or ""))
            file_path: Path | None = None

            if canonical_path:
                canonical = Path(str(canonical_path))
                file_path = canonical if canonical.is_absolute() else (REPO_ROOT / canonical)
            elif storage_root and relative_path:
                file_path = storage_root / str(relative_path)
            elif storage_root and file_name:
                file_path = storage_root / str(file_name)

            if file_path is None:
                continue

            file_path = file_path.resolve()
            file_path.parent.mkdir(parents=True, exist_ok=True)
            if not file_path.exists():
                file_path.write_bytes(_placeholder_bytes(str(file_name or file_path.name), mime_type))
    finally:
        connection.close()


def _is_project_module(module_name: str) -> bool:
    return any(
        module_name == prefix or module_name.startswith(f"{prefix}.")
        for prefix in PROJECT_MODULE_PREFIXES
    )


def _purge_project_modules() -> None:
    for module_name in list(sys.modules):
        if _is_project_module(module_name):
            sys.modules.pop(module_name, None)


def _database_url_for_path(db_path: Path) -> str:
    return f"sqlite+aiosqlite:///{db_path}"


def _sqlite_table_exists(db_path: Path, table_name: str) -> bool:
    if not db_path.exists():
        return False
    connection = sqlite3.connect(str(db_path))
    try:
        row = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table_name,),
        ).fetchone()
        return row is not None
    finally:
        connection.close()


def _seed_shared_smoke_dataset(db_path: Path) -> None:
    if not _sqlite_table_exists(db_path, "organizations"):
        return

    connection = sqlite3.connect(str(db_path))
    try:
        cursor = connection.cursor()

        cursor.execute(
            "INSERT OR REPLACE INTO organizations (id, name, billing_plan, is_active) VALUES (?, ?, ?, ?)",
            (SMOKE_ORG_A, "Smoke Tenant A", "producer", 1),
        )
        cursor.execute(
            "INSERT OR REPLACE INTO organizations (id, name, billing_plan, is_active) VALUES (?, ?, ?, ?)",
            (SMOKE_ORG_B, "Smoke Tenant B", "producer", 1),
        )

        users = [
            (
                SMOKE_ADMIN_USER_ID,
                SMOKE_ORG_A,
                "smoke_admin",
                "smoke_admin@example.com",
                "unused",
                "Smoke Admin",
                "ADMIN",
                1,
                "producer",
                "producer",
                "seed",
                "active",
                "admin",
                1,
                1,
            ),
            (
                SMOKE_TENANT_A_USER_ID,
                SMOKE_ORG_A,
                "smoke_tenant_a",
                "smoke_tenant_a@example.com",
                "unused",
                "Smoke Tenant A",
                "PRODUCER",
                1,
                "producer",
                "producer",
                "seed",
                "active",
                "standard",
                1,
                1,
            ),
            (
                SMOKE_TENANT_B_USER_ID,
                SMOKE_ORG_B,
                "smoke_tenant_b",
                "smoke_tenant_b@example.com",
                "unused",
                "Smoke Tenant B",
                "PRODUCER",
                1,
                "producer",
                "producer",
                "seed",
                "active",
                "standard",
                1,
                1,
            ),
        ]
        for row in users:
            cursor.execute(
                """
                INSERT OR REPLACE INTO users (
                    id, organization_id, username, email, hashed_password, full_name,
                    role, is_active, billing_plan, program, signup_type,
                    account_status, access_level, cid_enabled, onboarding_completed
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                row,
            )

        cursor.execute(
            """
            INSERT OR REPLACE INTO projects (
                id, organization_id, name, description, status, script_text
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                SMOKE_PROJECT_ID,
                SMOKE_ORG_A,
                "Project Alpha",
                "Smoke project for presentation and funding integration tests.",
                "development",
                "INT. STUDIO - DAY\nA smoke project validates presentation routes.",
            ),
        )

        if _sqlite_table_exists(db_path, "storage_sources"):
            cursor.execute(
                """
                INSERT OR REPLACE INTO storage_sources (
                    id, organization_id, project_id, name, source_type, mount_path, status, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    SMOKE_STORAGE_SOURCE_ID,
                    SMOKE_ORG_A,
                    SMOKE_PROJECT_ID,
                    "Smoke storyboard root",
                    "local",
                    str(SMOKE_STORAGE_ROOT),
                    "active",
                    SMOKE_ADMIN_USER_ID,
                ),
            )

        connection.commit()
    finally:
        connection.close()

    _ensure_shared_smoke_filesystem_fixture(db_path)


def _resolve_module_db_path(module) -> Path | None:
    raw_path = getattr(module, "TEST_DB_PATH", None)
    if raw_path is None:
        raw_path = getattr(module, "DB_PATH", None)
    if raw_path is None:
        return (REPO_ROOT / "ailinkcinema_s2.db").resolve()
    return Path(raw_path).resolve()


def _apply_test_environment(module) -> Path | None:
    db_path = _resolve_module_db_path(module)

    os.environ["APP_ENV"] = "test"
    os.environ["AUTH_SECRET_KEY"] = os.environ.get("AUTH_SECRET_KEY", "a" * 32)
    os.environ["APP_SECRET_KEY"] = os.environ.get("APP_SECRET_KEY", "a" * 32)
    os.environ["QUEUE_AUTO_START_SCHEDULER"] = "0"
    os.environ["USE_ALEMBIC"] = "1"
    os.environ["DATABASE_USE_ALEMBIC"] = "true"

    if db_path is not None:
        os.environ["DATABASE_URL"] = _database_url_for_path(db_path)

    return db_path


def _rebind_backend_globals(module) -> None:
    _purge_project_modules()
    importlib.invalidate_caches()

    app_module = importlib.import_module("app")
    database_module = importlib.import_module("database")
    importlib.import_module("models")
    auth_routes_module = importlib.import_module("routes.auth_routes")

    module.app = app_module.app
    module._integration_database_module = database_module

    if hasattr(module, "Base"):
        module.Base = database_module.Base
    if hasattr(module, "engine"):
        module.engine = database_module.engine
    if hasattr(module, "AsyncSessionLocal"):
        module.AsyncSessionLocal = database_module.AsyncSessionLocal
    if hasattr(module, "create_access_token"):
        module.create_access_token = auth_routes_module.create_access_token
    if hasattr(module, "google_drive_service") or hasattr(module, "OAuthTokenPayload"):
        google_drive_module = importlib.import_module("services.google_drive_service")
        module.google_drive_service = google_drive_module.google_drive_service
        module.OAuthTokenPayload = google_drive_module.OAuthTokenPayload
    if hasattr(module, "project_funding_service"):
        funding_service_module = importlib.import_module("services.project_funding_service")
        module.project_funding_service = funding_service_module.project_funding_service


def _install_alembic_bootstrap(module, db_path: Path | None) -> None:
    if db_path is None or not hasattr(module, "_force_initialize_schema"):
        return

    async def _force_initialize_schema() -> None:
        try:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "alembic",
                    "upgrade",
                    "head",
                ],
                check=True,
                capture_output=True,
                text=True,
                env={**os.environ, "DATABASE_URL": _database_url_for_path(db_path)},
            )
            return
        except subprocess.CalledProcessError:
            pass

        if db_path.exists():
            db_path.unlink()

        database_module = module._integration_database_module
        async with database_module.engine.begin() as connection:
            await connection.run_sync(database_module.Base.metadata.create_all)
            await database_module._bootstrap_sqlite_schema(connection)
            await database_module._bootstrap_funding_catalog_schema(connection)
            await database_module._bootstrap_project_funding_matcher_schema(connection)

    module._force_initialize_schema = _force_initialize_schema


def _install_alembic_run_proxy(module, db_path: Path | None) -> None:
    if db_path is None or not hasattr(module, "subprocess"):
        return

    def _run(command, *args, **kwargs):
        if (
            isinstance(command, list)
            and len(command) >= 5
            and command[1:5] == ["-m", "alembic", "upgrade", "head"]
        ):
            env = dict(kwargs.pop("env", None) or os.environ)
            env["DATABASE_URL"] = _database_url_for_path(db_path)

            if _sqlite_table_exists(db_path, "organizations"):
                subprocess.run(
                    [command[0], "-m", "alembic", "stamp", "head"],
                    check=True,
                    env=env,
                )
                _seed_shared_smoke_dataset(db_path)
                return subprocess.CompletedProcess(command, 0, "", "")

            try:
                completed = subprocess.run(command, *args, env=env, **kwargs)
                _seed_shared_smoke_dataset(db_path)
                return completed
            except subprocess.CalledProcessError as exc:
                stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
                stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
                combined_output = f"{stdout}\n{stderr}"
                if "table organizations already exists" not in combined_output:
                    raise

                subprocess.run(
                    [command[0], "-m", "alembic", "stamp", "head"],
                    check=True,
                    env=env,
                )
                _seed_shared_smoke_dataset(db_path)
                return subprocess.CompletedProcess(command, 0, stdout, stderr)

        return subprocess.run(command, *args, **kwargs)

    module.subprocess = types.SimpleNamespace(run=_run)


@pytest.fixture(autouse=True, scope="module")
def integration_module_backend_context(request):
    module = request.module
    db_path = _apply_test_environment(module)
    _rebind_backend_globals(module)
    _install_alembic_bootstrap(module, db_path)
    _install_alembic_run_proxy(module, db_path)
    if db_path is not None and hasattr(module, "DB_PATH") and not hasattr(module, "TEST_DB_PATH"):
        _seed_shared_smoke_dataset(db_path)
    yield
