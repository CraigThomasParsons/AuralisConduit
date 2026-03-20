# Task 4: End-to-End Dispatch Smoke Test

## Goals

- Run a real Auralis→Krax dispatch and verify the receipt exists
- Document the smoke test procedure so it can be repeated

## Requirements

- test uses a real job dropped in Auralis inbox
- test asserts `Krax/runs/<job_id>/receipt.json` is written within 30 seconds
- test asserts receipt contains `status: received`
- test is a script that can be re-run

## Acceptance Criteria

- smoke test script exits 0 on success, non-zero on failure
- passing the test proves Sprint1 is complete

## Implementation Steps

1. Write `Krax/tools/smoke_test_dispatch.sh` (or `.py`):
   - create a test job in `Auralis/inbox/test_<uuid>/briefing.md`
   - wait up to 60 seconds for `Krax/runs/*/receipt.json` to appear
   - verify `status == "received"` in receipt
   - print PASS or FAIL with details
2. Run the smoke test with both Auralis and Krax servers running.
3. Record the output in this file under Completion Notes.
4. If it fails, document the failure and fix before marking sprint complete.

## Handoff Artifacts

- `Krax/tools/smoke_test_dispatch.sh` created
- test output recorded in Completion Notes
