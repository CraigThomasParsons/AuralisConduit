# Task 4: Real Vera — vera.json Writer and Loop Signal

## Goals

- Write the final `vera.json` from evidence + evaluator output
- Signal Auralis that the verdict is ready (file presence is the signal)
- Retire fake_vera once real Vera is verified

## Requirements

- `vera.json` is written atomically to `Krax/runs/<job_id>/vera.json`
- it contains all fields from Sprint0 Vera→Auralis contract
- screenshot paths in `screenshots` field are absolute paths Auralis can read
- `evaluated_at` is a real timestamp
- once real Vera is verified, fake_vera polling is disabled (config flag)

## Acceptance Criteria

- `vera.json` exists at `Krax/runs/<job_id>/vera.json` after real Vera processes a job
- file validates against Sprint0 contract schema
- `screenshots` paths exist (not empty strings)
- switching `vera.mode: real` in config routes to real Vera; `fake` routes to fake_vera

## Implementation Steps

1. Add to `Vera/config.yaml`: `vera: {mode: fake}` — switch to `real` when ready.
2. In `vera_daemon.py`, assemble final `vera.json`:
   - `job_id` from krax_output
   - `status` from evaluator
   - `logs` from command_runner stdout/stderr
   - `screenshots` from evidence paths (absolute)
   - `observations` from evaluator
   - `confidence` from evaluator
   - `evaluated_at` = now UTC ISO-8601
   - `evaluator` = model name from config
3. Write atomically: write to `.vera.json.tmp`, rename to `vera.json`.
4. Log: `[TYS] Vera verdict written: <job_id> status=<status> confidence=<confidence>`.
5. After verifying real Vera works, add note to this file and set `mode: real` in config.

## Handoff Artifacts

- vera_daemon.py updated
- vera.json sample for a real job appended to Completion Notes
- fake_vera retirement note (when real Vera verified)
