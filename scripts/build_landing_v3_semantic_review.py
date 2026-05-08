#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BRIGHT_PROMPTS_PATH = ROOT / "src/comfyui_workflows/landing_semantic_v3/landing_semantic_prompts_v3_bright.json"
STRICT_PROMPTS_PATH = ROOT / "src/comfyui_workflows/landing_semantic_v3/landing_semantic_prompts_v3_strict.json"
BASE_PROMPTS_PATH = ROOT / "src/comfyui_workflows/landing_semantic_v3/landing_semantic_prompts_v3.json"
MEDIA_DIR = ROOT / "src_frontend" / "public" / "landing-media"
CANDIDATES_DIR = MEDIA_DIR / "candidates"
GENERATED_MANIFEST_PATH = MEDIA_DIR / "_landing_v3_generated_manifest.txt"
REVIEW_DIR = ROOT / ".tmp" / "landing_comfyui_v3" / "review"
HTML_PATH = REVIEW_DIR / "landing_v3_semantic_review.html"
DECISIONS_TEMPLATE_PATH = REVIEW_DIR / "landing_v3_semantic_decisions.template.json"


LANDING_TEXT_MAP: dict[str, dict[str, Any]] = {
    "landing-hero-main-v3": {
        "section": "Hero / CID",
        "title": "CID como sistema operativo de produccion",
        "text_lines": [
            "AILinkCinema combina creatividad visual, lienzo colaborativo e inteligencia artificial con un sistema real de produccion audiovisual.",
            "Desde la idea inicial hasta la entrega final, CID conecta guion, storyboard, planificacion, doblaje, sonido, VFX, montaje y distribucion en un mismo flujo de trabajo.",
            "CID interpreta el texto, estructura prompts coherentes y mantiene continuidad visual.",
        ],
    },
    "landing-problem-fragmented-v3": {
        "section": "Problema",
        "title": "La produccion sigue fragmentada",
        "text_lines": [
            "Guion, storyboard, produccion y post suelen operar en entornos separados. Cada fase pierde contexto de la anterior.",
            "Las herramientas de IA aparecen cada semana, pero ninguna esta disenada para integrarse en un flujo de produccion real.",
            "Sin trazabilidad, versionado ni supervision por departamento, las decisiones creativas se vuelven dificiles de gestionar.",
        ],
    },
    "landing-ai-reasoning-v3": {
        "section": "Analisis de guion",
        "title": "La IA razona antes de generar",
        "text_lines": [
            "Analiza el guion, identifica personajes, localizaciones y desglose tecnico. Recomienda planos y encuadres.",
            "Desglose tecnico de guion para produccion, con analisis por secuencias, personajes, localizaciones y necesidades reales de rodaje.",
            "La IA estructura, razona y recomienda.",
        ],
    },
    "landing-comfyui-generation-v3": {
        "section": "ComfyUI / generacion",
        "title": "Generacion visual controlada",
        "text_lines": [
            "Workflows de Flux/SDXL para storyboard, concept art y previz. Control de estilo, iluminacion y atmosfera.",
            "CID prepara el prompt, ComfyUI genera el frame y el sistema valida coherencia antes de seguir.",
            "No es una imagen suelta: forma parte del pipeline creativo y tecnico.",
        ],
    },
    "landing-cid-orchestration-v3": {
        "section": "Pipeline Builder / CID",
        "title": "CID orquesta todo el flujo",
        "text_lines": [
            "Pipeline completo: guion -> analisis -> prompt visual -> generacion -> revision -> entrega. Trazabilidad total.",
            "CID conecta guion, analisis, storyboard, concept art y delivery en un mismo flujo.",
            "El sistema que conecta la parte creativa con todos los departamentos de una produccion audiovisual.",
        ],
    },
    "landing-storyboard-preview-v3": {
        "section": "Storyboard / previsualizacion",
        "title": "Continuidad por escenas",
        "text_lines": [
            "Construye tu storyboard escena por escena. Cada plano mantiene coherencia narrativa, direccion de arte y continuidad visual.",
            "Storyboard y previz para alinear secuencias, puesta en escena y referencias visuales de produccion.",
            "Trabaja por escenas. Manten la continuidad visual.",
        ],
    },
    "landing-concept-keyvisual-v3": {
        "section": "Moodboards / Key Visual",
        "title": "Direccion artistica y material vendible",
        "text_lines": [
            "Construye referencias visuales por escena, personaje y atmosfera. Consolida la direccion artistica antes del rodaje.",
            "Convertir guion, concepto y propuesta visual en material claro para presentar y alinear.",
            "Look references, storyboard premium y pitch support.",
        ],
    },
    "landing-producers-studios-v3": {
        "section": "Productoras y estudios",
        "title": "Colaboracion real de produccion",
        "text_lines": [
            "Para equipos que necesitan ordenar desarrollo, operativa, materiales y control de proyecto en un mismo entorno.",
            "Disenado para productoras, directores y equipos tecnicos que necesitan un sistema, no solo herramientas sueltas.",
            "Director, productor y equipo pueden revisar, comentar y aprobar versiones.",
        ],
    },
    "landing-professional-differential-v3": {
        "section": "Diferencial profesional",
        "title": "Trazabilidad y supervision",
        "text_lines": [
            "Cada decision creativa, cada version y cada aprobacion quedan registradas.",
            "La IA acelera, pero las decisiones de calidad y entrega permanecen controladas por el director, el productor y el equipo tecnico.",
            "CID organiza, conecta y controla todo el flujo de produccion audiovisual.",
        ],
    },
    "landing-delivery-final-v3": {
        "section": "Post / Delivery",
        "title": "Cierre profesional y handoff",
        "text_lines": [
            "Para areas que necesitan trazabilidad, QC y continuidad desde el origen hasta la entrega final.",
            "Entrar en fases avanzadas con mas control sobre voz, QC, stems, trazabilidad y compliance.",
            "Validamos, revisamos y entregamos. Handoff limpio para cada siguiente fase.",
        ],
    },
}

