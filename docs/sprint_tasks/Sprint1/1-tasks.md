# Task 1: Auralis Post-Completion Job Writer

## Goals

- Patch `auralis_server.py` to write a `job.json` to Krax's inbox after each completed job
- The written file must conform to the Sprint0 Auralis→Krax contract

## Requirements

- job.json is written atomically (write to temp, rename)
- job.json is placed at `Krax/inbox/<job_id>/job.json`
- `job_id` is a new UUID4 (not the Auralis job ID — Krax owns its own identity)
- `goal`, `context`, and `instructions` are derived from the Auralis job briefing
- `source_run` points to the Auralis run directory
- Auralis continues to work normally if Krax inbox path does not exist (log, skip)

## Acceptance Criteria

- after a job completes in Auralis, `Krax/inbox/<job_id>/job.json` exists and is valid JSON
- JSON validates against the Sprint0 contract schema
- if Krax inbox is unreachable, Auralis logs a warning and continues — no crash

## Implementation Steps

1. Add a config key to `Auralis/config.yaml`: `krax_inbox_path: /home/craigpar/Code/Krax/inbox`
2. In `auralis_server.py`, after the archive step, call `write_krax_job(run_dir, config)`.
3. Implement `write_krax_job`:
   - build job dict from Sprint0 contract
   - derive `instructions` from `runs/<id>/briefing.md` content
   - derive `goal` from first non-empty line of briefing or a `goal.md` if present
   - write to `<krax_inbox_path>/<new_uuid>/job.json` atomically
4. Log: `[TYS] Krax job dispatched: <job_id>` on success.
5. Wrap in try/except — failure must not break Auralis completion flow.

## Handoff Artifacts

- patch applied to auralis_server.py
- config.yaml updated with krax_inbox_path
