# Sprint3 Goal: Vera Integration (Fake Then Real)

## Purpose

Wire Vera into the loop. Start with `fake_vera.py` always returning pass so the loop can run end-to-end. Then replace with real Vera: command execution, screenshot capture, Vision LLM evaluation, and the canonical `vera.json` verdict.

## Target Outcomes

- Phase A (Fake Vera): `fake_vera.py` reads `krax_output.json` and writes a valid `vera.json` with `status: pass` — loop can run
- Phase B (Real Vera): `vera_daemon.py` runs test commands, captures screenshots, evaluates with Vision LLM, writes `vera.json` with real status
- Vera polls for `krax_output.json` to appear, does not need to be explicitly triggered
- `vera.json` conforms to Sprint0 Vera→Auralis contract in both phases

## Acceptance Criteria

- Phase A: after krax_output.json appears → vera.json exists within 30 seconds with `status: pass`
- Phase B: vera.json contains real `observations`, `confidence`, and `screenshots`
- invalid krax_output.json → vera.json with `status: error`, `observations` explaining why
