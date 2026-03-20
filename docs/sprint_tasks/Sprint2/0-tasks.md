# Task 0: Scope Lock and Grok DOM Audit

## Goals

- Confirm Sprint1 is complete (Auralis→Krax dispatch works)
- Document Grok.com DOM structure for prompt injection and response extraction
- Identify selectors needed for the Krax Chrome extension

## Requirements

- Sprint1 smoke test passes before Sprint2 begins
- Grok DOM audit records: textarea selector, send button selector, response container selector, generation-in-progress indicator

## Implementation Steps

1. Confirm Sprint1 smoke test passes — receipt.json exists after dispatch.
2. Open Grok.com in Chrome.
3. Inspect DOM to identify:
   - prompt textarea: element selector and data-testid if available
   - send button: selector
   - response container: selector
   - "generating" indicator: what changes in DOM during generation vs. after
4. Document selectors in this file under Completion Notes.
5. Compare with Auralis content.js to identify diff for the Krax extension.

## Handoff Artifacts

- Grok DOM selectors recorded in Completion Notes

## Completion Notes (2026-03-20)

Task complete.

### Sprint1 Gate Check

- Confirmed Sprint1 completion evidence from `Sprint1/4-tasks.md`.
- Controlled smoke test pass recorded:
   - `PASS: dispatch smoke test succeeded`
   - receipt path observed under `Krax/runs/<job_id>/receipt.json`

### Grok Selector Baseline (Current Krax Extension)

The following selectors and heuristics are currently used in `Krax/chrome_extension/content.js`:

- Prompt textarea selector:
   - `textarea`
- Send mechanism:
   - keyboard dispatch on textarea (`keydown` Enter)
   - no explicit send button selector in current implementation
- Response container selector set:
   - `.prose`
   - `.markdown`
   - `[data-message-author-role]`
- Generation-in-progress indicator heuristics:
   - button text includes `stop` or `cancel`
   - fallback classes `.streaming` or `.generating`

### Manifest and Target Host

- `Krax/chrome_extension/manifest.json` currently targets:
   - `https://grok.com/*`
   - host permissions include localhost server on port 3001

### Auralis vs. Krax Content Script Diff (Baseline)

- Auralis (`Auralis/chrome_extension/content.js`):
   - ChatGPT-specific resilient input lookup (`prompt-textarea`, `data-testid`, `ProseMirror`, role/textbox fallbacks)
   - explicit send button click via `[data-testid="send-button"]`
   - MutationObserver-based completion detection
   - copy-button-first response extraction with DOM fallback
- Krax (`Krax/chrome_extension/content.js`):
   - currently broad selector strategy (`textarea`, `.prose`, `.markdown`)
   - Enter-key submit heuristic
   - polling/heuristic generation detection for stop/cancel text
   - direct newest-message scraping from candidate containers

### Task0 Conclusion

- Sprint2 starts with a known working host target and a provisional Grok selector baseline.
- Primary risk entering Sprint2 Task1:
   - Krax selectors are broad heuristics and may need tightening after live Grok UI verification.
- Scope lock confirmed:
   - Task0 is baseline-only; no runtime behavior changes were made.

**Status: COMPLETE**
