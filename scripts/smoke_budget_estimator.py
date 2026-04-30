#!/usr/bin/env python3
"""
Smoke test for Budget Estimator from Script.
"""

import sys
import os

os.chdir('/opt/SERVICIOS_CINE/src')
sys.path.insert(0, '.')

print("=== Running Budget Estimator Smoke Test ===\n")

print("1. Test BudgetEstimate model imports...")
try:
    from models.budget_estimator import (
        BudgetEstimate,
        BudgetLineItem,
        BUDGET_LEVELS,
        BUDGET_STATUSES,
    )
    print("   OK: Model imported")
except Exception as e:
    print(f"   FAIL: {e}")
    sys.exit(1)

print("2. Test budget rules imports...")
try:
    from services.budget_rules import (
        RULES,
        LEVEL_MULTIPLIERS,
        get_default_contingency_percent,
        CATEGORY_LABELS,
    )
    print(f"   OK: {len(RULES)} rules loaded")
except Exception as e:
    print(f"   FAIL: {e}")
    sys.exit(1)

print("3. Test budget estimator service imports...")
try:
    from services.budget_estimator_service import (
        analyze_script_text,
        generate_line_items,
        estimate_jornadas,
        build_role_summary,
        generate_budget_from_text,
    )
    print("   OK: Service functions imported")
except Exception as e:
    print(f"   FAIL: {e}")
    sys.exit(1)

print("4. Test script analysis...")
script = """
INT. COFFEE SHOP - DAY

JOHN enters the coffee shop. He sees MARY.

INT. OFFICE - NIGHT

JOHN and MARY talk in the office.

EXT. BEACH - NIGHT

Action scene with stunts.

INT. WAREHOUSE - DAY

The crew works on the set.
"""
metrics = analyze_script_text(script)
print(f"   Scenes: {metrics['scene_count']}")
print(f"   Locations: {metrics['location_count']}")
print(f"   Characters: {metrics['character_count']}")
print(f"   Night scenes: {metrics['night_count']}")

print("5. Test line items generation...")
line_items = generate_line_items(metrics, "medium")
print(f"   Generated {len(line_items)} line items")

print("6. Test jornadas estimation...")
jornadas = estimate_jornadas(metrics)
print(f"   Estimated {jornadas} jornadas")

print("7. Test budget routes imports...")
try:
    import routes.budget_routes
    print("   OK: Routes imported")
except Exception as e:
    print(f"   FAIL: {e}")
    sys.exit(1)

print("8. Test app includes budget router...")
from app import app
route_paths = [r.path for r in app.routes if hasattr(r, 'path')]
budget_routes = [p for p in route_paths if '/budgets' in p]
print(f"   OK: Found {len(budget_routes)} budget route(s)")

print("9. Test budget estimator service main functions...")
from services.budget_estimator_service import (
    get_active_budget,
    get_budget_by_id,
    list_budgets,
    get_budget_lines,
    recalculate_budget,
    archive_budget,
    budget_estimator_service,
)
print("   OK: All main functions available")

print("10. Test with a sample script for budget generation...")
from services.budget_estimator_service import (
    analyze_script_text,
    generate_line_items,
)
sample_script = """
EXT. PARK - DAY

A beautiful morning in the park. People walking their dogs.
Children playing. Birds singing.

INT. HOUSE - DAY

FAMILY having breakfast.

INT. OFFICE - NIGHT

Meeting in the dark office with flashlights.

EXT. CITY STREET - NIGHT

Car chase through the city.

INT. WAREHOUSE - DAY

Production crew setting up lights.
"""
sample_metrics = analyze_script_text(sample_script)
sample_items = generate_line_items(sample_metrics, "medium")
total = sum(item['total_estimated'] for item in sample_items)
print(f"   Total estimated: €{total:,.0f}")
assert total > 10000, "Total should be reasonable"

print("\nSUCCESS: Budget Estimator code is valid")
sys.exit(0)