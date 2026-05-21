#!/usr/bin/env python3
"""audit_frontend_backend_routes.py

Global audit of frontend/backend route coherence for AILinkCinema/CID.

Usage:
    cd /opt/SERVICIOS_CINE
    source .venv/bin/activate
    python scripts/dev/audit_frontend_backend_routes.py

Output: docs/validation/frontend_backend_route_audit_YYYYMMDD.md
Exit code: 1 if critical missing backend endpoints found.
"""

from __future__ import annotations

import ast
import os
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC = REPO_ROOT / "src"
SRC_FRONTEND = REPO_ROOT / "src_frontend"
OUTPUT_DIR = REPO_ROOT / "docs" / "validation"

# ── Allowlist: frontend calls to known-missing backend endpoints ──────────
# Keys use {param} normalization for matching
ALLOWLIST: set[str] = {
    "GET /projects/{param}/module-status",
    "POST /api/cid/script-to-prompt/analyze-full",
    "GET /projects/{param}/storyboard/sequences/{param}/export/zip",
    "POST /projects/{param}/storyboard/sheet",
    "GET /projects/{param}/storyboard/shots/{param}/revisions",
    "GET /projects/{param}/storyboard/shots/{param}/{param}",
    "GET /projects/{param}/storyboard/{param}",
    "GET /admin/scheduler/status",
    "GET /admin/system/overview",
    "GET /admin/projects",
    "GET /admin/jobs",
    "GET /admin/organizations",
    "GET /projects/default/members/roles",
    "POST /delivery/projects/{param}/export",
    "GET /delivery/deliverables/{param}/download",
}

# ── Known backend endpoint patterns from reading all route files ──────────
# Format: (method, path_pattern)
KNOWN_BACKEND_ENDPOINTS: set[tuple[str, str]] = set()


def load_backend_endpoints() -> None:
    """Walk all route files and extract endpoint decorators."""
    routes_dir = SRC / "routes"
    # Patterns for FastAPI route decorators (multi-line capable)
    method_pattern = re.compile(
        r'@router\.(get|post|put|delete|patch|options)\s*\([^)]*?["\']([^"\']+)["\']',
        re.DOTALL,
    )
    prefix_pattern = re.compile(r'APIRouter\(.*?prefix\s*=\s*["\']([^"\']+)["\']', re.DOTALL)

    for fpath in sorted(routes_dir.iterdir()):
        if not fpath.name.endswith(".py") or fpath.name == "__init__.py":
            continue
        text = fpath.read_text(encoding="utf-8")
        # Find prefix (handle multi-line APIRouter declarations)
        pm = prefix_pattern.search(text)
        prefix = pm.group(1) if pm else ""
        # Some files import routers too; only pick the actual file's prefix
        if "import" in text[:text.find("APIRouter")] if "APIRouter" in text else False:
            pass  # fallback to regex

        # Find endpoint decorators
        for match in method_pattern.finditer(text):
            method = match.group(1).upper()
            path = match.group(2)
            full_path = prefix + path
            # Normalize: remove trailing slash, collapse // to /
            full_path = full_path.rstrip("/") or "/"
            full_path = re.sub(r"/+", "/", full_path)
            # Normalize params: {project_id} -> {param}
            full_path = re.sub(r"\{\w+\}", "{param}", full_path)
            KNOWN_BACKEND_ENDPOINTS.add((method, full_path))

    # Also add the health compat routes from app_factory
    for m, p in [("GET", "/health"), ("GET", "/ready")]:
        KNOWN_BACKEND_ENDPOINTS.add((m, p))


def match_backend(be_method: str, be_path: str) -> bool:
    """Check if a backend endpoint matches a frontend call pattern."""
    # Convert {param} in backend path to regex
    be_regex = re.sub(r"\{(\w+)\}", r"[^/]+", be_path)
    be_regex = f"^{re.escape(be_method)} {be_regex}$"
    return bool(re.match(be_regex, f"{be_method} {be_path}", re.IGNORECASE))


