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
