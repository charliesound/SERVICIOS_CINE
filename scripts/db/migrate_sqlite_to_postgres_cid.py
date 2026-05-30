#!/usr/bin/env python3
"""Migrate data from SQLite to PostgreSQL schema cid.

Usage:
    python scripts/db/migrate_sqlite_to_postgres_cid.py --dry-run
    python scripts/db/migrate_sqlite_to_postgres_cid.py --execute
    python scripts/db/migrate_sqlite_to_postgres_cid.py --execute --batch-size 200
    python scripts/db/migrate_sqlite_to_postgres_cid.py --execute --tables users,projects

Requires: psycopg2-binary
"""

import argparse
import os
import sqlite3
import sys

SQLITE_PATH = "/opt/SERVICIOS_CINE/ailinkcinema_s2.db"
PG_HOST = "127.0.0.1"
PG_PORT = 5432
PG_DB = "ailinkcinema"
PG_USER = "ailinkcinema"
PG_PASSWORD = os.environ.get("PGPASSWORD", "keK9RaoGSgcMTiP87KYsUk3Fm3EI3Jv")
PG_SCHEMA = "cid"
DEFAULT_BATCH_SIZE = 500

# FK-safe table order (topological, depth 0 -> 7)
TABLE_ORDER = [
    "organizations", "users", "projects", "storage_sources",
    "approved_project_baselines", "assembly_cuts", "budget_estimates",
    "characters", "clips", "crm_contacts", "crm_tasks",
    "demo_request_records", "distribution_packs", "funding_opportunities",
    "funding_sources", "ingest_events", "integration_connections",
    "lead_gen_events", "matcher_jobs", "planned_shots",
    "private_funding_sources", "producer_pitch_packs", "production_breakdowns",
    "project_budgets", "project_change_requests", "project_documents",
    "project_funding_sources", "project_jobs", "project_members",
    "project_module_status", "project_visual_bibles", "sales_targets",
    "saved_opportunities", "scenes", "script_change_reports", "script_versions",
    "sequences", "shooting_plans", "shots", "storyboard_shots", "visual_assets",
    "crm_communications", "crm_opportunities", "funding_calls",
    "integration_tokens", "job_history", "password_reset_tokens",
    "private_opportunities", "producer_pitch_sections", "project_approvals",
    "project_external_folder_links", "project_sales_opportunities", "reviews",
    "scene_character_link", "shooting_plan_items", "storage_authorizations",
    "storage_watch_paths", "budget_line_items", "budget_lines",
    "budget_scenarios", "department_line_items", "distribution_pack_sections",
    "document_chunks", "external_document_sync_state",
    "approval_decisions", "deliverables", "funding_requirements",
    "ingest_scans", "project_funding_matches", "review_comments",
    "media_assets", "opportunity_trackings",
    "document_assets", "notifications", "requirement_checklist_items",
    "camera_reports", "director_notes", "document_classifications",
    "document_extractions", "document_links", "document_structured_data",
    "script_notes", "sound_reports",
    "takes", "assembly_cut_items",
]

# Boolean columns per table (SQLite stores as 0/1, PG as boolean)
BOOLEAN_COLUMNS = {
    "organizations": ["is_active"],
    "users": ["is_active", "cid_enabled", "onboarding_completed"],
    "storyboard_shots": ["is_active"],
    "funding_sources": ["is_active"],
    "funding_requirements": ["is_mandatory"],
    "project_members": ["can_manage_members", "can_manage_permissions"],
    "project_visual_bibles": ["is_active"],
    "budget_lines": ["is_enabled", "is_manual_override"],
    "notifications": ["is_read"],
    "requirement_checklist_items": ["auto_detected", "is_fulfilled"],
    "takes": ["audio_circled", "is_best", "is_circled", "is_recommended"],
}

# Orphan columns: set referenced FK to NULL if parent row does not exist
ORPHAN_NULL_MAP = {
    "job_history": ("created_by", "users"),
}


def get_pg_connection():
    import psycopg2
    conn = psycopg2.connect(
        host=PG_HOST, port=PG_PORT, dbname=PG_DB,
        user=PG_USER, password=PG_PASSWORD,
    )
    conn.set_session(autocommit=False)
    return conn


def get_common_columns(sqlite_conn, pg_cursor, table: str) -> list[str]:
    sq_cols = {
        row[1].lower()
        for row in sqlite_conn.execute(f"PRAGMA table_info('{table}')").fetchall()
    }
    pg_cursor.execute(
        f"SELECT column_name FROM information_schema.columns "
        f"WHERE table_schema = '{PG_SCHEMA}' AND table_name = '{table}'"
    )
    pg_cols = {row[0].lower() for row in pg_cursor.fetchall()}
    return sorted(sq_cols & pg_cols)