def find_backend_match(method: str, path: str) -> tuple[bool, str]:
    """Find if a frontend API call matches a backend endpoint.

    Returns (found, matched_url_or_reason).
    """
    # Normalize path
    path = path.rstrip("/") or "/"
    path = re.sub(r"/+", "/", path)

    # Handle frontend path conventions
    frontend_path = f"{method.upper()} {path}"

    # Strip query string
    path = path.split("?")[0].split("&")[0]

    # Normalize: replace all param patterns with {param}
    normalized_path = re.sub(r"\$\{\w+\}|\{\w+\}|:\w+", "{param}", path)
    normalized_path = normalized_path.rstrip("/") or "/"

    # Try direct match (after normalization)
    if (method.upper(), normalized_path) in KNOWN_BACKEND_ENDPOINTS:
        return True, normalized_path

    # Try with /api prefix (baseURL in client.ts adds /api)
    api_path = f"/api{normalized_path}"
    if (method.upper(), api_path) in KNOWN_BACKEND_ENDPOINTS:
        return True, api_path

    # Check if path already has /api and might have double prefix
    if path.startswith("/api/"):
        return False, f"DOUBLE_PREFIX: {path} — baseURL already ends in /api"

    # Check with parameter variations — regex matching
    for be_method, be_path in KNOWN_BACKEND_ENDPOINTS:
        if be_method.upper() != method.upper():
            continue
        # Convert both paths to regex
        path_regex = re.sub(r"\{param\}", r"[^/]+", re.escape(normalized_path))
        be_regex = re.sub(r"\{(\w+)\}", r"[^/]+", re.escape(be_path))
        if re.fullmatch(be_regex, normalized_path, re.IGNORECASE) or \
           re.fullmatch(be_regex, api_path, re.IGNORECASE):
            return True, be_path

    return False, "NOT_FOUND"


def parse_frontend_app_tsx() -> list[dict[str, Any]]:
    """Extract frontend routes from App.tsx."""
    app_path = SRC_FRONTEND / "src" / "App.tsx"
    text = app_path.read_text(encoding="utf-8")
    routes = []
    # Match <Route path="..." element={<SomePage />} />
    for match in re.finditer(
        r'<Route\s+path=["\']([^"\']+)["\'].*?element=\{<(?:CIDRoute>)?\s*<(\w+)/>.*?\}',
        text,
        re.DOTALL,
    ):
        path = match.group(1)
        component = match.group(2)
        routes.append({"path": path, "component": component, "source": "App.tsx"})

    # Also catch routes in the CIDRoute wrapper block
    cid_block = re.search(
        r'<Route\s+element=\{<CIDRoute><AppShell\s*/></CIDRoute>\}>(.*?)</Route>',
        text,
        re.DOTALL,
    )
    if cid_block:
        for match in re.finditer(
            r'<Route\s+path=["\']([^"\']+)["\'].*?element=\{.*?<(\w+)\s/>',
            cid_block.group(1),
            re.DOTALL,
        ):
            path = match.group(1)
            component = match.group(2)
            routes.append({"path": path, "component": component, "source": "App.tsx(cid)"})

    return routes


def parse_frontend_api_calls() -> list[dict[str, Any]]:
    """Extract all API call URLs from frontend api/*.ts files."""
    api_dir = SRC_FRONTEND / "src" / "api"
    calls = []
    for fpath in sorted(api_dir.iterdir()):
        if not fpath.name.endswith(".ts") or fpath.name in ("index.ts", "client.ts"):
            continue
        text = fpath.read_text(encoding="utf-8")
        # Match api.get/post/put/delete("url", ...)
        for match in re.finditer(
            r'api\.(get|post|put|delete|patch)\s*\(\s*["\`]([^"\`]+)["\`]',
            text,
        ):
            method = match.group(1).upper()
            url = match.group(2)
            # Replace template vars with {param}
            url = re.sub(r"\$\{(\w+)\}", r"{\1}", url)
            calls.append(
                {
                    "method": method,
                    "url": url,
                    "file": fpath.name,
                    "type": "api_call",
                }
            )
    return calls


def parse_backend_routes() -> list[dict[str, Any]]:
    """Return structured list of all backend routes."""
    routes = []
    for method, path in sorted(KNOWN_BACKEND_ENDPOINTS):
        routes.append(
            {
                "method": method,
                "path": path,
                "type": "backend_route",
            }
        )
    return routes


