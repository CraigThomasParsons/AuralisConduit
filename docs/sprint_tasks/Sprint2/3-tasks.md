# Task 3: krax_output.json Writer

## Goals

- Parse `grok.txt` to extract code blocks and implementation summary
- Write `krax_output.json` conforming to Sprint0 Krax→Vera contract
- Extract code files to `runs/<job_id>/extracted/`

## Requirements

- code blocks extracted from markdown (fenced ``` blocks)
- each code block saved as a file: `extracted/<language>_<index>.<ext>`
- `implementation_summary` is the first non-code paragraph of the response
- `expected_behavior` is derived from: the job's `instructions` field + any "expected" section in grok response
- `artifact_paths` lists all extracted files
- `krax_output.json` is written atomically

## Acceptance Criteria

- `runs/<job_id>/krax_output.json` exists and validates against Sprint0 schema
- `extracted/` directory contains all code blocks from grok.txt
- `artifact_paths` in krax_output.json matches actual files in extracted/

## Implementation Steps

1. Create `Krax/bin/lib/response_parser.py`:
   - `extract_code_blocks(text: str) -> list[{language, code}]`
   - `extract_summary(text: str) -> str` — first paragraph before any code block
2. In Krax server, when state reaches GROK_COMPLETE:
   - parse grok.txt
   - save extracted files to `runs/<job_id>/extracted/`
   - build krax_output dict from Sprint0 schema
   - write `runs/<job_id>/krax_output.json` atomically
   - set state to DONE (Vera pickup pending)
3. Log: `[TYS] krax_output.json written: <job_id>, <N> artifacts extracted`.

## Handoff Artifacts

- `Krax/bin/lib/response_parser.py` created
- krax_output.json written in runs/ for a real Grok response
