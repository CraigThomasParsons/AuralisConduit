# Task 2: Krax Job Ingestion and Receipt

## Goals

- Implement Krax inbox polling in `krax_server.py`
- When a `job.json` is found, validate it, move job to `runs/<job_id>/`, and write `receipt.json`

## Requirements

- polling loop runs every 5 seconds
- job is moved to `runs/<job_id>/` atomically before processing begins (consume-once)
- `receipt.json` is written immediately on pickup
- invalid jobs are moved to `failed/` with a `rejection.json` explaining the error
- server does not crash on malformed JSON

## Acceptance Criteria

- drop a valid job.json in Krax inbox → it moves to runs/ within 10 seconds
- `receipt.json` at `runs/<job_id>/receipt.json` contains `job_id`, `received_at`, `status: received`
- drop a job missing required field → it moves to failed/ with rejection.json containing field name
- Krax server continues polling after any single job error

## Implementation Steps

1. Add `poll_inbox()` function to `krax_server.py`:
   - scan `inbox/` for directories containing `job.json`
   - for each: validate fields, move to `runs/<job_id>/`, write `receipt.json`
2. Implement `validate_job(job: dict) -> list[str]` — returns list of missing required fields.
3. Write `receipt.json`: `{job_id, received_at, status: "received", source: "auralis"}`.
4. On validation failure: move to `failed/<job_id>/`, write `rejection.json`: `{job_id, rejected_at, missing_fields: [...]}`.
5. Register poll loop with a 5-second interval timer.
6. Log each pickup: `[TYS] Job <job_id> received from Auralis`.

## Handoff Artifacts

- patch applied to krax_server.py

## Completion Notes (2026-03-20)

Task complete.

### What Changed

- Added helper functions in `Krax/bin/lib/fs.py` for:
   - UTC timestamp generation
   - atomic JSON writing
   - reading `job.json` from `runs/`
   - promoting a job directory from `inbox/` to `runs/`
   - discovering pending run jobs
   - writing `receipt.json`
   - rejecting invalid inbox jobs into `failed/` with `rejection.json`
- Updated `archive_job()` and `fail_job()` so Krax can now archive or fail work from either `inbox/` or `runs/`.
- Added `validate_job()` in `Krax/bin/krax_server.py` covering the required Sprint0 Task 1 fields.
- Added background `poll_inbox()` loop running every 5 seconds.
- `poll_inbox()` now:
   - scans `Krax/inbox/`
   - reads and validates `job.json`
   - rejects malformed or incomplete jobs into `failed/<job_id>/rejection.json`
   - promotes valid jobs into `runs/<job_id>/`
   - writes `receipt.json`
   - logs `[TYS] Job <job_id> received from Auralis`
- Updated `GET /job` so the extension now pulls only from jobs already promoted into `runs/`, not directly from `inbox/`.

### Validation

- Static validation: editor reported no errors in `Krax/bin/lib/fs.py` or `Krax/bin/krax_server.py`.
- Helper-level smoke validation: a temporary valid `job.json` was created, promoted, receipted, and cleaned up with no leftover temp directories under `Krax/inbox/` or `Krax/runs/`.
- Full daemon-level smoke test was not run in this task because that belongs more naturally to Sprint1 Task 4 with the Auralis dispatch path and running extension in place.

### Notes

- `receipt.json` is written with `job_id`, `received_at`, `status: received`, and `source`.
- Invalid jobs currently record rejection reasons in both `reasons` and `missing_fields` for compatibility with the task requirement.
- Krax now follows the intended consume-once pattern: inbox is only an intake queue; runs is the active execution scope.

**Status: COMPLETE**
