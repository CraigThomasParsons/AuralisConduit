# Task 2: Krax → Vera Contract

## Goals

- Produce the canonical JSON schema for the output Krax hands to Vera
- This contract governs Sprint2 (Krax) and Sprint3 (Vera) — freeze it here

## Requirements

- all required fields named, typed, described
- artifact_paths points to files that Vera can actually read
- expected_behavior is human-readable and Vera can extract test criteria from it
- file location is canonical

## Acceptance Criteria

- schema is complete enough to write a Python validator
- `artifact_paths` field is well-defined (absolute paths or relative to Krax runs/)
- `expected_behavior` has a standard format Vera's evaluator can parse

## Implementation Steps

1. Draft the schema with these fields at minimum:
   - `job_id` (UUID4, required — matches the triggering job)
   - `implementation_summary` (str, required)
   - `files_changed` (list[str], required — paths of files written)
   - `commands_run` (list[str], required — commands executed by Krax)
   - `expected_behavior` (str, required — what to verify)
   - `artifact_paths` (list[str], required — extractable code or HTML files)
   - `completed_at` (ISO-8601 UTC, required)
   - `grok_response_path` (str, optional — path to raw grok.txt)
2. Confirm file location: `Krax/runs/<job_id>/krax_output.json`.
3. Define what Vera does if `artifact_paths` is empty: skip or fail with reason.
4. Define acceptance criteria field so Vera knows what "pass" means.

## Handoff Artifacts

- Finalized schema appended to this file under Completion Notes
