# Sprint2 Goal: Krax Grok Browser Driver

## Purpose

Make Krax actually drive Grok.com and extract code from it. When Krax receives a job, it injects the prompt into the open Grok tab, waits for completion, extracts the response, and writes `krax_output.json`.

## Target Outcomes

- Krax Chrome extension adapted to Grok DOM (not ChatGPT)
- Krax server sends job prompt to extension, extension injects into Grok
- Extension waits for Grok generation to finish (MutationObserver or polling)
- Response text and code blocks are extracted and returned to Krax server
- `runs/<job_id>/grok.txt` and `runs/<job_id>/krax_output.json` are written
- `krax_output.json` conforms to Sprint0 Krax→Vera contract

## Acceptance Criteria

- drop a job.json in Krax inbox → within 5 minutes `krax_output.json` exists
- `krax_output.json` validates against Sprint0 Krax→Vera contract schema
- `grok.txt` contains the raw Grok response text
- if Grok tab is not open, Krax logs a clear error and moves job to `failed/`
