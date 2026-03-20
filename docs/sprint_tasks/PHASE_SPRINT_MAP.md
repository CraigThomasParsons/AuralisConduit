# Phase Sprint Map

Date: 2026-03-20
Project: TYS Loop — Multi-LLM Closed-Loop Development System

## Sprint Sequence

1. Sprint0: Contracts and Scope Lock
2. Sprint1: Auralis → Krax Handoff Wire
3. Sprint2: Krax Grok Browser Driver
4. Sprint3: Vera Integration (Fake → Real)
5. Sprint4: Full Loop Closure
6. Sprint5: Hardening, Retry, and Observability

## One-Line Goal Per Sprint

- Sprint0: Freeze all three agent contracts and filesystem layout before touching code
- Sprint1: Auralis writes job.json; Krax reads it — end-to-end dispatch works
- Sprint2: Krax drives Grok.com, extracts code, produces krax_output.json
- Sprint3: Vera consumes krax_output.json and writes vera.json — fake first, real second
- Sprint4: Auralis reads vera.json; one full Think→Yield→Ship loop completes
- Sprint5: Contracts enforced, retries handled, audit trail complete

## Arcane Reuse Track

- Sprint0: define how TYS job, output, and verdict contracts map to Arcane correlation, attempt, status, and artifact semantics
- Sprint1: keep Auralis→Krax filesystem handoff compatible with Arcane's consume-once inbox/runs/failed/archive flow
- Sprint2: keep Krax output shape compatible with future Arcane stage worker outputs
- Sprint3: shape Vera verdicts so they can become Arcane validation-stage artifacts later
- Sprint4: model loop decisions as stage-style transitions that Arcane can eventually orchestrate
- Sprint5: identify which TYS pieces graduate back into Arcane runtime, projection, and bridge layers

## Status Notes

- 2026-03-20: Sprint map created. Sprint0 ready to start.
- 2026-03-20: Arcane reuse path added so TYS does not drift away from the existing factory architecture.
