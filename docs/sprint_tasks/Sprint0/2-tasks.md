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
- schema notes how output artifacts and behavior summary could map to Arcane stage outbox artifacts

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
5. Add Arcane compatibility notes for artifact refs, stage outputs, and future validation-stage handoff.

## Handoff Artifacts

- Finalized schema appended to this file under Completion Notes

## Completion Notes (2026-03-20)

Task complete.

### Canonical Location

- `Krax/runs/<job_id>/krax_output.json`

### Schema

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `schema_version` | str | yes | none | Contract version. Must be `v1`. |
| `job_id` | str (UUID4) | yes | none | Matches the triggering Krax job. |
| `correlation_id` | str (UUID4) | yes | none | Stable logical request identifier shared with upstream Auralis job. |
| `attempt` | int | yes | none | 1-based implementation attempt number for this output. |
| `status` | str | yes | none | Must be `ready_for_verification` for a valid Vera handoff. |
| `completed_at` | str (ISO-8601 UTC) | yes | none | Time Krax finished writing the output contract. |
| `implementation_summary` | str | yes | none | Short human-readable summary of what Grok/Krax produced. |
| `expected_behavior` | str | yes | none | Human-readable behavior Vera should verify. |
| `acceptance_checks` | list[str] | yes | none | Concrete checks Vera can convert into observations. |
| `files_changed` | list[str] | yes | `[]` | File paths changed or created by the generated implementation. |
| `commands_run` | list[str] | yes | `[]` | Commands Krax ran while shaping or validating the output. |
| `artifact_paths` | list[str] | yes | `[]` | Paths Vera can read directly for execution or hosting. Relative paths are resolved from `Krax/runs/<job_id>/`. |
| `grok_response_path` | str | no | `""` | Path to the raw Grok response text. |
| `source_job_path` | str | no | `""` | Path to the original `job.json` that produced this output. |
| `metadata` | dict | no | `{}` | Reserved for additive routing or environment details. |

### Example Payload

```json
{
   "schema_version": "v1",
   "job_id": "4c47825f-70d1-4e8d-a1c0-f5fc0dc1b98a",
   "correlation_id": "c6530d5c-0ef3-4223-9d8c-3a7f9c7817f2",
   "attempt": 1,
   "status": "ready_for_verification",
   "completed_at": "2026-03-20T20:10:00Z",
   "implementation_summary": "Generated a small Python function and extracted it into the run directory.",
   "expected_behavior": "The extracted Python module should expose a function that returns the requested value without runtime errors.",
   "acceptance_checks": [
      "Module imports without error.",
      "Function returns the requested value.",
      "No missing dependency or syntax error occurs during execution."
   ],
   "files_changed": [
      "extracted/add_two_numbers.py"
   ],
   "commands_run": [
      "python3 extracted/add_two_numbers.py"
   ],
   "artifact_paths": [
      "extracted/add_two_numbers.py"
   ],
   "grok_response_path": "response.txt",
   "source_job_path": "../inbox/4c47825f-70d1-4e8d-a1c0-f5fc0dc1b98a/job.json",
   "metadata": {
      "provider": "grok",
      "artifact_root": "extracted/"
   }
}
```

### Vera Interpretation Rules

- Vera resolves relative `artifact_paths` from `Krax/runs/<job_id>/`.
- Vera must treat `acceptance_checks` as the source checklist for `observations` in `vera.json`.
- If `artifact_paths` is empty, Vera must not continue with fake success behavior. It must write `vera.json` with `status: error` and explain that no executable or inspectable artifacts were supplied.
- If `expected_behavior` is empty or vague, Vera must treat that as input quality failure and return `status: partial` or `error` with a clear observation.

### Error Semantics

- Vera must reject any payload missing a required field.
- Vera must reject any payload where `schema_version != "v1"`.
- Vera must reject any payload where `status != "ready_for_verification"`.
- Vera must reject any payload where `attempt < 1`.
- Vera must reject any payload where `acceptance_checks` is empty.
- On rejection, Vera writes `vera.json` with `status: error`, preserving the rejection reasons in `observations`.

### Arcane Compatibility Notes

- `correlation_id` and `attempt` align directly with Arcane's event and retry semantics.
- `status` is intentionally explicit so this handoff can later become an Arcane stage-state transition rather than an implicit file side effect.
- `artifact_paths` is the file-handoff equivalent of Arcane stage outbox artifacts and should remain concrete, inspectable file references.
- `acceptance_checks` gives Vera a contractually stable input that later maps cleanly to Arcane review or validation-stage expectations.
- `implementation_summary` is the human-readable equivalent of an Arcane stage completion summary and should remain concise and audit-safe.

**Status: COMPLETE**