QUALITY_FLAGS = {
    "landing-hero-main-v3": "TOO ABSTRACT",
    "landing-problem-fragmented-v3": "GOOD CANDIDATE",
    "landing-ai-reasoning-v3": "NEEDS REGEN",
    "landing-comfyui-generation-v3": "NEEDS REGEN",
    "landing-cid-orchestration-v3": "TOO ABSTRACT",
    "landing-storyboard-preview-v3": "TOO ABSTRACT",
    "landing-concept-keyvisual-v3": "NEEDS REGEN",
    "landing-producers-studios-v3": "GOOD CANDIDATE",
    "landing-professional-differential-v3": "NEEDS REGEN",
    "landing-delivery-final-v3": "TOO DARK",
}


def load_prompt_pack() -> dict[str, Any]:
    for path in (BRIGHT_PROMPTS_PATH, STRICT_PROMPTS_PATH, BASE_PROMPTS_PATH):
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["_source_path"] = str(path.relative_to(ROOT)).replace("\\", "/")
            return payload
    raise FileNotFoundError("No landing semantic prompt pack found")


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


def load_candidates(suffix: str) -> dict[str, list[Path]]:
    grouped: dict[str, list[Path]] = {}
    if not CANDIDATES_DIR.exists():
        return grouped
    for path in sorted(CANDIDATES_DIR.glob(f"candidate-*-{suffix}-*.webp")):
        name = path.name
        image_key = name[len("candidate-"):].split(f"-{suffix}-")[0]
        grouped.setdefault(image_key, []).append(path)
    return grouped


def build_decisions_template(items: list[dict[str, Any]]) -> None:
    payload = {
        "status": "draft",
        "items": [
            {
                "image_key": item["image_key"],
                "current_file": item["image_file_name"],
                "decision": "REVIEW",
                "approved": False,
                "remap_to_file": None,
                "regenerate": False,
                "notes": "",
            }
            for item in items
        ],
    }
    DECISIONS_TEMPLATE_PATH.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def render_text_block(lines: list[str]) -> str:
    return "".join(f"<li>{escape(line)}</li>" for line in lines)


def render_candidate_gallery(paths: list[Path], empty_label: str) -> str:
    if not paths:
        return f'<div class="empty-box">{escape(empty_label)}</div>'
    cards = []
    for path in paths:
        cards.append(
            "<figure class=\"candidate-card\">"
            f"<img src=\"{escape(rel_asset(path))}\" alt=\"{escape(path.name)}\">"
            f"<figcaption>{escape(path.name)}</figcaption>"
            "</figure>"
        )
    return "<div class=\"candidate-grid\">" + "".join(cards) + "</div>"


def render_all_v3_gallery(paths: list[Path], title: str) -> str:
    cards = []
    for path in paths:
        cards.append(
            "<figure class=\"thumb-card\">"
            f"<img src=\"{escape(rel_asset(path))}\" alt=\"{escape(path.name)}\">"
            f"<figcaption>{escape(path.name)}</figcaption>"
            "</figure>"
        )
    content = "<div class=\"thumb-grid\">" + "".join(cards) + "</div>" if cards else '<div class="empty-box">No images found.</div>'
    return f"<section class=\"gallery-section\"><h2>{escape(title)}</h2>{content}</section>"


def quality_class(flag: str) -> str:
    return {
        "TOO DARK": "flag-dark",
        "TOO ABSTRACT": "flag-abstract",
        "GOOD CANDIDATE": "flag-good",
        "NEEDS REGEN": "flag-regen",
    }.get(flag, "flag-neutral")


