from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


COMMAND_NAME = "synthetic-visible-report"
PREFLIGHT_NAME = "synthetic-visible-report-preflight"
OUTPUT_FILENAME = "cid_local_media_agent_synthetic_visible_report_v1.md"
APPROVED_FIXTURE_BASENAME = "synthetic_demo_report_fixture_v1.json"

_ALLOWED_FLAGS_WITH_VALUE = {"--fixture", "--output-dir", "--format"}
_ALLOWED_BOOL_FLAGS = {"--allow-overwrite"}
_HELP_FLAGS = {"-h", "--help"}

_RENDERER_PATH = Path(__file__).with_name("cid_local_media_agent_synthetic_visible_report_renderer.py")


class PreflightError(Exception):
    def __init__(self, reason: str, message: str, exit_code: int) -> None:
        super().__init__(message)
        self.reason = reason
        self.message = message
        self.exit_code = exit_code


def _help_text() -> str:
    return (
        "CID Local Media Agent — synthetic-visible-report-preflight\n\n"
        "Uso:\n"
        "  synthetic-visible-report-preflight --fixture <fixture-json> "
        "--output-dir <existing-dir> --format markdown [--allow-overwrite]\n\n"
        "Preflight local de demo sintética. No genera informe.\n"
        "Revisión humana obligatoria antes de usar cualquier salida generada por CID.\n\n"
        "Opciones:\n"
        "  --fixture <fixture-json>  Fixture sintético aprobado.\n"
        "  --output-dir <dir>        Directorio local existente de salida prevista.\n"
        "  --format markdown        Formato permitido.\n"
        "  --allow-overwrite        Permite que exista el Markdown sintético esperado.\n"
    )


def _fail(reason: str, message: str, exit_code: int) -> int:
    print("PREFLIGHT_FAIL", file=sys.stderr)
    print(f"reason={reason}", file=sys.stderr)
    print(f"message={message}", file=sys.stderr)
    return exit_code


def _pass() -> int:
    print("PREFLIGHT_PASS")
    print(f"command={COMMAND_NAME}")
    print(f"expected_output={OUTPUT_FILENAME}")
    print("mode=synthetic-local-only")
    print("human_review=required")
    return 0


def _parse_args(argv: list[str]) -> dict[str, Any]:
    parsed: dict[str, Any] = {
        "fixture": None,
        "output_dir": None,
        "format": None,
        "allow_overwrite": False,
    }

    index = 0
    while index < len(argv):
        item = argv[index]

        if item in _HELP_FLAGS:
            parsed["help"] = True
            index += 1
            continue

        if item in _ALLOWED_BOOL_FLAGS:
            parsed["allow_overwrite"] = True
            index += 1
            continue

        if item in _ALLOWED_FLAGS_WITH_VALUE:
            if index + 1 >= len(argv):
                raise PreflightError(
                    "MISSING_OPTION_VALUE",
                    "Falta el valor de una opción requerida.",
                    2,
                )

            value = argv[index + 1]
            if item == "--fixture":
                parsed["fixture"] = value
            elif item == "--output-dir":
                parsed["output_dir"] = value
            elif item == "--format":
                parsed["format"] = value

            index += 2
            continue

        raise PreflightError(
            "OPTION_NOT_ALLOWED",
            "Opción no permitida para el preflight sintético.",
            2,
        )

    return parsed


def _load_fixture(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise PreflightError(
            "FIXTURE_NOT_FOUND",
            "No se encontró el fixture sintético indicado.",
            2,
        )

    if path.name != APPROVED_FIXTURE_BASENAME:
        raise PreflightError(
            "FIXTURE_NOT_APPROVED",
            "El fixture indicado no pertenece al contrato sintético aprobado.",
            2,
        )

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PreflightError(
            "FIXTURE_JSON_INVALID",
            "El fixture sintético no contiene JSON válido.",
            2,
        ) from exc

    if not isinstance(data, dict) or not data:
        raise PreflightError(
            "FIXTURE_SCHEMA_INVALID",
            "El fixture sintético no contiene la estructura mínima esperada.",
            2,
        )

    return data


def _validate(parsed: dict[str, Any]) -> None:
    if parsed.get("help"):
        return

    fixture_value = parsed.get("fixture")
    output_dir_value = parsed.get("output_dir")
    format_value = parsed.get("format")

    if not fixture_value or not output_dir_value or not format_value:
        raise PreflightError(
            "MISSING_REQUIRED_ARGUMENTS",
            "Faltan argumentos requeridos para el preflight sintético.",
            2,
        )

    if format_value != "markdown":
        raise PreflightError(
            "FORMAT_NOT_SUPPORTED",
            "El único formato permitido es markdown.",
            2,
        )

    if not _RENDERER_PATH.exists():
        raise PreflightError(
            "RENDERER_NOT_FOUND",
            "No se encontró el renderer sintético requerido.",
            3,
        )

    _load_fixture(Path(str(fixture_value)))

    output_dir = Path(str(output_dir_value))
    if not output_dir.exists():
        raise PreflightError(
            "OUTPUT_DIR_NOT_FOUND",
            "No se encontró el directorio local de salida.",
            3,
        )

    if not output_dir.is_dir():
        raise PreflightError(
            "OUTPUT_DIR_NOT_DIRECTORY",
            "La salida indicada no es un directorio.",
            4,
        )

    output_file = output_dir / OUTPUT_FILENAME
    if output_file.exists() and not parsed.get("allow_overwrite"):
        raise PreflightError(
            "OUTPUT_ALREADY_EXISTS",
            "El informe sintético esperado ya existe y overwrite no está permitido.",
            4,
        )


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)

    try:
        if not args:
            print(_help_text())
            return 0

        parsed = _parse_args(args)

        if parsed.get("help"):
            print(_help_text())
            return 0

        _validate(parsed)
        return _pass()

    except PreflightError as exc:
        return _fail(exc.reason, exc.message, exc.exit_code)
    except Exception:
        return _fail(
            "UNEXPECTED_CONTROLLED_FAILURE",
            "El preflight falló de forma controlada.",
            1,
        )


if __name__ == "__main__":
    raise SystemExit(main())
