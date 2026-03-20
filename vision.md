# Vision: TYS Loop — A Multi-LLM Closed-Loop Development System

Date: 2026-03-20

---

## What This Is

The TYS Loop (Think → Yield → Ship) is the first system where multiple AI intelligences collaborate through structured file artifacts to build and validate software — end to end — without human intervention per cycle.

It is not an AI assistant. It is not a coding tool.

It is a **distributed cognitive system** where distinct agents own distinct phases and hand off through enforced contracts.

---

## The Loop

```
You + Auralis + ChatGPT      ← THINK
        ↓
    Krax + Grok              ← YIELD (Build)
        ↓
      Vera                   ← SHIP (Verify)
        ↓
   Auralis + ChatGPT         ← REFLECT
        ↓
  (repeat until pass)
```

---

## The Three Agents

### Auralis — The Conduit (Structurer)

**Role:** Translate human intent into structured jobs. Receive Vera's verdict and synthesize the reflection pass back to ChatGPT.

**What it already does:**
- Monitors `inbox/` for job folders containing `briefing.md`, `context.md`, `goals.md`
- Drives the ChatGPT web interface via Chrome Extension + local server (port 3000)
- Captures responses, archives jobs, extracts scripts to `scratchpad/`
- Runs as a systemd user service

**What it needs to do in the TYS loop:**
- Write a structured `job.json` to Krax's inbox after capturing ChatGPT's response
- Read Vera's verdict JSON and produce a reflection prompt back to ChatGPT
- Decide loop continuation: pass → done; fail → regenerate → repeat

---

### Krax — The Executor (Builder via Grok)

**Role:** Take a structured job from Auralis, drive Grok.com, extract the implementation, and produce output artifacts.

**What it has:**
- Local server (`krax_server.py`) on port 3001
- Chrome Extension adapted from Auralis architecture, targeting Grok DOM
- `inbox/`, `runs/`, `docs/`, `archive/` directory layout

**What it does in the TYS loop:**
- Polls inbox for `job.json` from Auralis
- Injects structured prompt into active Grok.com tab
- Waits for generation to complete (DOM observer)
- Extracts plan, code blocks, and explanations
- Writes `runs/<job_id>/grok.txt` and `runs/<job_id>/krax_output.json`
- Signals Vera that output is ready

---

### Vera — Reality (Validator)

**Role:** Execute what Krax built, capture evidence, return a structured verdict.

**What it has:**
- `vera_daemon.py` — main systemd service
- `fake_vera.py` — always returns pass (Phase 1 stand-in)
- Evidence capture: `grim` (Wayland) / `scrot` (X11) screenshots
- AI evaluator: Vision LLM assessment of screenshots against acceptance criteria
- `evidence/`, `verdicts/`, `logs/` directories

**What it does in the TYS loop:**
- Reads `krax_output.json` to know what to test
- Runs test commands or hosts Krax's output
- Takes screenshots of the result
- Sends evidence to Vision LLM for PASS/FAIL evaluation
- Writes `runs/<job_id>/vera.json` in the canonical verdict contract
- Auralis polls for this file to close the loop

---

## The Critical Rule

> **Everything must be files.**

No hidden state. No memory in agents. No implicit context.

```
/factory/
  inbox/krax/        ← Auralis drops job.json here
  runs/<job_id>/     ← Krax writes grok.txt, krax_output.json
                     ← Vera writes vera.json
  artifacts/         ← Extracted code, screenshots, evidence
```

This is what prevents:
- Infinite hallucination loops (Vera catches them)
- State corruption (files are atomic and inspectable)
- Debugging black holes (every step leaves a trace)

---

## Why This Is Different

Most people stop at "one AI helping me code."

This system has:
- **Role separation**: Auralis thinks, Krax builds, Vera validates — no overlap
- **Contracts at every boundary**: no vague text passing; every handoff is a typed JSON file
- **Closed loop with reality**: Vera runs the actual code; hallucinations fail the build
- **File-first state**: everything is inspectable, replayable, and auditable

