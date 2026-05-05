from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTH_ROUTES = ROOT / "src" / "routes" / "auth_routes.py"
CID_TEST_ROUTES = ROOT / "src" / "routes" / "cid_test_routes.py"
CID_TEST_MODE = ROOT / "src" / "services" / "cid_test_mode.py"


def assert_contains(text: str, needle: str, message: str) -> None:
    if needle not in text:
        raise AssertionError(message)


def assert_not_contains(text: str, needle: str, message: str) -> None:
    if needle in text:
        raise AssertionError(message)


def main() -> int:
    auth_text = AUTH_ROUTES.read_text(encoding="utf-8")
    routes_text = CID_TEST_ROUTES.read_text(encoding="utf-8")
    mode_text = CID_TEST_MODE.read_text(encoding="utf-8")

    assert_not_contains(
        auth_text,
        "apply_test_override",
        "auth_routes.py still references apply_test_override",
    )
    assert_not_contains(
        routes_text,
        "db.commit(",
        "cid_test_routes.py still commits to the database",
    )
    assert_not_contains(
        routes_text,
        "db.add(Project)",
        "cid_test_routes.py still adds a real Project",
    )
    assert_contains(
        mode_text,
        'os.getenv("CID_INTERNAL_TEST_MODE_ENABLED", "false")',
        "CID internal test mode default is not safely disabled",
    )

    print("PASS: auth_routes.py has no global test override")
    print("PASS: cid_test_routes.py has no db.commit()")
    print("PASS: cid_test_routes.py does not add a real Project")
    print("PASS: CID_INTERNAL_TEST_MODE_ENABLED defaults to false")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
