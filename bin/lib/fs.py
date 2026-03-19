import os
import shutil
from typing import Optional, Dict

AURALIS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
INBOX_DIR = os.path.join(AURALIS_ROOT, "inbox")
RUNS_DIR = os.path.join(AURALIS_ROOT, "runs")
OUTBOX_DIR = os.path.join(AURALIS_ROOT, "outbox")
ARCHIVE_DIR = os.path.join(AURALIS_ROOT, "archive")
FAILED_DIR = os.path.join(AURALIS_ROOT, "failed")

REQUIRED_FILES = ["briefing.md"]
OPTIONAL_FILES = ["context.md", "goals.md", "success.md", "steps.md", "url.txt"]

def find_jobs():
    """Returns a list of job IDs (subdirectories in inbox)."""
    jobs = []
    if not os.path.exists(INBOX_DIR):
        return []
    
    for item in os.listdir(INBOX_DIR):
        job_path = os.path.join(INBOX_DIR, item)
        if os.path.isdir(job_path):
            jobs.append(item)
    return sorted(jobs)

def read_job_files(job_id: str) -> Dict[str, str]:
    """Reads content of all md files in the job directory."""
    job_dir = os.path.join(INBOX_DIR, job_id)
    data = {}
    
    for fname in REQUIRED_FILES + OPTIONAL_FILES:
        fpath = os.path.join(job_dir, fname)
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                data[fname] = f.read().strip()
                
    # Validate requirements
    for fname in REQUIRED_FILES:
        if fname not in data:
            raise ValueError(f"Job {job_id} missing required file: {fname}")
            
    return data

def compose_briefing(job_id: str, job_data: Dict[str, str]) -> str:
    """Combines job markdown files into a single prompt."""
    lines = []
    # Order of presentation
    order = ["briefing.md", "context.md", "goals.md", "success.md", "steps.md"]

    # Execution Mode Logic (Phase 4 Refactor)
    # If the briefing contains strict indicators, we must NOT add agent boilerplate headers.
    raw_briefing = job_data.get("briefing.md", "")
    if "===FILE:" in raw_briefing:
        # Execution Job: Return pure content with clean newlines
        body_lines = []
        for fname in order:
            if fname in job_data:
                body_lines.append(job_data[fname])
                
        return "\n\n".join(body_lines)
    
    # Chat Mode: Add headers and footers
    lines.append(f"## AURALIS AUTOMATION AGENT - Job ID: {job_id}")
    lines.append("I am Auralis, an automated agent executing this job.")
    lines.append("")
    
    for fname in order:
        if fname in job_data:
            section_name = fname.replace(".md", "").upper()
            lines.append(f"### {section_name}")
            lines.append(job_data[fname])
            lines.append("")
            
    lines.append("### INSTRUCTIONS FOR RESPONSE")
    lines.append("1. Acknowledge this briefing.")
    lines.append("2. Provide response in NUMBERED STEPS.")
    lines.append("3. Provide file outputs in CODE BLOCKS with the filename on the first line.")
    lines.append("4. Act as the hands to solve this task.")
    
    return "\n\n".join(lines)

def init_run(job_id: str) -> str:
    """Creates a run directory for the job and returns its path."""
    run_dir = os.path.join(RUNS_DIR, job_id)
    os.makedirs(run_dir, exist_ok=True)
    return run_dir

def archive_job(job_id: str):
    """Moves job from inbox to archive."""
    src = os.path.join(INBOX_DIR, job_id)
    dst = os.path.join(ARCHIVE_DIR, job_id)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.move(src, dst)

def fail_job(job_id: str):
    """Moves job from inbox to failed."""
    src = os.path.join(INBOX_DIR, job_id)
    dst = os.path.join(FAILED_DIR, job_id)
    if os.path.exists(dst):
        shutil.rmtree(dst)
    shutil.move(src, dst)

def write_handoff(job_id: str, run_dir: str):
    """Writes a handoff marker file to outbox."""
    os.makedirs(OUTBOX_DIR, exist_ok=True)
    handoff_path = os.path.join(OUTBOX_DIR, f"{job_id}_handoff.md")
    with open(handoff_path, "w") as f:
        f.write(f"# Job {job_id} Handoff\n")
        f.write(f"Run Directory: {run_dir}\n")
        f.write("Status: Proxied to ChatGPT.\n")
