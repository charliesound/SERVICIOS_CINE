#!/usr/bin/env python3
"""
Generate FCPXML variants from dual-system fixture.
"""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.services.fcpxml_dual_system_variant_service import fcpxml_dual_system_variant_service

FIXTURE_BASE = Path("/opt/SERVICIOS_CINE/docs/validation/dual_system_real_20260428")

def main():
    assembly_path = FIXTURE_BASE / "assembly.json"
    relink_path = FIXTURE_BASE / "reports" / "media_relink_report.json"
    
    if not assembly_path.exists():
        print(f"ERROR: assembly.json not found at {assembly_path}")
        return 1
    
    assembly_data = json.loads(assembly_path.read_text())
    relink_report = json.loads(relink_path.read_text()) if relink_path.exists() else {}
    
    resolved_assets = relink_report.get("resources", {})
    
    conservative_xml, experimental_xml, conservative_name, experimental_name, manifest = (
        fcpxml_dual_system_variant_service.build_fcpxml_variants(
            project_name="Apartment",
            assembly_cut=assembly_data,
            resolved_assets=resolved_assets,
        )
    )
    
    base = FIXTURE_BASE / "fcpxml"
    base.mkdir(parents=True, exist_ok=True)
    
    (base / conservative_name).write_bytes(conservative_xml)
    (base / experimental_name).write_bytes(experimental_xml)
    (base / "manifest.json").write_text(json.dumps(manifest, indent=2))
    
    print(f"Generated FCPXML variants:")
    print(f"  - {conservative_name}")
    print(f"  - {experimental_name}")
    print(f"  - manifest.json")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())