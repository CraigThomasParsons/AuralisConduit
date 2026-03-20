# Task 2: Auralis Loop Decision Logic

## Goals

- Implement `handle_vera_verdict()` that decides what happens next
- Pass: archive and done. Fail: regenerate. Max attempts: escalate.

## Requirements

- decision is purely based on `vera.json` status and `attempt` count
- decision is logged with full context (job_id, status, attempt, action taken)
- each path (pass, fail, escalate) writes a status file for observability

## Acceptance Criteria

- pass: `Auralis/archive/<job_id>/loop_result.json` written with `outcome: pass`
- fail (< max_attempts): new Krax job dispatched with incremented `attempt`
- fail (>= max_attempts): job moved to escalated, `escalation.json` written with all attempt history

## Implementation Steps

1. Implement `handle_vera_verdict(tracking: dict, verdict: dict)`:
   ```
   if verdict.status == "pass":
       → archive_loop(tracking, verdict)
   elif tracking.attempt < tracking.max_attempts:
       → redispatch_to_krax(tracking, verdict)
   else:
       → escalate(tracking, verdict)
   ```
2. Implement `archive_loop`: write `loop_result.json`, move to archive.
3. Implement `escalate`:
   - collect all attempt verdicts into `escalation.json`
   - move to `Auralis/inbox/escalated/<job_id>/`
   - log at WARNING level
4. Implement `redispatch_to_krax`:
   - increment `attempt` in tracking
   - generate reflection prompt (Task 3)
   - drop new Auralis job in inbox with revised briefing
   - or directly write new Krax job.json with incremented attempt

## Handoff Artifacts

- loop decision logic implemented in auralis_server.py
