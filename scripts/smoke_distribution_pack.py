#!/usr/bin/env python3
"""
Smoke test for Distribution / Cinemas / Platforms Pack module.
"""

import sys
import os
import json

os.chdir("/opt/SERVICIOS_CINE")
sys.path.insert(0, "/opt/SERVICIOS_CINE/src")


def test_models_import():
    print("1. Testing Distribution models import...")
    from models.distribution import (
        DistributionPack, DistributionPackSection, SalesTarget, ProjectSalesOpportunity,
        PACK_TYPE, PACK_STATUS, SALES_TARGET_TYPES, SALES_OPPORTUNITY_STATUS,
    )
    print(f"   OK: DistributionPack, SalesTarget, ProjectSalesOpportunity")
    print(f"   OK: Pack types: {PACK_TYPE}")
    return True


def test_distribution_service_import():
    print("2. Testing distribution_pack_service import...")
    from services.distribution_pack_service import (
        generate_distribution_pack,
        get_distribution_pack,
        get_active_distribution_pack,
        list_distribution_packs,
        update_distribution_pack,
        approve_distribution_pack,
        archive_distribution_pack,
        export_distribution_pack_json,
        export_distribution_pack_markdown,
    )
    print("   OK: All distribution service functions imported")
    return True


def test_sales_service_import():
    print("3. Testing sales_target_service import...")
    from services.sales_target_service import (
        create_sales_target,
        list_sales_targets,
        suggest_sales_targets_for_project,
        create_sales_opportunity,
        list_project_sales_opportunities,
        SAMPLE_SALES_TARGETS,
    )
    print(f"   OK: All sales service functions imported")
    print(f"   OK: Sample targets: {len(SAMPLE_SALES_TARGETS)}")
    return True


def test_routes_import():
    print("4. Testing distribution routes import...")
    from routes import distribution_pack_routes
    print("   OK: Distribution routes imported")
    return True


def test_sales_routes_import():
    print("5. Testing sales targets routes import...")
    from routes import sales_targets_routes
    print("   OK: Sales targets routes imported")
    return True


def test_app_includes_routes():
    print("6. Testing app includes routers...")
    from app import app
    routes = [r.path for r in app.routes]
    dist_routes = [r for r in routes if "distribution" in r]
    sales_routes = [r for r in routes if "sales-targets" in r]
    if dist_routes and sales_routes:
        print(f"   OK: Found {len(dist_routes)} distribution routes")
        print(f"   OK: Found {len(sales_routes)} sales routes")
        return True
    print("   FAIL: Routes not found")
    return False


def test_dashboard_integration():
    print("7. Testing dashboard distribution integration...")
    from routes.project_routes import router as project_router
    routes = [r.path for r in project_router.routes]
    dashboard_routes = [r for r in routes if "dashboard" in r]
    if dashboard_routes:
        print("   OK: Dashboard route found")
        return True
    print("   FAIL: Dashboard route not found")
    return False


def test_pack_type_generation():
    print("8. Testing pack type generation...")
    from models.distribution import PACK_TYPE
    from services.distribution_pack_service import _generate_commercial_positioning
    
    class MockProject:
        name = "Test Project"
    
    positionings = {}
    for pack_type in PACK_TYPE:
        pos = _generate_commercial_positioning(pack_type, MockProject())
        positionings[pack_type] = pos
    
    if all(positionings.values()):
        print(f"   OK: Generated {len(positionings)} positioning types")
        return True
    print("   FAIL: Positioning generation failed")
    return False


def test_export_functions():
    print("9. Testing export functions...")
    from services.distribution_pack_service import export_distribution_pack_json, export_distribution_pack_markdown
    
    class MockPack:
        id = "test-id"
        project_id = "test-project"
        title = "Test Pack"
        pack_type = "distributor"
        status = "generated"
        logline = "Test logline"
        short_synopsis = "Test synopsis"
        commercial_positioning = "Test positioning"
        target_audience = "Test audience"
        comparable_titles_json = "[]"
        release_strategy_json = "{}"
        exploitation_windows_json = "[]"
        territory_strategy_json = "[]"
        marketing_hooks_json = "[]"
        available_materials_json = "[]"
        technical_specs_json = "{}"
        sales_arguments_json = "[]"
        risks_json = "[]"
    
    pack = MockPack()
    json_export = export_distribution_pack_json(pack)
    md_export = export_distribution_pack_markdown(pack)
    
    print(f"   OK: JSON export: {len(json_export)} keys")
    print(f"   OK: Markdown export: {len(md_export)} chars")
    return True


def main():
    print("=" * 60)
    print("Running Distribution Pack Smoke Test")
    print("=" * 60)
    print()

    tests = [
        test_models_import,
        test_distribution_service_import,
        test_sales_service_import,
        test_routes_import,
        test_sales_routes_import,
        test_app_includes_routes,
        test_dashboard_integration,
        test_pack_type_generation,
        test_export_functions,
    ]

    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"   ERROR: {e}")
            results.append(False)
        print()

    print("=" * 60)
    if all(results):
        print("SUCCESS: Distribution Pack code is valid")
        print("=" * 60)
        return 0
    else:
        print(f"FAILURE: {sum(1 for r in results if not r)} test(s) failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())