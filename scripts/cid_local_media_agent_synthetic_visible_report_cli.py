from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

COMMAND_NAME = "synthetic-visible-report"
OUTPUT_FILENAME = "cid_local_media_agent_synthetic_visible_report_v1.md"

_ALLOWED_FLAGS_WITH_VALUE = {"--fixture", "--output-dir", "--format"}
_ALLOWED_BOOL_FLAGS = {"--allow-overwrite"}
_HELP_FLAGS = {"-h", "--help"}

_RENDERER_PATH = Path(__file__).with_name("cid_local_media_agent_synthetic_visible_report_renderer.py")


def _load_renderer() -> Any:
    spec = importlib.util.spec_from_file_location(
        "cid_local_media_agent_synthetic_visible_report_renderer",
        _RENDERER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Synthetic renderer module could not be loaded.")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _help_text() -> str:
    return "\n".join(
        [
            "CID Local Media Agent — synthetic-visible-report",
            "",
            "Uso:",
            "  synthetic-visible-report --fixture <fixture-json> --output-dir <dir> --format markdown [--allow-overwrite]",
            "",
            "Alcance:",
            "  Demo sintética local. No analiza media real.",
            "  No sincroniza audio/vídeo real.",
            "  No transcribe audio real.",
            "  No traduce diálogo real.",
            "  No genera subtítulos finales.",
            "  No exporta a NLE.",
            "  No sube material del cliente.",
            "  Revisión humana obligatoria.",
            "  CID es asistivo y no sustitutivo.",
            "",
            "Opciones permitidas:",
            "  --fixture          Fixture sintético controlado.",
            "  --output-dir       Directorio de salida ya existente y controlado.",
            "  --format markdown  Formato permitido.",
            "  --allow-overwrite  Permite sobrescribir el Markdown sintético existente.",
            "",
        ]
    )


def _error(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 2


def _parse_args(argv: list[str]) -> tuple[dict[str, str | bool], str | None]:
    parsed: dict[str, str | bool] = {
        "--allow-overwrite": False,
        "--format": "markdown",
    }

    index = 0
    while index < len(argv):
        arg = argv[index]

        if arg in _HELP_FLAGS:
            parsed["--help"] = True
            index += 1
            continue

        if arg in _ALLOWED_BOOL_FLAGS:
            parsed[arg] = True
            index += 1
            continue

        if arg in _ALLOWED_FLAGS_WITH_VALUE:
            if index + 1 >= len(argv):
                return parsed, "falta el valor de una opción permitida."
            value = argv[index + 1]
            if value.startswith("--"):
                return parsed, "falta el valor de una opción permitida."
            parsed[arg] = value
            index += 2
            continue

        return parsed, "opción no permitida para esta demo sintética."

    return parsed, None


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    if not args:
        print(_help_text())
        return 0

    parsed, parse_error = _parse_args(args)
    if parsed.get("--help"):
        print(_help_text())
        return 0

    if parse_error:
        return _error(parse_error)

    fixture = parsed.get("--fixture")
    output_dir = parsed.get("--output-dir")
    report_format = parsed.get("--format", "markdown")
    allow_overwrite = bool(parsed.get("--allow-overwrite", False))

    if not isinstance(fixture, str):
        return _error("falta --fixture.")
    if not isinstance(output_dir, str):
        return _error("falta --output-dir.")
    if report_format != "markdown":
        return _error("solo se permite --format markdown.")

    try:
        renderer = _load_renderer()
        renderer.render_synthetic_visible_report_markdown(
            fixture,
            output_dir,
            allow_overwrite=allow_overwrite,
        )
    except Exception:
        return _error("no se pudo generar el informe sintético con los parámetros permitidos.")

    print(f"OK: generado {OUTPUT_FILENAME}")
    print("Demo sintética local-first. Revisión humana obligatoria.")
    print("No analiza media real ni sube material del cliente.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
