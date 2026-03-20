# Task 1: Fake Vera — Reads krax_output, Writes vera.json

## Goals

- Patch `fake_vera.py` to read `krax_output.json` and write a valid `vera.json`
- This enables the full loop to run end-to-end before real testing is ready
- `vera.json` must conform to Sprint0 Vera→Auralis contract

## Requirements

- Vera polls `Krax/runs/` for new `krax_output.json` files not yet processed
- `vera.json` is written to `Krax/runs/<job_id>/vera.json`
- `status` is always `pass` for fake Vera
- `confidence` is `1.0` (fake certainty)
- `observations` contains one entry: `{check: "fake_pass", result: "pass", detail: "Fake Vera always passes"}`

## Acceptance Criteria

- after `krax_output.json` appears → `vera.json` appears within 30 seconds
- `vera.json` validates against Sprint0 Vera→Auralis contract
- fake_vera does not crash if `krax_output.json` is malformed — writes `status: error` instead

## Implementation Steps

1. Add config to `Vera/config.yaml`: `krax_runs_path: /home/craigpar/Code/Krax/runs`
2. Rewrite `Vera/bin/fake_vera.py` as a polling daemon:
   - scan `krax_runs_path/*/krax_output.json` for files with no sibling `vera.json`
   - for each: read and validate, write `vera.json` in Sprint0 format
   - poll every 10 seconds
3. Implement `write_vera_json(job_id, runs_path, status, observations, confidence)`.
4. On malformed krax_output: write `vera.json` with `status: error`, `observations: [{check: "input_validation", result: "fail", detail: "<error>"}]`.
5. Log: `[TYS] Vera verdict written: <job_id> status=pass`.

## Handoff Artifacts

- `Vera/bin/fake_vera.py` updated
- sample vera.json written and validated
