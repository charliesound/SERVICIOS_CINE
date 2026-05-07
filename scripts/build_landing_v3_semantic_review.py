#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROMPTS_PATH = ROOT / "src/comfyui_workflows/landing_semantic_v3/landing_semantic_prompts_v3.json"
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
            "CID conecta el lienzo creativo con guion, desglose, storyboard, planificacion, produccion, doblaje, sonido, VFX, montaje, promocion y entrega en un flujo real.",
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
        "section": "Pipeline Builder / IA",
        "title": "La IA razona antes de generar",
        "text_lines": [
            "Analiza el guion, identifica personajes, localizaciones y desglose tecnico. Recomienda planos y encuadres.",
            "Desglose tecnico de guion para produccion, con analisis por secuencias, personajes, localizaciones y necesidades reales de rodaje.",
            "La IA estructura, razona y recomienda.",
        ],
    },
    "landing-comfyui-generation-v3": {
        "section": "Pipeline Builder / ComfyUI",
        "title": "ComfyUI como motor visual controlado",
        "text_lines": [
            "Workflows de Flux/SDXL para storyboard, concept art y previz. Control de estilo, iluminacion y atmosfera.",
            "ComfyUI genera la imagen.",
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
        "section": "Storyboard / Previsualizacion",
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
        "section": "Audiencia / Productoras y estudios",
        "title": "Colaboracion real de produccion",
        "text_lines": [
            "Para equipos que necesitan ordenar desarrollo, operativa, materiales y control de proyecto en un mismo entorno.",
            "Disenado para productoras, directores y equipos tecnicos que necesitan un sistema, no solo herramientas sueltas.",
            "Para quienes trabajan con fases, aprobaciones, dependencias y entregables reales.",
        ],
    },
    "landing-professional-differential-v3": {
        "section": "Diferencial profesional",
        "title": "Trazabilidad y supervision",
        "text_lines": [
            "Cada decision creativa, cada version y cada aprobacion quedan registradas. El equipo sabe que se decidio, cuando y por que.",
            "La IA acelera, pero las decisiones de calidad y entrega permanecen controladas por el director, el productor y el equipo tecnico.",
            "La mayoria de herramientas de IA generan contenido. CID organiza, conecta y controla todo el flujo de produccion audiovisual.",
        ],
    },
    "landing-delivery-final-v3": {
        "section": "Post / Delivery",
        "title": "Cierre profesional y handoff",
        "text_lines": [
            "Para areas que necesitan trazabilidad, QC y continuidad desde el origen hasta la entrega final.",
            "Entrar en fases avanzadas con mas control sobre voz, QC, stems, trazabilidad y compliance.",
            "Validamos, revisamos y entregamos. Seguridad, legalidad, control de cambios y handoff limpio para cada siguiente fase.",
        ],
    },
}


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


def load_candidates() -> dict[str, list[Path]]:
    grouped: dict[str, list[Path]] = {}
    if not CANDIDATES_DIR.exists():
        return grouped
    for path in sorted(CANDIDATES_DIR.glob("candidate-*-strict-*.webp")):
        name = path.name
        if not name.startswith("candidate-"):
            continue
        image_key = name[len("candidate-"):].split("-strict-")[0]
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


def render_candidate_gallery(paths: list[Path]) -> str:
    if not paths:
        return '<div class="empty-box">No strict candidates available yet.</div>'
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


