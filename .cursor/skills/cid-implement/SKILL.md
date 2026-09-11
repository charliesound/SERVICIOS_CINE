---
name: cid-implement
description: >-
  Executes low/medium-risk CID implementations with the accelerated flow.
  Use when explicitly invoked as cid-implement, or when the user asks for a
  bounded CID implementation using OBJECTIVE / AUTHORIZED FILES / REQUIRED
  BEHAVIOR / FORBIDDEN AREAS / TESTS / STOP CONDITION.
disable-model-invocation: true
---

# cid-implement

Accelerated CID implementation for low/medium risk. `AGENTS.md` is authority.

## Required input blocks

Ask for any missing block, then use all six:

```text
OBJECTIVE
AUTHORIZED FILES
REQUIRED BEHAVIOR
FORBIDDEN AREAS
TESTS
STOP CONDITION
```

## Workflow

1. `cd /opt/SERVICIOS_CINE && source .venv/bin/activate`
2. Read `AGENTS.md`. Run `git status --short`.
3. Implement only under AUTHORIZED FILES.
4. Follow REQUIRED BEHAVIOR. Respect FORBIDDEN AREAS.
5. Hard bans unless OBJECTIVE explicitly authorizes otherwise:
   - no `git add` / commit / tag / push
   - no real media access (E:/F: roots, scanner, transcription)
   - no DB / migrations
   - no package/install/uninstall
   - no persistent state mutation outside authorized files
6. Run TESTS as directed (prefer targeted `PYTHONPATH=src pytest … -q`).
7. End with `git diff` + `git status --short`.
8. Stop before publication. Honor STOP CONDITION.

## Delivery

Report: what changed, commands/results, remaining risks, and that publication was not performed.