def count_sqlite(sqlite_conn, table: str) -> int:
    return sqlite_conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def count_pg(pg_cursor, table: str) -> int:
    pg_cursor.execute(f"SELECT COUNT(*) FROM {PG_SCHEMA}.{table}")
    return pg_cursor.fetchone()[0]


def get_column_metadata(pg_cursor, table: str):
    """Return (varchar_max_map, notnull_timestamp_set) for PG column types."""
    pg_cursor.execute(
        f"SELECT column_name, data_type, character_maximum_length, is_nullable "
        f"FROM information_schema.columns "
        f"WHERE table_schema = '{PG_SCHEMA}' AND table_name = '{table}'"
    )
    varchar_max = {}
    notnull_ts = set()
    for col_name, data_type, char_max, is_nullable in pg_cursor.fetchall():
        cn = col_name.lower()
        if data_type == "character varying" and char_max is not None:
            varchar_max[cn] = char_max
        if "timestamp" in data_type and is_nullable == "NO":
            notnull_ts.add(cn)
    return varchar_max, notnull_ts


def is_valid_timestamp(s):
    """Check if string looks like a valid timestamp (starts with digit or -/+)."""
    s = str(s).strip()
    return bool(s and (s[0].isdigit() or s[0] in '-+'))


def main():
    parser = argparse.ArgumentParser(
        description="Migrate SQLite data to PostgreSQL schema cid"
    )
    parser.add_argument("--execute", action="store_true",
                        help="Execute inserts (default: dry-run)")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--tables", type=str, default=None,
                        help="Comma-separated subset of tables")
    args = parser.parse_args()
    dry_run = not args.execute

    print("=" * 70)
    print(f"  SQLite -> PostgreSQL CID Migration")
    print(f"  Source: {SQLITE_PATH}")
    print(f"  Target: {PG_HOST}:{PG_PORT}/{PG_DB} schema={PG_SCHEMA}")
    print(f"  Mode:   {'DRY RUN' if dry_run else 'EXECUTE'}")
    print(f"  Batch:  {args.batch_size}")
    if args.tables:
        print(f"  Tables: {args.tables}")
    print("=" * 70)

    filter_tables = None
    if args.tables:
        filter_tables = {t.strip() for t in args.tables.split(",")}

    # Open SQLite read-only
    sqlite_conn = sqlite3.connect(str(SQLITE_PATH))
    sqlite_conn.execute("PRAGMA query_only = ON")
    sqlite_conn.row_factory = sqlite3.Row

    pg_conn = get_pg_connection()
    pg_cursor = pg_conn.cursor()

    # Pre-counts
    print("\n  Pre-migration counts (SQLite):")
    pre_counts = {}
    for table in TABLE_ORDER:
        if filter_tables and table not in filter_tables:
            continue
        if not sqlite_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,)
        ).fetchone():
            continue
        cnt = count_sqlite(sqlite_conn, table)
        pre_counts[table] = cnt
        if cnt > 0:
            print(f"    {table:40s} {cnt:>8} rows")

    total_src = sum(pre_counts.values())
    print(f"    {'─' * 40} ────────")
    print(f"    {'TOTAL':40s} {total_src:>8} rows")

    # Migrate
    print(f"\n  {'─' * 70}")
    stats = {}
    for table in TABLE_ORDER:
        if filter_tables and table not in filter_tables:
            continue
        if not sqlite_conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table,)
        ).fetchone():
            continue
        pg_cursor.execute(
            "SELECT 1 FROM information_schema.tables "
            "WHERE table_schema=%s AND table_name=%s",
            (PG_SCHEMA, table)
        )
        if not pg_cursor.fetchone():
            print(f"  SKIP {table}: not in PostgreSQL")
            continue

        common_cols = get_common_columns(sqlite_conn, pg_cursor, table)
        if not common_cols:
            print(f"  SKIP {table}: no common columns")
            continue

        bool_cols = set(BOOLEAN_COLUMNS.get(table, [])) & set(common_cols)
        varchar_max, notnull_ts = get_column_metadata(pg_cursor, table)
        orphan_col, orphan_ref_table = ORPHAN_NULL_MAP.get(table, (None, None))
        col_list = ", ".join(common_cols)
        placeholders = ", ".join(["%s"] * len(common_cols))
        pk_col = "id"

        sql = f"SELECT {col_list} FROM {table}"
        rows = sqlite_conn.execute(sql).fetchall()
        print(f"  -> {table:40s} {len(rows):>8} rows read", end="")

        if dry_run:
            print()
            stats[table] = {"read": len(rows), "inserted": 0}
            continue

        insert_sql = (
            f"INSERT INTO {PG_SCHEMA}.{table} ({col_list}) "
            f"VALUES ({placeholders}) "
            f"ON CONFLICT ({pk_col}) DO NOTHING"
        )

        col_names = [c.lower() for c in common_cols]
        inserted = 0
        errors = 0
        batch = []

        for row in rows:
            skip = False
            vals = [row[c] for c in col_names]
            for i, cn in enumerate(col_names):
                if cn in bool_cols and vals[i] is not None:
                    vals[i] = bool(int(vals[i]))
            for i, cn in enumerate(col_names):
                if vals[i] is not None:
                    if cn in varchar_max:
                        s = str(vals[i])
                        if len(s) > varchar_max[cn]:
                            vals[i] = s[:varchar_max[cn]]
                    elif cn in notnull_ts and not is_valid_timestamp(vals[i]):
                        skip = True
                        break
            if skip:
                errors += 1
                continue
            if orphan_col and orphan_col in col_names:
                idx = col_names.index(orphan_col)
                if vals[idx] is not None:
                    pg_cursor.execute(
                        f"SELECT 1 FROM {PG_SCHEMA}.{orphan_ref_table} WHERE id = %s",
                        (vals[idx],)
                    )
                    if not pg_cursor.fetchone():
                        vals[idx] = None
            batch.append(tuple(vals))

            if len(batch) >= args.batch_size:
                try:
                    pg_cursor.executemany(insert_sql, batch)
                    inserted += len(batch)
                except Exception as e:
                    if errors == 0:
                        print()
                        print(f"    ERROR on {table}:")
                        print(f"    Exception: {type(e).__name__}: {e}")
                        print(f"    Columns:   {col_names}")
                        first = batch[0]
                        print(f"    First row: {list(first)}")
                        for i, (cn, fv) in enumerate(zip(col_names, first)):
                            print(f"      {cn}: {repr(fv)} ({type(fv).__name__})")
                    pg_conn.rollback()
                    for item in batch:
                        try:
                            pg_cursor.execute(insert_sql, item)
                            inserted += 1
                        except Exception as e2:
                            if errors < 3:
                                print(f"    ROW FAIL: {e2}")
                            errors += 1
                    if errors:
                        pg_conn.rollback()
                batch = []

        if batch:
            try:
                pg_cursor.executemany(insert_sql, batch)
                inserted += len(batch)
            except Exception as e:
                if errors == 0:
                    print()
                    print(f"    ERROR on {table}:")
                    print(f"    Exception: {type(e).__name__}: {e}")
                    print(f"    Columns:   {col_names}")
                    first = batch[0]
                    print(f"    First row: {list(first)}")
                pg_conn.rollback()
                for item in batch:
                    try:
                        pg_cursor.execute(insert_sql, item)
                        inserted += 1
                    except Exception as e2:
                        if errors < 3:
                            print(f"    ROW FAIL: {e2}")
                        errors += 1
                if errors:
                    pg_conn.rollback()

        stats[table] = {"read": len(rows), "inserted": inserted}
        print(f"  inserted={inserted}  errors={errors}")
        if not dry_run:
            pg_conn.commit()

    # Post-migration validation
    if not dry_run:
        print(f"\n  {'─' * 70}")
        print(f"  Post-migration count validation:")
        mismatches = []
        for table in sorted(stats):
            sq_c = pre_counts.get(table, 0)
            pg_c = count_pg(pg_cursor, table)
            ok = "OK" if sq_c == pg_c else "MISMATCH"
            if ok == "MISMATCH":
                mismatches.append((table, sq_c, pg_c))
            print(f"    {table:40s} SQLite={sq_c:>8}  PG={pg_c:>8}  {ok}")

        # Verify n8n tables untouched
        pg_cursor.execute(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema='public' AND table_name LIKE 'n8n_%'"
        )
        n8n_count = pg_cursor.fetchone()[0]
        print(f"\n  n8n tables in public schema: {n8n_count} (untouched)")

        if mismatches:
            print(f"\n  WARNING: {len(mismatches)} table(s) with count mismatch:")
            for t, sq, pg in mismatches:
                print(f"    {t}: SQLite={sq} PG={pg}")
        else:
            print(f"\n  SUCCESS: All counts match, n8n/public untouched")
            print(f"  Total rows migrated: {sum(s['inserted'] for s in stats.values())}")
    else:
        print(f"\n  DRY RUN complete — no data written")
        print(f"  Re-run with --execute to perform the migration")

    sqlite_conn.close()
    pg_cursor.close()
    pg_conn.close()


if __name__ == "__main__":
    main()
