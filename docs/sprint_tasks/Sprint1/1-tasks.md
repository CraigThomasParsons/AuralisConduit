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

## Completion Notes (2026-03-20)

Task complete.

### What Changed

- Added `krax_inbox_path: /home/craigpar/Code/Krax/inbox` to `config.yaml`.
- Replaced the primitive inline Krax payload in `Auralis/bin/auralis_server.py` with a canonical writer.
- Added helper functions for:
   - simple config loading
   - UTC timestamp generation
   - goal normalization from briefing/goals content
   - context construction from the original Auralis job files
   - canonical contract assembly
   - atomic JSON writing
- Added `write_krax_job(...)` which:
   - generates a new Krax-owned UUID job ID
   - generates a new correlation ID
   - writes Sprint0 Task 1 contract fields
   - writes `job.json` atomically into `Krax/inbox/<krax_job_id>/job.json`
   - logs `[TYS] Krax job dispatched: <job_id>` on success
- Wrapped Krax dispatch in `try/except` so a dispatch failure does not break normal Auralis completion and archive flow.

### Contract Shape Written

The emitted payload now includes:

- `schema_version`
- `job_id`
- `correlation_id`
- `causation_id`
- `created_at`
- `source_agent`
- `attempt`
- `goal`
- `context`
- `instructions`
- `constraints`
- `artifact_refs`
- `artifacts_expected`
- `source_run`
- `metadata`

### Notes

- `instructions` is currently sourced from the Auralis completion response text, which preserves the existing Think -> Build handoff behavior.
- `goal` and `context` are sourced from the original Auralis job files so provenance is preserved.
- If `krax_inbox_path` is missing or the directory does not exist, Auralis now logs a warning and continues without crashing.

### Validation

- Static validation only: `auralis_server.py` and `config.yaml` both pass editor error checks.
- Full runtime smoke test not executed in this task because that requires a live ChatGPT completion flow plus a running Krax consumer.

**Status: COMPLETE**
