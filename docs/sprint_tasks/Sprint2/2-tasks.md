# Task 2: Krax Server Prompt Dispatch and Response Capture

## Goals

- When Krax picks up a job from inbox, it builds a structured prompt and serves it to the extension
- When the extension POSTs the Grok response back, Krax saves it and advances the job

## Requirements

- `/job` endpoint returns the current pending job's prompt or `null` if none
- prompt is built from `job.json` fields: goal + instructions + constraints formatted as markdown
- `/complete` endpoint receives the raw Grok response text
- raw response is written to `runs/<job_id>/grok.txt` atomically
- server tracks which job is in-flight (only one at a time)

## Acceptance Criteria

- GET `/job` returns `{"job_id": "...", "prompt": "..."}` when a job is pending
- GET `/job` returns `{"job": null}` when no job is pending
- POST `/complete` with `{"job_id": "...", "response": "..."}` writes grok.txt
- job state transitions: `received → in_progress → grok_complete`

## Implementation Steps

1. Add state machine to Krax server: `PENDING`, `IN_PROGRESS`, `GROK_COMPLETE`, `DONE`, `FAILED`.
2. When inbox poll picks up job (Task 2, Sprint1): set state to `PENDING`.
3. Implement `GET /job`:
   - if PENDING: build prompt from job fields, set state to IN_PROGRESS, return prompt
   - else: return `{"job": null}`
4. Implement POST `/complete`:
   - validate job_id matches in-flight job
   - write grok.txt atomically
   - set state to GROK_COMPLETE
5. Implement `build_prompt(job: dict) -> str` — formats goal, context, instructions, constraints as markdown.

## Handoff Artifacts

- patch applied to krax_server.py
