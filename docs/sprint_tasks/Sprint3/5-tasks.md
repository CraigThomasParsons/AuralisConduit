# Task 5: End-to-End Vera Smoke Test

## Goals

- Run a full Auralis→Krax→Vera cycle and verify verdicts are produced correctly
- Test both fake and real Vera paths

## Requirements

- Phase A test: fake_vera produces vera.json with status=pass within 30 seconds
- Phase B test: real Vera produces vera.json with real status, confidence, screenshots

## Implementation Steps

1. Phase A test:
   - Drop test job in Auralis inbox
   - Wait for `krax_output.json` (Sprint2 path)
   - Wait for `vera.json` — verify `status: pass`, `confidence: 1.0`
   - PASS

2. Phase B test:
   - Switch Vera config to `mode: real`
   - Drop test job with simple goal: "Write a Python script that prints 'Hello TYS Loop'"
   - Wait for vera.json
   - Verify: `status` is pass or fail (either is acceptable — real evaluation)
   - Verify: `screenshots` list is non-empty, paths exist
   - Verify: `observations` has at least one entry
   - PASS regardless of status — we're testing the plumbing, not the code quality

3. Document results in Completion Notes.

## Handoff Artifacts

- smoke test results recorded in Completion Notes
- any Vera config changes recorded
