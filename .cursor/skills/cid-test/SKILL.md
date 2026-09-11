---
name: cid-test
description: >-
  Selects and runs the minimal CID pytest set for modified files via
  cid-test-auditor. Use when explicitly invoked as cid-test, or when the user
  asks for targeted CID test audit before publication.
disable-model-invocation: true
---

# cid-test

Targeted CID test audit. `AGENTS.md` is authority.

## Workflow

1. `cd /opt/SERVICIOS_CINE && source .venv/bin/activate` (repo `.venv` only).
2. Read `AGENTS.md`. Inspect changed files (`git status --short`, `git diff --name-only`).
3. Invoke or follow project subagent `cid-test-auditor`.
4. Select the minimal related tests for the modified paths.
5. Run directed tests first, e.g.:
   `PYTHONPATH=src pytest <paths_or_-k> -q`
6. Run LMA regression only when the change justifies it.
7. Do not run full suite unless explicitly requested or risk is high.
8. Do not modify code or tests. Do not commit/tag/push.
9. Do not access real media roots E:/F: or run scanner/transcription on real media.

## Delivery

Return exactly:

```text
TEST_AUDIT_APPROVED=True/False
TEST_COMMANDS=
TEST_RESULTS=
FAILURES=
REGRESSION_RISK=
RECOMMENDED_NEXT_ACTION=
```

Include exact commands and exact outcomes. If tests fail: analyze and report; do not auto-fix files.
