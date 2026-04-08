# Render jobs retention and cleanup (homelab)

## Decision taken
- No automatic deletion in Sprint 6.
- Manual cleanup only, with explicit confirmation.
- Default retention policy:
  - keep newest `200` jobs
  - optional extra filter: delete jobs older than `14` days

This keeps operation safe for demos and avoids accidental data loss.

## Cleanup command
Script:
- `apps/api/scripts/render_jobs_cleanup.py`

Dry-run (default):

```bash
cd apps/api
python scripts/render_jobs_cleanup.py --db-path data/render_jobs.db --keep-last 200 --older-than-days 14
```

Apply deletion (explicit):

```bash
cd apps/api
python scripts/render_jobs_cleanup.py --db-path data/render_jobs.db --keep-last 200 --older-than-days 14 --confirm
```

## Safety rules
- Always run dry-run first.
- Take backup before confirmed cleanup:
  - use `bash scripts/demo_backup.sh --env .env.demo --label pre-cleanup`
- Do not run cleanup during live demo.

## What gets deleted
- Rows from `render_jobs` table matching policy criteria.
- No deletion of shots/storage data.
- No media files are touched (none managed in this sprint).

## Warnings
- If `--keep-last` is too low, useful troubleshooting history can disappear.
- If `--older-than-days` is too aggressive, you may delete recent failures needed for debugging.
