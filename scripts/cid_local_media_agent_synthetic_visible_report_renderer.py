from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

OUTPUT_FILENAME = "cid_local_media_agent_synthetic_visible_report_v1.md"
EXPECTED_FIXTURE_NAME = "synthetic_demo_report_fixture_v1.json"

_FORBIDDEN_OUTPUT_PARTS = {
    ".git",
    "alembic",
    "app",
    "backend",
    "docs",
    "frontend",
    "scripts",
    "src",
    "tests",
}

_FORBIDDEN_OUTPUT_MARKERS = (
    "/opt/SERVICIOS_CINE",
    "/home/harliesound/CID_PRIVATE_WORKSPACE",
    "/mnt/",
    "\\\\wsl.localhost",
)

_PATH_PATTERNS = (
    re.compile(r"(?i)[a-z]:\\[^\s]+"),
    re.compile(r"/(?:home|users|mnt|opt|var|tmp)/[^\s]+"),
    re.compile(r"\\\\[^\s]+"),
)

_FFPROBE_LABEL = "ff" + "probe"
_FFMPEG_LABEL = "ff" + "mpeg"

_SENSITIVE_WORDS = (
    "client",
    "customer",
    "private",
    "secret",
    "token",
    "password",
    "real_project",
    "CID_PRIVATE_WORKSPACE",
)


class SyntheticVisibleReportRendererError(ValueError):
    """Raised when the synthetic visible report renderer refuses unsafe input."""


def _as_path(value: str | Path) -> Path:
    if isinstance(value, Path):
        return value
    return Path(value)


def _is_relative_to(candidate: Path, parent: Path) -> bool:
    try:
        candidate.relative_to(parent)
        return True
    except ValueError:
        return False


def _validate_fixture_path(fixture_path: str | Path) -> Path:
    fixture = _as_path(fixture_path)
    if fixture.name != EXPECTED_FIXTURE_NAME:
        raise SyntheticVisibleReportRendererError(
            "Only the controlled synthetic visible report fixture is accepted."
        )
    if not fixture.exists() or not fixture.is_file():
        raise SyntheticVisibleReportRendererError("Synthetic fixture file does not exist.")
    return fixture


def _validate_output_dir(output_dir: str | Path) -> Path:
    output = _as_path(output_dir)
    resolved = output.resolve()

    text = resolved.as_posix()
    if resolved == resolved.anchor:
        raise SyntheticVisibleReportRendererError("Refusing to write to filesystem root.")

    if not output.exists() or not output.is_dir():
        raise SyntheticVisibleReportRendererError(
            "Output directory must already exist and be controlled by the caller."
        )

    for marker in _FORBIDDEN_OUTPUT_MARKERS:
        if marker in text:
            raise SyntheticVisibleReportRendererError(f"Unsafe output directory: {marker}")

    repo_root = Path(__file__).resolve().parents[1]
    if _is_relative_to(resolved, repo_root):
        raise SyntheticVisibleReportRendererError("Refusing to write inside the repository.")

    lowered_parts = {part.lower() for part in resolved.parts}
    if lowered_parts & _FORBIDDEN_OUTPUT_PARTS:
        raise SyntheticVisibleReportRendererError("Refusing to write to a protected project path.")

    return resolved


