# Task 2: Real Vera — Command Runner and Evidence Capture

## Goals

- Implement real test execution in `vera_daemon.py`: run commands from `krax_output.json`
- Capture screenshots as evidence after command execution
- This is Phase B — fake_vera runs in parallel until this is verified

## Requirements

- `commands_run` from krax_output.json are executed in a subprocess
- stdout/stderr captured and saved to `Vera/evidence/<job_id>/output.txt`
- screenshot captured after command execution: `evidence/<job_id>/screenshot.png`
- screenshot method: `grim` (Wayland) with `scrot` fallback (X11)
- commands run in a sandboxed directory: `Vera/evidence/<job_id>/sandbox/`
- hard timeout: 5 minutes per command; killed and marked failed after timeout

## Acceptance Criteria

- given a krax_output.json with `commands_run: ["python3 solution.py"]`:
  - command runs in sandbox
  - `evidence/<job_id>/output.txt` contains stdout/stderr
  - `evidence/<job_id>/screenshot.png` exists
- timeout kills the command and records `timed_out: true` in evidence

## Implementation Steps

1. Implement `Vera/bin/lib/command_runner.py`:
   - `run_command(cmd: str, sandbox_dir: Path, timeout: int = 300) -> CommandResult`
   - `CommandResult`: `{returncode, stdout, stderr, timed_out}`
2. Implement `Vera/bin/lib/screenshot.py`:
   - try `grim <output_path>` (Wayland)
   - fallback: `scrot <output_path>` (X11)
3. In `vera_daemon.py`, after picking up `krax_output.json`:
   - create `evidence/<job_id>/sandbox/`
   - copy `artifact_paths` files into sandbox
   - run each command in `commands_run`
   - capture screenshot
   - save evidence

## Handoff Artifacts

- `Vera/bin/lib/command_runner.py` created
- `Vera/bin/lib/screenshot.py` created
- vera_daemon.py updated to call both
