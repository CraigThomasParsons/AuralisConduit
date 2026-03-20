# Task 5: Overnight Resilience Test

## Goals

- Run the system unattended for 1+ hours with multiple jobs and verify no stuck states

## Requirements

- queue 5 jobs in Auralis inbox
- all Auralis, Krax, and Vera daemons running as systemd user services
- no human intervention during the test window
- after 1 hour: check loop_status.py shows all jobs in terminal state (done, failed, or escalated)
- zero stuck jobs (in-flight jobs older than 30 minutes are a failure)

## Acceptance Criteria

- all 5 jobs reach a terminal state within 90 minutes
- no agent daemon has crashed (check systemd status)
- audit.jsonl exists for each job with no gaps in event sequence
- loop_status.py shows correct terminal state for each job

## Implementation Steps

1. Ensure all three daemons are running as systemd user services:
   - `systemctl --user status auralis-server`
   - `systemctl --user status krax-server` (if set up)
   - `systemctl --user status vera`
2. Queue 5 test jobs in Auralis inbox with varied goals.
3. Start test at a known time and note the time.
4. After 90 minutes: run `loop_status.py` and record output.
5. Check all 5 jobs for terminal state.
6. Check daemon health: `systemctl --user status auralis-server krax-server vera`.
7. Record pass/fail and any anomalies in Completion Notes.

## Handoff Artifacts

- loop_status.py output at 90-minute mark in Completion Notes
- daemon status output in Completion Notes
- this is the Sprint5 exit gate and system MVP acceptance
