# Task 0: Scope Lock and Reliability Audit

## Goals

- Confirm Sprint4 is complete (full loop runs end-to-end)
- Enumerate all failure modes that the system does not currently handle
- Prioritize for Sprint5 implementation

## Requirements

- Sprint4 all three smoke tests pass
- Failure mode inventory covers: network failures, process crashes, malformed data, timeout expiry

## Implementation Steps

1. Confirm Sprint4 exit gate: all three smoke test scenarios pass.
2. Walk the full loop path and enumerate failure modes:
   - Auralis: ChatGPT tab closed, response capture fails, Krax inbox write fails
   - Krax: server crashes mid-job, Grok tab closed, extension disconnects, response parsing fails
   - Vera: daemon crashes mid-job, screenshot fails (no display), Vision LLM API down, timeout
3. Classify each: transient (retry) vs. permanent (fail + notify).
4. Produce failure mode table in Completion Notes.

## Handoff Artifacts

- failure mode table in Completion Notes
