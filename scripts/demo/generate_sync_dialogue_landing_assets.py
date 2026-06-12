#!/usr/bin/env python3
"""Generate a controlled visual assets pack for the AILink Sync Dialogue landing.

Generates 6 PNG images, README.md and assets_manifest.json from the
controlled-metadata demo fixture so no real media is ever touched.
"""

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DEMO_SCRIPT = "scripts/demo/create_sync_dialogue_metadata_demo.py"

EXPECTED_PNGS = (
    "hero-report-mockup.png",
    "report-summary.png",
    "match-suggestions-table.png",
    "media-files-table.png",
    "privacy-local-first.png",
    "linkedin-beta-card.png",
)

FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_MONO_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

BKG = "#1a1a2e"
BKG_CARD = "#232338"
TEXT = "#e0e0e0"
TEXT_DIM = "#8a8a8a"
ACCENT = "#4a90d9"
ACCENT_GREEN = "#3a7d4f"
ALERT = "#d4a017"
WHITE = "#f5f5f5"
BLACK = "#0f0f1a"
BORDER = "#2d2d4a"
TABLE_HEADER = "#232338"
TABLE_ALT = "#1f1f35"
HIGH_BADGE = "#3a7d4f"
MEDIUM_BADGE = "#d4a017"
LOW_BADGE = "#b54747"

W = 1200
H = 800


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_SANS_BOLD if bold else FONT_SANS
    return ImageFont.truetype(path, size)


def _load_mono(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_MONO, size)


def _rounded_rect(draw, xy, radius, fill, outline=None):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline)


def _draw_table_row(draw, x, y, cols, widths, font, fill_row, align_right=None):
    align_right = align_right or set()
    cx = x
    for i, (col, w) in enumerate(zip(cols, widths)):
        align = "right" if i in align_right else "left"
        if align == "right":
            tx = cx + w - 8
            draw.text((tx, y), str(col), fill=TEXT, font=font, anchor="rt")
        else:
            draw.text((cx + 8, y), str(col), fill=TEXT, font=font)
        cx += w


def _confidence_text(val: str) -> str:
    return val


def _read_demo_data(demo_dir: Path):
    """Return (summary_dict, media_rows, match_rows) from a finished demo dir."""
    with open(demo_dir / "scan_result.json") as f:
        scan = json.load(f)
    media = scan.get("media_files", [])
    matches = scan.get("match_suggestions", [])
    summary = scan.get("summary", {})
    return summary, media, matches


# ---------------------------------------------------------------------------
# Image builders
# ---------------------------------------------------------------------------

