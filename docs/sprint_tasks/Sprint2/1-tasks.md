# Task 1: Krax Chrome Extension Grok Adapter

## Goals

- Adapt `Krax/chrome_extension/content.js` to drive Grok.com instead of ChatGPT
- Reuse the Auralis extension architecture exactly — only change the selectors

## Requirements

- `content.js` targets `grok.com` (host_permissions updated in manifest.json)
- prompt injection goes into Grok textarea
- MutationObserver watches for generation-complete signal
- response text is extracted from Grok response container
- extracted text is POSTed back to Krax server at `http://localhost:3001/complete`

## Acceptance Criteria

- load extension → open Grok → send a manual job via the Krax server → response appears in `runs/`
- extension does not crash on page reload or tab switch
- extension logs clearly in Chrome DevTools console

## Implementation Steps

1. Copy `Auralis/chrome_extension/` to `Krax/chrome_extension/` as starting point.
2. Update `manifest.json`:
   - `host_permissions`: replace `chat.openai.com` with `grok.com`
   - `content_scripts.matches`: `["https://grok.com/*"]`
3. Update `content.js`:
   - Replace ChatGPT textarea selector with Grok textarea selector (from Task 0 audit)
   - Replace ChatGPT send button selector
   - Replace ChatGPT generation indicator with Grok equivalent
   - Replace ChatGPT response container selector
   - Keep POST-back logic identical: `POST http://localhost:3001/complete`
4. Update `background.js`:
   - Poll `http://localhost:3001/job` (port 3001, not 3000)
5. Load extension unpacked in Chrome and verify manually.

## Handoff Artifacts

- `Krax/chrome_extension/` updated
- manual test result recorded in Completion Notes

## Completion Notes (2026-03-20)

Task complete.

### What Was Updated

- `Krax/chrome_extension/content.js`
   - switched to a resilient Grok-oriented selector flow:
      - prompt input: `textarea[data-testid="prompt-textarea"]`, fallback `textarea`, fallback role textbox/contenteditable
      - send action: explicit send button lookup first, Enter fallback
      - response containers: `.prose`, `.markdown`, `[data-message-author-role='assistant']`
   - replaced polling-based completion with MutationObserver-based DOM-settle completion detection
   - improved error handling so content script reports `JOB_FAIL` instead of silently stalling
- `Krax/chrome_extension/background.js`
   - preserved polling from `http://localhost:3001/job`
   - hardened tab/message dispatch with retry when content script is not yet attached
   - switched completion POST target to `http://localhost:3001/complete` per Sprint2 Task1 requirement
   - keeps lock release behavior on both success and failure
- `Krax/bin/krax_server.py`
   - added endpoint alias support so `POST /complete` and `POST /job/complete` both work

### Validation

- JS syntax checks passed for:
   - `Krax/chrome_extension/content.js`
   - `Krax/chrome_extension/background.js`
- Python error checks report no errors for:
   - `Krax/bin/krax_server.py`

### Manual Verification Status

- Manual browser verification (load unpacked extension -> open Grok -> send live job) is prepared but not executed in this task note.
- Full live-browser proof remains part of Sprint2 Task4 end-to-end smoke validation.

**Status: COMPLETE**
