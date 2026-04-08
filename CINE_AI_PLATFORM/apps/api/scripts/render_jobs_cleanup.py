from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable, Optional


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manual and safe cleanup for render jobs SQLite table")
    parser.add_argument(
        "--db-path",
        default="data/render_jobs.db",
        help="Path to render jobs sqlite database (default: data/render_jobs.db)",
    )
    parser.add_argument(
        "--keep-last",
        type=int,
        default=200,
        help="Keep newest N jobs (default: 200)",
    )
    parser.add_argument(
        "--older-than-days",
        type=int,
        default=None,
        help="Additionally mark jobs older than X days for deletion",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help="Apply deletion. Without this flag the script runs in dry-run mode.",
    )
    return parser.parse_args()


def parse_iso(value: str) -> Optional[datetime]:
    if not isinstance(value, str) or not value.strip():
        return None

    normalized = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)


def chunked(items: list[str], size: int) -> Iterable[list[str]]:
    for index in range(0, len(items), size):
        yield items[index : index + size]


def main() -> int:
    args = parse_args()
    db_path = Path(args.db_path)

    if not db_path.exists():
        print(f"Database not found: {db_path}")
        return 1

    if args.keep_last < 0:
        print("--keep-last must be >= 0")
        return 1

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    try:
        rows = conn.execute(
            """
            SELECT job_id, created_at, status
            FROM render_jobs
            ORDER BY created_at DESC
            """
        ).fetchall()

        total = len(rows)
        if total == 0:
            print("No jobs found. Nothing to clean.")
            return 0

        candidates: set[str] = set()

        if args.keep_last < total:
            for row in rows[args.keep_last :]:
                candidates.add(str(row["job_id"]))

        if args.older_than_days is not None:
            cutoff = datetime.now(timezone.utc) - timedelta(days=max(args.older_than_days, 0))
            for row in rows:
                created_at = parse_iso(str(row["created_at"]))
                if created_at is None:
                    continue
                if created_at < cutoff:
                    candidates.add(str(row["job_id"]))

        candidate_list = sorted(candidates)

        print(f"DB: {db_path}")
        print(f"Total jobs: {total}")
        print(f"Keep last: {args.keep_last}")
        if args.older_than_days is not None:
            print(f"Older than days: {args.older_than_days}")
        print(f"Candidates for deletion: {len(candidate_list)}")

        if len(candidate_list) == 0:
            print("Nothing to delete.")
            return 0

        preview = candidate_list[:10]
        for job_id in preview:
            print(f"- {job_id}")
        if len(candidate_list) > len(preview):
            print(f"... and {len(candidate_list) - len(preview)} more")

        if not args.confirm:
            print("Dry-run mode: no rows deleted. Use --confirm to apply cleanup.")
            return 0

        deleted = 0
        for group in chunked(candidate_list, 200):
            placeholders = ",".join("?" for _ in group)
            cursor = conn.execute(
                f"DELETE FROM render_jobs WHERE job_id IN ({placeholders})",
                tuple(group),
            )
            deleted += int(cursor.rowcount)

        conn.commit()
        print(f"Deleted rows: {deleted}")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
