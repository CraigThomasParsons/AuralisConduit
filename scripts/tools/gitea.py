#!/usr/bin/env python3
"""Day-to-day Gitea CLI for Auralis.
Commands: find-issue <fragment> | comment <N> <msg> | close <N> | reopen <N>
          pr <branch> <title> [body] | sprint-status
Token: GITEA_TOKEN env var or ~/.config/pulse/gitea_token
"""
import os, sys, requests
from pathlib import Path

GITEA_URL   = "http://192.168.2.48:3000"
OWNER       = "craigpars"
REPO        = "Auralis"
BASE_BRANCH = "main"
TOKEN_FILE  = Path.home() / ".config" / "pulse" / "gitea_token"

def load_token() -> str:
    t = os.environ.get("GITEA_TOKEN", "").strip()
    if t: return t
    if TOKEN_FILE.exists():
        t = TOKEN_FILE.read_text().strip()
        if t: return t
    sys.exit(f"No Gitea token. Set GITEA_TOKEN or write to {TOKEN_FILE}")

TOKEN   = load_token()
HEADS   = {"Authorization": f"token {TOKEN}", "Content-Type": "application/json"}
API     = f"{GITEA_URL}/api/v1"

def get(p, **kw):
    r = requests.get(f"{API}{p}", headers=HEADS, params=kw)
    try: return r.status_code, r.json()
    except: return r.status_code, {}

def post(p, d):
    r = requests.post(f"{API}{p}", headers=HEADS, json=d)
    try: return r.status_code, r.json()
    except: return r.status_code, {}

def patch(p, d):
    r = requests.patch(f"{API}{p}", headers=HEADS, json=d)
    try: return r.status_code, r.json()
    except: return r.status_code, {}

def find_issue(frag):
    frag = frag.lower(); page = 1
    while True:
        st, issues = get(f"/repos/{OWNER}/{REPO}/issues", type="issues", state="open", limit=50, page=page)
        if st != 200 or not isinstance(issues, list): print(f"Error: HTTP {st}"); return
        for i in issues:
            if frag in i.get("title","").lower():
                labels = ", ".join(l["name"] for l in i.get("labels",[]))
                print(f"  #{i['number']}  {i['title']}  [{labels}]")
        if len(issues) < 50: break
        page += 1

def comment(n, msg):
    st, b = post(f"/repos/{OWNER}/{REPO}/issues/{n}/comments", {"body": msg})
    print(f"  {'✓' if st in (200,201) else '✗'} #{n}")

def close(n):
    st, b = patch(f"/repos/{OWNER}/{REPO}/issues/{n}", {"state": "closed"})
    print(f"  {'✓' if st==201 else '✗'} #{n} closed")

def reopen(n):
    st, b = patch(f"/repos/{OWNER}/{REPO}/issues/{n}", {"state": "open"})
    print(f"  {'✓' if st==201 else '✗'} #{n} reopened")

def pr(branch, title, body=""):
    st, p = post(f"/repos/{OWNER}/{REPO}/pulls", {"title": title, "body": body, "head": branch, "base": BASE_BRANCH})
    if st in (200,201): print(f"  ✓ PR #{p.get('number')} {p.get('html_url')}")
    else: print(f"  ✗ HTTP {st}  {p.get('message','')}")

def sprint_status():
    st, ms = get(f"/repos/{OWNER}/{REPO}/milestones", limit=20, state="all")
    if st != 200 or not isinstance(ms, list): print(f"Error: HTTP {st}"); return
    print(f"\n{GITEA_URL}/{OWNER}/{REPO} — Sprint Status\n")
    for m in ms:
        c, o = m.get("closed_issues",0), m.get("open_issues",0)
        print(f"  [{\"█\" * c + \"░\" * o}] {c}/{c+o}  {m['title']}")

args = sys.argv[1:]
if not args: print(__doc__); sys.exit(0)
cmd = args[0]
if   cmd == "find-issue"    and len(args)>1: find_issue(args[1])
elif cmd == "comment"       and len(args)>2: comment(int(args[1]), args[2])
elif cmd == "close"         and len(args)>1: close(int(args[1]))
elif cmd == "reopen"        and len(args)>1: reopen(int(args[1]))
elif cmd == "pr"            and len(args)>2: pr(args[1], args[2], args[3] if len(args)>3 else "")
elif cmd == "sprint-status":                 sprint_status()
else: sys.exit(f"Unknown: {cmd}")
