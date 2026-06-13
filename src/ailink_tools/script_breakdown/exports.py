"""Export functions for Script-to-Production Breakdown demo."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from .schemas import BreakdownResult

ALLOWED_EXTENSIONS = {".json", ".md"}


def _validate_path(path: Path, allowed_suffixes: set) -> None:
    """Validate that the path is safe and has an allowed extension."""
    if not path.name:
        raise ValueError("Ruta vacía no permitida")
    if path.suffix.lower() not in allowed_suffixes:
        raise ValueError(
            f"Extensión no permitida: {path.suffix}. "
            f"Permitidas: {allowed_suffixes}"
        )


def export_json(result: BreakdownResult, path: Path) -> Path:
    """Export breakdown result to JSON file.

    Args:
        result: The breakdown result to export.
        path: The output file path (must end in .json).

    Returns:
        The path to the created file.

    Raises:
        ValueError: If the path is invalid or has wrong extension.
    """
    _validate_path(path, {".json"})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(result.to_json(indent=2), encoding="utf-8")
    return path


def _traffic_light_emoji(light: str) -> str:
    """Convert traffic light to emoji for markdown."""
    mapping = {
        "verde": "\U0001f7e2",
        "amarillo": "\U0001f7e1",
        "naranja": "\U0001f7e0",
        "rojo": "\U0001f534",
        "gris": "\u26ab",
    }
    return mapping.get(light, "\u26ab")


def _build_markdown(result: BreakdownResult) -> str:
    """Build markdown content from breakdown result."""
    lines: List[str] = []

    # Header
    lines.append(f"# Desglose de Producción: {result.project['title']}")
    lines.append("")

    # Metadata
    lines.append("## Metadata de Aislamiento")
    lines.append("")
    lines.append(f"- **organization_id**: `{result.metadata['organization_id']}`")
    lines.append(f"- **tenant_id**: `{result.metadata['tenant_id']}`")
    lines.append(f"- **project_id**: `{result.metadata['project_id']}`")
    lines.append(f"- **film_id**: `{result.metadata['film_id']}`")
    lines.append(f"- **productora**: {result.metadata['organization_name']}")
    lines.append("")

    # Project summary
    lines.append("## Resumen del Proyecto")
    lines.append("")
    lines.append(f"- **Título**: {result.project['title']}")
    lines.append(f"- **Tipo**: {result.project['type']}")
    lines.append(f"- **Género**: {result.project['genre']}")
    lines.append(f"- **Duración**: {result.project['duration_minutes']} minutos")
    lines.append(f"- **Rodaje**: {result.project['shooting_weeks']} semanas")
    lines.append(f"- **Moneda**: {result.project['currency']}")
    lines.append("")

    # Scenes
    lines.append(f"## Escenas ({len(result.scenes)})")
    lines.append("")
    lines.append("| ID | Escena | Localización | I/E | D/N | Personajes | Complejidad |")
    lines.append("|-----|--------|--------------|-----|-----|------------|-------------|")
    for s in result.scenes:
        chars = ", ".join(s.characters)
        lines.append(
            f"| {s.scene_id} | {s.number}. {s.header} | {s.location} | "
            f"{s.int_ext} | {s.day_night} | {chars} | {s.complexity} |"
        )
    lines.append("")

    # Characters
    lines.append(f"## Personajes ({len(result.characters)})")
    lines.append("")
    lines.append("| ID | Nombre | Rol | Escenas | Edad | Complejidad |")
    lines.append("|-----|--------|-----|---------|------|-------------|")
    for c in result.characters:
        scenes_str = ", ".join(str(x) for x in c.scenes)
        lines.append(
            f"| {c.character_id} | {c.name} | {c.role} | "
            f"{scenes_str} | {c.age} | {c.complexity} |"
        )
    lines.append("")

    # Locations
    lines.append(f"## Localizaciones ({len(result.locations)})")
    lines.append("")
    lines.append("| ID | Nombre | Tipo | I/E | Escenas | Permisos | Complejidad |")
    lines.append("|-----|--------|------|-----|---------|----------|-------------|")
    for loc in result.locations:
        scenes_str = ", ".join(str(x) for x in loc.scenes)
        lines.append(
            f"| {loc.location_id} | {loc.name} | {loc.type} | "
            f"{loc.int_ext} | {scenes_str} | {loc.permits} | {loc.complexity} |"
        )
    lines.append("")

    # Risks
    lines.append(f"## Riesgos ({len(result.risks)})")
    lines.append("")
    lines.append("| ID | Riesgo | Impacto | Probabilidad | Mitigación |")
    lines.append("|-----|--------|---------|--------------|------------|")
    for r in result.risks:
        lines.append(
            f"| {r.risk_id} | {r.description} | {r.impact} | "
            f"{r.probability} | {r.mitigation} |"
        )
    lines.append("")

    # Viability
    lines.append("## Viabilidad")
    lines.append("")
    v = result.viability
    emoji = _traffic_light_emoji(v["global_traffic_light"])
    lines.append(f"**Viabilidad global**: {v['global_score']}/10 {emoji} {v['summary']}")
    lines.append("")
    lines.append("| Indicador | Puntuación | Semáforo | Justificación | Recomendación |")
    lines.append("|-----------|------------|----------|---------------|---------------|")
    for ind in v["indicators"]:
        emoji = _traffic_light_emoji(ind["traffic_light"])
        lines.append(
            f"| {ind['indicator']} | {ind['score']}/{ind['max_score']} | "
            f"{emoji} {ind['traffic_light']} | {ind['justification']} | "
            f"{ind['recommendation']} |"
        )
    lines.append("")

    # Budget
    lines.append("## Presupuesto Preliminar")
    lines.append("")
    lines.append("| ID | Categoría | Baja | Media | Alta | Confianza | Supuestos |")
    lines.append("|-----|-----------|------|-------|------|-----------|-----------|")
    for b in result.preliminary_budget:
        lines.append(
            f"| {b.budget_id} | {b.category} | {b.low:,} | {b.mid:,} | "
            f"{b.high:,} | {b.confidence} | {b.assumptions} |"
        )
    lines.append("")

    # Recommendations
    lines.append("## Recomendaciones")
    lines.append("")
    for i, rec in enumerate(result.recommendations, 1):
        lines.append(f"{i}. {rec}")
    lines.append("")

    # Human review notes
    lines.append("## Notas de Revisión Humana")
    lines.append("")
    for note in result.human_review_notes:
        lines.append(f"- {note}")
    lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append(
        "*Este documento es un desglose orientativo generado por un parser "
        "determinista de demo. Requiere revisión humana.*"
    )
    lines.append("")

    return "\n".join(lines)


def export_markdown(result: BreakdownResult, path: Path) -> Path:
    """Export breakdown result to Markdown file.

    Args:
        result: The breakdown result to export.
        path: The output file path (must end in .md).

    Returns:
        The path to the created file.

    Raises:
        ValueError: If the path is invalid or has wrong extension.
    """
    _validate_path(path, {".md"})
    path.parent.mkdir(parents=True, exist_ok=True)
    content = _build_markdown(result)
    path.write_text(content, encoding="utf-8")
    return path
