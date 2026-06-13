---
name: ailink-sync-dialogue-product-guard
description: Use this skill when working on AILink Sync Dialogue product scope, demo/beta claims, privacy boundaries, local-first positioning, and separation from CID SaaS.
---

# AILink Sync Dialogue Product Guard

Use this skill for AILink Sync Dialogue phases that affect product scope,
positioning, commercial claims, demo readiness, beta wording, privacy promises,
or separation from CID SaaS.

## Product Boundary

AILink Sync Dialogue is an independent tool, not CID SaaS. It is local-first and
its current state is beta/demo controlada, not a final product.

Keep three concepts separate:

- Independent tool: AILink Sync Dialogue.
- Future integration inside CID: a possible later bridge, only if a future phase
  explicitly designs and validates it.
- Integral SaaS CID: CID — Cinematic Intelligence Direction, the authenticated
  SaaS platform with its own contracts, tenants, plans, modules, credits, jobs,
  and runtime boundaries.

Do not use AILink Sync Dialogue as proof that CID SaaS is production-ready. This
skill does not turn AILink Sync Dialogue into proof of CID SaaS maturity.

## Allowed Scope When The Phase Permits It

This skill may guide work on:

- Documentation.
- Demo material.
- Reports.
- Scanner behavior.
- Matching behavior.
- Exports.
- Tests for AILink Sync Dialogue.

Only work on those areas when the active phase explicitly allows them. Before
editing, require explicit no-goals, allowed files, validation commands, and a
clear final state.

## Claims Guard

Keep commercial claims prudent and evidence-based.

Do not promise:

- Final automatic synchronization.
- Final automatic editing.
- Real DaVinci/Avid/Premiere integration when it is not implemented.
- Cloud processing.
- Production public release.
- A final installable product unless a later phase validates that claim.

Use wording such as beta/demo controlada, local-first, private demo, evidence
baseline, or limited pilot when that matches the phase.

## Privacy Guard

Preserve privacy by default.

- Do not upload real audiovisual material.
- Do not promise cloud processing.
- Do not require customer footage to leave the customer's local environment.
- Do not include private footage, paths, exports, metadata dumps, or sensitive
  production material in docs, tests, fixtures, or generated artifacts.

## Separation From Sensitive CID Areas

Do not mix AILink Sync Dialogue with:

- CRM.
- Payments.
- Public landing activation.
- Productive VPS.
- CID backend runtime.
- CID billing, tenants, plans, credits, jobs, or module access.
- Docker, Alembic, `.env`, models, DB, payments, configuration, or operational
  scripts.

This skill does not authorize changes to backend runtime, frontend runtime,
Docker, Alembic, `.env`, models, DB, payments, configuration, or operational
scripts.

## Review Discipline

When a phase includes commercial claims, demo-public wording, launch material, or
public-facing beta copy, recommend OpenCode or another independent reviewer as an external auditor before the phase is closed. The auditor reviews claims, demo pública, and product risks; the auditor does not need to edit the repo.

Future AILink Sync Dialogue skills require their own explicit phase.

Maintain the operating rule: un agente escribe, otro audita.

## Required Before Editing

Before changing any file, confirm:

1. The phase ID.
2. Whether the work is documentation/test-only or runtime-authorized.
3. The allowed files.
4. Explicit no-goals.
5. The exact claims that are allowed and forbidden.
6. Privacy constraints and fixture constraints.
7. Validation commands.
8. Whether OpenCode or another reviewer must audit claims before closing.

If those items are missing, stop and ask for phase clarification before editing.
