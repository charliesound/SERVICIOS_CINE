#!/usr/bin/env python3
"""
Materialización de proyectos legacy: media_assets -> storyboard_shots.

Este script normaliza proyectos que tienen media_assets pero no storyboard_shots,
creando shots derivados de los assets existentes de forma idempotente.

Uso:
    python scripts/materialize_legacy_storyboard_shots.py [--project-id PROJECT_ID] [--dry-run]

Opciones:
    --project-id PROJECT_ID  Procesar un proyecto específico (opcional)
    --dry-run           Simular sin escribir a la base de datos
    --verbose          Mostrar detalle de cada operación
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

DEFAULT_DB_PATH = Path("/opt/SERVICIOS_CINE/ailinkcinema_s2.db")
DEFAULT_SEQUENCE_ID = "legacy_default"

IDX_ID = 0
IDX_PROJECT_ID = 1
IDX_ORG_ID = 2
IDX_FILE_NAME = 3
IDX_METADATA_JSON = 5
IDX_CREATED_AT = 11


def get_connection():
    import sqlite3
    return sqlite3.connect(DEFAULT_DB_PATH)


def decode_metadata(metadata_json):
    if not metadata_json:
        return {}
    try:
        return json.loads(metadata_json)
    except (json.JSONDecodeError, TypeError):
        return {}


def asset_sort_key(asset_row):
    metadata = decode_metadata(asset_row[IDX_METADATA_JSON])

    shot_order = metadata.get("shot_order")
    if shot_order is not None:
        try:
            order = int(shot_order)
        except (ValueError, TypeError):
            order = 0
    else:
        order = 0

    created_at = asset_row[IDX_CREATED_AT]
    created_ts = created_at if created_at else ""

    file_name = asset_row[IDX_FILE_NAME]

    return (order, created_ts, file_name)


def derive_narrative_text(asset_row):
    metadata = decode_metadata(asset_row[IDX_METADATA_JSON])

    prompt_summary = metadata.get("prompt_summary")
    if prompt_summary:
        return str(prompt_summary).strip()[:500] or None

    file_name = asset_row[IDX_FILE_NAME]
    if file_name:
        return f"Shot from {file_name}"

    return None


def extract_metadata_field(asset_row, field):
    metadata = decode_metadata(asset_row[IDX_METADATA_JSON])
    value = metadata.get(field)
    if value is not None:
        return str(value).strip()[:100] or None
    return None


def group_assets_by_sequence(assets):
    grouped = {}

    for asset in assets:
        metadata = decode_metadata(asset[IDX_METADATA_JSON])
        sequence_id = metadata.get("sequence_id")
        if sequence_id:
            sequence_id = str(sequence_id).strip() or None

        if sequence_id is None:
            sequence_id = DEFAULT_SEQUENCE_ID

        if sequence_id not in grouped:
            grouped[sequence_id] = []
        grouped[sequence_id].append(asset)

    return grouped


def materialize_project(
    conn,
    project_id,
    dry_run=False,
    verbose=False,
):
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM storyboard_shots WHERE project_id = ?",
        (project_id,),
    )
    existing_count = cursor.fetchone()[0] or 0

    cursor.execute(
        "SELECT id, project_id, organization_id, file_name, file_extension, metadata_json, "
        "mime_type, asset_type, content_ref, canonical_path, relative_path, created_at "
        "FROM media_assets WHERE project_id = ?",
        (project_id,),
    )
    assets = cursor.fetchall()

    if not assets:
        if verbose:
            print(f"[WARN] Proyecto {project_id}: sin media_assets")
        return 0, 0

    cursor.execute(
        "SELECT organization_id FROM projects WHERE id = ?",
        (project_id,),
    )
    proj_row = cursor.fetchone()
    if proj_row is None:
        if verbose:
            print(f"[WARN] Proyecto {project_id}: no encontrado")
        return 0, 0

    organization_id = proj_row[0]

    if existing_count > 0:
        if verbose:
            print(f"[SKIP] Proyecto {project_id}: ya tiene {existing_count} storyboard_shots")
        return existing_count, 0

    assets_by_sequence = group_assets_by_sequence(assets)
    created_count = 0

    for sequence_id, sequence_assets in assets_by_sequence.items():
        sequence_assets_sorted = sorted(
            sequence_assets,
            key=asset_sort_key,
        )

        for idx, asset in enumerate(sequence_assets_sorted):
            asset_id = asset[IDX_ID]

            narrative_text = derive_narrative_text(asset)
            shot_type = extract_metadata_field(asset, "shot_type")
            visual_mode = extract_metadata_field(asset, "visual_mode")

            created_count += 1

            if not dry_run:
                import uuid
                shot_id = str(uuid.uuid4())
                now = datetime.now(timezone.utc).isoformat()

                cursor.execute(
                    """
                    INSERT INTO storyboard_shots (
                        id, project_id, organization_id, sequence_id, sequence_order,
                        narrative_text, asset_id, shot_type, visual_mode,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        shot_id,
                        project_id,
                        organization_id,
                        sequence_id,
                        idx + 1,
                        narrative_text,
                        asset_id,
                        shot_type,
                        visual_mode,
                        now,
                        now,
                    ),
                )

    if not dry_run:
        conn.commit()

    return existing_count, created_count


def materialize_all_projects(
    conn,
    dry_run=False,
    verbose=False,
):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM projects")
    projects = cursor.fetchall()

    results = {}
    for (project_id,) in projects:
        existing, created = materialize_project(
            conn, project_id, dry_run=dry_run, verbose=verbose
        )
        results[project_id] = (existing, created)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Materializar proyectos legacy a storyboard_shots"
    )
    parser.add_argument(
        "--project-id",
        help="ID de proyecto específico a materializar",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simular sin escribir a la base de datos",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Mostrar detalle de operaciones",
    )
    parser.add_argument(
        "--db-path",
        default=str(DEFAULT_DB_PATH),
        help="Ruta a la base de datos SQLite",
    )
    args = parser.parse_args()

    db_path = Path(args.db_path)
    if not db_path.exists():
        print(f"[ERROR] Base de datos no encontrada: {db_path}")
        return 1

    conn = get_connection()
    try:
        if args.project_id:
            existing, created = materialize_project(
                conn, args.project_id, dry_run=args.dry_run, verbose=args.verbose
            )

            if args.dry_run:
                print(f"[DRY-RUN] Proyecto {args.project_id}: {existing} existentes, {created} a crear")
            else:
                print(f"[OK] Proyecto {args.project_id}: {existing} existentes, {created} shots creados")

            return 0 if created > 0 else 1

        results = materialize_all_projects(
            conn, dry_run=args.dry_run, verbose=args.verbose
        )

        materializados = 0
        omitidos = 0
        total_creados = 0

        for pid, (existing, created) in results.items():
            if existing > 0:
                omitidos += 1
            else:
                materializados += 1
                total_creados += created

        if args.dry_run:
            print(f"[DRY-RUN] Total: {materializados} proyectos a materializar, {omitidos} omitidos, {total_creados} shots a crear")
        else:
            print(f"[RESUMEN] Proyectos: {materializados} materializados, {omitidos} ya tenían shots")
            print(f"[RESUMEN] Total shots creados: {total_creados}")

        return 0 if total_creados > 0 else 1

    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())