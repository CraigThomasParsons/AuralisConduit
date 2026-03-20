# Task 2: Retry Logic — Krax and Vera

## Goals

- Transient failures (server crash, timeout, API error) retry up to N times automatically
- Permanent failures do not retry — they move to failed/

## Requirements

- Krax: if Grok extension does not respond within 10 minutes, retry the job up to 3 times
- Vera: if Vision LLM API returns an error, retry up to 3 times with 30s backoff
- Retry count is tracked in a `retry_state.json` in the job's runs/ directory
- On retry exhaustion: job moves to failed/, writes clear `failure_reason.json`

## Acceptance Criteria

- kill Grok tab during Krax processing → Krax retries after 10 min timeout (up to 3 times)
- Vision LLM returns 500 error → Vera retries after 30s, up to 3 times
- retry count visible in `retry_state.json`

## Implementation Steps

1. Add `retry_state.json` to `Krax/runs/<job_id>/`:
   - `{attempt: 1, max_retries: 3, last_failure: null, next_retry_at: null}`
2. In Krax server: when extension timeout occurs, increment retry count, re-serve job.
3. In Vera daemon: wrap Vision LLM call in retry loop with exponential backoff.
4. On exhaustion: write `failure_reason.json`, move to `failed/`.

## Handoff Artifacts

- Krax retry logic implemented
- Vera retry logic implemented
