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
