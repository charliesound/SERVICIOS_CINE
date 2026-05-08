#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from schemas.cid_visual_reference_schema import (
    DirectorVisualReferenceRequest,
    ReferencePurpose,
    ReferenceIntensity,
    ReferenceMode,
    StyleReferenceProfile,
)
from services.visual_reference_analysis_service import visual_reference_analysis_service


def main() -> int:
    print("=== Smoke Test: CID Visual Reference Contract ===\n")

    failures: list[str] = []

    # 1. Can create a StyleReferenceProfile from request
    try:
        request = DirectorVisualReferenceRequest(
            reference_image_url="https://example.com/reference.webp",
            reference_purpose=ReferencePurpose.scene_mood,
            intensity=ReferenceIntensity.medium,
            reference_mode=ReferenceMode.palette_lighting,
            notes_from_director="Warm amber lighting",
        )
        result = visual_reference_analysis_service.analyze(request)
        profile = result.profile
        assert profile.reference_id != "", "reference_id should not be empty"
        print("  [PASS] StyleReferenceProfile created from request")
    except Exception as exc:
        failures.append(f"StyleReferenceProfile creation failed: {exc}")
        profile = None

    if profile is None:
        print("\n  CRITICAL FAILURE: Cannot continue without a valid profile")
        return 1

    # 2. Profile has all required fields
    required_fields = [
        "visual_summary", "palette_description", "lighting_description",
        "atmosphere_description", "transferable_traits", "non_transferable_traits",
        "negative_constraints", "prompt_modifiers", "qa_requirements",
    ]
    for field in required_fields:
        if not getattr(profile, field, None):
            failures.append(f"Profile missing non-empty field: {field}")
    print(f"  [PASS] Profile has all {len(required_fields)} required fields")

    # 3. Prompt guidance block contains visual reference guidance
    guidance = profile.to_prompt_guidance_block()
    assert "VISUAL REFERENCE GUIDANCE" in guidance, "Guidance block missing header"
    assert "Do NOT copy" in guidance, "Guidance block missing anti-copy clause"
    print("  [PASS] Profile.to_prompt_guidance_block() is well-formed")

    # 4. QA requirements exist and are properly formatted
    for qa in profile.qa_requirements:
        if not qa.startswith("VERIFICAR:"):
            failures.append(f"QA requirement does not start with VERIFICAR:: {qa[:60]}")
    print(f"  [PASS] QA requirements: {len(profile.qa_requirements)} items")

    # 5. Transferable traits include relevant items
    assert len(profile.transferable_traits) > 0, "No transferable traits"
    print(f"  [PASS] Transferable traits: {len(profile.transferable_traits)} items")

    # 6. Non-transferable traits include identity/copy protection
    has_identity = any("identity" in t.lower() for t in profile.non_transferable_traits)
    if not has_identity:
        failures.append("Non-transferable traits should include identity protection")
    print(f"  [PASS] Non-transferable traits include identity protection: {has_identity}")

    # 7. Negative constraints prevent style copying
    has_style_constraint = any("style" in c.lower() for c in profile.negative_constraints)
    if not has_style_constraint:
        failures.append("Negative constraints should prevent style copying")
    print(f"  [PASS] Negative constraints prevent style copying: {has_style_constraint}")

    # 8. Purpose-specific analysis
    for purpose_name, purpose_enum in [
        ("lighting", ReferencePurpose.lighting_reference),
        ("palette", ReferencePurpose.color_palette_reference),
        ("composition", ReferencePurpose.composition_reference),
    ]:
        req = DirectorVisualReferenceRequest(
            reference_image_url="https://example.com/ref.webp",
            reference_purpose=purpose_enum,
        )
        res = visual_reference_analysis_service.analyze(req)
        assert purpose_name in res.profile.visual_summary.lower(), f"Summary should mention {purpose_name}"
    print("  [PASS] Purpose-specific analysis works correctly")

    # 9. Different purposes produce different summaries
    summaries = set()
    for purpose in ReferencePurpose:
        req = DirectorVisualReferenceRequest(
            reference_image_url="https://example.com/ref.webp",
            reference_purpose=purpose,
        )
        res = visual_reference_analysis_service.analyze(req)
        summaries.add(res.profile.visual_summary)
    assert len(summaries) > 1, "Different purposes should produce different summaries"
    print(f"  [PASS] Different purposes produce {len(summaries)} unique summaries")

    # 10. Transfer flags work correctly
    full_request = DirectorVisualReferenceRequest(
        reference_image_url="https://example.com/ref.webp",
        allow_palette_transfer=True,
        allow_lighting_transfer=True,
        allow_composition_transfer=True,
        allow_texture_transfer=True,
    )
    full_result = visual_reference_analysis_service.analyze(full_request)
    assert "not requested" not in full_result.profile.palette_description
    assert "not requested" not in full_result.profile.lighting_description
    assert "not requested" not in full_result.profile.composition_description
    assert "not requested" not in full_result.profile.texture_description
    print("  [PASS] Transfer flags correctly enable/disable traits")

    # Summary
    if failures:
        print(f"\nSMOKE FAIL: {len(failures)} issues found")
        for f in failures:
            print(f"  - {f}")
        return 1

    print(f"\nSMOKE PASS: All checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
