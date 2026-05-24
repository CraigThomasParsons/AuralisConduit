#!/usr/bin/env python3
"""Sync Auralis sprint plan to Gitea issues and milestones.
Idempotent — safe to re-run. Skips existing titles.
Usage: python3 scripts/tools/sync_to_gitea.py
"""
import os, sys, requests
from pathlib import Path

GITEA_URL  = "http://192.168.2.48:3000"
OWNER      = "craigpars"
REPO       = "Auralis"
TOKEN_FILE = Path.home() / ".config" / "pulse" / "gitea_token"

MILESTONES = [('Phase 1 — Foundation & Contracts', 'Contracts and scope lock. Auralis→Krax handoff wire. Sprint0+Sprint1.'), ('Phase 2 — Provider Drivers', 'Krax Grok browser driver. Vera integration fake→real. Sprint2+Sprint3.'), ('Phase 3 — Loop Closure & Hardening', 'Full TYS loop closure. Contracts enforced, retries, audit trail. Sprint4+Sprint5.')]

SPRINTS = [('Contracts And Scope Lock', 'Phase 1 — Foundation & Contracts', 'Complete'), ('Auralis Krax Handoff Wire', 'Phase 1 — Foundation & Contracts', 'Complete'), ('Krax Grok Browser Driver', 'Phase 2 — Provider Drivers', 'In Progress'), ('Vera Integration Fake To Real', 'Phase 2 — Provider Drivers', 'Planned'), ('Full Loop Closure', 'Phase 3 — Loop Closure & Hardening', 'Planned'), ('Hardening Retry And Observability', 'Phase 3 — Loop Closure & Hardening', 'Planned')]

LABELS = [('sprint', '0075ca'), ('status: complete', '1a7f37'), ('status: in-progress', 'e4810d'), ('status: planned', '6e7781')]

STATUS_MAP = {'Complete': 'status: complete', 'In Progress': 'status: in-progress', 'Planned': 'status: planned'}

def load_token():
    t = os.environ.get("GITEA_TOKEN","").strip()
    if t: return t
    if TOKEN_FILE.exists():
        t = TOKEN_FILE.read_text().strip()
        if t: return t
    sys.exit("No Gitea token.")

TOKEN = load_token()
HEADS = {"Authorization": f"token {TOKEN}", "Content-Type": "application/json"}
API   = f"{GITEA_URL}/api/v1"

def get(p, **kw):
    r = requests.get(f"{API}{p}", headers=HEADS, params=kw)
    try: return r.status_code, r.json()
    except: return r.status_code, {}

def post(p, d):
    r = requests.post(f"{API}{p}", headers=HEADS, json=d)
    try: return r.status_code, r.json()
    except: return r.status_code, {}

def ensure_label(name, color):
    st, labels = get(f"/repos/{OWNER}/{REPO}/labels", limit=50)
    if st == 200 and isinstance(labels, list):
        for l in labels:
            if l.get("name") == name: return l["id"]
    st, b = post(f"/repos/{OWNER}/{REPO}/labels", {"name": name, "color": f"#{color}"})
    if st in (200,201): print(f"  + label {name}"); return b["id"]
    print(f"  ✗ label {name} HTTP {st}"); return None

def ensure_milestone(title, desc):
    st, ms = get(f"/repos/{OWNER}/{REPO}/milestones", limit=50, state="all")
    if st == 200 and isinstance(ms, list):
        for m in ms:
            if m.get("title") == title: return m["id"]
    st, b = post(f"/repos/{OWNER}/{REPO}/milestones", {"title": title, "description": desc})
    if st in (200,201): print(f"  + milestone {title}"); return b["id"]
    print(f"  ✗ milestone {title} HTTP {st}"); return None

def issue_exists(title):
    for state in ("open","closed"):
        page = 1
        while True:
            st, issues = get(f"/repos/{OWNER}/{REPO}/issues", type="issues", state=state, limit=50, page=page)
            if st != 200 or not isinstance(issues, list): break
            for i in issues:
                if i.get("title") == title: return i["number"]
            if len(issues) < 50: break
            page += 1
    return None

def create_issue(title, body, ms_id, label_ids):
    existing = issue_exists(title)
    if existing:
        print(f"  · #{existing:>3}  {title[:60]}  (exists)")
        return existing
    payload = {"title": title, "body": body}
    if ms_id: payload["milestone"] = ms_id
    if label_ids: payload["labels"] = label_ids
    st, issue = post(f"/repos/{OWNER}/{REPO}/issues", payload)
    if st in (200,201): print(f"  ✓ #{issue.get('number','?'):>3}  {title[:60]}"); return issue.get("number")
    print(f"  ✗  {title[:60]} HTTP {st}"); return None

print(f"\nTarget: {GITEA_URL}/{OWNER}/{REPO}\n")

print("── Labels ─────────────────────────────────────────")
label_ids = {}
for name, color in LABELS:
    lid = ensure_label(name, color)
    if lid: label_ids[name] = lid

print("\n── Milestones ──────────────────────────────────────")
ms_ids = {}
for title, desc in MILESTONES:
    mid = ensure_milestone(title, desc)
    if mid: ms_ids[title] = mid

print("\n── Issues ──────────────────────────────────────────")
failed = 0
for sprint_title, ms_title, status in SPRINTS:
    ms_id     = ms_ids.get(ms_title)
    sl        = STATUS_MAP.get(status, "status: planned")
    lids      = [v for k,v in label_ids.items() if k in ("sprint", sl)]
    if create_issue(sprint_title, f"## {sprint_title}\n\nPhase: {ms_title}\nStatus: {status}", ms_id, lids) is None:
        failed += 1

print(f"\n── Done  Total: {len(SPRINTS)}  Failed: {failed}")
print(f"  {GITEA_URL}/{OWNER}/{REPO}/issues\n")
