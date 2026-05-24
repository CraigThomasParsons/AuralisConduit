#!/usr/bin/env python3
"""Populate Gitea project board Backlog for Auralis.
NOTE: Gitea 1.26.x has no board REST API — script exits cleanly with instructions.
Set PROJECT_ID at the top after creating the board on Gitea.
Usage: python3 scripts/tools/populate_board.py
"""
import os, sys, requests
from pathlib import Path

GITEA_URL  = "http://192.168.2.48:3000"
OWNER      = "craigpars"
REPO       = "Auralis"
PROJECT_ID = None   # set after creating project board on Gitea
TOKEN_FILE = Path.home() / ".config" / "pulse" / "gitea_token"

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
    except: return r.status_code, {"_raw": r.text}

def post(p, d):
    r = requests.post(f"{API}{p}", headers=HEADS, json=d)
    try: return r.status_code, r.json()
    except: return r.status_code, {}

if PROJECT_ID is None:
    print(f"\n✗ Set PROJECT_ID first. Create board at {GITEA_URL}/{OWNER}/{REPO}/projects")
    sys.exit(1)

st, cols = get(f"/projects/{PROJECT_ID}/columns")
if st != 200 or not isinstance(cols, list):
    print(f"\n✗ Gitea 1.26.x has no project board API (HTTP {st}).")
    print(f"  Populate manually: {GITEA_URL}/{OWNER}/{REPO}/projects/{PROJECT_ID}")
    sys.exit(1)

backlog_id = next((c["id"] for c in cols if "backlog" in c.get("title","").lower()), cols[0]["id"] if cols else None)
issues, page = [], 1
while True:
    st2, batch = get(f"/repos/{OWNER}/{REPO}/issues", type="issues", state="open", limit=50, page=page)
    if st2 != 200 or not isinstance(batch, list): break
    issues.extend(batch)
    if len(batch) < 50: break
    page += 1

ok = fail = 0
for i in issues:
    st3, _ = post(f"/projects/columns/{backlog_id}/cards", {"content_id": i["id"], "content_type": "issues"})
    if st3 in (200, 201, 422): ok += 1
    else: fail += 1; print(f"  ✗ #{i['number']} HTTP {st3}")

print(f"Done. Processed {ok}, Failed {fail}")
print(f"Board: {GITEA_URL}/{OWNER}/{REPO}/projects/{PROJECT_ID}")