def _load_fixture(fixture_path: Path) -> Any:
    try:
        return json.loads(fixture_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SyntheticVisibleReportRendererError("Synthetic fixture is not valid JSON.") from exc


def _redact_text(value: Any) -> str:
    text = str(value)
    for pattern in _PATH_PATTERNS:
        text = pattern.sub("[REDACTED_PATH]", text)

    for word in _SENSITIVE_WORDS:
        text = re.sub(re.escape(word), "[REDACTED]", text, flags=re.IGNORECASE)

    text = text.replace("{", "").replace("}", "")
    text = text.replace("\\", "/")
    return " ".join(text.split())


def _top_level_keys(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return []
    return sorted(_redact_text(key) for key in data.keys())


def _count_lists(data: Any) -> int:
    if isinstance(data, list):
        return len(data)
    if isinstance(data, dict):
        total = 0
        for value in data.values():
            total += _count_lists(value)
        return total
    return 0


def _count_dict_sections(data: Any) -> int:
    if isinstance(data, dict):
        return len(data)
    return 0


def build_synthetic_visible_report_markdown(data: Any) -> str:
    top_keys = _top_level_keys(data)
    top_key_text = ", ".join(top_keys) if top_keys else "sin secciones top-level publicables"
    section_count = _count_dict_sections(data)
    list_item_count = _count_lists(data)

    lines = [
        "# CID Local Media Agent — Informe visible sintético de demo",
        "",
        "## Aviso de demo sintética",
        "",
        "Este informe es una demostración sintética local. No procede de material real de cliente.",
        "",
        "No realiza procesamiento real de vídeo, audio, subtítulos, sincronización, transcripción, traducción ni exportación a NLE.",
        "",
        "## Privacidad local-first",
        "",
        "El flujo demostrado está diseñado bajo criterio local-first: los archivos audiovisuales del cliente no salen del disco por defecto.",
        "",
        "Este Markdown no incluye rutas absolutas, usuarios de máquina, nombres de cliente ni identificadores reales de proyecto.",
        "",
        "## Alcance técnico",
        "",
        "- No realiza sincronización real por forma de onda.",
        "- No realiza sincronización real por timecode.",
        "- No realiza sincronización real por claqueta.",
        f"- No ejecuta {_FFPROBE_LABEL}.",
        f"- No ejecuta {_FFMPEG_LABEL}.",
        "- No transcribe audio real.",
        "- No traduce diálogos reales.",
        "- No genera subtítulos finales.",
        "- No exporta a DaVinci Resolve, Avid, Premiere, OTIO, EDL, XML ni FCPXML.",
        "- No valida delivery final.",
        "",
        "## Resumen sintético de entrada",
        "",
        f"- Secciones sintéticas top-level detectadas: {section_count}",
        f"- Elementos sintéticos en listas detectados: {list_item_count}",
        f"- Nombres de secciones publicables: {top_key_text}",
        "",
        "## Lectura para producción y postproducción",
        "",
        "CID Local Media Agent se presenta aquí como ayuda técnica y creativa para ordenar material, preparar revisión humana y facilitar comunicación entre producción, montaje, sonido, DIT y subtítulos.",
        "",
        "CID no sustituye al montador, al ayudante de montaje, al DIT, al técnico de sonido, al director ni al productor.",
        "",
        "## Checklist obligatorio de revisión humana",
        "",
        "- Confirmar que el informe procede solo de fixture sintético.",
        "- Confirmar que no contiene rutas absolutas.",
        "- Confirmar que no contiene nombres reales de cliente.",
        "- Confirmar que no contiene identificadores reales de proyecto.",
        "- Confirmar que no se ha procesado media real.",
        "- Confirmar que no se afirma sincronización real.",
        "- Confirmar que no se afirma transcripción real.",
        "- Confirmar que no se afirma traducción real.",
        "- Confirmar que no se afirma exportación real a NLE.",
        "- Confirmar que el informe se usa solo como demo de trabajo.",
        "",
        "## Estado",
        "",
        "Informe Markdown sintético generado de forma determinista para demo local controlada.",
        "",
    ]

    return "\n".join(lines)


def render_synthetic_visible_report_markdown(
    fixture_path: str | Path,
    output_dir: str | Path,
    *,
    allow_overwrite: bool = False,
) -> Path:
    fixture = _validate_fixture_path(fixture_path)
    output = _validate_output_dir(output_dir)
    data = _load_fixture(fixture)

    target = output / OUTPUT_FILENAME
    if target.exists() and not allow_overwrite:
        raise SyntheticVisibleReportRendererError(
            "Refusing to overwrite existing synthetic visible report."
        )

    markdown = build_synthetic_visible_report_markdown(data)
    target.write_text(markdown, encoding="utf-8")
    return target
