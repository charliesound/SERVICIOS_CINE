#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROMPTS_PATH = ROOT / "src/comfyui_workflows/landing_semantic_v5/landing_semantic_prompts_v5_reference_guided.json"
REFERENCE_MAP_PATH = ROOT / "src/comfyui_workflows/landing_semantic_v5/landing_reference_map_v5.json"
REFERENCE_MAP_EXAMPLE_PATH = ROOT / "src/comfyui_workflows/landing_semantic_v5/landing_reference_map_v5.example.json"
REF_IMAGES_DIR = ROOT / ".tmp" / "landing_comfyui_v5" / "reference_images"
MEDIA_DIR = ROOT / "src_frontend" / "public" / "landing-media"
GENERATED_MANIFEST_PATH = MEDIA_DIR / "_landing_v5_generated_manifest.txt"
REVIEW_DIR = ROOT / ".tmp" / "landing_comfyui_v5" / "review"
HTML_PATH = REVIEW_DIR / "landing_v5_semantic_review.html"

LANDING_TEXT_MAP: dict[str, dict[str, Any]] = {
    "landing-hero-main-v5": {
        "section": "Hero / Pipeline completo",
        "tagline": "CID conecta guion, storyboard, planificacion y distribucion en un mismo flujo",
        "text_lines": [
            "AILinkCinema combina creatividad visual, lienzo colaborativo e inteligencia artificial con un sistema real de produccion audiovisual.",
            "CID conecta guion, storyboard, planificacion, doblaje, sonido, VFX, montaje y distribucion en un mismo flujo de trabajo.",
        ],
    },
    "landing-problem-fragmented-v5": {
        "section": "Problema / Fragmentacion",
        "tagline": "Cada fase pierde contexto de la anterior",
        "text_lines": [
            "Guion, storyboard, produccion y post suelen operar en entornos separados.",
            "Las herramientas de IA aparecen cada semana, pero ninguna esta disenada para integrarse en un flujo de produccion real.",
        ],
    },
    "landing-ai-reasoning-v5": {
        "section": "Analisis de guion",
        "tagline": "La IA razona antes de generar",
        "text_lines": [
            "Desglose automatico de guion con identificacion de personajes, localizaciones, planos y necesidades de produccion.",
            "Analiza el guion, identifica personajes, localizaciones y desglose tecnico. Recomienda planos y encuadres.",
        ],
    },
    "landing-concept-keyvisual-v5": {
        "section": "Moodboard / Biblia visual",
        "tagline": "Direccion artistica antes del rodaje",
        "text_lines": [
            "Construye referencias visuales por escena, personaje y atmosfera.",
            "Consolida la direccion artistica antes del rodaje.",
        ],
    },
    "landing-storyboard-preview-v5": {
        "section": "Storyboard / Previsualizacion",
        "tagline": "Continuidad visual entre planos",
        "text_lines": [
            "Construye tu storyboard escena por escena. Cada plano mantiene coherencia narrativa y continuidad visual.",
            "Genera storyboards por plano con encuadre, angulo e iluminacion.",
        ],
    },
    "landing-comfyui-generation-v5": {
        "section": "Generacion visual controlada",
        "tagline": "ComfyUI dentro del pipeline de produccion",
        "text_lines": [
            "Workflows de Flux/SDXL para storyboard, concept art y previz. Control de estilo, iluminacion y atmosfera.",
        ],
    },
    "landing-cid-orchestration-v5": {
        "section": "Pipeline Builder / Orquestacion",
        "tagline": "Guion -> Analisis -> Prompt -> ComfyUI -> Storyboard -> Revision -> Entrega",
        "text_lines": [
            "Orquesta el flujo completo: guion -> analisis -> prompt visual -> ComfyUI -> storyboard -> revision -> entrega. Trazabilidad total.",
        ],
    },
    "landing-producers-studios-v5": {
        "section": "Colaboracion en produccion",
        "tagline": "Director, productor y equipo revisan y aprueban versiones",
        "text_lines": [
            "Comparte storyboards, moodboards y versiones con tu equipo.",
            "Director, productor y equipo pueden revisar, comentar y aprobar versiones.",
        ],
    },
    "landing-professional-differential-v5": {
        "section": "Trazabilidad profesional",
        "tagline": "Cada decision queda registrada",
        "text_lines": [
            "Cada decision creativa, cada version y cada aprobacion quedan registradas.",
            "La IA acelera, pero las decisiones de calidad y entrega permanecen controladas.",
        ],
    },
    "landing-delivery-final-v5": {
        "section": "Delivery / QC final",
        "tagline": "Validamos, revisamos y entregamos",
        "text_lines": [
            "Entrar en fases avanzadas con mas control sobre voz, QC, stems, trazabilidad y compliance.",
            "Validamos, revisamos y entregamos. Handoff limpio para cada siguiente fase.",
        ],
    },
    "landing-visual-bible-v5": {
        "section": "Biblia visual / Referencias CID",
        "tagline": "Guion + personajes + localizaciones + paleta + continuidad",
        "text_lines": [
            "CID construye una biblia visual cinematografica: coteja el guion con referencias de personajes, localizaciones, paleta de color, continuidad, planos y atmosfera.",
            "Toda la informacion visual del proyecto organizada y cruzada antes de generar prompts para ComfyUI.",
        ],
    },
}

