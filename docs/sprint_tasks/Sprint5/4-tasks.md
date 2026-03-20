# Task 4: Loop Status Dashboard Script

## Goals

- A single script shows the current state of all in-flight and recent jobs
- Human can run it at any time to understand what the system is doing

## Requirements

- script: `Auralis/tools/loop_status.py`
- output: table with columns: job_id, stage, status, attempt, age, last_event
- stages: auralis | krax | vera | done | failed | escalated
- reads from: Auralis runs/, Krax runs/, escalated/
- no dependencies beyond stdlib and existing project dirs

## Acceptance Criteria

- `python3 tools/loop_status.py` runs without error on a fresh terminal
- output shows at least one row for any in-flight or recently completed job
- `--failed` flag shows only failed/escalated jobs

## Implementation Steps

1. Create `Auralis/tools/loop_status.py`:
   - scan `Auralis/runs/*/krax_tracking.json` for in-flight jobs
   - scan `Auralis/archive/*/loop_result.json` for completed jobs (last 24h)
   - scan `Auralis/inbox/escalated/*/escalation.json` for escalated jobs
   - cross-reference with `Krax/runs/*/receipt.json` and `Krax/runs/*/vera.json`
   - print summary table using stdlib tabulate or simple column alignment
2. Add `--failed` flag to filter to failed/escalated only.
3. Add `--job <job_id>` to show full detail for a single job.

## Handoff Artifacts

- `Auralis/tools/loop_status.py` created
- sample output in Completion Notes
