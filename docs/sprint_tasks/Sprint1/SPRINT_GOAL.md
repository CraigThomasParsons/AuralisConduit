# Sprint1 Goal: Auralis → Krax Handoff Wire

## Purpose

Wire Auralis to Krax so that when Auralis completes a ChatGPT job, it writes a structured `job.json` to Krax's inbox and Krax reads and acknowledges it.

No Grok yet. No Vera yet. Just the handoff.

## Target Outcomes

- Auralis server writes `job.json` (Sprint0 contract) after any job completes
- Krax server reads and validates `job.json` on startup and on poll
- Krax acknowledges receipt: moves job to `runs/<job_id>/` and writes `receipt.json`
- A smoke test demonstrates the full Auralis→Krax dispatch path end-to-end
- No changes to Grok extension this sprint

## Acceptance Criteria

- drop a job in Auralis inbox → it completes → `Krax/inbox/<job_id>/job.json` exists
- Krax picks up job → `Krax/runs/<job_id>/receipt.json` exists
- receipt.json contains `job_id`, `received_at`, `status: received`
- validation rejects a job missing any required field (logs error, moves to Krax failed/)
