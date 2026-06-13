#!/usr/bin/env python3
"""CLI for Script-to-Production Breakdown demo prototype.

Usage:
    python scripts/ailink_script_breakdown_demo.py \
        --input-demo <path> \
        --output-dir <path> \
        [--json-name breakdown.json] \
        [--markdown-name breakdown.md] \
        [--force]

Exit codes:
    0 - success
    2 - argument error or unsupported input
    3 - unexpected error
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure the src directory is in the path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ailink_tools.script_breakdown.demo_parser import (
    parse_demo_script,
)
from ailink_tools.script_breakdown.exports import (
    export_json,
    export_markdown,
)


def _validate_output_dir(output_dir: Path) -> None:
    """Validate that the output directory is safe."""
    path_str = str(output_dir)

    # Reject empty-ish paths
    if not path_str or path_str.strip() in ("", "/"):
        raise ValueError("output-dir no puede estar vacío o ser raíz")

    # Reject root
    if output_dir == Path("/"):
        raise ValueError("output-dir no puede ser /")

    # Reject /mnt paths (WSL) - check both forward and back slashes
    normalized = path_str.replace("\\", "/")
    if normalized.startswith("/mnt/"):
        raise ValueError("rutas /mnt/ no permitidas")


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Script-to-Production Breakdown Demo Prototype"
    )
    parser.add_argument(
        "--input-demo",
        "--demo-file",
        required=True,
        help="Ruta al guion demo controlado",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directorio de salida para archivos generados",
    )
    parser.add_argument(
        "--json-name",
        default="breakdown.json",
        help="Nombre del archivo JSON (default: breakdown.json)",
    )
    parser.add_argument(
        "--markdown-name",
        default="breakdown.md",
        help="Nombre del archivo Markdown (default: breakdown.md)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Sobrescribir archivos existentes",
    )

    args = parser.parse_args(argv)

    try:
        # Validate input file
        input_path = Path(args.input_demo)
        if not input_path.exists():
            print(
                f"Error: archivo de entrada no encontrado: {input_path}",
                file=sys.stderr,
            )
            return 2

        # Read input
        text = input_path.read_text(encoding="utf-8")

        # Parse
        result = parse_demo_script(text)

        # Validate output directory
        output_dir = Path(args.output_dir)
        _validate_output_dir(output_dir)

        # Build output paths
        json_path = output_dir / args.json_name
        md_path = output_dir / args.markdown_name

        # Check for existing files
        if not args.force:
            if json_path.exists():
                print(
                    f"Error: archivo ya existe: {json_path}. "
                    "Usa --force para sobrescribir.",
                    file=sys.stderr,
                )
                return 2
            if md_path.exists():
                print(
                    f"Error: archivo ya existe: {md_path}. "
                    "Usa --force para sobrescribir.",
                    file=sys.stderr,
                )
                return 2

        # Export
        export_json(result, json_path)
        export_markdown(result, md_path)

        print(f"Exportado JSON: {json_path}")
        print(f"Exportado Markdown: {md_path}")
        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Error inesperado: {e}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
