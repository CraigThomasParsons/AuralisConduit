# Task 1: Auralis → Krax Contract

## Goals

- Produce the canonical JSON schema for the job that Auralis hands to Krax
- This contract governs Sprint1 implementation — freeze it here

## Requirements

- all required fields are named, typed, and described
- all optional fields are named, typed, described, and have a default
- an example payload is included
- the file location is specified (`inbox/krax/job.json` or equivalent)
- error semantics are defined: what happens if a field is missing

## Acceptance Criteria

- schema is complete enough to write a Python validator from it
- location is canonical — not ambiguous between agents
- example payload is valid against the schema
- schema notes how `job_id`, `correlation_id`, `attempt`, and artifact expectations map into Arcane concepts

## Implementation Steps

1. Draft the schema with these fields at minimum:
   - `job_id` (UUID4, required)
   - `goal` (str, required)
   - `context` (str, required)
   - `instructions` (str, required)
   - `constraints` (list[str], optional, default [])
   - `artifacts_expected` (list[str], optional, default [])
   - `created_at` (ISO-8601 UTC, required)
   - `correlation_id` (UUID4, required)
   - `source_run` (str, optional — path to Auralis run that produced this job)
2. Review against vision.md contract definition.
3. Confirm file drop location: `Krax/inbox/<job_id>/job.json`.
4. Write error semantics: Krax must reject and log any job missing required fields.
5. Add Arcane compatibility notes for correlation, retry attempt, status progression, and artifact references.

## Handoff Artifacts

- Finalized schema appended to this file under Completion Notes
