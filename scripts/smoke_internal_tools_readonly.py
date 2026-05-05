from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADMIN_ROUTES = ROOT / "src" / "routes" / "admin_routes.py"
INTERNAL_SCHEMAS = ROOT / "src" / "schemas" / "internal_admin_schema.py"


def assert_contains(text: str, needle: str, message: str) -> None:
    if needle not in text:
        raise AssertionError(message)


def assert_not_contains(text: str, needle: str, message: str) -> None:
    if needle in text:
        raise AssertionError(message)


def main() -> int:
    admin_text = ADMIN_ROUTES.read_text(encoding="utf-8")
    schema_text = INTERNAL_SCHEMAS.read_text(encoding="utf-8")

    assert_contains(admin_text, '@router.get("/internal/dashboard"', "Missing internal dashboard route")
    assert_contains(admin_text, '@router.get("/internal/users"', "Missing internal users route")
    assert_contains(admin_text, '@router.get("/internal/organizations"', "Missing internal organizations route")
    assert_contains(admin_text, 'get_tenant_context', "admin_routes.py must use get_tenant_context")
    assert_contains(admin_text, 'tenant.is_admin', "admin_routes.py must enforce real admin access")

    assert_not_contains(admin_text, '@router.post("/internal', "Read-only sprint must not add POST internal routes")
    assert_not_contains(admin_text, '@router.patch("/internal', "Read-only sprint must not add PATCH internal routes")
    assert_not_contains(admin_text, '@router.delete("/internal', "Read-only sprint must not add DELETE internal routes")
    assert_not_contains(admin_text, 'hashed_password', "admin_routes.py must not expose sensitive password fields")
    assert_not_contains(schema_text, 'hashed_password', "internal admin schemas must not expose password fields")

    print("PASS: internal dashboard/users/organizations routes exist")
    print("PASS: no mutable /api/admin/internal routes were added")
    print("PASS: admin_routes.py uses get_tenant_context and tenant.is_admin")
    print("PASS: internal responses do not expose password hash fields")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
