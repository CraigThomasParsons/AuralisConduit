# Auralis TYS Loop - Handoff Document

## Current State (Phase 1.5 & Phase 2 Complete)
- **Phase 1.5 (Grok Snippet Attachments)**: Completed. Auralis parses code blocks from ChatGPT and transmits them to Krax as an `attachments` array. Krax dynamically synthesizes `DataTransfer` blobs to inject these files natively into Grok's hidden file input.
- **Phase 2 (PostalService Integration)**: Completed. The hardcoded directory drops (`write_krax_job` / `dispatch_report_to_auralis`) have been entirely stripped out. Both servers now construct isolated `letter.toml` manifests in their `outbox/` directories and emit `package_ready` AMQP signals directly to the local RabbitMQ `postal.signals` exchange via `lib/post_office.py`.
- **Extension Tab Routing**: Fixed catastrophic loop bugs. Background scripts now use `chrome.tabs.update()` cleanly instead of endlessly spinning up new ChatGPT contexts.

## Immediate Browser-Bridge Status (2026-08-18)
The stalled ChatGPT bridge has been hardened in the working tree. The content script now uses visible/enabled selector fallbacks, waits for a new assistant turn, observes only that turn for completion, falls back from clipboard to scoped DOM extraction, and emits stage-specific failure diagnostics. The background worker waits for tab/content-script readiness, retries boundedly, validates server acknowledgements, and always releases its in-memory job lock after a terminal acknowledgement attempt.

### Remaining Live Gate
Reload the unpacked Auralis extension so Chrome picks up the changed scripts, restart the Auralis server, and run one authenticated ChatGPT job. Confirm `runs/<job_id>/response.txt`, archive movement, the PostalService package (`job.json` plus `letter.toml`), and the matching Krax `receipt.json`. Do not mark Auralis unblocked until this live evidence exists.

### Automated Evidence
- Python parser baseline: 4 tests passing.
- Codeception completion acceptance test: 1 test / 5 assertions passing.
- Content-bridge selector tests: 3 tests passing.
- JavaScript syntax checks pass for both extension scripts.

## Moving to Phase 3
Continue the existing sprint order after the live gate: finish Krax Sprint2 Tasks 2-4, then Vera integration, full-loop closure, and hardening. Playwright remains a separately scoped later migration rather than part of this repair.
