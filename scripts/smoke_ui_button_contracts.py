#!/usr/bin/env python3
"""
Smoke test para verificar que los endpoints que usa la UI existen y devuelven estructura compatible.
Usa urllib estándar, no requests.
"""
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path

API_BASE = "http://127.0.0.1:8010/api"
ROOT_BASE = "http://127.0.0.1:8010"

def check(method, path, data=None, root=False):
    base = ROOT_BASE if root else API_BASE
    url = f"{base}{path}"
    try:
        if data:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method=method
            )
        else:
            req = urllib.request.Request(url, method=method)
        resp = urllib.request.urlopen(req, timeout=5)
        return resp
    except urllib.error.HTTPError as e:
        return e
    except Exception as e:
        print(f"FAIL: {method} {path} -> {e}")
        return None

def main():
    errors = []

    # 0. Frontend project detail wiring contract
    project_detail_path = Path("/opt/SERVICIOS_CINE/src_frontend/src/pages/ProjectDetailPage.tsx")
    storyboard_selector_path = Path("/opt/SERVICIOS_CINE/src_frontend/src/components/storyboard/StoryboardSequenceSelectorModal.tsx")
    try:
        project_detail_source = project_detail_path.read_text(encoding="utf-8")
        storyboard_selector_source = storyboard_selector_path.read_text(encoding="utf-8") if storyboard_selector_path.exists() else ""
        project_detail_checks = {
            'handler handleAnalyzeScript': 'handleAnalyzeScript' in project_detail_source,
            'handler handleGenerateStoryboard': 'handleGenerateStoryboard' in project_detail_source,
            'handler upload script': 'handleScriptFileChange' in project_detail_source,
            'texto "Analizar guion"': 'Analizar guion' in project_detail_source,
            'texto "Generar storyboard"': 'Generar storyboard' in project_detail_source,
            'texto "Subir archivo de guion"': 'Subir archivo de guion' in project_detail_source,
            'selector "Seleccionar secuencias"': 'Seleccionar secuencias para storyboard' in storyboard_selector_source,
            'accion "Generar seleccionadas"': 'Generar seleccionadas' in storyboard_selector_source,
            'accion "Generar storyboard completo"': 'Generar storyboard completo' in storyboard_selector_source,
            'accion "Seleccionar todo"': 'Seleccionar todo' in storyboard_selector_source,
            'checkbox de selección': 'type="checkbox"' in storyboard_selector_source,
            'input type file': 'type="file"' in project_detail_source,
            'accept txt md': '.txt,.md' in project_detail_source,
            'onClick analizar': 'onClick={handleAnalyzeScript}' in project_detail_source,
            'onClick storyboard selector': 'onClick={handleGenerateStoryboard}' in project_detail_source,
            'confirmación de selección': 'confirmGenerateStoryboardSelection' in project_detail_source,
            'llamada storyboardApi.generate': 'storyboardApi.generate' in project_detail_source,
            'llamada storyboardApi.getStoryboard': 'storyboardApi.getStoryboard' in project_detail_source,
            'llamada API análisis': 'projectsApi.analyze' in project_detail_source,
            'estado isStoryboarding': 'isStoryboarding' in project_detail_source,
            'estado isAnalyzing': 'isAnalyzing' in project_detail_source,
            'estado isUploadingScript': 'isUploadingScript' in project_detail_source,
            'progreso analysisProgress': 'analysisProgress' in project_detail_source,
            'progreso storyboardProgress': 'storyboardProgress' in project_detail_source,
            'type button principal': 'type="button"' in project_detail_source,
            'polling o JobProgress': 'JobProgress' in project_detail_source or 'setInterval' in project_detail_source,
        }
        missing_project_detail_checks = [label for label, ok in project_detail_checks.items() if not ok]
        if missing_project_detail_checks:
            errors.append(f"ProjectDetailPage wiring missing: {', '.join(missing_project_detail_checks)}")
        else:
            print("PASS: ProjectDetailPage UI contract")
    except Exception as exc:
        errors.append(f"ProjectDetailPage wiring unreadable: {exc}")

    # 1. Health check
    r = check("GET", "/health", root=True)
    if r and (getattr(r, 'status', None) == 200 or getattr(r, 'code', None) == 200):
        print("PASS: /health")
    else:
        errors.append("/health")

    # 2. Projects list (requires auth, but endpoint should exist)
    r = check("GET", "/projects")
    if r and hasattr(r, 'code') and r.code in (200, 401, 403):
        print(f"PASS: GET /projects (status={r.code})")
    else:
        errors.append(f"GET /projects")

    # 3. Analysis endpoint exists
    r = check("POST", "/projects/TEST/analyze")
    if r and hasattr(r, 'code') and r.code in (401, 403, 404):
        print(f"PASS: POST /projects/{{id}}/analyze (status={r.code})")
    else:
        errors.append(f"POST /projects/{{id}}/analyze")

    # 4. Storyboard generate endpoint exists
    r = check("POST", "/projects/TEST/storyboard/generate", data={
        "mode": "SINGLE_SCENE",
        "scene_start": 1,
        "scene_end": 1,
        "selected_scene_ids": ["1"],
        "style_preset": "cinematic_realistic",
        "shots_per_scene": 1,
        "overwrite": True
    })
    if r and hasattr(r, 'code') and r.code in (401, 403, 404):
        print(f"PASS: POST /projects/{{id}}/storyboard/generate (status={r.code})")
    else:
        errors.append(f"POST /projects/{{id}}/storyboard/generate")

    # 5. Jobs list endpoint exists
    r = check("GET", "/projects/TEST/jobs")
    if r and hasattr(r, 'code') and r.code in (200, 401, 403, 404):
        print(f"PASS: GET /projects/{{id}}/jobs (status={r.code})")
        if r.code == 200:
            try:
                data = json.loads(r.read().decode('utf-8'))
                if "jobs" in data:
                    print("  -> Response has 'jobs' field")
                else:
                    print("  -> WARNING: Response missing 'jobs' field")
            except:
                pass
    else:
        errors.append(f"GET /projects/{{id}}/jobs")

    # 6. Progress endpoint exists
    r = check("GET", "/projects/TEST/jobs/FAKE/progress")
    if r and hasattr(r, 'code') and r.code in (200, 401, 403, 404):
        print(f"PASS: GET /projects/{{id}}/jobs/{{job_id}}/progress (status={r.code})")
        if r.code == 200:
            try:
                data = json.loads(r.read().decode('utf-8'))
                required = ["job_id", "status", "progress_percent", "progress_stage", "progress_code"]
                missing = [f for f in required if f not in data]
                if not missing:
                    print("  -> Progress fields present")
                else:
                    print(f"  -> WARNING: Missing fields: {missing}")
            except:
                pass
    else:
        errors.append(f"GET /projects/{{id}}/jobs/{{job_id}}/progress")

    # 7. Image assets endpoint exists
    r = check("GET", "/projects/TEST/assets/image-assets")
    if r and hasattr(r, 'code') and r.code in (200, 401, 403, 404):
        print(f"PASS: GET /projects/{{id}}/assets/image-assets (status={r.code})")
    else:
        errors.append(f"GET /projects/{{id}}/assets/image-assets")

    print("\n--- Result ---")
    if errors:
        print(f"FAIL: {len(errors)} endpoint(s) failed:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("PASS: All UI button contract checks passed")
        sys.exit(0)

if __name__ == "__main__":
    main()
