#!/usr/bin/env python3
"""Audit Auralis Gitea state: milestones, labels, issue counts, in-progress.
Usage: python3 scripts/tools/check_gitea_state.py
"""
import os, sys, requests
from pathlib import Path

GITEA_URL  = "http://192.168.2.48:3000"
OWNER      = "craigpars"
REPO       = "Auralis"
TOKEN_FILE = Path.home() / ".config" / "pulse" / "gitea_token"

def load_token():
    t = os.environ.get("GITEA_TOKEN","").strip()
    if t: return t
    if TOKEN_FILE.exists():
        t = TOKEN_FILE.read_text().strip()
        if t: return t
    sys.exit("No Gitea token. Set GITEA_TOKEN env var.")

TOKEN   = load_token()
HEADS   = {"Authorization": f"token {TOKEN}"}
API     = f"{GITEA_URL}/api/v1"

def fetch(p, **kw): return requests.get(f"{API}{p}", headers=HEADS, params=kw).json()
def sec(t): print(f"\n{'─'*52}\n  {t}\n{'─'*52}")

print(f"\n{REPO} — Gitea State")

sec("Milestones")
for m in (fetch(f"/repos/{OWNER}/{REPO}/milestones", limit=20) or []):
    c, o = m.get("closed_issues",0), m.get("open_issues",0)
    print(f"  [{\"█\"*c + \"░\"*o}] {c}/{c+o}  {m['title']}")

sec("Labels")
for l in (fetch(f"/repos/{OWNER}/{REPO}/labels", limit=20) or []):
    print(f"  id={l['id']:<4}  color={l['color']}  {l['name']}")

sec("Issue Counts")
opens   = fetch(f"/repos/{OWNER}/{REPO}/issues", type="issues", state="open",   limit=50)
closeds = fetch(f"/repos/{OWNER}/{REPO}/issues", type="issues", state="closed", limit=50)
print(f"  Open:   {len(opens)   if isinstance(opens,   list) else '?'}")
print(f"  Closed: {len(closeds) if isinstance(closeds, list) else '?'}")
if isinstance(opens, list):
    ip = [i for i in opens if any(l.get("name")=="status: in-progress" for l in i.get("labels",[]))]
    if ip:
        print(f"\n  In Progress ({len(ip)}):")
        for i in ip: print(f"    #{i['number']}  {i['title']}")

print(f"\n  Issues:  {GITEA_URL}/{OWNER}/{REPO}/issues")
print(f"  Board:   {GITEA_URL}/{OWNER}/{REPO}/milestones\n")
