# Task 0: Scope Lock and Baseline

## Goals

- Confirm sprint1 boundary: Auralis→Krax dispatch only; no Grok, no Vera
- Confirm Sprint0 contracts are frozen before writing code
- Snapshot the current state of Auralis server and Krax server

## Requirements

- Sprint0 contracts are complete and not changing this sprint
- Auralis `auralis_server.py` completion hook is identified (the line where archive happens)
- Krax `krax_server.py` inbox polling location is identified

## Acceptance Criteria

- sprint boundary confirmed in notes
- relevant Auralis code line identified for hook insertion
- relevant Krax code line identified for inbox polling insertion

## Implementation Steps

1. Read Sprint0 contracts — confirm all three are frozen.
2. Read `Auralis/bin/auralis_server.py` — find the post-completion hook point (where job is archived).
3. Read `Krax/bin/krax_server.py` — find or add the inbox polling loop.
4. Document both hook points by file path and function name.

## Handoff Artifacts

- hook point notes appended to this file under Completion Notes

## Completion Notes (2026-03-20)

Task complete.

### Sprint Boundary Confirmation

- Sprint1 remains strictly Auralis -> Krax dispatch wiring.
- Out of scope for Sprint1:
	- Grok DOM hardening
	- `krax_output.json` contract enforcement
	- Vera polling or verdict handling
- Sprint0 contracts are treated as frozen inputs for Sprint1 implementation.

### Auralis Hook Point

- File: `Auralis/bin/auralis_server.py`
- Class: `AuralisHandler`
- Function: `do_POST()`
- Route: `if self.path == '/job/complete':`
- Exact insertion seam: immediately before `fs.archive_job(job_id)`.

Current flow in that function is:
1. save `response.txt`
2. extract snippets
3. parse/execute actions
4. write a primitive Krax `job.json`
5. write handoff marker with `fs.write_handoff(job_id, run_dir)`
6. archive with `fs.archive_job(job_id)`

Why this is the correct seam:
- all Auralis response artifacts already exist by this point
- the function already emits a draft Krax payload here
- replacing the primitive draft with the frozen Sprint0 contract is a local change
- archive should remain the final step after successful dispatch

### Krax Hook Point

- File: `Krax/bin/krax_server.py`
- Class: `KraxHandler`
- Function: `do_GET()`
- Route: `if self.path == '/job':`
- Current polling source: `jobs = fs.find_jobs()`

Current flow in that function is:
1. poll inbox with `fs.find_jobs()`
2. select oldest job ID
3. read prompt files with `fs.read_job_files(job_id)`
4. compose prompt with `fs.compose_briefing(job_id, job_data)`
5. initialize run dir with `fs.init_run(job_id)`
6. serve prompt JSON to extension

Why this is the correct seam:
- Krax already has the inbox polling entry point
- Sprint1 needs to strengthen this path from markdown-file jobs to canonical `job.json` intake
- `do_GET('/job')` is where receipt creation, validation, and promotion from inbox to runs should start

### Implementation Guidance For Sprint1

- Auralis implementation should replace the primitive handoff payload in `do_POST('/job/complete')` with the frozen Task 1 contract.
- Krax implementation should evolve `fs.find_jobs()` + `fs.read_job_files()` usage so it can ingest canonical `job.json` payloads and write `receipt.json`.
- No new architectural seam is required; both repos already expose the right insertion points.

**Status: COMPLETE**
