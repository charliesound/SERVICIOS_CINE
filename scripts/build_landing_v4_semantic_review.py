#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROMPTS_PATH = ROOT / "src/comfyui_workflows/landing_semantic_v4/landing_semantic_prompts_v4.json"
MEDIA_DIR = ROOT / "src_frontend" / "public" / "landing-media"
GENERATED_MANIFEST_PATH = MEDIA_DIR / "_landing_v4_generated_manifest.txt"
REVIEW_DIR = ROOT / ".tmp" / "landing_comfyui_v4" / "review"
HTML_PATH = REVIEW_DIR / "landing_v4_semantic_review.html"

LANDING_TEXT_MAP: dict[str, dict[str, Any]] = {
    "landing-hero-main-v4": {
        "section": "Hero / Pipeline completo",
        "tagline": "CID conecta guion, storyboard, planificacion y distribucion en un mismo flujo",
        "text_lines": [
            "AILinkCinema combina creatividad visual, lienzo colaborativo e inteligencia artificial con un sistema real de produccion audiovisual.",
            "CID conecta guion, storyboard, planificacion, doblaje, sonido, VFX, montaje y distribucion en un mismo flujo de trabajo.",
        ],
    },
    "landing-problem-fragmented-v4": {
        "section": "Problema / Fragmentacion",
        "tagline": "Cada fase pierde contexto de la anterior",
        "text_lines": [
            "Guion, storyboard, produccion y post suelen operar en entornos separados.",
            "Las herramientas de IA aparecen cada semana, pero ninguna esta disenada para integrarse en un flujo de produccion real.",
        ],
    },
    "landing-ai-reasoning-v4": {
        "section": "Analisis de guion",
        "tagline": "La IA razona antes de generar",
        "text_lines": [
            "Desglose automatico de guion con identificacion de personajes, localizaciones, planos y necesidades de produccion.",
            "Analiza el guion, identifica personajes, localizaciones y desglose tecnico. Recomienda planos y encuadres.",
        ],
    },
    "landing-concept-keyvisual-v4": {
        "section": "Moodboard / Biblia visual",
        "tagline": "Direccion artistica antes del rodaje",
        "text_lines": [
            "Construye referencias visuales por escena, personaje y atmosfera.",
            "Consolida la direccion artistica antes del rodaje.",
        ],
    },
    "landing-storyboard-preview-v4": {
        "section": "Storyboard / Previsualizacion",
        "tagline": "Continuidad visual entre planos",
        "text_lines": [
            "Construye tu storyboard escena por escena. Cada plano mantiene coherencia narrativa y continuidad visual.",
            "Genera storyboards por plano con encuadre, angulo e iluminacion.",
        ],
    },
    "landing-comfyui-generation-v4": {
        "section": "Generacion visual controlada",
        "tagline": "ComfyUI dentro del pipeline de produccion",
        "text_lines": [
            "Workflows de Flux/SDXL para storyboard, concept art y previz. Control de estilo, iluminacion y atmosfera.",
        ],
    },
    "landing-cid-orchestration-v4": {
        "section": "Pipeline Builder / Orquestacion",
        "tagline": "Guion -> Analisis -> Prompt -> ComfyUI -> Storyboard -> Revision -> Entrega",
        "text_lines": [
            "Orquesta el flujo completo: guion -> analisis -> prompt visual -> ComfyUI -> storyboard -> revision -> entrega. Trazabilidad total.",
        ],
    },
    "landing-producers-studios-v4": {
        "section": "Colaboracion en produccion",
        "tagline": "Director, productor y equipo revisan y aprueban versiones",
        "text_lines": [
            "Comparte storyboards, moodboards y versiones con tu equipo.",
            "Director, productor y equipo pueden revisar, comentar y aprobar versiones.",
        ],
    },
    "landing-professional-differential-v4": {
        "section": "Trazabilidad profesional",
        "tagline": "Cada decision queda registrada",
        "text_lines": [
            "Cada decision creativa, cada version y cada aprobacion quedan registradas.",
            "La IA acelera, pero las decisiones de calidad y entrega permanecen controladas.",
        ],
    },
    "landing-delivery-final-v4": {
        "section": "Delivery / QC final",
        "tagline": "Validamos, revisamos y entregamos",
        "text_lines": [
            "Entrar en fases avanzadas con mas control sobre voz, QC, stems, trazabilidad y compliance.",
            "Validamos, revisamos y entregamos. Handoff limpio para cada siguiente fase.",
        ],
    },
    "landing-visual-bible-v4": {
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
    }.get(flag, "flag-neutral")


def render_qa_checklist(qa_rules: list[str]) -> str:
    if not qa_rules:
        return '<div class="info-block"><em>No QA rules defined</em></div>'
    items = "".join(f"<li><span class=\"qa-check\">[ ]</span> {escape(rule)}</li>" for rule in qa_rules)
    return f'<div class="info-block checklist"><strong>QA Checklist V4</strong><ul>{items}</ul></div>'


def build_review_html() -> str:
    prompt_pack = load_prompt_pack()
    items = prompt_pack.get("items", [])
    manifest = parse_generated_manifest()
    available_v3 = sorted(MEDIA_DIR.glob("landing-*-v3.webp"))
    available_v4 = sorted(MEDIA_DIR.glob("landing-*-v4.webp"))

    sections: list[str] = []
    for index, item in enumerate(items, start=1):
        image_key = item["image_key"]
        v4_path = MEDIA_DIR / item["target_file_name"]
        v3_candidates = [p for p in available_v3 if image_key.replace("-v4", "-v3") in p.name]
        v4_src = rel_asset(v4_path) if v4_path.exists() else ""
        v3_src = rel_asset(v3_candidates[0]) if v3_candidates else ""
        landing_text = LANDING_TEXT_MAP.get(image_key, {})
        manifest_row = manifest.get(image_key, {})
        flag = QUALITY_FLAGS.get(image_key, "NEEDS REGENERATION")

        v3_visual = (
            f"<img class=\"compare-image\" src=\"{escape(v3_src)}\" alt=\"V3 current\">"
            if v3_src
            else '<div class="missing-image">No V3 image</div>'
        )
        v4_visual = (
            f"<img class=\"compare-image\" src=\"{escape(v4_src)}\" alt=\"V4 candidate\">"
            if v4_src
            else '<div class="missing-image pending">V4 pending render</div>'
        )
        manifest_html = (
            f"<div class=\"manifest-box\">{escape(manifest_row.get('raw', 'imported'))}</div>"
            if manifest_row
            else '<div class=\"manifest-box\">Not yet imported</div>'
        )

        qa_rules = item.get("qa_rules", [])

        sections.append(
            "<section class=\"review-card\">"
            f"<div class=\"review-index\">Block {index:02d}</div>"
            f"<div class=\"quality-flag {quality_class(flag)}\">{escape(flag)}</div>"
            f"<h2>{escape(item['block_label'])}</h2>"
            "<div class=\"review-grid\">"
            "<div class=\"visual-column\">"
            "<div class=\"image-comparison\">"
            "<div class=\"compare-group\">"
            f"<div class=\"compare-label\">V3 actual</div>{v3_visual}"
            "</div>"
            "<div class=\"compare-group\">"
            f"<div class=\"compare-label\">V4 candidato</div>{v4_visual}"
            "</div>"
            "</div>"
            f"<div class=\"file-chip\">Target: {escape(item['target_file_name'])}</div>"
            f"{manifest_html}"
            "</div>"
            "<div class=\"text-column\">"
            f"<div class=\"meta-kicker\">{escape(landing_text.get('section', 'Landing'))}</div>"
            f"<h3>{escape(landing_text.get('tagline', item.get('landing_copy_focus', 'Visual')))}</h3>"
            "<div class=\"info-block\"><strong>Texto del bloque</strong><ul>"
            f"{render_text_block(list(landing_text.get('text_lines', [item.get('landing_copy_focus', '')])))}"
            "</ul></div>"
            f"<div class=\"info-block\"><strong>Intencion semantica</strong><p>{escape(item.get('semantic_intent', ''))}</p></div>"
            f"<div class=\"info-block\"><strong>Elementos requeridos</strong><p>{escape(item.get('required_elements', ''))}</p></div>"
            f"<div class=\"info-block\"><strong>Composicion</strong><p>{escape(item.get('composition_notes', ''))}</p></div>"
            f"<div class=\"info-block\"><strong>Iluminacion</strong><p>{escape(item.get('lighting_notes', ''))}</p></div>"
            f"<div class=\"info-block\"><strong>Color</strong><p>{escape(item.get('color_notes', ''))}</p></div>"
            f"<div class=\"info-block\"><strong>Lenguaje cinematografico</strong><p>{escape(item.get('cinematic_language', ''))}</p></div>"
            f"<div class=\"info-block\"><strong>Prompt V4</strong><pre>{escape(item.get('positive_prompt', ''))}</pre></div>"
            f"{render_qa_checklist(qa_rules)}"
            "</div>"
            "</div>"
            "</section>"
        )

    v4_gallery = "".join(
        f"<figure class=\"thumb-card\"><img src=\"{escape(rel_asset(p))}\" alt=\"{escape(p.name)}\"><figcaption>{escape(p.name)}</figcaption></figure>"
        for p in available_v4
    )
    v3_gallery = "".join(
        f"<figure class=\"thumb-card\"><img src=\"{escape(rel_asset(p))}\" alt=\"{escape(p.name)}\"><figcaption>{escape(p.name)}</figcaption></figure>"
        for p in available_v3
    )

    html_doc = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Landing V4 Semantic Review</title>
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
    .flag-neutral {{ background: rgba(150,164,181,0.12); color: var(--muted); border-color: rgba(150,164,181,0.26); }}
    h2 {{ margin: 14px 0 18px; font-size: 30px; line-height: 1.1; padding-right: 180px; }}
    h3 {{ margin: 0 0 10px; font-size: 18px; }}
    .review-grid {{ display: grid; grid-template-columns: minmax(420px, 1fr) minmax(380px, 0.95fr); gap: 22px; align-items: start; }}
    .visual-column, .text-column {{ display: flex; flex-direction: column; gap: 14px; }}
    .image-comparison {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
    .compare-group {{ display: flex; flex-direction: column; gap: 6px; }}
    .compare-label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.12em; color: var(--muted); }}
    .compare-image {{ width: 100%; display: block; border-radius: 18px; border: 1px solid var(--line); background: #0a1016; min-height: 180px; object-fit: cover; }}
    .file-chip {{ display: inline-block; padding: 8px 12px; border-radius: 999px; background: rgba(255,255,255,0.05); color: var(--muted); font-size: 13px; }}
    .manifest-box, .missing-image {{ padding: 14px; border-radius: 16px; border: 1px solid var(--line); background: var(--panel-2); color: var(--muted); line-height: 1.5; }}
    .missing-image {{ color: var(--danger); min-height: 180px; display: flex; align-items: center; justify-content: center; text-align: center; }}
    .pending {{ color: var(--amber); border-color: rgba(241,178,74,0.3); }}
    .meta-kicker {{ color: var(--amber); font-size: 12px; letter-spacing: 0.16em; text-transform: uppercase; }}
    .info-block {{ padding: 16px; border-radius: 18px; border: 1px solid var(--line); background: rgba(255,255,255,0.03); }}
    .info-block strong {{ display: block; margin-bottom: 10px; color: var(--text); }}
    .info-block p, .info-block li {{ margin: 0; color: var(--muted); line-height: 1.6; }}
    .info-block ul {{ margin: 0; padding-left: 18px; display: grid; gap: 8px; }}
    pre {{ margin: 0; white-space: pre-wrap; word-break: break-word; color: #d6e1ed; font-size: 13px; line-height: 1.55; }}
    .qa-check {{ color: var(--amber); }}
    .thumb-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 14px; }}
    .thumb-card {{ margin: 0; padding: 12px; border: 1px solid var(--line); border-radius: 18px; background: rgba(255,255,255,0.03); }}
    .thumb-card img {{ width: 100%; display: block; border-radius: 18px; border: 1px solid var(--line); background: #0a1016; }}
    figcaption {{ margin-top: 8px; font-size: 12px; color: var(--muted); line-height: 1.4; word-break: break-word; }}
    .gallery-section {{ margin-top: 28px; padding: 22px; border: 1px solid var(--line); border-radius: 28px; background: rgba(16,22,29,0.92); }}
    .gallery-section h2 {{ margin-top: 0; padding-right: 0; }}
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
      <h1>Landing V4 Semantic Review</h1>
      <p>Revision semantica V4 vs V3. Cada bloque muestra la imagen V3 actual, el candidato V4 si existe, y los criterios semanticos que debe cumplir.</p>
      <p>Prompt pack: <code>{escape(str(PROMPTS_PATH.relative_to(ROOT)))}</code></p>
      <p>Las imagenes V4 se importan desde ComfyUI a <code>public/landing-media/landing-*-v4.webp</code></p>
    </section>
    {''.join(sections)}
    <section class="gallery-section">
      <h2>Todas las imagenes V4 disponibles</h2>
      <div class="thumb-grid">{v4_gallery if v4_gallery else '<div class="missing-image">No V4 images imported yet. Run render + import pipeline.</div>'}</div>
    </section>
    <section class="gallery-section">
      <h2>Todas las imagenes V3 (referencia)</h2>
      <div class="thumb-grid">{v3_gallery if v3_gallery else '<div class="missing-image">No V3 images found.</div>'}</div>
    </section>
  </div>
</body>
</html>
"""
    return html_doc


def main() -> int:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    HTML_PATH.write_text(build_review_html(), encoding="utf-8")
    print(f"V4 Semantic review: {HTML_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