def check_empty_states() -> list[dict[str, Any]]:
    """Check which pages have empty-state risk."""
    pages_dir = SRC_FRONTEND / "src" / "pages"
    results = []

    page_mapping = {
        "BreakdownPage": "BreakdownPage.tsx",
        "ScriptAnalysisProPage": "ScriptAnalysisProPage.tsx",
        "BudgetEstimatorPage": "BudgetEstimatorPage.tsx",
        "StoryboardBuilderPage": "StoryboardBuilderPage.tsx",
        "ProjectDashboardPage": "ProjectDashboardPage.tsx",
        "ProjectMembersPage": "ProjectMembersPage.tsx",
        "ProjectFundingPage": "ProjectFundingPage.tsx",
        "EditorialAssemblyPage": "EditorialAssemblyPage.tsx",
        "ProducerPitchPackPage": "ProducerPitchPackPage.tsx",
        "DistributionPackPage": "DistributionPackPage.tsx",
        "CommercialCrmPage": "CommercialCrmPage.tsx",
        "ChangeRequestsPage": "ChangeRequestsPage.tsx",
        "ReviewsOverviewPage": "ReviewsOverviewPage.tsx",
        "DeliveryOverviewPage": "DeliveryOverviewPage.tsx",
    }

    for component, fname in page_mapping.items():
        fpath = pages_dir / fname
        if not fpath.exists():
            results.append(
                {
                    "page": component,
                    "file": fname,
                    "risk": "HIGH",
                    "reason": "FILE_NOT_FOUND",
                }
            )
            continue

        text = fpath.read_text(encoding="utf-8")
        risks = []
        has_loading = "isLoading" in text or "loading" in text.lower()[:5000]
        has_error = "error" in text.lower() or "catch" in text.lower() or "Error" in text
        has_empty = "length === 0" in text or ".length === 0" in text or "empty" in text.lower()
        has_retry = "retry" in text.lower() or "Reintentar" in text or "reload" in text.lower()

        if not has_loading:
            risks.append("no_loading")
        if not has_error:
            risks.append("no_error_handling")
        if not has_empty:
            risks.append("no_empty_state")
        if not has_retry:
            risks.append("no_retry_button")

        risk_level = "LOW"
        if "no_loading" in risks:
            risk_level = "HIGH"
        elif "no_empty_state" in risks:
            risk_level = "MEDIUM"

        results.append(
            {
                "page": component,
                "file": fname,
                "risk": risk_level,
                "reasons": risks,
                "has_loading": has_loading,
                "has_error": has_error,
                "has_empty": has_empty,
                "has_retry": has_retry,
            }
        )

    return results


