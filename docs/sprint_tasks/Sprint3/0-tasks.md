# Task 0: Scope Lock and Vera Baseline

## Goals

- Confirm Sprint2 is complete (krax_output.json is being written correctly)
- Read Vera's current `fake_vera.py` and `vera_daemon.py` to understand starting point
- Identify what needs to change for Phase A (fake) and Phase B (real)

## Requirements

- Sprint2 smoke test passes before Sprint3 begins
- Vera's existing `fake_vera.py` output format is documented
- Vera's existing `vera_daemon.py` architecture is understood
- Phase A vs Phase B scope is confirmed

## Implementation Steps

1. Confirm Sprint2: `Krax/runs/<job_id>/krax_output.json` exists for a real Grok run.
2. Read `Vera/bin/fake_vera.py` — document its current input/output.
3. Read `Vera/bin/vera_daemon.py` — document polling model, evidence capture, evaluator call.
4. Confirm Phase A scope: fake_vera only reads krax_output.json path and writes vera.json.
5. Confirm Phase B scope: real test execution, screenshot, Vision LLM.
6. Confirm Vera polls `Krax/runs/*/krax_output.json` — path agreement with Krax.

## Handoff Artifacts

- baseline notes appended to this file under Completion Notes
