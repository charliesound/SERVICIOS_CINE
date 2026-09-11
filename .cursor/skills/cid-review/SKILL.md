---
name: cid-review
description: >-
  Reviews CID diffs against authorized scope and AGENTS.md before closure or
  publication. Use when explicitly invoked as cid-review, or when the user asks
  for a CID code review / pre-publication review without editing files.
disable-model-invocation: true
---

# cid-review

Read-only CID review before considering work closed. `AGENTS.md` is authority.

## Workflow

1. `cd /opt/SERVICIOS_CINE && source .venv/bin/activate`
2. Read `AGENTS.md`.
3. Inspect scope: authorized paths vs actual changes (`git status --short`, `git diff`, `git diff --cached`).
4. Run `git diff --check` (and `git diff --cached --check` if staged).
5. Invoke or recommend the project subagent `cid-code-reviewer` for an independent pass.
6. Do not modify files. Do not commit, tag, or push.

## Check for

- bugs / regressions
- changes outside authorized scope
- unauthorized media access risk
- accidental persistence
- DB / migrations
- Windows/WSL path mistakes
- security issues
- behavior without test coverage

## Delivery

Return exactly:

```text
APPROVED=True/False
# or NOT_APPROVED when False

FINDINGS=
RISK_LEVEL=
UNAUTHORIZED_SCOPE=
RECOMMENDED_FIXES=
```

Use `APPROVED=True` only when the diff is safe and in scope. Otherwise `APPROVED=False` / `NOT_APPROVED`.
