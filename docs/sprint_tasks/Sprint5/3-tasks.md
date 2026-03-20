# Task 3: Unified Audit Trail

## Goals

- Every job's full journey is recorded in a single human-readable audit file
- Audit covers: Auralis pick-up → Krax dispatch → Grok response → Vera verdict → loop decision

## Requirements

- audit file: `Auralis/runs/<auralis_job_id>/audit.jsonl` — append-only, one event per line
- each event has: `ts`, `agent`, `event`, `job_id`, `detail`
- events: `auralis.job_started`, `auralis.krax_dispatched`, `krax.job_received`, `krax.grok_complete`, `vera.verdict`, `auralis.loop_pass`, `auralis.loop_fail`, `auralis.escalated`
- audit is not used for control flow — it is observation-only

## Acceptance Criteria

- run a full loop → `audit.jsonl` has all expected events in chronological order
- events are valid JSON lines (each line parses independently)
- `cat audit.jsonl | python3 -c "import sys,json; [json.loads(l) for l in sys.stdin]"` exits 0

## Implementation Steps

1. Create shared `AuditLogger` class (duplicated with version stamp in each agent):
   - `log(agent, event, job_id, detail)` — appends to the configured audit file
2. Each agent appends to its own audit log:
   - Auralis: `Auralis/runs/<auralis_id>/audit.jsonl`
   - Krax: `Krax/runs/<krax_id>/audit.jsonl`
   - Vera: `Vera/evidence/<krax_id>/audit.jsonl`
3. On loop pass: Auralis merges Krax and Vera audit files into the canonical audit.jsonl.

## Handoff Artifacts

- AuditLogger implemented in all three agents
- sample audit.jsonl for a full loop in Completion Notes
