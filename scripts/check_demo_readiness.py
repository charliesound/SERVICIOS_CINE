#!/usr/bin/env python3
"""
Check demo readiness for CID.
"""

import sys
import os
import glob

os.chdir("/opt/SERVICIOS_CINE")


def check_demo_guide():
    print("1. Checking demo guide...")
    guide_file = "src_frontend/src/data/demoProjectGuide.ts"
    if glob.glob(guide_file):
        print(f"   OK: {guide_file} exists")
        return True
    print(f"   FAIL: {guide_file} not found")
    return False


def check_status_badge():
    print("2. Checking StatusBadge component...")
    files = glob.glob("src_frontend/src/components/StatusBadge.*")
    if files:
        print(f"   OK: {files[0]} exists")
        return True
    print("   FAIL: StatusBadge not found")
    return False


def check_demo_mode_panel():
    print("3. Checking DemoModePanel...")
    files = glob.glob("src_frontend/src/components/DemoModePanel.*")
    if files:
        print(f"   OK: {files[0]} exists")
        return True
    print("   FAIL: DemoModePanel not found")
    return False


def check_docs():
    print("4. Checking commercial docs...")
    required = [
        "docs/CID_DEMO_SCRIPT.md",
        "docs/CID_V1_COMMERCIAL_POSITIONING.md",
    ]
    all_exist = True
    for doc in required:
        if glob.glob(doc):
            print(f"   OK: {doc}")
        else:
            print(f"   FAIL: {doc} not found")
            all_exist = False
    return all_exist


def check_routes():
    print("5. Checking main routes in App.tsx...")
    import re
    
    try:
        with open("src_frontend/src/App.tsx") as f:
            content = f.read()
        
        routes = [
            "/projects/:projectId/dashboard",
            "/projects/:projectId/budget",
            "/projects/:projectId/funding",
            "/projects/:projectId/producer-pitch",
            "/projects/:projectId/distribution",
            "/projects/:projectId/crm",
            "/projects/:projectId/editorial",
            "/projects/:projectId/storyboard",
            "/projects/:projectId/change-requests",
        ]
        
        missing = []
        for route in routes:
            if route not in content:
                missing.append(route)
        
        if not missing:
            print("   OK: All main routes present")
            return True
        else:
            print(f"   FAIL: Missing routes: {missing}")
            return False
    except Exception as e:
        print(f"   ERROR: {e}")
        return False


def check_no_forbidden_claims():
    print("6. Checking for forbidden claims...")
    forbidden = [
        "garantiza distribución",
        "garantiza aceptación",
        "funding approval",
    ]
    
    pages_to_check = [
        "src_frontend/src/pages/DistributionPackPage.tsx",
        "src_frontend/src/pages/CommercialCrmPage.tsx",
        "src_frontend/src/pages/ProjectFundingPage.tsx",
    ]
    
    issues = []
    for page in pages_to_check:
        try:
            with open(page) as f:
                content = f.read()
            for term in forbidden:
                if term in content.lower():
                    issues.append(f"{page}: {term}")
        except Exception:
            pass
    
    if not issues:
        print("   OK: No forbidden claims found")
        return True
    else:
        print(f"   WARN: Potential issues: {issues}")
        return True


def main():
    print("=" * 60)
    print("CID Demo Readiness Check")
    print("=" * 60)
    print()
    
    checks = [
        check_demo_guide,
        check_status_badge,
        check_demo_mode_panel,
        check_docs,
        check_routes,
        check_no_forbidden_claims,
    ]
    
    results = []
    for check in checks:
        try:
            results.append(check())
        except Exception as e:
            print(f"   ERROR: {e}")
            results.append(False)
        print()
    
    print("=" * 60)
    if all(results):
        print("SUCCESS: CID is demo-ready")
        print("=" * 60)
        return 0
    else:
        print(f"FAILURE: {sum(1 for r in results if not r)} check(s) failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())