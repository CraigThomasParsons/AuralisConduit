# Task 4: End-to-End Loop Smoke Test

## Goals

- Run one complete Think→Yield→Ship→Reflect cycle without human intervention
- Verify the loop actually closes: pass archives, fail re-dispatches

## Requirements

- test 1: job that will pass — verify archive and loop_result.json
- test 2: job that will fail — verify reflection briefing is generated and second Krax job is dispatched
- test 3: job that fails 3 times — verify escalation path

## Implementation Steps

1. Test 1 — Pass path:
   - Drop job: "Write a Python function that returns 42"
   - Monitor: Auralis→Krax→Grok→krax_output→Vera→vera.json→loop_result
   - Assert: `Auralis/archive/<id>/loop_result.json` with `outcome: pass`
   - Time: allow up to 20 minutes

2. Test 2 — Fail path (use fake Vera for predictability):
   - Temporarily patch fake_vera to always return `status: fail`
   - Drop job
   - Assert: reflection briefing appears in Auralis inbox
   - Assert: second Krax job dispatched with `attempt: 2`

3. Test 3 — Escalation:
   - Configure `max_attempts: 1` for test
   - Drop job with fake Vera returning fail
   - Assert: `Auralis/inbox/escalated/<job_id>/escalation.json` exists

4. Record all three results in Completion Notes.
5. Restore fake_vera to `status: pass` and restore `max_attempts: 3`.

## Handoff Artifacts

- test results for all three scenarios in Completion Notes
- this is the Sprint4 exit gate — all three must pass
