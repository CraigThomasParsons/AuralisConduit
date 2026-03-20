# Task 1: Auralis vera.json Poller

## Goals

- After Auralis dispatches a job to Krax, it polls for `vera.json` to appear
- Polling is non-blocking — Auralis can still handle other jobs

## Requirements

- Auralis tracks in-flight Krax jobs in a manifest file: `Auralis/runs/<auralis_job_id>/krax_tracking.json`
- `krax_tracking.json` contains: `krax_job_id`, `krax_runs_path`, `dispatched_at`, `attempt`, `max_attempts`
- Auralis polls every 30 seconds for `<krax_runs_path>/<krax_job_id>/vera.json`
- Timeout: 15 minutes; if vera.json not found, treat as fail with `status: timeout`
- On finding vera.json: load it and pass to loop decision logic (Task 2)

## Acceptance Criteria

- after dispatching to Krax, `krax_tracking.json` exists in Auralis runs
- when vera.json appears, Auralis detects it within 60 seconds
- on timeout, Auralis creates a synthetic vera.json with `status: error` and continues the loop

## Implementation Steps

1. In `auralis_server.py`, when writing krax job.json (Sprint1 Task 1): also write `krax_tracking.json`.
2. Add a background polling thread or async task in Auralis server:
   - load all `runs/*/krax_tracking.json` files
   - for each without a verdict yet: check for `vera.json`
   - on find: call `handle_vera_verdict(tracking, verdict)`
   - on timeout: synthesize `{status: error, ...}` and call `handle_vera_verdict`
3. Mark verdict as handled in `krax_tracking.json`: add `verdict_received_at`.

## Handoff Artifacts

- auralis_server.py updated with poller
