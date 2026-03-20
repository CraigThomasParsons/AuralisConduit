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
- the diagram clearly identifies which parts can later map to Arcane inbox, outbox, failed, archive, projection, and bridge layers

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

## Completion Notes (2026-03-20)

Task complete.

### Canonical Filesystem Diagram

```text
/home/craigpar/Code/
├── Auralis/
│   ├── inbox/
│   │   ├── <auralis_job_id>/
│   │   │   ├── briefing.md
│   │   │   ├── context.md
│   │   │   └── goals.md
│   │   └── escalated/
│   │       └── <krax_job_id>/
│   │           └── escalation.json
│   ├── runs/
│   │   └── <auralis_job_id>/
│   │       ├── response.txt
│   │       ├── extracted/
│   │       ├── krax_tracking.json
│   │       └── loop_result.json
│   └── archive/
│       └── <auralis_job_id>/
│
├── Krax/
│   ├── inbox/
│   │   └── <krax_job_id>/
│   │       └── job.json
│   ├── runs/
│   │   └── <krax_job_id>/
│   │       ├── job.json               ← copied or moved from inbox on pickup
│   │       ├── response.txt           ← raw Grok response
│   │       ├── extracted/
│   │       │   └── ...generated files
│   │       ├── extracted_files.json
│   │       ├── receipt.json           ← Sprint1 target
│   │       ├── krax_output.json       ← Vera input
│   │       └── vera.json              ← Auralis input
│   ├── failed/
│   │   └── <krax_job_id>/
│   │       └── rejection.json
│   └── archive/
│       └── <krax_job_id>/
│
└── Vera/
   ├── evidence/
   │   └── <krax_job_id>/
   │       ├── output.txt
   │       ├── screenshot.png
   │       └── audit.jsonl
   ├── verdicts/
   │   └── <krax_job_id>.json         ← optional local copy, not the canonical handoff
   └── logs/
      └── vera.log
```

### Shared Handoff Rules

- `Krax/runs/<krax_job_id>/` is the canonical shared handoff zone between all three agents.
- Auralis writes `job.json` to `Krax/inbox/<krax_job_id>/job.json`.
- Krax owns promotion from `inbox/` to `runs/` and writes `receipt.json`, `response.txt`, `extracted/`, and `krax_output.json`.
- Vera reads `krax_output.json` from the Krax run directory and writes `vera.json` back into that same directory.
- Auralis polls only `vera.json` and never reads Vera's internal `evidence/` structure directly unless needed for escalation or debugging.

### Polling Model

- Auralis polls `Krax/runs/*/vera.json` via `krax_tracking.json` references.
- Vera polls `Krax/runs/*/krax_output.json` or a future equivalent receipt-based manifest.
- Krax polls only its own `inbox/`.
- No agent should rely on mutable in-memory state owned by another agent.

### Arcane Mapping

| TYS Path or Concept | Arcane Analogue | Mapping Rule |
|---------------------|-----------------|--------------|
| `Auralis/inbox/` | external conversation drop zone | External reasoning ingress before factory orchestration |
| `Krax/inbox/` | stage inbox | Consume-once queue with explicit claim semantics |
| `Krax/runs/<job_id>/` | stage execution scope | One immutable run scope containing artifacts and status files |
| `Krax/failed/` | stage failed queue | Terminal rejected or exhausted handoffs |
| `Auralis/archive/` / `Krax/archive/` | archive/history | Completed attempt history |
| `vera.json` | validation-stage terminal artifact | Validation verdict that can map to review or blocker outcomes |
| future audit/projection files | Arcane event stream and projections | Append-only writes plus derived status snapshots |

### Gap Register

| Agent | Gap | Severity | Delivering Sprint |
|-------|-----|----------|-------------------|
| Auralis | does not write canonical `job.json` to Krax inbox | blocking | Sprint1 |
| Auralis | does not write `krax_tracking.json` or poll for `vera.json` | blocking | Sprint4 |
| Auralis | no timeout synthesis for missing Vera verdicts | high | Sprint4 |
| Krax | does not ingest the frozen `job.json` contract | blocking | Sprint1 |
| Krax | does not write `receipt.json` on pickup | blocking | Sprint1 |
| Krax | Grok DOM adapter not yet hardened to the real site structure | blocking | Sprint2 |
| Krax | current `krax_output.json` implementation is thinner than the frozen contract | blocking | Sprint2 |
| Vera | `fake_vera.py` still keys off outbox markers instead of the shared run contract | blocking | Sprint3 |
| Vera | `fake_vera.py` writes unstructured `observations` today | high | Sprint3 |
| Vera | `vera_daemon.py` is QAQueue-native rather than Krax-run-native | blocking | Sprint3 |
| All | no enforced schema validation at read/write boundaries | high | Sprint5 |
| All | no shared audit trail or projection-style status view | medium | Sprint5 |

### Reuse Summary

- Reuse Auralis's browser-driven ChatGPT ingress pattern as-is.
- Reuse Krax's browser-driven Grok response capture pattern as-is, but strengthen its contracts.
- Reuse Vera's real evidence capture and evaluation stack, but rewire the input/output boundaries from QAQueue to Krax runs.
- Reuse ArcaneArcadeMachineFactory's queue semantics, retry semantics, validation discipline, and eventual projection model as the runtime reference.

**Status: COMPLETE**
