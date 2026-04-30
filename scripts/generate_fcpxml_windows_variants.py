#!/usr/bin/env python3
"""
Generate Windows FCPXML variants with corrected offsets.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
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
    
    wINDOWS_BASE = FIXTURE_BASE.parent / "dual_system_real_20260428_windows"
    
    (wINDOWS_BASE / "fcpxml" / "assembly_conservative_windows.fcpxml").write_bytes(conservative_xml)
    (wINDOWS_BASE / "fcpxml" / "assembly_linked_audio_experimental_windows.fcpxml").write_bytes(experimental_xml)
    
    print("Generated Windows FCPXML variants:")
    print(f"  - {wINDOWS_BASE}/fcpxml/assembly_conservative_windows.fcpxml")
    print(f"  - {wINDOWS_BASE}/fcpxml/assembly_linked_audio_experimental_windows.fcpxml")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())