QUALITY_FLAGS: dict[str, str] = {}


def load_prompt_pack() -> dict[str, Any]:
    return json.loads(PROMPTS_PATH.read_text(encoding="utf-8"))


def load_reference_map() -> dict[str, Any]:
    ref_path = REFERENCE_MAP_PATH if REFERENCE_MAP_PATH.exists() else REFERENCE_MAP_EXAMPLE_PATH
    return json.loads(ref_path.read_text(encoding="utf-8"))


def parse_generated_manifest() -> dict[str, dict[str, str]]:
    if not GENERATED_MANIFEST_PATH.exists():
        return {}
    parsed: dict[str, dict[str, str]] = {}
    for raw_line in GENERATED_MANIFEST_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = line.split("\t")
        image_key = parts[0].strip()
        payload: dict[str, str] = {"image_key": image_key}
        if len(parts) > 1:
            payload["file_name"] = parts[1].strip()
        if len(parts) > 2:
            payload["raw"] = parts[2].strip()
            for token in parts[2].split():
                if "=" not in token:
                    continue
                key, value = token.split("=", 1)
                payload[key.strip()] = value.strip()
        parsed[image_key] = payload
    return parsed


def rel_asset(path: Path) -> str:
    return os.path.relpath(path, REVIEW_DIR).replace(os.sep, "/")


def escape(value: str) -> str:
    return html.escape(value, quote=True)


def render_text_block(lines: list[str]) -> str:
    return "".join(f"<li>{escape(line)}</li>" for line in lines)


def quality_class(flag: str) -> str:
    return {
        "TOO GENERIC": "flag-generic",
        "TOO DARK": "flag-dark",
        "WRONG SEMANTICS": "flag-semantic",
        "GOOD CANDIDATE": "flag-good",
        "NEEDS REGENERATION": "flag-regen",
        "REFERENCE GUIDED": "flag-ref",
    }.get(flag, "flag-neutral")


def render_qa_checklist(qa_rules: list[str]) -> str:
    if not qa_rules:
        return '<div class="info-block"><em>No QA rules defined</em></div>'
    items = "".join(f"<li><span class=\"qa-check\">[ ]</span> {escape(rule)}</li>" for rule in qa_rules)
    return f'<div class="info-block checklist"><strong>QA Checklist V5</strong><ul>{items}</ul></div>'


V5_COMPARISON_CHECKLIST = [
    "Se parece a la referencia?",
    "Representa el texto del bloque?",
    "Tiene claridad visual?",
    "Tiene vida / dinamismo?",
    "Es cinematografica?",
    "Evita abstraccion generica?",
    "Funciona para web (legible en miniatura)?",
    "Se entiende en 2-3 segundos?",
]


def render_comparison_checklist() -> str:
    items = "".join(f"<li><span class=\"qa-check\">[ ]</span> {escape(q)}</li>" for q in V5_COMPARISON_CHECKLIST)
    return f'<div class="info-block checklist v5-check"><strong>Comparacion V5</strong><ul>{items}</ul></div>'


