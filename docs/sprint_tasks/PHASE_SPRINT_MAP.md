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

## Status Notes

- 2026-03-20: Sprint map created. Sprint0 ready to start.
