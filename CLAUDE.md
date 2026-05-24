# Auralis — AI Agent Context

Read this file at the start of every session.

---

## What This Project Is

**Auralis Conduit** — a local-first bridge that turns ChatGPT into a native layer
of the development environment. A lightweight local Python server + Chrome Extension
drives the ChatGPT web interface without the OpenAI API, sending prompts and
capturing responses into the local filesystem.

Role in the ecosystem: **the input layer** of the TYS (Think→Yield→Ship) Loop.
Auralis sends jobs → Krax executes with Grok → Vera validates visually → Auralis
reads the verdict and loops.

Full vision: `docs/context.md`, `docs/contracts.md`

---

## Part Of

**ArcaneArcadeMachineFactory ecosystem** — see `ArcaneArcadeMachineFactory/CLAUDE.md`

Immediate pipeline partners:
- `Vera` — visual QA; reads `krax_output.json`, writes `vera.json`
- `ContextControlledDevelopmentFactory` — dispatches sprint jobs to Auralis inbox

---

## Key Locations

| What | Where |
|---|---|
| Sprint tracker | `docs/sprint_tasks/AUTO_CONTINUE_TRACKER.md` |
| Sprint map | `docs/sprint_tasks/PHASE_SPRINT_MAP.md` |
| Per-sprint tasks | `docs/sprint_tasks/Sprint0/` … `Sprint5/` |
| Inbox (jobs in) | `inbox/` |
| Outbox (results out) | `outbox/` |
| Archive | `archive/` |
| Chrome extension | `chrome_extension/` |
| Python server | `bin/` |
| Gitea CLI | `scripts/tools/gitea.py` |

---

## Gitea

| Item | Value |
|---|---|
| Repo | `http://192.168.2.48:3000/craigpars/Auralis` |
| Gitea remote | `gitea` — `git remote add gitea ssh://git@192.168.2.48:2222/craigpars/Auralis.git` |
| GitHub remote | `origin` (AuralisConduit) |

```bash
python3 scripts/tools/gitea.py sprint-status
python3 scripts/tools/sync_to_gitea.py      # 3 milestones, 6 issues
```

### Issue Map

| # | Title | Status |
|---|---|---|
| 1 | Contracts And Scope Lock | Complete |
| 2 | Auralis Krax Handoff Wire | Complete |
| 3 | Krax Grok Browser Driver | In Progress |
| 4 | Vera Integration Fake To Real | Planned |
| 5 | Full Loop Closure | Planned |
| 6 | Hardening Retry And Observability | Planned |

---

## Current State (2026-05-23)

- Sprint0 (Contracts): complete
- Sprint1 (Handoff Wire): complete
- Sprint2 (Krax Grok Driver): **in progress** — Tasks 0+1 done, Tasks 2+ remaining
- Sprint3–5: planned

Read `docs/sprint_tasks/AUTO_CONTINUE_TRACKER.md` and the Sprint2 folder before resuming.

---

## Branch Naming

`feature/name` | `fix/name` | `docs/name` | `checkpoint/name`

PRs target `main`.

---

## Sensitive Files — Never Commit

`.env` `*.key` `config.yaml` (contains credentials) `~/.config/pulse/gitea_token`
