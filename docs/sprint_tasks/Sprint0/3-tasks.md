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

## Completion Notes (2026-03-20)

Task complete.

### Canonical Location

- `Krax/runs/<job_id>/vera.json`

### Schema

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `schema_version` | str | yes | none | Contract version. Must be `v1`. |
| `job_id` | str (UUID4) | yes | none | The Krax job ID being evaluated. |
| `correlation_id` | str (UUID4) | yes | none | Stable logical request identifier shared across Auralis, Krax, and Vera. |
| `attempt` | int | yes | none | 1-based execution attempt being judged. |
| `status` | enum | yes | none | One of `pass`, `fail`, `partial`, `error`. |
| `logs` | list[str] | yes | `[]` | Relevant stdout, stderr, or daemon log lines from validation. |
| `screenshots` | list[str] | no | `[]` | Evidence capture paths. Can be empty for non-visual or early-fail cases. |
| `observations` | list[object] | yes | none | Structured findings used by Auralis for reflection or escalation. |
| `confidence` | float | yes | none | Value in `[0.0, 1.0]` representing evaluator confidence. |
| `evaluated_at` | str (ISO-8601 UTC) | yes | none | When Vera finalized the verdict. |
| `evaluator` | str | no | `"fake_vera"` or configured model name | Which evaluator produced the verdict. |
| `metadata` | dict | no | `{}` | Reserved for additive evidence and runtime metadata. |

### Observation Shape

Each item in `observations` must have this shape:

```json
{
   "check": "string",
   "result": "pass | fail",
   "detail": "string"
}
```

### Example Payload

```json
{
   "schema_version": "v1",
   "job_id": "4c47825f-70d1-4e8d-a1c0-f5fc0dc1b98a",
   "correlation_id": "c6530d5c-0ef3-4223-9d8c-3a7f9c7817f2",
   "attempt": 1,
   "status": "fail",
   "logs": [
      "python3 extracted/add_two_numbers.py",
      "AssertionError: expected 2, got 3"
   ],
   "screenshots": [
      "/home/craigpar/Code/Vera/evidence/4c47825f-70d1-4e8d-a1c0-f5fc0dc1b98a/screenshot.png"
   ],
   "observations": [
      {
         "check": "Function returns requested value.",
         "result": "fail",
         "detail": "Observed return value did not match expected output."
      },
      {
         "check": "Module imports without error.",
         "result": "pass",
         "detail": "Import completed successfully."
      }
   ],
   "confidence": 0.92,
   "evaluated_at": "2026-03-20T20:25:00Z",
   "evaluator": "gpt-4o",
   "metadata": {
      "evidence_root": "/home/craigpar/Code/Vera/evidence/4c47825f-70d1-4e8d-a1c0-f5fc0dc1b98a"
   }
}
```

### Auralis Polling Policy

- Auralis polls for `Krax/runs/<job_id>/vera.json` every 5 seconds.
- Poll timeout is 10 minutes from Krax dispatch time.
- If timeout expires, Auralis synthesizes a timeout verdict equivalent to:
   - `status = error`
   - `logs = ["Timed out waiting for vera.json"]`
   - `observations = [{"check": "vera_timeout", "result": "fail", "detail": "No verdict arrived within 10 minutes."}]`
- Timeout handling must feed the same loop decision path as any other fail/error verdict.

### Loop Decision Table

| Vera status | Attempt state | Auralis action |
|-------------|---------------|----------------|
| `pass` | any | Archive job, write loop result, stop |
| `fail` | `attempt < 3` | Build reflection prompt and dispatch a new Krax job |
| `fail` | `attempt >= 3` | Escalate to human inbox and stop |
| `partial` | any | Treat as fail |
| `error` | any | Treat as fail |

### Error Semantics

- Auralis must reject any verdict missing a required field.
- Auralis must reject any verdict where `schema_version != "v1"`.
- Auralis must reject any verdict where `status` is not one of the four allowed enum values.
- Auralis must reject any verdict where `confidence` is outside `[0.0, 1.0]`.
- Auralis must reject any verdict where `observations` is not a list of structured objects.
- Invalid verdicts are treated as `status = error` and routed through the normal retry/escalation path.

### Arcane Compatibility Notes

- `status` maps cleanly to a future Arcane validation or review-stage terminal outcome.
- `attempt` and `correlation_id` remain directly reusable for Arcane retry and traceability semantics.
- `observations` is intentionally structured so it can later become stage review findings or blocker reasons in Arcane.
- Escalation after retry exhaustion mirrors Arcane user-action-required semantics and should remain explicit rather than implicit daemon behavior.

**Status: COMPLETE**
