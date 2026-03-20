# Task 3: Auralis Reflection Prompt Generator

## Goals

- When Vera returns a fail verdict, Auralis generates a reflection prompt for ChatGPT
- The reflection prompt explains what failed and asks for an improved implementation
- ChatGPT's response becomes the new instructions sent to Krax

## Requirements

- reflection prompt is a markdown briefing file dropped into Auralis inbox
- it includes: original goal, original instructions, Vera's observations, failed checks
- it asks ChatGPT to revise the implementation given the failures
- ChatGPT's response is captured and becomes the new Krax job's `instructions` field

## Acceptance Criteria

- on fail verdict: a new briefing.md appears in `Auralis/inbox/reflect_<job_id>/`
- Auralis processes it → ChatGPT response captured → new Krax job dispatched with attempt+1
- reflection briefing explicitly lists each failed observation entry

## Implementation Steps

1. Implement `build_reflection_briefing(original_job: dict, verdict: dict) -> str`:
   - Heading: "Reflection: Attempt <N> failed for: <goal>"
   - Section: Original Instructions
   - Section: Failures Observed (each `observation` where `result == fail`)
   - Section: Request — "Please provide a revised implementation addressing the failures above"
2. Write the briefing to `Auralis/inbox/reflect_<job_id>/briefing.md`
3. Auralis picks it up normally via inbox polling → ChatGPT → response → new Krax job
4. Ensure the `attempt` counter in the new job.json is incremented.

## Handoff Artifacts

- `build_reflection_briefing()` implemented
- sample reflection briefing appended to this file under Completion Notes
