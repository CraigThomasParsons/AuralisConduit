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