def build_review_html() -> str:
    prompt_pack = load_prompt_pack()
    items = prompt_pack.get("items", [])
    manifest = parse_generated_manifest()
    candidates = load_candidates()
    available_v3 = sorted(MEDIA_DIR.glob("landing-*-v3.webp"))
    available_candidate_paths = sorted(CANDIDATES_DIR.glob("candidate-*-strict-*.webp")) if CANDIDATES_DIR.exists() else []

    build_decisions_template(items)

    sections: list[str] = []
    for index, item in enumerate(items, start=1):
        image_key = item["image_key"]
        current_path = MEDIA_DIR / item["image_file_name"]
        current_src = rel_asset(current_path) if current_path.exists() else ""
        landing_text = LANDING_TEXT_MAP.get(image_key, {})
        manifest_row = manifest.get(image_key, {})
        candidate_paths = candidates.get(image_key, [])
        decision_stub = (
            f"APPROVE: false\n"
            f"REMAP_TO: \n"
            f"REGENERATE: false\n"
            f"NOTES: \n"
        )

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
            f"<h2>{escape(item['block_label'])}</h2>"
            "<div class=\"review-grid\">"
            "<div class=\"visual-column\">"
            f"{current_visual}"
            f"<div class=\"file-chip\">Current file: {escape(item['image_file_name'])}</div>"
            f"{manifest_html}"
            "<h3>Strict candidates available</h3>"
            f"{render_candidate_gallery(candidate_paths)}"
            "</div>"
            "<div class=\"text-column\">"
            f"<div class=\"meta-kicker\">{escape(landing_text.get('section', 'Landing'))}</div>"
            f"<h3>{escape(landing_text.get('title', item['landing_copy_focus']))}</h3>"
            "<div class=\"info-block\"><strong>Texto real de landing</strong><ul>"
            f"{render_text_block(list(landing_text.get('text_lines', [item['landing_copy_focus']])))}"
            "</ul></div>"
            f"<div class=\"info-block\"><strong>Visual intent</strong><p>{escape(item['image_intent'])}</p></div>"
            f"<div class=\"info-block\"><strong>Prompt usado</strong><pre>{escape(item['image_prompt'])}</pre></div>"
            "<div class=\"info-block checklist\"><strong>Checklist</strong>"
            "<ul>"
            "<li>[ ] Representa el texto</li>"
            "<li>[ ] Se entiende sin leer el prompt</li>"
            "<li>[ ] Tiene estetica premium cinematografica</li>"
            "<li>[ ] Encaja con las demas</li>"
            "<li>[ ] Evita texto, logos o watermarks</li>"
            "<li>[ ] Sirve como imagen web</li>"
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
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: Arial, sans-serif; background: radial-gradient(circle at top, #15202d 0%, var(--bg) 48%); color: var(--text); }}
    .shell {{ width: min(1440px, calc(100% - 32px)); margin: 0 auto; padding: 28px 0 64px; }}
    .intro {{ margin-bottom: 28px; padding: 24px; border: 1px solid var(--line); border-radius: 24px; background: rgba(16,22,29,0.92); }}
    .intro h1 {{ margin: 0 0 12px; font-size: 34px; }}
    .intro p {{ margin: 0 0 10px; color: var(--muted); line-height: 1.6; }}
    .intro code {{ color: var(--amber); }}
    .review-card {{ margin-bottom: 22px; padding: 22px; border: 1px solid var(--line); border-radius: 28px; background: linear-gradient(180deg, rgba(17,24,33,0.98), rgba(10,14,19,0.98)); box-shadow: 0 24px 80px rgba(0,0,0,0.22); }}
    .review-index {{ display: inline-block; padding: 6px 10px; border-radius: 999px; background: rgba(241,178,74,0.12); color: var(--amber); font-size: 12px; letter-spacing: 0.12em; text-transform: uppercase; }}
    h2 {{ margin: 14px 0 18px; font-size: 30px; line-height: 1.1; }}
    h3 {{ margin: 0 0 10px; font-size: 18px; }}
    .review-grid {{ display: grid; grid-template-columns: minmax(420px, 1fr) minmax(360px, 0.92fr); gap: 22px; align-items: start; }}
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
    .candidate-grid, .thumb-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 14px; }}
    .candidate-card, .thumb-card {{ margin: 0; padding: 12px; border: 1px solid var(--line); border-radius: 18px; background: rgba(255,255,255,0.03); }}
    figcaption {{ margin-top: 8px; font-size: 12px; color: var(--muted); line-height: 1.4; word-break: break-word; }}
    .gallery-section {{ margin-top: 28px; padding: 22px; border: 1px solid var(--line); border-radius: 28px; background: rgba(16,22,29,0.92); }}
    .gallery-section h2 {{ margin-top: 0; }}
    @media (max-width: 980px) {{
      .review-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="shell">
    <section class="intro">
      <h1>Landing V3 semantic review</h1>
      <p>Revision para validar si cada imagen realmente comunica el texto de su bloque antes de aplicar referencias definitivas.</p>
      <p>Edita manualmente <code>{escape(os.path.relpath(DECISIONS_TEMPLATE_PATH, ROOT).replace(os.sep, '/'))}</code> y usa este HTML como hoja de QA visual-semantic.</p>
    </section>
    {''.join(sections)}
    {render_all_v3_gallery(available_v3, 'Todas las imagenes V3 disponibles')}
    {render_all_v3_gallery(available_candidate_paths, 'Todos los candidatos strict disponibles')}
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
