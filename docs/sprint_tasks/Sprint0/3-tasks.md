# Task 3: Vera → Auralis Contract

## Goals

- Produce the canonical JSON schema for the verdict Vera returns to Auralis
- This contract governs Sprint3 (Vera) and Sprint4 (loop closure) — freeze it here

## Requirements

- `status` is an enum — no free-form strings
- `confidence` is a float 0.0–1.0 from the Vision LLM
- `observations` is a list of structured objects, not a blob of text
- file location is canonical and Auralis knows to poll it

## Acceptance Criteria

- schema is complete enough for Auralis to make a loop decision from status alone
- `status` enum is fully defined: pass, fail, partial, error
- `observations` has enough structure for Auralis to build a meaningful reflection prompt
- Auralis polling strategy is documented (poll interval, timeout, what to do on timeout)
- schema notes how Vera verdict states map to Arcane validation or review stage outcomes

## Implementation Steps

1. Draft the schema with these fields at minimum:
   - `job_id` (UUID4, required)
   - `status` (enum: pass | fail | partial | error, required)
   - `logs` (list[str], required — stdout/stderr lines)
   - `screenshots` (list[str], optional — paths to evidence captures)
   - `observations` (list[{check: str, result: pass|fail, detail: str}], required)
   - `confidence` (float 0.0–1.0, required — from Vision LLM)
   - `evaluated_at` (ISO-8601 UTC, required)
   - `evaluator` (str, optional — which Vision LLM was used)
2. Confirm file location: `Krax/runs/<job_id>/vera.json`.
   (Vera writes here; Auralis polls here — shared via Krax runs/ directory)
3. Define Auralis polling: poll every 5s, timeout at 10 minutes, write `vera_timeout.json` if expired.
4. Define loop decision table:
   - pass → archive job, done
   - fail + attempts < 3 → Auralis generates revised prompt, new Krax job
   - fail + attempts >= 3 → escalate to human inbox, stop loop
   - partial → treat as fail
   - error → treat as fail
5. Add Arcane compatibility notes for validation verdicts, retry exhaustion, and user-escalation semantics.

## Handoff Artifacts

- Finalized schema and loop decision table appended to this file under Completion Notes
