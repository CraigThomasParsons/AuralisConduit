# Task 4: End-to-End Grok Smoke Test

## Goals

- Run a full Auralis→Krax→Grok→krax_output cycle and verify output
- Document the procedure as a repeatable test

## Requirements

- test uses a simple goal: "Write a Python function that adds two numbers"
- result: grok.txt and krax_output.json both exist in runs/
- krax_output.json validates against Sprint0 schema
- extracted/ contains at least one Python file

## Implementation Steps

1. Ensure Auralis server, Krax server, and Krax extension are running.
2. Ensure Grok.com is open in Chrome with Krax extension loaded.
3. Drop a test job in Auralis inbox with goal: "Write a Python function that adds two numbers, with a docstring."
4. Wait for `Krax/runs/<job_id>/krax_output.json` to appear (up to 10 minutes).
5. Verify schema compliance: run `python3 contracts/auralis_to_krax.py --validate runs/<job_id>/krax_output.json`.
6. Record result in Completion Notes.

## Handoff Artifacts

- smoke test output recorded in Completion Notes
- note any Grok DOM changes that required selector updates
