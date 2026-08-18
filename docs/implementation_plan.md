# Multi-Agent TYS Loop Implementation Plan

## Goal Description
Implement a multi-LLM closed-loop development system (Think → Yield → Ship).
The loop: `Auralis (Think) → Krax (Build via Grok) → Vera (Verify via Vision/Tests) → Auralis (Reflect)`.
The communication routing will eventually be managed by **ThePostalService** utilizing RabbitMQ signaling and registry drop-boxes.

## User Review Required
> [!IMPORTANT]
> The plan is broken into three phases to build the Minimal Viable Loop first, before fully automating Vera's vision capabilities.
> Please review the Minimal Contracts and phasing below to ensure they align with the TYS vision.

---

## Minimal Contracts (The Glue)

Everything is files. No implicit agent memory.

1. **Auralis → Krax Contract** (`job.json`)
```json
{
  "job_id": "string",
  "goal": "what we are trying to achieve",
  "context": "relevant system context",
  "instructions": "what Krax must do",
  "constraints": [],
  "artifacts_expected": []
}
```

2. **Krax → Vera Contract** (`krax_output.json`)
```json
{
  "job_id": "string",
  "implementation_summary": "...",
  "files_changed": [],
  "commands_run": [],
  "expected_behavior": "..."
}
```

3. **Vera → Auralis Contract** (`vera.json`)
```json
{
  "job_id": "string",
  "status": "pass | fail | partial",
  "logs": [],
  "screenshots": [],
  "observations": [],
  "confidence": 0.0
}
```

---

## Phase 1: Minimal TYS Loop (This Week)

**Objective**: Complete the loop once with Krax v0.1 and a "Fake" Vera, verifying file-based handoffs.

1. **Krax v0.1 (Execution Agent)**:
   - Port the Auralis Chrome Extension logic to target `grok.com`.
   - Setup `krax_server.py` to listen for jobs, submit prompts to Grok, scrape the response, and generate `runs/<job_id>/krax_output.json`.
2. **Auralis Updates**:
   - Instruct Auralis to compile ChatGPT's intent into the strict `job.json` format and drop it to Krax.
3. **Fake Vera**:
   - Create a dummy agent script that reads `krax_output.json` and immediately returns a hardcoded "pass" `vera.json`.
4. **Reflect Loop**:
   - Auralis reads `vera.json` and posts the summary back to ChatGPT to close the loop.

---

## Phase 2: ThePostalService Integration

**Objective**: Remove point-to-point hardcoding. Use ThePostalService to route standard packages between agents.

1. **Service Registration**:
   - Create TOML profiles in `ThePostalService/registry/` defining the inbox/outbox paths for Auralis, Krax, and Vera.
2. **Package Delivery**:
   - Update Auralis, Krax, and Vera to encapsulate their output contracts alongside `letter.toml` and `manifest.toml` in their respective `outbox/` directories.
3. **RabbitMQ Signals**:
   - Implement RabbitMQ push hooks (`package_ready`) in each agent upon writing to the outbox, allowing ThePostalService to seamlessly shift state files into the next agent's `inbox/`.

---

## Phase 3: Vera Automation (Reality Check)

**Objective**: Replace "Fake Vera" with the fully capable UI driving and Vision LLM evaluation logic.

1. **Desktop Driving**:
   - Implement `test_executor.py` utilizing `ydotool` and `xdotool` for headless UI interactions per the Piper Phase 2 specifications.
2. **Visual Evidence**:
   - Implement `evidence_capture.py` using `grim`/`scrot` to capture the state of the desktop after Krax's generated code renders.
3. **Verdict Generation**:
   - Process the screenshots using a Vision LLM to compare visual reality against the `krax_output.json` expected behavior.
   - Generate true dynamic `vera.json` payloads (Pass/Fail/Partial) to bounce back to Auralis.

---

## Verification Plan

- [ ] Complete Phase 1: Observe a complete end-to-end cycle flowing from Auralis -> Krax -> Fake Vera -> Auralis without manual intervention.
- [ ] Complete Phase 2: Verify all passing operates over ThePostalService and RabbitMQ.
- [ ] Complete Phase 3: Submit a visually failing prompt intentionally and ensure Vera flags the visual regression and routes the failure context back to Auralis to try again.