def build_review_html() -> str:
    prompt_pack = load_prompt_pack()
    items = prompt_pack.get("items", [])
    ref_manifest = load_reference_map()
    ref_items = {item["image_key"]: item for item in ref_manifest.get("items", [])}
    gen_manifest = parse_generated_manifest()
    available_v4 = sorted(MEDIA_DIR.glob("landing-*-v4.webp"))
    available_v5 = sorted(MEDIA_DIR.glob("landing-*-v5.webp"))

    sections: list[str] = []
    for index, item in enumerate(items, start=1):
        image_key = item["image_key"]
        v4_key = item.get("v4_source_key", "")
        v5_path = MEDIA_DIR / f"{image_key}.webp"
        v4_path = MEDIA_DIR / f"{v4_key}.webp" if v4_key else None

        ref_entry = ref_items.get(image_key, {})
        ref_filename = ref_entry.get("reference_image_file", "")
        ref_role = ref_entry.get("reference_role", "style")
        ref_strength = ref_entry.get("reference_strength", 0.55)
        ref_image_path = REF_IMAGES_DIR / ref_filename if ref_filename else None

        v5_src = rel_asset(v5_path) if v5_path.exists() else ""
        v4_src = rel_asset(v4_path) if v4_path and v4_path.exists() else ""
        ref_src = rel_asset(ref_image_path) if ref_image_path and ref_image_path.exists() else ""

        manifest_row = gen_manifest.get(image_key, {})
        flag = QUALITY_FLAGS.get(image_key, "REFERENCE GUIDED")

        v4_visual = (
            f"<img class=\"compare-image\" src=\"{escape(v4_src)}\" alt=\"V4 reference\">"
            if v4_src
            else '<div class="missing-image">No V4 image</div>'
        )
        ref_visual = (
            f"<img class=\"compare-image ref-border\" src=\"{escape(ref_src)}\" alt=\"Reference\">"
            if ref_src
            else '<div class="missing-image">No reference image mapped</div>'
        )
        v5_visual = (
            f"<img class=\"compare-image\" src=\"{escape(v5_src)}\" alt=\"V5 candidate\">"
            if v5_src
            else '<div class="missing-image pending">V5 pending render</div>'
        )

        manifest_html = (
            f"<div class=\"manifest-box\">{escape(manifest_row.get('raw', 'imported'))}</div>"
            if manifest_row
            else '<div class="manifest-box">Not yet imported</div>'
        )

        ref_info = (
            f"Role: {ref_role} | Strength: {ref_strength}"
            if ref_filename
            else "No reference mapped"
        )

        qa_rules = item.get("qa_rules", [])
        composition_lock = item.get("composition_lock", "Not specified")
        lighting_lock = item.get("lighting_lock", "Not specified")
        semantic_must_have = item.get("semantic_must_have", [])
        semantic_must_not_have = item.get("semantic_must_not_have", [])

        must_have_html = "".join(f"<li>{escape(m)}</li>" for m in semantic_must_have) if semantic_must_have else "<li>None</li>"
        must_not_html = "".join(f"<li>{escape(m)}</li>" for m in semantic_must_not_have) if semantic_must_not_have else "<li>None</li>"

        sections.append(
            "<section class=\"review-card\">"
            f"<div class=\"review-index\">Block {index:02d}</div>"
            f"<div class=\"quality-flag {quality_class(flag)}\">{escape(flag)}</div>"
            f"<h2>{escape(item.get('visual_intent', item['image_key']))}</h2>"
            "<div class=\"review-grid\">"
            "<div class=\"visual-column\">"
            "<div class=\"image-comparison\">"
            "<div class=\"compare-group\">"
            f"<div class=\"compare-label\">V4 actual</div>{v4_visual}"
            "</div>"
            "<div class=\"compare-group\">"
            f"<div class=\"compare-label\">Referencia <span class=\"ref-badge\">{escape(ref_info)}</span></div>{ref_visual}"
            "</div>"
            "<div class=\"compare-group\">"
            f"<div class=\"compare-label\">V5 generado</div>{v5_visual}"
            "</div>"
            "</div>"
            f"<div class=\"file-chip\">Target: {image_key}.webp</div>"
            f"{manifest_html}"
            f"<div class=\"info-block ref-detail\"><strong>Referencia</strong><p>{escape(ref_info)}</p></div>"
            "</div>"
            "<div class=\"text-column\">"
            f"<div class=\"meta-kicker\">{escape(LANDING_TEXT_MAP.get(image_key, {}).get('section', 'Landing V5'))}</div>"
            f"<h3>{escape(LANDING_TEXT_MAP.get(image_key, {}).get('tagline', 'Visual'))}</h3>"
            "<div class=\"info-block\"><strong>Texto del bloque</strong><ul>"
            f"{render_text_block(LANDING_TEXT_MAP.get(image_key, {}).get('text_lines', ['']))}"
            "</ul></div>"
            f"<div class=\"info-block\"><strong>Intencion visual</strong><p>{escape(item.get('visual_intent', ''))}</p></div>"
            f"<div class=\"info-block\"><strong>Composition Lock</strong><p>{escape(composition_lock)}</p></div>"
            f"<div class=\"info-block\"><strong>Lighting Lock</strong><p>{escape(lighting_lock)}</p></div>"
            "<div class=\"info-block\"><strong>Must Have</strong><ul>" f"{must_have_html}</ul></div>"
            "<div class=\"info-block\"><strong>Must Not Have</strong><ul>" f"{must_not_html}</ul></div>"
            f"<div class=\"info-block\"><strong>Prompt V5</strong><pre>{escape(item.get('positive_prompt', ''))}</pre></div>"
            f"{render_qa_checklist(qa_rules)}"
            f"{render_comparison_checklist()}"
            "</div>"
            "</div>"
            "</section>"
        )

    v5_gallery = "".join(
        f"<figure class=\"thumb-card\"><img src=\"{escape(rel_asset(p))}\" alt=\"{escape(p.name)}\"><figcaption>{escape(p.name)}</figcaption></figure>"
        for p in available_v5
    )
    v4_gallery = "".join(
        f"<figure class=\"thumb-card\"><img src=\"{escape(rel_asset(p))}\" alt=\"{escape(p.name)}\"><figcaption>{escape(p.name)}</figcaption></figure>"
        for p in available_v4
    )

    ref_gallery = "".join(
        f"<figure class=\"thumb-card\"><img class=\"ref-border\" src=\"{escape(rel_asset(p))}\" alt=\"{escape(p.name)}\"><figcaption>{escape(p.name)}</figcaption></figure>"
        for p in sorted(REF_IMAGES_DIR.glob("*")) if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    )

    html_doc = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Landing V5 Semantic Review - Reference Guided</title>
  <style>
    :root {{
      color-scheme: dark;
      --bg: #07090c;
      --panel: #10161d;
      --panel-2: #171f29;
      --line: rgba(255,255,255,0.08);
      --text: #ecf1f6;
      --muted: #96a4b5;
      --amber: #f1b24a;
      --danger: #f38e8e;
      --warning: #ffb86b;
      --good: #7fe0a0;
      --regen: #ff7d7d;
      --ref-border: #4a9eff;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Arial, sans-serif; background: radial-gradient(circle at top, #1a2734 0%, var(--bg) 48%); color: var(--text); }}
    .shell {{ width: min(1480px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 64px; }}
    .intro {{ margin-bottom: 28px; padding: 24px; border: 1px solid var(--line); border-radius: 24px; background: rgba(16,22,29,0.92); }}
    .intro h1 {{ margin: 0 0 12px; font-size: 34px; }}
    .intro p {{ margin: 0 0 10px; color: var(--muted); line-height: 1.6; }}
    .intro code {{ color: var(--amber); }}
    .review-card {{ position: relative; margin-bottom: 22px; padding: 22px; border: 1px solid var(--line); border-radius: 28px; background: linear-gradient(180deg, rgba(17,24,33,0.98), rgba(10,14,19,0.98)); box-shadow: 0 24px 80px rgba(0,0,0,0.22); }}
    .review-index {{ display: inline-block; padding: 6px 10px; border-radius: 999px; background: rgba(241,178,74,0.12); color: var(--amber); font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase; }}
    .quality-flag {{ position: absolute; right: 22px; top: 22px; padding: 8px 12px; border-radius: 999px; font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; border: 1px solid transparent; }}
    .flag-dark {{ background: rgba(255,125,125,0.12); color: var(--danger); border-color: rgba(255,125,125,0.26); }}
    .flag-generic {{ background: rgba(255,184,107,0.12); color: var(--warning); border-color: rgba(255,184,107,0.26); }}
    .flag-semantic {{ background: rgba(255,125,125,0.12); color: var(--regen); border-color: rgba(255,125,125,0.26); }}
    .flag-good {{ background: rgba(127,224,160,0.12); color: var(--good); border-color: rgba(127,224,160,0.26); }}
    .flag-regen {{ background: rgba(255,125,125,0.12); color: var(--regen); border-color: rgba(255,125,125,0.26); }}
    .flag-ref {{ background: rgba(74,158,255,0.12); color: var(--ref-border); border-color: rgba(74,158,255,0.26); }}
    .flag-neutral {{ background: rgba(150,164,181,0.12); color: var(--muted); border-color: rgba(150,164,181,0.26); }}
    h2 {{ margin: 14px 0 18px; font-size: 30px; line-height: 1.1; padding-right: 180px; }}
    h3 {{ margin: 0 0 10px; font-size: 18px; }}
    .review-grid {{ display: grid; grid-template-columns: minmax(420px, 1fr) minmax(380px, 0.95fr); gap: 22px; align-items: start; }}
    .visual-column, .text-column {{ display: flex; flex-direction: column; gap: 14px; }}
    .image-comparison {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }}
    .compare-group {{ display: flex; flex-direction: column; gap: 6px; }}
    .compare-label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.12em; color: var(--muted); }}
    .compare-image {{ width: 100%; display: block; border-radius: 18px; border: 1px solid var(--line); background: #0a1016; min-height: 180px; object-fit: cover; }}
    .ref-border {{ border-color: var(--ref-border) !important; box-shadow: 0 0 12px rgba(74,158,255,0.2); }}
    .ref-badge {{ display: inline-block; padding: 2px 8px; border-radius: 999px; background: rgba(74,158,255,0.15); color: var(--ref-border); font-size: 10px; }}
    .file-chip {{ display: inline-block; padding: 8px 12px; border-radius: 999px; background: rgba(255,255,255,0.05); color: var(--muted); font-size: 13px; }}
    .manifest-box, .missing-image {{ padding: 14px; border-radius: 16px; border: 1px solid var(--line); background: var(--panel-2); color: var(--muted); line-height: 1.5; }}
    .missing-image {{ color: var(--danger); min-height: 180px; display: flex; align-items: center; justify-content: center; text-align: center; }}
    .pending {{ color: var(--amber); border-color: rgba(241,178,74,0.3); }}
    .meta-kicker {{ color: var(--amber); font-size: 12px; letter-spacing: 0.16em; text-transform: uppercase; }}
    .info-block {{ padding: 16px; border-radius: 18px; border: 1px solid var(--line); background: rgba(255,255,255,0.03); }}
    .info-block strong {{ display: block; margin-bottom: 10px; color: var(--text); }}
    .info-block p, .info-block li {{ margin: 0; color: var(--muted); line-height: 1.6; }}
    .info-block ul {{ margin: 0; padding-left: 18px; display: grid; gap: 8px; }}
    .ref-detail {{ border-color: rgba(74,158,255,0.2); }}
    .v5-check {{ border-color: rgba(127,224,160,0.2); }}
    pre {{ margin: 0; white-space: pre-wrap; word-break: break-word; color: #d6e1ed; font-size: 13px; line-height: 1.55; }}
    .qa-check {{ color: var(--amber); }}
    .thumb-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 14px; }}
    .thumb-card {{ margin: 0; padding: 12px; border: 1px solid var(--line); border-radius: 18px; background: rgba(255,255,255,0.03); }}
    .thumb-card img {{ width: 100%; display: block; border-radius: 18px; border: 1px solid var(--line); background: #0a1016; }}
    figcaption {{ margin-top: 8px; font-size: 12px; color: var(--muted); line-height: 1.4; word-break: break-word; }}
    .gallery-section {{ margin-top: 28px; padding: 22px; border: 1px solid var(--line); border-radius: 28px; background: rgba(16,22,29,0.92); }}
    .gallery-section h2 {{ margin-top: 0; padding-right: 0; }}
    @media (max-width: 1100px) {{
      .image-comparison {{ grid-template-columns: 1fr; }}
    }}
    @media (max-width: 980px) {{
      .review-grid {{ grid-template-columns: 1fr; }}
      .image-comparison {{ grid-template-columns: 1fr; }}
      h2 {{ padding-right: 0; }}
      .quality-flag {{ position: static; margin-top: 12px; display: inline-block; }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <section class="intro">
      <h1>Landing V5 Semantic Review — Reference Guided</h1>
      <p>Comparacion V5 reference-guided vs V4. Cada bloque muestra V4, referencia y V5 generado.</p>
      <p>Prompt pack: <code>{escape(str(PROMPTS_PATH.relative_to(ROOT)))}</code></p>
      <p>Las imagenes V5 se importan desde ComfyUI a <code>public/landing-media/landing-*-v5.webp</code></p>
      <p>Las referencias visuales estan en <code>.tmp/landing_comfyui_v5/reference_images/</code></p>
    </section>
    {''.join(sections)}
    {f'''<section class="gallery-section"><h2>Referencias visuales disponibles ({len(ref_gallery)})</h2><div class="thumb-grid">{ref_gallery if ref_gallery else '<div class="missing-image">No reference images copied yet. Run prepare script.</div>'}</div></section>''' if True else ''}
    {f'''<section class="gallery-section"><h2>Todas las imagenes V5 disponibles</h2><div class="thumb-grid">{v5_gallery if v5_gallery else '<div class="missing-image">No V5 images imported yet. Run render + import pipeline.</div>'}</div></section>''' if True else ''}
    {f'''<section class="gallery-section"><h2>Todas las imagenes V4 (referencia base)</h2><div class="thumb-grid">{v4_gallery if v4_gallery else '<div class="missing-image">No V4 images found.</div>'}</div></section>''' if True else ''}
  </div>
</body>
</html>
"""
    return html_doc


def main() -> int:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    HTML_PATH.write_text(build_review_html(), encoding="utf-8")
    print(f"V5 Semantic review: {HTML_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