def build_hero_report(output_path: Path, summary, matches, media):
    img = Image.new("RGB", (W, H), BKG)
    draw = ImageDraw.Draw(img)
    font_h1 = _load_font(36, bold=True)
    font_h2 = _load_font(22, bold=True)
    font_body = _load_font(16)
    font_small = _load_font(13)
    font_badge = _load_font(14, bold=True)
    font_micro = _load_font(11)

    # Title bar
    _rounded_rect(draw, (40, 30, W - 40, 100), 10, BKG_CARD)
    draw.text((60, 42), "AILink Sync Dialogue — Ingest Report", fill=WHITE, font=font_h1)
    draw.text((60, 78), "Demo controlada con metadata generada", fill=TEXT_DIM, font=font_small)

    # Summary cards
    cards_data = [
        ("Vídeos", str(summary.get("video_count", 0))),
        ("Audios", str(summary.get("audio_count", 0))),
        ("Matches", str(summary.get("match_suggestions_count", 0) or len(matches))),
        ("Confianza alta", str(sum(1 for m in matches if m.get("confidence") == "high"))),
    ]
    cw = (W - 120) // 4
    for i, (label, val) in enumerate(cards_data):
        cx = 50 + i * (cw + 10)
        _rounded_rect(draw, (cx, 120, cx + cw - 10, 200), 8, BKG_CARD, BORDER)
        draw.text((cx + 16, 130), label, fill=TEXT_DIM, font=font_small)
        draw.text((cx + 16, 152), val, fill=WHITE, font=font_h2)

    # Match suggestions table header
    draw.text((50, 230), "Match suggestions", fill=WHITE, font=font_h2)
    match_cols = ["vídeo", "audio", "conf.", "score", "estrategia"]
    match_widths = [240, 240, 80, 80, 200]
    mx = 50
    my = 270
    _draw_table_row(draw, mx, my, match_cols, match_widths, font_small, ACCENT)
    draw.rectangle((mx, my - 2, mx + sum(match_widths), my + 22), fill=ACCENT, width=0)
    _draw_table_row(draw, mx, my, match_cols, match_widths, _load_font(12, bold=True), WHITE)

    # Table rows
    font_tr = _load_font(13)
    for idx, m in enumerate(matches[:3]):
        ry = my + 28 + idx * 28
        bg = TABLE_ALT if idx % 2 else BKG_CARD
        draw.rectangle((mx, ry, mx + sum(match_widths), ry + 24), fill=bg)
        conf = m.get("confidence", "low")
        conf_color = {"high": HIGH_BADGE, "medium": MEDIUM_BADGE, "low": LOW_BADGE}.get(conf, TEXT_DIM)
        vals = [
            m.get("video_relative_path", "").split("/")[-1],
            m.get("audio_relative_path", "").split("/")[-1],
            conf.upper(),
            f"{m.get('score', 0):.2f}",
            m.get("strategy", ""),
        ]
        _draw_table_row(draw, mx, ry + 2, vals, match_widths, font_tr, bg)

    # Privacy microtext
    micro = "Demo local con metadata controlada  |  El material no sale del disco del cliente"
    draw.text((W // 2, H - 30), micro, fill=TEXT_DIM, font=font_micro, anchor="mb")

    img.save(output_path, "PNG")


def build_report_summary(output_path: Path, summary, media):
    img = Image.new("RGB", (800, 500), BKG)
    draw = ImageDraw.Draw(img)
    font_h1 = _load_font(28, bold=True)
    font_h2 = _load_font(18, bold=True)
    font_body = _load_font(15)
    font_small = _load_font(13)

    _rounded_rect(draw, (30, 30, 770, 470), 12, BKG_CARD, BORDER)

    draw.text((50, 48), "Resumen del reporte", fill=WHITE, font=font_h1)
    draw.text((50, 84), "Demo controlada  |  AILink Sync Dialogue", fill=TEXT_DIM, font=font_small)

    rows_data = [
        ("Total archivos", str(summary.get("total_files", 0))),
        ("Vídeos detectados", str(summary.get("video_count", 0))),
        ("Audios detectados", str(summary.get("audio_count", 0))),
        ("Sin soporte", str(summary.get("unsupported_count", 0))),
        ("Sugerencias de match", str(summary.get("match_suggestions_count", 0))),
    ]
    y = 120
    for label, val in rows_data:
        draw.text((60, y), label, fill=TEXT, font=font_body)
        draw.text((520, y), val, fill=ACCENT, font=font_body, anchor="rt")
        y += 36

    # Divider
    y += 8
    draw.line((50, y, 750, y), fill=BORDER, width=1)

    y += 20
    draw.text((60, y), "Formato de salida", fill=TEXT_DIM, font=font_small)
    formats = ["report.html", "media_files.csv", "match_suggestions.csv", "scan_result.json"]
    fx = 60
    for f in formats:
        _rounded_rect(draw, (fx, y + 24, fx + 160, y + 56), 6, TABLE_ALT, BORDER)
        draw.text((fx + 12, y + 32), f, fill=TEXT, font=_load_font(13))
        fx += 172

    img.save(output_path, "PNG")


def build_match_suggestions_table(output_path: Path, matches):
    img = Image.new("RGB", (800, 600), BKG)
    draw = ImageDraw.Draw(img)
    font_h1 = _load_font(22, bold=True)
    font_header = _load_font(12, bold=True)
    font_row = _load_font(12)

    draw.text((40, 24), "Match suggestions — demo controlada", fill=WHITE, font=font_h1)

    headers = ["video_relative_path", "audio_relative_path", "confidence", "score",
               "strategy", "reasons", "duration_delta_seconds"]
    widths = [150, 150, 80, 60, 90, 120, 80]
    x0 = 30
    y0 = 70
    col_start = x0

    # Header
    draw.rectangle((x0, y0, x0 + sum(widths), y0 + 26), fill=ACCENT)
    _draw_table_row(draw, x0, y0 + 4, headers, widths, font_header, ACCENT)

    # Rows
    y_row = y0 + 30
    font_row = _load_font(11)
    for idx, m in enumerate(matches):
        bg = TABLE_ALT if idx % 2 else BKG_CARD
        draw.rectangle((x0, y_row, x0 + sum(widths), y_row + 24), fill=bg)

        conf = m.get("confidence", "low")
        vals = [
            m.get("video_relative_path", "").split("/")[-1],
            m.get("audio_relative_path", "").split("/")[-1],
            conf,
            f"{m.get('score', 0):.2f}",
            m.get("strategy", ""),
            "; ".join(m.get("reasons", []))[:22],
            f"{m.get('duration_delta_seconds', 0):.1f}",
        ]
        _draw_table_row(draw, x0, y_row + 2, vals, widths, font_row, bg)

        # Badge color
        conf_short = conf[:4].upper()
        c_color = {"high": HIGH_BADGE, "medi": MEDIUM_BADGE, "low": LOW_BADGE}.get(conf_short, TEXT_DIM)
        bx = x0 + sum(widths[:2]) + 8
        _rounded_rect(draw, (bx, y_row + 3, bx + 60, y_row + 21), 4, c_color)
        draw.text((bx + 30, y_row + 5), conf_short, fill=WHITE, font=_load_font(10, bold=True), anchor="mt")

        y_row += 28

    img.save(output_path, "PNG")


def build_media_files_table(output_path: Path, media):
    img = Image.new("RGB", (800, 600), BKG)
    draw = ImageDraw.Draw(img)
    font_h1 = _load_font(22, bold=True)
    font_header = _load_font(12, bold=True)
    font_row = _load_font(11)

    draw.text((40, 24), "Media files — inventario de escaneo", fill=WHITE, font=font_h1)

    headers = ["filename", "type", "duration", "codec", "timecode"]
    widths = [220, 80, 90, 120, 120]
    x0 = 30
    y0 = 70

    draw.rectangle((x0, y0, x0 + sum(widths), y0 + 26), fill=ACCENT)
    _draw_table_row(draw, x0, y0 + 4, headers, widths, font_header, ACCENT)

    y_row = y0 + 30
    for idx, m in enumerate(media):
        bg = TABLE_ALT if idx % 2 else BKG_CARD
        draw.rectangle((x0, y_row, x0 + sum(widths), y_row + 24), fill=bg)

        tc = m.get("timecode") or "—"
        vals = [
            m.get("filename", ""),
            m.get("kind", "").upper(),
            f"{m.get('duration_seconds', 0):.1f}s",
            m.get("codec_name", ""),
            tc,
        ]
        _draw_table_row(draw, x0, y_row + 2, vals, widths, font_row, bg)

        # Kind badge
        kind = m.get("kind", "")
        kx = x0 + widths[0] + 8
        k_color = ACCENT if kind == "video" else ACCENT_GREEN
        _rounded_rect(draw, (kx, y_row + 3, kx + 60, y_row + 21), 4, k_color)
        draw.text((kx + 30, y_row + 5), kind.upper(), fill=WHITE, font=_load_font(10, bold=True), anchor="mt")

        y_row += 28

    img.save(output_path, "PNG")


def build_privacy_local_first(output_path: Path):
    Wp, Hp = 800, 400
    img = Image.new("RGB", (Wp, Hp), BKG)
    draw = ImageDraw.Draw(img)
    font_h1 = _load_font(30, bold=True)
    font_body = _load_font(18)
    font_small = _load_font(14)

    _rounded_rect(draw, (40, 30, Wp - 40, Hp - 30), 16, BKG_CARD, BORDER)

    # Shield icon emulation with text
    draw.text((Wp // 2, 70), "Privacidad local", fill=WHITE, font=font_h1, anchor="mt")

    messages = [
        "El material no sale del disco del cliente.",
        "Sin nube en esta versión.",
        "Outputs generados localmente: reportes, CSVs y JSON.",
    ]
    y = 140
    for msg in messages:
        draw.text((Wp // 2, y), msg, fill=TEXT, font=font_body, anchor="mt")
        y += 40

    draw.line((Wp // 2 - 120, y, Wp // 2 + 120, y), fill=BORDER, width=1)
    y += 20

    detail = (
        "AILink Sync Dialogue trabaja completamente en local. "
        "No sube vídeo ni audio a servidores. "
        "Recomendado para material sensible o proyectos privados."
    )
    for line in textwrap.wrap(detail, width=60):
        draw.text((Wp // 2, y), line, fill=TEXT_DIM, font=font_small, anchor="mt")
        y += 24

    # Badge
    _rounded_rect(draw, (Wp // 2 - 100, Hp - 80, Wp // 2 + 100, Hp - 50), 8, ACCENT_GREEN)
    draw.text((Wp // 2, Hp - 76), "Local-First", fill=WHITE, font=_load_font(16, bold=True), anchor="mt")

    img.save(output_path, "PNG")


def build_linkedin_beta_card(output_path: Path, summary, matches):
    Wl, Hl = 1080, 1080
    img = Image.new("RGB", (Wl, Hl), BKG)
    draw = ImageDraw.Draw(img)
    font_brand = _load_font(24)
    font_h1 = _load_font(48, bold=True)
    font_body = _load_font(22)
    font_cta = _load_font(18, bold=True)
    font_small = _load_font(16)

    # Top bar
    _rounded_rect(draw, (60, 40, Wl - 60, 90), 8, BKG_CARD)
    draw.text((100, 52), "AILinkCinema  ·  AILink Sync Dialogue", fill=WHITE, font=font_brand)

    # Main message
    draw.text((Wl // 2, 260), "Beta privada", fill=ACCENT, font=font_h1, anchor="mt")
    draw.text((Wl // 2, 340), "Prepara vídeo y audio para montaje", fill=WHITE, font=_load_font(36, bold=True), anchor="mt")
    draw.text((Wl // 2, 400), "con una demo local y controlada.", fill=WHITE, font=_load_font(36, bold=True), anchor="mt")

    # Stats row
    stats = [
        (str(summary.get("video_count", 0)), "vídeos"),
        (str(summary.get("audio_count", 0)), "audios"),
        (str(len(matches)), "sugerencias"),
    ]
    sw = 200
    sx = (Wl - (len(stats) * sw + (len(stats) - 1) * 20)) // 2
    for i, (val, _label) in enumerate(stats):
        sx_i = sx + i * (sw + 20)
        _rounded_rect(draw, (sx_i, 500, sx_i + sw, 580), 10, BKG_CARD, BORDER)
        draw.text((sx_i + sw // 2, 520), val, fill=ACCENT, font=_load_font(32, bold=True), anchor="mt")
        draw.text((sx_i + sw // 2, 556), _label, fill=TEXT_DIM, font=_load_font(14), anchor="mt")

    # CTA
    _rounded_rect(draw, (Wl // 2 - 170, 680, Wl // 2 + 170, 750), 12, ACCENT)
    draw.text((Wl // 2, 700), "Solicita acceso beta", fill=WHITE, font=font_cta, anchor="mt")

    # Footer
    draw.text((Wl // 2, 840), "Escuelas, productoras y equipos de postproducción", fill=TEXT_DIM, font=_load_font(18), anchor="mt")
    draw.text((Wl // 2, 950), "Demo local con metadata controlada. Sin material real de cliente.", fill=TEXT_DIM, font=_load_font(14), anchor="mt")

    img.save(output_path, "PNG")


# ---------------------------------------------------------------------------
# Manifest & README
# ---------------------------------------------------------------------------

def _make_manifest(output_dir: Path, expected_pngs, has_media, has_matches):
    assets = []
    png_infos = {
        "hero-report-mockup.png": {
            "purpose": "Hero image for the landing page showing the report with match suggestions",
            "source": "Generated from create_sync_dialogue_metadata_demo.py controlled demo",
        },
        "report-summary.png": {
            "purpose": "Summary card showing file counts and output formats",
            "source": "Generated from create_sync_dialogue_metadata_demo.py summary data",
        },
        "match-suggestions-table.png": {
            "purpose": "Table of match suggestions with confidence, score, strategy and reasons",
            "source": "Generated from create_sync_dialogue_metadata_demo.py match suggestions",
        },
        "media-files-table.png": {
            "purpose": "Inventory table of detected video and audio files",
            "source": "Generated from create_sync_dialogue_metadata_demo.py media files",
        },
        "privacy-local-first.png": {
            "purpose": "Privacy-focused card stating local-first principles",
            "source": "Generated programmatically with static copy",
        },
        "linkedin-beta-card.png": {
            "purpose": "Square social media image for LinkedIn and Facebook beta announcement",
            "source": "Generated from demo summary data with beta messaging",
        },
    }
    for fname in expected_pngs:
        fp = output_dir / fname
        info = png_infos.get(fname, {"purpose": "", "source": ""})
        entry = {
            "file_name": fname,
            "purpose": info["purpose"],
            "width": 0,
            "height": 0,
            "source": info["source"],
            "public_safe": True,
            "notes": "No real media, no personal data, no client names. Controlled demo only.",
        }
        if fp.exists():
            try:
                with Image.open(fp) as im:
                    entry["width"], entry["height"] = im.size
            except Exception:
                pass
        assets.append(entry)
    return {"version": 1, "assets": assets}


def _make_readme(output_dir: Path, expected_pngs):
    lines = [
        "# AILink Sync Dialogue — Landing Visual Assets Pack",
        "",
        "Este paquete contiene los assets visuales generados para la landing de AILink Sync Dialogue.",
        "",
        "## Origen",
        "",
        "Todos los assets se generan a partir de la demo controlada de metadata:",
        "",
        "`scripts/demo/create_sync_dialogue_metadata_demo.py`",
        "",
        "No se ha utilizado material real de clientes, proyectos ni producciones.",
        "No se han subido archivos a ningún servidor.",
        "",
        "## Assets incluidos",
        "",
    ]
    descriptions = {
        "hero-report-mockup.png": "Imagen principal del hero de landing. Muestra el reporte HTML con resumen de conteos y tabla de match suggestions.",
        "report-summary.png": "Tarjeta de resumen con totales de vídeo/audio y formatos de salida.",
        "match-suggestions-table.png": "Tabla de sugerencias de sincronía con confianza, score y estrategia.",
        "media-files-table.png": "Inventario de archivos detectados con tipo, duración, codec y timecode.",
        "privacy-local-first.png": "Pieza visual sobre privacidad local: el material no sale del disco del cliente.",
        "linkedin-beta-card.png": "Imagen cuadrada para redes sociales (1080×1080) con CTA de beta privada.",
    }
    for fname in expected_pngs:
        desc = descriptions.get(fname, "")
        lines.append(f"- `{fname}`: {desc}" if desc else f"- `{fname}`")
    lines += [
        "",
        "## Cómo regenerar",
        "",
        "```bash",
        "cd /opt/SERVICIOS_CINE",
        "source .venv/bin/activate",
        "python scripts/demo/generate_sync_dialogue_landing_assets.py \\",
        "    --output-dir docs/product/assets/ailink_sync_dialogue \\",
        "    --force",
        "```",
        "",
        "## Privacidad",
        "",
        "Todos los assets usan exclusivamente metadata controlada y nombres de archivo genéricos.",
        "Ningún asset contiene:",
        "- Rutas de sistema personales",
        "- Nombres reales de clientes o producciones",
        "- Material audiovisual sensible",
        "- Emails o datos personales",
        "- Logos de terceros sin autorización",
        "",
        "## Uso previsto",
        "",
        "- Landing pública de AILink Sync Dialogue",
        "- Publicaciones en LinkedIn y Facebook",
        "- Presentaciones comerciales",
        "- Mockups básicos de producto",
        "",
    ]
    (output_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Generate landing visual assets for AILink Sync Dialogue"
    )
    p.add_argument(
        "--output-dir",
        required=True,
        help="Output directory for generated assets",
    )
    p.add_argument("--force", action="store_true", help="Overwrite existing files")
    p.add_argument("--quiet", action="store_true", help="Reduce output")
    return p.parse_args(argv)


def validate_output_dir(path: str):
    raw = path.strip()
    if not raw:
        sys.exit("Error: --output-dir cannot be empty")
    if raw == "/":
        sys.exit("Error: --output-dir cannot be root")
    if raw.startswith("/mnt/"):
        sys.exit("Error: --output-dir cannot be under /mnt/")
    if "\\" in raw:
        sys.exit("Error: Windows-style paths are not allowed")
    return raw


def main():
    args = parse_args()
    out_raw = validate_output_dir(args.output_dir)
    output_dir = Path(out_raw).resolve()

    # Run the controlled demo
    demo_dir = output_dir.parent / ".sync_demo_tmp"
    if args.force and demo_dir.exists():
        shutil.rmtree(demo_dir)
    if not demo_dir.exists():
        demo_dir.mkdir(parents=True)

    subprocess.run(
        [
            sys.executable, "scripts/demo/create_sync_dialogue_metadata_demo.py",
            "--output-dir", str(demo_dir),
            "--force",
            "--quiet",
        ],
        check=True,
        cwd=Path(__file__).resolve().parent.parent.parent,
    )

    summary, media, matches = _read_demo_data(demo_dir)

    if not args.quiet:
        print(f"Demo data loaded: {summary.get('video_count', 0)} videos, "
              f"{summary.get('audio_count', 0)} audios, {len(matches)} matches")

    # Create output directory
    if output_dir.exists():
        if args.force:
            for f in EXPECTED_PNGS:
                (output_dir / f).unlink(missing_ok=True)
        else:
            sys.exit(f"Error: {output_dir} exists. Use --force to overwrite.")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate PNG assets
    if not args.quiet:
        print(f"Generating assets in {output_dir} ...")

    builder_calls = [
        (build_hero_report, "hero-report-mockup.png", summary, matches, media),
        (build_report_summary, "report-summary.png", summary, media),
        (build_match_suggestions_table, "match-suggestions-table.png", matches),
        (build_media_files_table, "media-files-table.png", media),
        (build_privacy_local_first, "privacy-local-first.png"),
        (build_linkedin_beta_card, "linkedin-beta-card.png", summary, matches),
    ]
    for call in builder_calls:
        func = call[0]
        fname = call[1]
        func_args = call[2:]
        out_path = output_dir / fname
        func(out_path, *func_args)
        if not args.quiet:
            sz = out_path.stat().st_size
            print(f"  {fname}  ({sz:,} bytes)")

    # Generate README and manifest
    _make_readme(output_dir, EXPECTED_PNGS)
    manifest = _make_manifest(output_dir, EXPECTED_PNGS, bool(media), bool(matches))
    (output_dir / "assets_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    if not args.quiet:
        print(f"\nDone. {len(EXPECTED_PNGS)} assets generated.")
        print(f"README: {output_dir / 'README.md'}")
        print(f"Manifest: {output_dir / 'assets_manifest.json'}")

    # Cleanup demo temp
    if demo_dir.exists():
        shutil.rmtree(demo_dir)


if __name__ == "__main__":
    main()
