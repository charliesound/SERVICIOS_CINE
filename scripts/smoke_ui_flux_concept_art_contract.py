#!/usr/bin/env python3
"""Smoke test: verify frontend files for Flux concept art exist and are well-formed.
Does NOT start a browser or call /prompt."""

import re
import sys
from pathlib import Path
import os

REPO_ROOT = Path(__file__).resolve().parents[1]
FAILED = False


def check(label: str, condition: bool, detail: str = "") -> None:
    global FAILED
    if condition:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}  {detail}")
        FAILED = True


def file_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def main() -> int:
    global FAILED

    # 1. API client exists
    print("\n--- 1. API client ---")
    api_file = REPO_ROOT / "src_frontend" / "src" / "api" / "conceptArt.ts"
    check("conceptArt.ts exists", api_file.exists())
    api_text = file_text(api_file)

    check("has compileProjectConceptArtWorkflowDryRun", "compileProjectConceptArtWorkflowDryRun" in api_text)
    check("has compileProjectKeyVisualWorkflowDryRun", "compileProjectKeyVisualWorkflowDryRun" in api_text)
    check("uses /concept-art/compile-workflow-dry-run", "/concept-art/compile-workflow-dry-run" in api_text)
    check("uses /key-visual/compile-workflow-dry-run", "/key-visual/compile-workflow-dry-run" in api_text)
    check("imports client from ./client", "from './client'" in api_text or 'from "@/api/client"' in api_text)

    # 2. Types exist
    print("\n--- 2. Types ---")
    types_file = REPO_ROOT / "src_frontend" / "src" / "types" / "conceptArt.ts"
    check("conceptArt.ts types exists", types_file.exists())
    types_text = file_text(types_file)
    check("has ConceptArtDryRunPayload", "ConceptArtDryRunPayload" in types_text)
    check("has ConceptArtDryRunResponse", "ConceptArtDryRunResponse" in types_text)
    check("has ConceptArtPipeline", "ConceptArtPipeline" in types_text)
    check("has CompiledWorkflowPreview", "CompiledWorkflowPreview" in types_text)

    # 3. Component exists
    print("\n--- 3. Component ---")
    comp_file = REPO_ROOT / "src_frontend" / "src" / "components" / "concept-art" / "ConceptArtDryRunPanel.tsx"
    check("ConceptArtDryRunPanel.tsx exists", comp_file.exists())
    comp_text = file_text(comp_file)
    check("has Mode selector", "concept_art" in comp_text and "key_visual" in comp_text)
    check("has Prompt textarea", "prompt" in comp_text and "negativePrompt" in comp_text)
    check("has width/height parameters", "width" in comp_text and "height" in comp_text and "steps" in comp_text)
    check("has Config button", "Preparar Concept Art" in comp_text or "Preparar Key Visual" in comp_text)
    check("has progress phases", "validating" in comp_text and "resolving" in comp_text and "compiling" in comp_text)
    check("has dry-run warning", "Dry-run" in comp_text and "ComfyUI" in comp_text)
    prompt_refs = [line for line in comp_text.split("\n") if "/prompt" in line and "llamado a /prompt" not in line]
    check("no /prompt call (except warning)", len(prompt_refs) == 0, str(prompt_refs))
    render_refs = [line for line in comp_text.split("\n") if "render" in line.lower() and "safe_to_render" not in line and "safe to render" not in line.lower() and "no se ejecuta render" not in line.lower() and "no se ha ejecutado render" not in line.lower()]
    check("no render call (except safe_to_render / warning)", len(render_refs) == 0, str(render_refs))

    # 4. Page integration
    print("\n--- 4. Page integration ---")
    page_file = REPO_ROOT / "src_frontend" / "src" / "pages" / "ProjectDetailPage.tsx"
    check("ProjectDetailPage.tsx exists", page_file.exists())
    page_text = file_text(page_file)
    check("imports ConceptArtDryRunPanel", "ConceptArtDryRunPanel" in page_text)
    check("has concept-art tab", "'concept-art'" in page_text or '"concept-art"' in page_text)
    check("has Concept Art label", "Concept Art" in page_text)

    # 5. No prompt/render calls
    print("\n--- 5. Security check ---")
    all_src = "\n".join([api_text, types_text, comp_text, page_text])
    prompt_lines = [line for line in all_src.split("\n") if "/prompt" in line and "llamado a /prompt" not in line]
    check("no /prompt in frontend code (except warning)", len(prompt_lines) == 0, str(prompt_lines))
    risk_patterns = ["api_key", "sk-", "password", "secret"]
    for pattern in risk_patterns:
        if pattern in all_src:
            check(f"no {pattern} in frontend", False)
            FAILED = True

    # Summary
    print()
    if FAILED:
        print("SMOKE UI CONTRACT FAILED")
        return 1
    else:
        print("SMOKE UI CONTRACT PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(main())
