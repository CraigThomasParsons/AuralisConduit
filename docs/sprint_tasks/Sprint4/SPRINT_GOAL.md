# Sprint4 Goal: Full Loop Closure

## Purpose

Close the loop. When Vera writes `vera.json`, Auralis reads it and either declares the job done (pass) or generates a revised prompt and sends another job to Krax (fail). One complete Think→Yield→Ship→Reflect cycle runs without human intervention.

## Target Outcomes

- Auralis polls for `vera.json` after dispatching a Krax job
- On pass: Auralis archives the job and optionally sends a summary to ChatGPT
- On fail: Auralis sends a reflection prompt to ChatGPT, captures the revised instructions, and dispatches a new Krax job
- Loop respects a max-attempts limit (3) before escalating to human inbox
- The loop runs once successfully end-to-end

## Acceptance Criteria

- drop a job in Auralis inbox → full cycle runs → result appears in archive without human touch
- on fail: a second Krax job is automatically dispatched with improved instructions
- on max-attempts exceeded: job is moved to `Auralis/inbox/escalated/` for human review
- loop attempt counter is tracked in the job.json `attempt` field