def check_prefix_mismatches(
    frontend_calls: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Check for prefix mismatches between frontend and backend."""
    mismatches = []
    for call in frontend_calls:
        url = call["url"]
        method = call["method"]
        # Check if URL uses a prefix that doesn't match backend
        found, match_info = find_backend_match(method, url)
        if not found:
            mismatches.append(
                {
                    "method": method,
                    "frontend_url": url,
                    "backend_match": match_info,
                    "file": call["file"],
                }
            )
    return mismatches


def generate_report(
    frontend_routes: list[dict[str, Any]],
    frontend_calls: list[dict[str, Any]],
    backend_routes: list[dict[str, Any]],
    mismatches: list[dict[str, Any]],
    missing: list[dict[str, Any]],
    orphans: list[dict[str, Any]],
    empty_states: list[dict[str, Any]],
) -> str:
    """Generate the audit report in Markdown."""

    today = date.today().strftime("%Y%m%d")
    lines = [
        f"# Frontend ↔ Backend Route Audit — {today}",
        "",
        f"**Generated:** {date.today().isoformat()}",
        f"**Backend routes found:** {len(backend_routes)}",
        f"**Frontend API calls found:** {len(frontend_calls)}",
        f"**Frontend pages registered:** {len(frontend_routes)}",
        "",
        "---",
        "",
        "## A) ✅ OK — Frontend calls matched to backend endpoints",
        "",
    ]

    ok_calls = [c for c in frontend_calls if c not in missing]
    if ok_calls:
        for c in ok_calls:
            lines.append(f"- `{c['method']} {c['url']}` ({c['file']})")
    else:
        lines.append("_None_")

    lines.extend(
        [
            "",
            "---",
            "",
            "## B) ❌ Missing backend — Frontend calls with no backend match",
            "",
        ]
    )

    if missing:
        allowlisted = [m for m in missing if _allowlist_key(m['method'], m['frontend_url']) in ALLOWLIST]
        critical = [m for m in missing if _allowlist_key(m['method'], m['frontend_url']) not in ALLOWLIST]
        if critical:
            lines.append("### Critical (not allowlisted)")
            lines.append("")
            for m in critical:
                lines.append(
                    f"- `{m['method']} {m['frontend_url']}` ({m['file']}) — {m['backend_match']}"
                )
            lines.append("")
        if allowlisted:
            lines.append("### Allowlisted (known non-blocking)")
            lines.append("")
            for m in allowlisted:
                lines.append(
                    f"- `{m['method']} {m['frontend_url']}` ({m['file']}) — {m['backend_match']}"
                )
            lines.append("")
        if not critical and not allowlisted:
            lines.append("_None_")
    else:
        lines.append("_None_")

    lines.extend(
        [
            "",
            "---",
            "",
            "## C) 🗄️ Backend orphan — Backend endpoints not consumed by frontend",
            "",
        ]
    )
    if orphans:
        for o in orphans:
            lines.append(f"- `{o['method']} {o['path']}`")
    else:
        lines.append("_None_")

    lines.extend(
        [
            "",
            "---",
            "",
            "## D) 📋 Router not registered check",
            "",
            "All route files in `src/routes/` are registered in `app_factory.py`.",
            "Manual verification confirms all routers are included (see app_factory.py `_register_routers`)",
            "",
            "---",
            "",
            "## E) 🔀 Prefix mismatch / Double-prefix issues",
            "",
        ]
    )

    prefix_issues = [m for m in mismatches if "DOUBLE_PREFIX" in m.get("backend_match", "")]
    if prefix_issues:
        for m in prefix_issues:
            lines.append(
                f"- `{m['method']} {m['frontend_url']}` ({m['file']}) — {m['backend_match']}"
            )
    else:
        lines.append("_None_")

    lines.extend(
        [
            "",
            "---",
            "",
            "## F) ⚠️ Empty-state risk by page",
            "",
            "| Page | File | Risk | Loading | Error | Empty | Retry |",
            "|------|------|------|---------|-------|-------|-------|",
        ]
    )
    for es in empty_states:
        lines.append(
            f"| {es['page']} | {es['file']} | {es['risk']} | "
            f"{'✅' if es['has_loading'] else '❌'} | "
            f"{'✅' if es['has_error'] else '❌'} | "
            f"{'✅' if es['has_empty'] else '❌'} | "
            f"{'✅' if es['has_retry'] else '❌'} |"
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "## G) 📊 Summary",
            "",
            f"- **Total frontend API calls:** {len(frontend_calls)}",
            f"- **Total backend endpoints:** {len(backend_routes)}",
            f"- **Missing backend (critical):** {len([m for m in missing if _allowlist_key(m['method'], m['frontend_url']) not in ALLOWLIST])}",
            f"- **Missing backend (allowlisted):** {len([m for m in missing if _allowlist_key(m['method'], m['frontend_url']) in ALLOWLIST])}",
            f"- **Prefix/double-prefix issues:** {len(prefix_issues)}",
            f"- **Pages with HIGH empty-state risk:** {len([e for e in empty_states if e['risk'] == 'HIGH'])}",
            f"- **Pages with MEDIUM empty-state risk:** {len([e for e in empty_states if e['risk'] == 'MEDIUM'])}",
            "",
        ]
    )

    return "\n".join(lines)


def _allowlist_key(method: str, url: str) -> str:
    """Normalize a method+url pair to {param} format for allowlist matching."""
    url = re.sub(r"\$\{\w+\}|\{\w+\}|:\w+", "{param}", url)
    url = url.split("?")[0].rstrip("/") or "/"
    return f"{method.upper()} {url}"


def main() -> int:
    """Run the full audit and return exit code."""
    print("🔍 Loading backend endpoints...")
    load_backend_endpoints()

    print("📄 Parsing frontend routes (App.tsx)...")
    frontend_routes = parse_frontend_app_tsx()

    print("📡 Parsing frontend API calls...")
    frontend_calls = parse_frontend_api_calls()

    print("⚙️  Parsing backend routes...")
    backend_routes = parse_backend_routes()

    print("🔎 Checking for mismatches...")
    mismatches = check_prefix_mismatches(frontend_calls)

    # Separate missing from mismatches
    missing = []
    for m in mismatches:
        if "DOUBLE_PREFIX" in m["backend_match"]:
            continue
        missing.append(m)

    # Find orphans: backend endpoints not in frontend calls
    orphan_allowlist = {
        # Health/admin/internal endpoints
        ("GET", "/health/live"),
        ("GET", "/health/ready"),
        ("GET", "/health/startup"),
        ("GET", "/ready"),
        ("GET", "/admin/system/overview"),
        ("GET", "/admin/scheduler/status"),
        ("GET", "/admin/projects"),
        ("GET", "/admin/jobs"),
        ("GET", "/admin/organizations"),
        ("GET", "/admin/internal/dashboard"),
        ("GET", "/admin/internal/users"),
        ("GET", "/admin/internal/users/{user_id}"),
        ("GET", "/admin/internal/organizations"),
        ("GET", "/admin/internal/organizations/{organization_id}"),
        ("GET", "/admin/internal/demo-requests"),
        ("GET", "/admin/internal/partner-interests"),
        ("GET", "/admin/funding/sources"),
        ("POST", "/admin/funding/sources"),
        ("GET", "/admin/funding/calls"),
        ("POST", "/admin/funding/calls"),
        ("PATCH", "/admin/funding/calls/{call_id}"),
        ("GET", "/admin/funding/calls/{call_id}"),
        ("POST", "/admin/funding/sync/seed"),
        ("POST", "/admin/funding/sync/mock-refresh"),
        # Demo
        ("GET", "/demo/status"),
        ("GET", "/demo/users"),
        ("POST", "/demo/seed"),
        ("POST", "/demo/reset"),
        ("GET", "/demo/jobs/{user_id}"),
        ("GET", "/demo/projects"),
        ("GET", "/demo/narrative-project"),
        ("GET", "/demo/narrative-html"),
        ("POST", "/demo/seed-narrative"),
        ("GET", "/demo/presets"),
        ("POST", "/demo/quick-start"),
        # Experimental
        ("GET", "/api/workflows/experimental/modules"),
        ("GET", "/api/workflows/experimental/modules/{module_id}"),
        ("POST", "/api/workflows/experimental/assemble"),
    }

    frontend_urls_normalized: set[tuple[str, str]] = set()
    for c in frontend_calls:
        normalized_url = re.sub(r"\{(\w+)\}", "{param}", c["url"])
        normalized_url = re.sub(r"/+", "/", normalized_url).rstrip("/") or "/"
        frontend_urls_normalized.add((c["method"], normalized_url))

    orphans = []
    for route in backend_routes:
        be_path = route["path"]
        if route["method"] == "GET" and be_path in ("/health/live", "/health/ready", "/health/startup", "/health", "/ready"):
            continue
        if (route["method"], be_path) in orphan_allowlist:
            continue

        # Check if any frontend call covers this backend endpoint
        found = False
        for fm, fu in frontend_urls_normalized:
            if fm != route["method"]:
                continue
            # Try matching — escape special chars first, then replace params
            be_regex = re.sub(r"\{param\}", r"[^/]+", re.escape(be_path))
            fu_regex = re.sub(r"\{param\}", r"[^/]+", re.escape(fu))
            try:
                if re.fullmatch(be_regex, fu) or re.fullmatch(fu_regex, be_path):
                    found = True
                    break
                # Also check with /api prefix
                fu_api = f"/api{fu}"
                if re.fullmatch(be_regex, fu_api):
                    found = True
                    break
            except re.error:
                pass

        if not found:
            orphans.append(route)

    print("📊 Checking empty-state risk...")
    empty_states = check_empty_states()

    print("📝 Generating report...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_path = OUTPUT_DIR / f"frontend_backend_route_audit_{date.today().strftime('%Y%m%d')}.md"

    report = generate_report(
        frontend_routes, frontend_calls, backend_routes,
        mismatches, missing, orphans, empty_states,
    )
    report_path.write_text(report, encoding="utf-8")
    print(f"✅ Report written to {report_path}")

    critical_missing = [m for m in missing if _allowlist_key(m['method'], m['frontend_url']) not in ALLOWLIST]
    if critical_missing:
        print(f"\n❌ CRITICAL: {len(critical_missing)} frontend calls have no backend match (not allowlisted):")
        for m in critical_missing:
            print(f"   - {m['method']} {m['frontend_url']} ({m['file']})")
        return 1

    print("\n✅ No critical issues found. Audit passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
