---
name: cid-release-checklist
description: Use this skill before closing an AILinkCinema/CID phase to validate diff, tests, guards, commit message, tag name, push state, and clean workspace.
---

# CID Release Checklist

Use this skill before committing, tagging, pushing, or closing a phase.

## Manual commit discipline

Do not run `git commit`, `git tag`, or `git push` unless the user explicitly asks for it.

## Pre-commit inspection

Run or request these commands:

```bash
git status --short --untracked-files=all
git diff --stat
git diff --check
git diff --cached --stat
git diff --cached --check
```

## Standard validations

Use the smallest relevant test set first, then broader guards.

Typical commands:

```bash
python -m py_compile <changed_python_files>
python -m pytest <relevant_tests> -q
python -m pytest tests/unit/test_config.py -q
bash scripts/dev/<database-regression-guard>.sh
bash scripts/dev/guard_wsl_repo.sh
```

## Commit proposal format

Suggest:

- Commit message.
- Tag name.
- Push commands.

But do not execute them without user approval.

## Final closing report

Include:

1. Phase ID.
2. Commit hash, if committed.
3. Tag, if tagged.
4. Files changed.
5. Tests passed.
6. Guards passed.
7. Workspace status.
8. Next recommended phase.
