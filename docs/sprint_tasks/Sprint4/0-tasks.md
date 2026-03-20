# Task 0: Scope Lock and Loop Design Review

## Goals

- Confirm Sprint3 is complete (vera.json is being written for real jobs)
- Review the loop state machine before implementing
- Confirm max-attempts logic and escalation path

## Requirements

- Sprint3 smoke test (Phase B) passes
- Loop state machine is documented: states, transitions, terminal states
- Escalation path is confirmed: where do escalated jobs go, how does human re-inject them

## Implementation Steps

1. Confirm Sprint3 Phase B: vera.json exists with real status for a real job.
2. Document loop state machine:
   - States: DISPATCHED → VERA_PENDING → PASS (terminal) | FAIL | MAX_ATTEMPTS (terminal) | ESCALATED (terminal)
   - Transitions: on vera.json status
3. Confirm max attempts = 3 (configurable).
4. Confirm escalation: move to `Auralis/inbox/escalated/<job_id>/` with `escalation.json` summarizing all attempts.
5. Note: the `attempt` counter lives in the job.json and increments on each Krax re-dispatch.

## Handoff Artifacts

- state machine diagram appended to this file under Completion Notes
