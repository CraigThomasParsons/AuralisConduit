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
