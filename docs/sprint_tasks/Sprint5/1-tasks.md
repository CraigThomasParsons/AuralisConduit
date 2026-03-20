# Task 1: Contract Enforcement at All Boundaries

## Goals

- Every JSON file crossing an agent boundary is validated before processing
- Violations are rejected loudly and moved to failed/ — never silently processed

## Requirements

- Auralis validates krax job.json before writing (using Sprint1 schema)
- Krax validates job.json on read, krax_output.json before writing
- Vera validates krax_output.json on read, vera.json before writing
- Auralis validates vera.json on read

## Acceptance Criteria

- inject job.json with missing `goal` field → Krax rejects, moves to failed/, logs field name
- inject krax_output.json with missing `artifact_paths` → Vera rejects, writes error vera.json
- inject malformed JSON (syntax error) → caught, logged, moved to failed/, no crash

## Implementation Steps

1. Create `Krax/contracts/schema_v1.py` (or similar) with all three schemas as typed dicts or dataclasses.
2. Add `validate_or_raise(data: dict, schema_name: str)` that raises `ContractViolationError` with clear message.
3. Add contract check at every read point:
   - Krax server: on job.json read
   - Krax server: before writing krax_output.json
   - Vera daemon: on krax_output.json read
   - Vera daemon: before writing vera.json
   - Auralis: on vera.json read
4. Wrap all contract checks so failures move to failed/ and log at ERROR level.

## Handoff Artifacts

- schema module created
- all read/write points patched with contract checks
