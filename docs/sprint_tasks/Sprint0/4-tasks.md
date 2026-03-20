# Task 4: Filesystem Layout and Gap Register

## Goals

- Produce one canonical directory diagram that all three agents reference
- List every gap between current agent state and TYS loop requirements

## Requirements

- diagram covers all three agent repos and the shared run directory
- gap register names the owning agent, the gap, the severity, and the delivering sprint
- no ambiguity about where files are written vs read

## Acceptance Criteria

- diagram is complete — an implementer can set up the filesystem from it alone
- gap register covers every missing piece with a sprint owner
- no two agents have conflicting assumptions about where a shared file lives

## Implementation Steps

1. Produce the filesystem diagram covering:
   - `Auralis/inbox/`, `Auralis/runs/`, `Auralis/archive/`
   - `Krax/inbox/`, `Krax/runs/`
   - `Vera/evidence/`, `Vera/verdicts/`
   - shared `Krax/runs/<job_id>/` as the handoff zone between all three
2. Confirm Krax runs/ is the shared zone: Auralis drops job.json, Krax writes krax_output.json, Vera writes vera.json — all in same `<job_id>/` directory.
3. Document the polling model: Auralis polls for `vera.json`; Vera polls for `krax_output.json`.
4. Produce gap register table:

   | Agent | Gap | Severity | Delivering Sprint |
   |-------|-----|----------|-------------------|
   | Auralis | does not write job.json to Krax inbox | blocking | Sprint1 |
   | Auralis | does not poll for vera.json | blocking | Sprint4 |
   | Krax | job.json ingestion not implemented | blocking | Sprint1 |
   | Krax | Grok DOM adapter not complete | blocking | Sprint2 |
   | Krax | krax_output.json format not enforced | blocking | Sprint2 |
   | Vera | fake_vera.py reads no real input | blocking | Sprint3 |
   | Vera | vera_daemon.py does not write canonical vera.json | blocking | Sprint3 |
   | All | contract validation not enforced at any boundary | high | Sprint5 |

5. Write summary: what each agent can do today that is reused as-is.

## Handoff Artifacts

- canonical filesystem diagram appended to this file under Completion Notes
- gap register table appended to this file under Completion Notes
