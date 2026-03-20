# Task 3: Contract Validation Layer

## Goals

- Extract the Auralis→Krax contract into a shared Python module
- Both Auralis (writer) and Krax (reader) import from the same schema definition
- This prevents contract drift between agents

## Requirements

- single source of truth for required fields, optional fields, and types
- Auralis uses it to build the job dict
- Krax uses it to validate the job dict
- schema lives in a location both can import (or is duplicated with a version stamp)

## Acceptance Criteria

- `contracts/auralis_to_krax.py` (or equivalent) defines the schema
- Auralis imports `build_krax_job()` from it
- Krax imports `validate_krax_job()` from it
- schema version is a constant in the file: `SCHEMA_VERSION = "v1"`

## Implementation Steps

1. Create `Krax/contracts/auralis_to_krax.py`:
   - `SCHEMA_VERSION = "v1"`
   - `REQUIRED_FIELDS = [...]`
   - `validate_krax_job(job: dict) -> list[str]` — returns missing field names
   - `build_krax_job(goal, context, instructions, ...) -> dict` — builds valid job dict
2. Update Auralis writer (Task 1) to import `build_krax_job` or mirror the schema.
   (Since separate repos, Auralis duplicates the schema with a version constant — acceptable for now.)
3. Update Krax ingestion (Task 2) to use `validate_krax_job`.
4. Document the duplication explicitly: both copies must have `SCHEMA_VERSION = "v1"` — if they diverge, the loop will break.

## Handoff Artifacts

- `Krax/contracts/auralis_to_krax.py` created
- Auralis server updated to stamp schema version in job.json
