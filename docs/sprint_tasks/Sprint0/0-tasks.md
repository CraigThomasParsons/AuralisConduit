# Task 0: Scope Lock and Baseline

## Goals

- Confirm the sprint boundary: no code changes this sprint
- Inventory current state of all three agents
- Identify what each agent can and cannot do today

## Requirements

- document Auralis current capabilities and gaps
- document Krax current capabilities and gaps
- document Vera current capabilities and gaps
- inventory ArcaneArcadeMachineFactory patterns that TYS should reuse instead of redefining
- confirm sprint0 exits only on contracts — no implementation in scope

## Acceptance Criteria

- three-agent capability table is complete
- Arcane reuse inventory is complete
- sprint boundary is explicit in the notes

## Implementation Steps

1. Read Auralis README and bin/ to confirm current inbox→runs flow works end-to-end.
2. Read Krax README and bin/krax_server.py to confirm server structure.
3. Read Vera README, bin/fake_vera.py, and bin/vera_daemon.py to confirm verdict output shape.
4. Produce a single table: agent | what works today | what is missing for TYS loop.
5. Read ArcaneArcadeMachineFactory Sprint2 architecture and contract docs.
6. Produce a second table: TYS concern | Arcane reusable component | reuse rule.
7. Confirm sprint0 scope: contracts only.

## Handoff Artifacts

- capability table appended to this file under Completion Notes
- Arcane reuse inventory appended to this file under Completion Notes

## Completion Notes (2026-03-20)

Task complete.

### Capability Table

| Agent | What Works Today | What Is Missing For TYS Loop |
|-------|------------------|------------------------------|
| Auralis | Local HTTP server on port 3000; inbox polling via `fs.find_jobs()`; prompt composition from job files; ChatGPT extension handoff through `GET /job`; completion intake through `POST /job/complete`; response extraction; snippet extraction; allowlisted command execution in `scratchpad/`; archive flow | No structured `job.json` write to Krax; no contract validator; no in-flight Krax tracking; no Vera verdict polling; no retry-aware loop decision logic |
| Krax | Local HTTP server on port 3001; Grok-targeted prompt dispatch through `GET /job`; completion intake through `POST /job/complete`; raw response persistence; snippet extraction into `runs/<job_id>/extracted/`; minimal `krax_output.json`; fail path and archive flow | Does not ingest the planned Auralis contract; no `receipt.json`; no schema validation; no explicit state machine; `krax_output.json` is still minimal and not yet aligned with the full contract |
| Vera (fake) | Polls Krax handoff markers; reads `krax_output.json`; writes `vera.json`; generates a reflection job back into Auralis inbox | Uses marker files instead of the planned shared run contract; verdict payload is not yet fully canonical; no validation; no timeout handling |
| Vera (real) | QAQueue-centered daemon exists; can claim tasks, run test instructions, compile evidence, call AI evaluator, submit verdicts, publish events | Not wired to Krax runs; does not read `krax_output.json`; does not write canonical `vera.json` to shared runs; current flow is QAQueue-native rather than TYS-native |

### Arcane Reuse Inventory

| TYS Concern | Arcane Reusable Component | Reuse Rule |
|-------------|---------------------------|------------|
| Filesystem orchestration | `stage_runtime.py` + `stage_workers.py` consume-once queue flow | Keep TYS inbox, runs, failed, and archive semantics compatible with Arcane's claim-and-move model |
| Contract validation discipline | `arcane_event_contract.py` | Use the same fail-loud pattern: required fields, schema version, attempt tracking, and explicit validation errors |
| Retry and correlation semantics | Arcane event envelope fields: `correlation_id`, `causation_id`, `attempt`, `artifact_refs`, `status` | Design TYS contracts so these fields map directly instead of inventing parallel meanings |
| Read model / status snapshot | `arcane_event_projections.py` | Later TYS status should be derived from append-only writes plus a projection, not hidden daemon memory |
| Validation stage model | Arcane stage failure and review semantics | Vera verdicts should be shape-compatible with a future Arcane validation stage or review gate |
| Live visibility | `bridge/ws_broker.py` + Godot chatroom/status consumers | Treat this as a later optional bridge target; do not make TYS depend on Godot now |

### Baseline Conclusion

- Sprint0 remains contract-only. No implementation work is required to close this task.
- Auralis already solves the external reasoning ingress.
- Krax already solves most of the browser-driving pattern but still needs the proper inbound contract and stronger output contract.
- Vera already has two useful forms: fake loop-closer and real validator. The gap is not capability; the gap is wiring and contract alignment.
- ArcaneArcadeMachineFactory should be treated as the runtime reference model for queue semantics, status semantics, and future reintegration.

**Status: COMPLETE**
