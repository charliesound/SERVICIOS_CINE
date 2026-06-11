# CID AI Job Worker Mock Execution Wrapper — PostgreSQL Concurrency Contract v1

## Status

This document describes the current PostgreSQL concurrency and idempotency contract for the CID AI Job Worker Mock Execution Wrapper.

Base commit: `e8e7036 test: add CID AI job stale in-progress check`.

The contract is PostgreSQL-only and has been validated against a real `TEST_DATABASE_URL`.

## Scope

This contract covers the current mock execution wrapper for CID AI jobs.

Covered components:

- `AIJobWorkerMockExecutionService`
- `AIJobExecutionAttemptRepository`
- `AIJobExecutionAttempt`
- PostgreSQL-backed integration tests using independent sessions
- idempotency by execution attempt
- payload fingerprint validation
- terminal replay
- conflict handling
- `SELECT ... FOR UPDATE` locking behavior
- conservative `IN_PROGRESS` behavior

Out of scope:

- real queue execution
- external AI provider execution
- distributed worker orchestration
- cancellation API
- automatic stale attempt reclaim/retry
- credit compensation for real provider failures

## Idempotency key

The persisted idempotency key for mock worker execution is:

`organization_id + job_id + execution_attempt_id`

The database must enforce uniqueness for that tuple. This prevents duplicate persisted attempts for the same logical execution attempt.

## Payload fingerprint contract

Each execution command is fingerprinted.

The stored fingerprint distinguishes safe replay from conflicting reuse of the same execution attempt id with different payload.

Rules:

1. If an existing attempt has the same fingerprint and is terminal, the wrapper returns a replay result.
2. If an existing attempt has a different fingerprint, the wrapper rejects it with a controlled fingerprint mismatch error.
3. A mismatched fingerprint must not call the worker.
4. A mismatched fingerprint must not mutate the existing attempt row.

## PostgreSQL guarantees

The current contract depends on PostgreSQL behavior.

Required guarantees:

- unique constraint on `organization_id + job_id + execution_attempt_id`
- transaction isolation sufficient for conflicting inserts
- `SELECT ... FOR UPDATE` row locking
- independent sessions in integration tests
- no SQLite fallback

SQLite is not part of this contract.

## Savepoint and IntegrityError handling

The wrapper creates a new `AIJobExecutionAttempt` for first execution.

If a concurrent insert wins first, PostgreSQL raises an `IntegrityError` on the losing session because of the unique constraint.

The wrapper protects the insert with a nested transaction / savepoint:

`session.begin_nested()`

Contract:

1. The failed insert rolls back only the savepoint.
2. The outer session remains usable.
3. The wrapper then loads the existing attempt with `SELECT ... FOR UPDATE`.
4. The wrapper decides between terminal replay, fingerprint mismatch, or in-progress conflict.
5. The worker must not be called by the losing actor unless the wrapper safely owns the new attempt.

## SELECT ... FOR UPDATE behavior

When an existing attempt is found, the repository reads it using `SELECT ... FOR UPDATE`.

Contract:

1. If another transaction holds a row lock on the attempt, the wrapper waits.
2. The wrapper must not bypass the lock.
3. The wrapper must not call the worker while waiting on an existing terminal attempt.
4. After the lock is released, the wrapper must continue deterministically.
5. Terminal replay after lock release must not call the worker.

## IN_PROGRESS behavior

The current behavior is conservative.

If an existing attempt is `IN_PROGRESS`, the wrapper raises `AIJobWorkerMockExecutionInProgressError`.

This applies even if the attempt appears old/stale.

Current model limitations:

- no `expires_at`
- no `timeout_at`
- no explicit stale reclaim policy
- no automatic retry ownership transfer

Contract:

1. `IN_PROGRESS` does not call the worker.
2. `IN_PROGRESS` does not create a second attempt.
3. `IN_PROGRESS` does not mutate the existing fingerprint/status.
4. The session remains usable after the controlled error.
5. Any future stale reclaim policy must be introduced explicitly and tested separately.

## Test map

| Test | Guarantee |
|---|---|
| `test_first_execution_persists_attempt` | First execution creates and persists one attempt. |
| `test_terminal_replay_same_fingerprint_does_not_call_worker_again` | Same fingerprint terminal replay returns safely without calling worker again. |
| `test_fingerprint_mismatch_does_not_call_worker_again_or_mutate_row` | Different payload for same key is rejected without worker call or row mutation. |
| `test_in_progress_conflict_baseline_does_not_call_worker` | Existing `IN_PROGRESS` attempt produces controlled conflict and no worker call. |
| `test_concurrent_same_key_same_payload_calls_worker_at_most_once` | Same-key/same-payload concurrent calls execute worker at most once. |
| `test_concurrent_same_key_different_payload_rejects_mismatched_fingerprint` | Same-key/different-payload concurrent calls reject the loser with fingerprint mismatch/conflict and only one attempt persists. |
| `test_terminal_replay_waits_for_for_update_lock_without_calling_worker` | Terminal replay waits on PostgreSQL `FOR UPDATE` lock and does not call worker. |
| `test_stale_in_progress_attempt_does_not_duplicate_worker_or_attempt` | Stale/old `IN_PROGRESS` remains conservative: no worker call, no duplicate attempt, no mutation. |

## Known limitations

The current wrapper is safe for the mock execution path but is not yet a full distributed worker execution system.

Known limits:

1. No automatic stale `IN_PROGRESS` reclaim.
2. No attempt timeout ownership transfer.
3. No cancellation API.
4. No real queue contract.
5. No external AI provider contract.
6. No exactly-once guarantee across future distributed workers without additional queue/locking design.
7. No real provider compensation policy.
8. No full credit reservation/settlement integration in this wrapper contract.
9. No route/API contract documented here.
10. No tenant-facing cancellation or retry semantics.

## Recommended next phases

Recommended next phases:

1. `request_cancel_ai_job` / controlled cancellation contract.
2. timeout/reclaim policy for stale `IN_PROGRESS`.
3. real worker queue contract.
4. provider execution contract.
5. credit reservation and settlement integration for real execution.
6. API/route contract for job execution lifecycle.
7. operational observability: logs, metrics, attempt tracing and admin inspection.