---

## The Three Contracts

### Auralis → Krax (`inbox/krax/job.json`)

```json
{
  "job_id": "string (UUID4)",
  "goal": "what we are trying to achieve",
  "context": "relevant system context",
  "instructions": "what Krax must do",
  "constraints": [],
  "artifacts_expected": [],
  "created_at": "ISO-8601 UTC",
  "correlation_id": "string (UUID4)"
}
```

### Krax → Vera (`runs/<job_id>/krax_output.json`)

```json
{
  "job_id": "string",
  "implementation_summary": "...",
  "files_changed": [],
  "commands_run": [],
  "expected_behavior": "...",
  "artifact_paths": [],
  "completed_at": "ISO-8601 UTC"
}
```

### Vera → Auralis (`runs/<job_id>/vera.json`)

```json
{
  "job_id": "string",
  "status": "pass | fail | partial",
  "logs": [],
  "screenshots": [],
  "observations": [],
  "confidence": 0.0,
  "evaluated_at": "ISO-8601 UTC"
}
```

---

## Phases

| Phase | Name | What Happens |
|-------|------|--------------|
| THINK | Auralis + ChatGPT | Human intent becomes structured job |
| YIELD | Krax + Grok | Structured job becomes implementation |
| SHIP | Vera | Implementation meets reality: pass or fail |
| REFLECT | Auralis + ChatGPT | Failure becomes improved intent |

---

## Minimal First Loop (What to Build First)

1. Auralis drops `job.json` in Krax inbox after any job completes
2. Krax reads it, sends to Grok, saves `grok.txt`
3. Fake Vera reads `grok.txt`, always writes `vera.json` with `status: pass`
4. Auralis reads `vera.json`, sends 1-line summary to ChatGPT

This closes the loop with zero real testing. Then replace Fake Vera with Real Vera.

---

## What Makes This Special

You've already solved the hardest problem: **reliable, contract-based automation of a web LLM interface with Auralis.**

Everything else is:
- Repeating the same Chrome extension pattern for Grok (Krax)
- Adding a test runner with file output (Vera)
- Wiring the verdict back to Auralis

The architecture is already proven. Now it scales across multiple intelligences.

---

## Arcane Reuse Path

This TYS loop should not become a parallel system with its own incompatible runtime rules.

It should be treated as a proving ground for capabilities that can later be folded back into ArcaneArcadeMachineFactory.

### What Should Stay Aligned With Arcane

- Contract fields: keep `correlation_id`, `attempt`, timestamps, and artifact path semantics compatible with Arcane's event and job contracts.
- Filesystem flow: keep the same consume-once queue pattern Arcane uses in `stage_runtime.py` and `stage_workers.py` — inbox, runs, failed, archive, outbox-style handoff.
- Validation model: use the same contract-first approach Arcane uses in `arcane_event_contract.py` — invalid payloads fail loudly, not silently.
- Read model pattern: TYS should eventually expose job status the same way Arcane exposes projection state — append-only writes plus derived status snapshots.
- UI bridge potential: Vera and Krax status should be representable later in Arcane's chatroom and WebSocket layers without inventing a second live-status protocol.

### Likely Reuse Back Into ArcaneArcadeMachineFactory

- Auralis as the external reasoning ingress for factory jobs that need ChatGPT refinement.
- Krax as a specialized implementation worker for code-generation stages.
- Vera as a validation stage that can sit beside or inside Arcane's existing stage pipeline.
- TYS retry, audit, and verdict handling as reusable runtime primitives for Arcane's stage orchestration.

### Rule

Every new TYS contract should be mappable into ArcaneArcadeMachineFactory without lossy translation.

If a TYS field cannot be mapped to Arcane concepts like correlation, causation, attempt, status, or artifact refs, that is a design smell and should be corrected during Sprint0.
