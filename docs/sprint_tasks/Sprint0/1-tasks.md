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

## Completion Notes (2026-03-20)

Task complete.

### Canonical Location

- `Krax/inbox/<job_id>/job.json`

### Schema

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `schema_version` | str | yes | none | Contract version. Must be `v1`. |
| `job_id` | str (UUID4) | yes | none | Unique Krax job identity. |
| `correlation_id` | str (UUID4) | yes | none | Groups all retries and downstream artifacts for one logical request. |
| `causation_id` | str (UUID4) or null | no | null | Upstream event or run identifier that caused this job to exist. |
| `created_at` | str (ISO-8601 UTC) | yes | none | Timestamp when Auralis emitted the job. |
| `source_agent` | str | yes | none | Must be `auralis`. |
| `attempt` | int | yes | `1` | 1-based implementation attempt counter. |
| `goal` | str | yes | none | Short statement of what Krax is expected to achieve. |
| `context` | str | yes | none | Relevant project and implementation context. |
| `instructions` | str | yes | none | The concrete build instructions sent to Krax/Grok. |
| `constraints` | list[str] | no | `[]` | Hard limits Krax must not violate. |
| `artifact_refs` | list[str] | no | `[]` | Input artifacts or source files that inform the job. |
| `artifacts_expected` | list[str] | no | `[]` | Expected output artifacts or deliverables. |
| `source_run` | str | no | `""` | Path to the Auralis run directory that produced this job. |
| `metadata` | dict | no | `{}` | Reserved for additive future routing fields. |

### Example Payload

```json
{
   "schema_version": "v1",
   "job_id": "4c47825f-70d1-4e8d-a1c0-f5fc0dc1b98a",
   "correlation_id": "c6530d5c-0ef3-4223-9d8c-3a7f9c7817f2",
   "causation_id": null,
   "created_at": "2026-03-20T19:40:00Z",
   "source_agent": "auralis",
   "attempt": 1,
   "goal": "Generate the first implementation of the requested feature.",
   "context": "Project uses a local browser-driven automation loop and file-based handoffs.",
   "instructions": "Implement the requested code change and return extracted files for validation.",
   "constraints": [
      "Preserve existing public APIs unless explicitly told otherwise.",
      "Write outputs as files under the Krax run directory."
   ],
   "artifact_refs": [
      "/home/craigpar/Code/Auralis/runs/job_001/response.txt"
   ],
   "artifacts_expected": [
      "krax_output.json",
      "extracted/*"
   ],
   "source_run": "/home/craigpar/Code/Auralis/runs/job_001",
   "metadata": {
      "project_slug": "tys-loop"
   }
}
```

### Error Semantics

- Krax must reject any payload missing a required field.
- Krax must reject any payload where `schema_version != "v1"`.
- Krax must reject any payload where `job_id` or `correlation_id` is not UUID4.
- Krax must reject any payload where `attempt < 1`.
- Krax must reject any payload where `goal`, `context`, or `instructions` is empty after trim.
- Rejected jobs move to `Krax/failed/<job_id>/` with `rejection.json` containing `job_id`, `rejected_at`, and `reasons`.
- Rejection is terminal for that emitted job file; Auralis decides whether to regenerate another job.

### Arcane Compatibility Notes

- `correlation_id` maps directly to Arcane correlation semantics and must remain stable across retries.
- `causation_id` gives TYS a clean path into Arcane's causation model when these jobs later become stage events.
- `attempt` maps directly to Arcane's 1-based retry semantics and must increment only for execution retries, not transport/provider failures.
- `artifact_refs` is the TYS equivalent of Arcane artifact references and should contain upstream evidence or source files, not expected outputs.
- `artifacts_expected` is not the same as `artifact_refs`; it describes desired deliverables and can later map to stage-specific output expectations.
- This contract is intentionally shaped so it can be wrapped into an Arcane job payload or event envelope without lossy translation.

**Status: COMPLETE**