def build_review_html() -> str:
    prompt_pack = load_prompt_pack()
    items = prompt_pack.get("items", [])
    manifest = parse_generated_manifest()
    strict_candidates = load_candidates("strict")
    bright_candidates = load_candidates("bright")
    available_v3 = sorted(MEDIA_DIR.glob("landing-*-v3.webp"))
    all_strict_paths = sorted(CANDIDATES_DIR.glob("candidate-*-strict-*.webp")) if CANDIDATES_DIR.exists() else []
    all_bright_paths = sorted(CANDIDATES_DIR.glob("candidate-*-bright-*.webp")) if CANDIDATES_DIR.exists() else []

    build_decisions_template(items)

    sections: list[str] = []
    for index, item in enumerate(items, start=1):
        image_key = item["image_key"]
        current_path = MEDIA_DIR / item["image_file_name"]
        current_src = rel_asset(current_path) if current_path.exists() else ""
        landing_text = LANDING_TEXT_MAP.get(image_key, {})
        manifest_row = manifest.get(image_key, {})
        strict_paths = strict_candidates.get(image_key, [])
        bright_paths = bright_candidates.get(image_key, [])
        flag = QUALITY_FLAGS.get(image_key, "NEEDS REGEN")
        decision_stub = "APPROVE: false\nREMAP_TO: \nREGENERATE: false\nNOTES: \n"

        current_visual = (
            f"<img class=\"hero-image\" src=\"{escape(current_src)}\" alt=\"{escape(item['image_file_name'])}\">"
            if current_src
            else '<div class="missing-image">Current assigned image not found.</div>'
        )
        manifest_html = (
            f"<div class=\"manifest-box\">Manifest: {escape(manifest_row.get('raw', 'not found'))}</div>"
            if manifest_row
            else '<div class="manifest-box">Manifest: not found</div>'
        )

        sections.append(
            "<section class=\"review-card\">"
            f"<div class=\"review-index\">Block {index:02d}</div>"
            f"<div class=\"quality-flag {quality_class(flag)}\">{escape(flag)}</div>"
            f"<h2>{escape(item['block_label'])}</h2>"
            "<div class=\"review-grid\">"
            "<div class=\"visual-column\">"
            f"{current_visual}"
            f"<div class=\"file-chip\">Current file: {escape(item['image_file_name'])}</div>"
            f"{manifest_html}"
            "<div class=\"candidate-group\"><h3>Strict candidates</h3>"
            f"{render_candidate_gallery(strict_paths, 'No strict candidates available yet.')}"
            "</div>"
            "<div class=\"candidate-group\"><h3>Bright candidates</h3>"
            f"{render_candidate_gallery(bright_paths, 'No bright candidates available yet.')}"
            "</div>"
            "</div>"
            "<div class=\"text-column\">"
            f"<div class=\"meta-kicker\">{escape(landing_text.get('section', 'Landing'))}</div>"
            f"<h3>{escape(landing_text.get('title', item.get('landing_copy_focus', 'Landing visual')))}</h3>"
            "<div class=\"info-block\"><strong>Texto del bloque</strong><ul>"
            f"{render_text_block(list(landing_text.get('text_lines', [item.get('landing_copy_focus', '')])))}"
            "</ul></div>"
            f"<div class=\"info-block\"><strong>Visual intent</strong><p>{escape(item.get('visual_intent') or item.get('image_intent', ''))}</p></div>"
            f"<div class=\"info-block\"><strong>Semantic focus</strong><p>{escape(item.get('semantic_focus', ''))}</p></div>"
            f"<div class=\"info-block\"><strong>Composition notes</strong><p>{escape(item.get('composition_notes', ''))}</p></div>"
            f"<div class=\"info-block\"><strong>Lighting notes</strong><p>{escape(item.get('lighting_notes', ''))}</p></div>"
            f"<div class=\"info-block\"><strong>Color notes</strong><p>{escape(item.get('color_notes', ''))}</p></div>"
            f"<div class=\"info-block\"><strong>Prompt usado</strong><pre>{escape(item.get('image_prompt', ''))}</pre></div>"
            "<div class=\"info-block checklist\"><strong>Checklist de QA</strong>"
            "<ul>"
            "<li>[ ] Claridad</li>"
            "<li>[ ] Vida</li>"
            "<li>[ ] Coherencia con el texto</li>"
            "<li>[ ] Elegancia premium</li>"
            "<li>[ ] Legibilidad web</li>"
            "<li>[ ] Potencial para video</li>"
            "</ul></div>"
            "<div class=\"info-block\"><strong>Decision manual</strong>"
            f"<textarea>{escape(decision_stub)}</textarea>"
            "</div>"
            "</div>"
            "</div>"
            "</section>"
        )

    html_doc = f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Landing V3 Semantic Review</title>
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
    .flag-abstract {{ background: rgba(255,184,107,0.12); color: var(--warning); border-color: rgba(255,184,107,0.26); }}
    .flag-good {{ background: rgba(127,224,160,0.12); color: var(--good); border-color: rgba(127,224,160,0.26); }}
    .flag-regen {{ background: rgba(255,125,125,0.12); color: var(--regen); border-color: rgba(255,125,125,0.26); }}
    h2 {{ margin: 14px 0 18px; font-size: 30px; line-height: 1.1; padding-right: 180px; }}
    h3 {{ margin: 0 0 10px; font-size: 18px; }}
    .review-grid {{ display: grid; grid-template-columns: minmax(420px, 1fr) minmax(380px, 0.95fr); gap: 22px; align-items: start; }}
    .visual-column, .text-column {{ display: flex; flex-direction: column; gap: 14px; }}
    .hero-image, .thumb-card img, .candidate-card img {{ width: 100%; display: block; border-radius: 18px; border: 1px solid var(--line); background: #0a1016; }}
    .hero-image {{ min-height: 280px; object-fit: cover; }}
    .file-chip {{ display: inline-block; padding: 8px 12px; border-radius: 999px; background: rgba(255,255,255,0.05); color: var(--muted); font-size: 13px; }}
    .manifest-box, .empty-box, .missing-image {{ padding: 14px; border-radius: 16px; border: 1px solid var(--line); background: var(--panel-2); color: var(--muted); line-height: 1.5; }}
    .missing-image {{ color: var(--danger); min-height: 280px; display: flex; align-items: center; justify-content: center; text-align: center; }}
    .meta-kicker {{ color: var(--amber); font-size: 12px; letter-spacing: 0.16em; text-transform: uppercase; }}
    .info-block {{ padding: 16px; border-radius: 18px; border: 1px solid var(--line); background: rgba(255,255,255,0.03); }}
    .info-block strong {{ display: block; margin-bottom: 10px; color: var(--text); }}
    .info-block p, .info-block li {{ margin: 0; color: var(--muted); line-height: 1.6; }}
    .info-block ul {{ margin: 0; padding-left: 18px; display: grid; gap: 8px; }}
    pre {{ margin: 0; white-space: pre-wrap; word-break: break-word; color: #d6e1ed; font-size: 13px; line-height: 1.55; }}
    textarea {{ width: 100%; min-height: 130px; resize: vertical; border-radius: 14px; border: 1px solid var(--line); background: #0b1117; color: var(--text); padding: 14px; font: 13px/1.5 monospace; }}
    .candidate-group {{ display: flex; flex-direction: column; gap: 10px; }}
    .candidate-grid, .thumb-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 14px; }}
    .candidate-card, .thumb-card {{ margin: 0; padding: 12px; border: 1px solid var(--line); border-radius: 18px; background: rgba(255,255,255,0.03); }}
    figcaption {{ margin-top: 8px; font-size: 12px; color: var(--muted); line-height: 1.4; word-break: break-word; }}
    .gallery-section {{ margin-top: 28px; padding: 22px; border: 1px solid var(--line); border-radius: 28px; background: rgba(16,22,29,0.92); }}
    .gallery-section h2 {{ margin-top: 0; padding-right: 0; }}
    @media (max-width: 980px) {{
      .review-grid {{ grid-template-columns: 1fr; }}
      h2 {{ padding-right: 0; }}
      .quality-flag {{ position: static; margin-top: 12px; display: inline-block; }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <section class="intro">
      <h1>Landing V3 semantic review</h1>
      <p>Revision visual-semantica para validar claridad, vida, coherencia con el texto y potencial de video antes de aplicar referencias definitivas.</p>
      <p>Prompt pack fuente: <code>{escape(prompt_pack.get('_source_path', 'unknown'))}</code></p>
      <p>Edita manualmente <code>{escape(os.path.relpath(DECISIONS_TEMPLATE_PATH, ROOT).replace(os.sep, '/'))}</code> y usa este HTML como hoja de QA.</p>
    </section>
    {''.join(sections)}
    {render_all_v3_gallery(available_v3, 'Todas las imagenes V3 disponibles')}
    {render_all_v3_gallery(all_strict_paths, 'Todos los candidatos strict disponibles')}
    {render_all_v3_gallery(all_bright_paths, 'Todos los candidatos bright disponibles')}
  </div>
</body>
</html>
"""
    return html_doc


def main() -> int:
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    HTML_PATH.write_text(build_review_html(), encoding="utf-8")
    print(f"Semantic review written to {HTML_PATH.relative_to(ROOT)}")
    print(f"Decisions template written to {DECISIONS_TEMPLATE_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
