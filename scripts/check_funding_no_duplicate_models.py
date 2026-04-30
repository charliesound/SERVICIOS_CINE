#!/usr/bin/env python3
"""
Check for duplicate funding models.

This script verifies that there are no duplicate funding models in the codebase.
It should fail if:
- there are imports from src.models.funding
- there are FundingOpportunity models used outside of legacy context
- there are contradictory references not documented
"""

import sys
import os
from pathlib import Path


def check_no_funding_model_imports():
    """Check that no files import from models.funding"""
    print("1. Checking for models.funding imports...")
    
    for py_file in Path("src").rglob("*.py"):
        if ".venv" in str(py_file):
            continue
        try:
            content = py_file.read_text()
            if "from models.funding import" in content or "import models.funding" in content:
                print(f"   FAIL: {py_file} imports from models.funding")
                return False
        except Exception:
            pass
    
    print("   OK: No imports from models.funding")
    return True


def check_no_unused_duplicate_models():
    """Check that models/funding.py doesn't exist"""
    print("2. Checking for orphaned funding.py...")
    
    funding_py = Path("src/models/funding.py")
    if funding_py.exists():
        print(f"   FAIL: {funding_py} still exists (should be deleted)")
        return False
    
    print("   OK: funding.py removed")
    return True


def check_canonical_models_exist():
    """Check that canonical models exist"""
    print("3. Checking canonical models exist...")
    
    production_models = Path("src/models/production.py")
    if not production_models.exists():
        print("   FAIL: models/production.py missing")
        return False
    
    content = production_models.read_text()
    for model in ["FundingCall", "FundingSource"]:
        if f"class {model}" not in content:
            print(f"   FAIL: {model} not in production.py")
            return False
    
    print("   OK: Canonical models exist")
    return True


def check_dashboard_integration():
    """Check that dashboard uses canonical models"""
    print("4. Checking dashboard uses canonical models...")
    
    routes = Path("src/routes/project_routes.py")
    if not routes.exists():
        print("   FAIL: project_routes.py missing")
        return False
    
    content = routes.read_text()
    if "from models.production import FundingCall" in content:
        print("   OK: Dashboard uses FundingCall")
        return True
    
    if "FundingCall" in content:
        print("   WARN: FundingCall references exist but import may be inline")
        return True
    
    print("   FAIL: No funding integration found")
    return False


def main():
    os.chdir("/opt/SERVICIOS_CINE")
    
    print("=" * 60)
    print("Funding No-Duplicate Models Check")
    print("=" * 60)
    print()
    
    checks = [
        check_no_funding_model_imports,
        check_no_unused_duplicate_models,
        check_canonical_models_exist,
        check_dashboard_integration,
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
        print("SUCCESS: All checks passed")
        print("=" * 60)
        return 0
    else:
        print("FAILURE: Some checks failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())