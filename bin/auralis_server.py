#!/usr/bin/env python3
import http.server
import socketserver
import json
import os
import sys
import uuid
from datetime import datetime, timezone

# Ensure we can import from lib
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

import subprocess
import shlex
from lib import fs, parser

PORT = 3000
SCHEMA_VERSION = "v1"


def load_config(config_path: str) -> dict:
    config = {}

    if not os.path.exists(config_path):
        return config

    with open(config_path, "r", encoding="utf-8") as config_file:
        for raw_line in config_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue

            key, value = line.split(":", 1)
            config[key.strip()] = value.strip()

    return config


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def first_non_empty_line(text: str) -> str:
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line:
            return line
    return ""


def normalize_goal(job_data: dict) -> str:
    explicit_goal = job_data.get("goals.md", "").strip()
    if explicit_goal:
        return first_non_empty_line(explicit_goal)

    briefing = job_data.get("briefing.md", "").strip()
    if briefing:
        return first_non_empty_line(briefing)

    return "Implement the requested task."


def build_context(job_id: str, job_data: dict, run_dir: str) -> str:
    context_parts = [f"Auralis source job: {job_id}"]

    for key in ("context.md", "goals.md", "success.md", "steps.md"):
        value = job_data.get(key, "").strip()
        if value:
            label = key.replace(".md", "")
            context_parts.append(f"{label}: {value}")

    context_parts.append(f"source_run: {run_dir}")
    return "\n\n".join(context_parts)


def build_krax_contract(source_job_id: str, job_data: dict, run_dir: str, instructions: str) -> tuple[str, dict]:
    krax_job_id = str(uuid.uuid4())
    correlation_id = str(uuid.uuid4())

    contract = {
        "schema_version": SCHEMA_VERSION,
        "job_id": krax_job_id,
        "correlation_id": correlation_id,
        "causation_id": None,
        "created_at": utc_now_iso(),
        "source_agent": "auralis",
        "attempt": 1,
        "goal": normalize_goal(job_data),
        "context": build_context(source_job_id, job_data, run_dir),
        "instructions": instructions.strip(),
        "constraints": [],
        "artifact_refs": [
            os.path.join(run_dir, "response.txt"),
        ],
        "artifacts_expected": [
            "krax_output.json",
            "extracted/*",
        ],
        "source_run": run_dir,
        "metadata": {
            "auralis_job_id": source_job_id,
        },
    }

    return krax_job_id, contract


def write_json_atomic(file_path: str, payload: dict):
    temp_path = f"{file_path}.tmp"
    with open(temp_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    os.replace(temp_path, file_path)


def write_krax_job(source_job_id: str, job_data: dict, run_dir: str, instructions: str, config: dict):
    krax_inbox_root = config.get("krax_inbox_path", "").strip()
    if not krax_inbox_root:
        print("[TYS] Warning: krax_inbox_path is not configured; skipping Krax dispatch.")
        return

    if not os.path.isdir(krax_inbox_root):
        print(f"[TYS] Warning: Krax inbox path does not exist: {krax_inbox_root}; skipping Krax dispatch.")
        return

    krax_job_id, krax_contract = build_krax_contract(source_job_id, job_data, run_dir, instructions)
    krax_job_dir = os.path.join(krax_inbox_root, krax_job_id)
    os.makedirs(krax_job_dir, exist_ok=True)

    krax_payload_path = os.path.join(krax_job_dir, "job.json")
    write_json_atomic(krax_payload_path, krax_contract)
    print(f"[TYS] Krax job dispatched: {krax_job_id}")


CONFIG = load_config(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yaml"))

class AuralisHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*') # Allow extension to access
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        if self.path == '/job':
            # 1. Find next job
            jobs = fs.find_jobs()
            if not jobs:
                self._set_headers(200)
                self.wfile.write(json.dumps(None).encode())
                return

            job_id = jobs[0]
            try:
                # 2. Read job data
                job_data = fs.read_job_files(job_id)
                briefing = fs.compose_briefing(job_id, job_data)
                url = job_data.get("url.txt", "https://chatgpt.com/")
                
                # 3. Create run dir (if not exists)
                fs.init_run(job_id)
                
                response = {
                    "id": job_id,
                    "url": url,
                    "prompt": briefing
                }
                self._set_headers(200)
                self.wfile.write(json.dumps(response).encode())
            except Exception as e:
                print(f"Error reading job {job_id}: {e}")
                self._set_headers(500)
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self._set_headers(404)

    def do_POST(self):
        if self.path == '/job/complete':
            length = int(self.headers.get('content-length'))
            raw_data = self.rfile.read(length)
            print(f"DEBUG: Received payload size: {length}")
            
            try:
                data = json.loads(raw_data)
            except json.JSONDecodeError as e:
                print(f"DEBUG: JSON Parse Error: {e}")
                print(f"DEBUG: Raw Data: {raw_data}")
                self._set_headers(400)
                return
            
            job_id = data.get("id")
            result_text = data.get("response")
            debug_info = data.get("debug", "No debug info")
            
            print(f"DEBUG: Job ID: {job_id}")
            print(f"DEBUG: Client Log: {debug_info}")
            print(f"DEBUG: Response length: {len(result_text) if result_text else 0}")
            
            if not job_id:
                self._set_headers(400)
                return

            if not isinstance(result_text, str) or not result_text.strip():
                self._set_headers(400)
                self.wfile.write(json.dumps({"error": "Missing response text"}).encode())
                return

            print(f"[*] Job {job_id} completed by Extension.")
            job_data = fs.read_job_files(job_id)
            
            # 1. Save Response Text
            run_dir = os.path.join(fs.RUNS_DIR, job_id)
            os.makedirs(run_dir, exist_ok=True)
            
            with open(os.path.join(run_dir, "response.txt"), "w") as f:
                f.write(result_text)
                
            # =============== EXTRACT SNIPPETS ==================
            # Delegate parsing of snippet blocks to the parser library
            extracted_snippets = parser.extract_snippet_files(result_text)
            
            # Build an extraction directory to isolate parsed code from other run files
            extracted_dir = os.path.join(run_dir, "extracted")
            
            # Start tracking extraction metadata for the manifest
            manifest = []
            
            # Process returned files only if any valid code blocks were discovered
            if extracted_snippets:
                
                # Ensure the container directory exists before attempting writes
                os.makedirs(extracted_dir, exist_ok=True)
                
                # Iterate each tracked snippet payload structure
                for snippet in extracted_snippets:
                    
                    # Establish a stable unique filename in case of collisions
                    final_filename = snippet.filename
                    target_file_path = os.path.join(extracted_dir, final_filename)
                    counter = 2
                    
                    # Prevent overwrites by detecting collisions automatically 
                    while os.path.exists(target_file_path):
                        
                        # Split name and extension to inject the counter properly
                        base, ext = os.path.splitext(snippet.filename)
                        final_filename = f"{base}.{counter}{ext}"
                        target_file_path = os.path.join(extracted_dir, final_filename)
                        counter += 1
                        
                    # Write the fully realized code string out to the targeted path
                    with open(target_file_path, "w") as sf:
                        sf.write(snippet.code)
                        
                    # Maintain context for debugging and tracking
                    print(f"  - Extracted snippet: {final_filename}")
                    
                    # Append strict property definitions to our run manifest array
                    manifest.append({
                        "filename": final_filename,
                        "language": snippet.language,
                        "detection_method": snippet.detection_method,
                        "confidence": snippet.confidence
                    })
                    
                # Store the manifest index beside the snippets
                manifest_path = os.path.join(run_dir, "extracted_files.json")
                with open(manifest_path, "w") as mf:
                    mf.write(json.dumps(manifest, indent=2))
            # ===================================================
                
            # 2. Parse & Execute (Phase 4.5)
            print(f"  - Parsing response...")
            actions = parser.parse_response(result_text)
            
            log_lines = []
            
            repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            scratchpad_dir = os.path.join(repo_root, "scratchpad")
            os.makedirs(scratchpad_dir, exist_ok=True)
            
            # ALLOWLIST for Phase 4.5
            ALLOWED_COMMANDS = [
                "python", "python3", 
                "pip", "pip3", 
                "node", "npm", 
                "ls", "cat", "echo", "pwd",
                "mkdir", "cp", "mv"
            ]

            for action in actions:
                try:
                    if action["type"] == "file":
                        # Validate and map to scratchpad
                        target_path = parser.validate_path(repo_root, action["path"])
                        
                        # Ensure dir exists
                        os.makedirs(os.path.dirname(target_path), exist_ok=True)
                        
                        with open(target_path, "w") as f:
                            f.write(action["content"])
                            
                        log_lines.append(f"Wrote file: {target_path}")
                        print(f"  - Wrote: {target_path}")
                        
                    elif action["type"] == "run":
                        # Controlled Execution
                        cmd_str = action["content"].strip()
                        # Split safely? For now strictly simple commands.
                        # We just check if it starts with allowed command.
                        
                        cmd_parts = shlex.split(cmd_str)
                        if not cmd_parts:
                            continue
                            
                        base_cmd = cmd_parts[0]
                        if base_cmd not in ALLOWED_COMMANDS:
                            msg = f"Skipped forbidden command: {base_cmd}"
                            log_lines.append(msg)
                            print(f"  - {msg}")
                            continue
                        
                        print(f"  - Running: {cmd_str}")
                        log_lines.append(f"CMD: {cmd_str}")
                        
                        try:
                            res = subprocess.run(
                                cmd_str, 
                                shell=True, 
                                cwd=scratchpad_dir,
                                capture_output=True,
                                text=True,
                                timeout=5,
                                stdin=subprocess.DEVNULL
                            )
                            log_lines.append(f"EXIT: {res.returncode}")
                            if res.stdout:
                                log_lines.append(f"STDOUT:\n{res.stdout}")
                            if res.stderr:
                                log_lines.append(f"STDERR:\n{res.stderr}")
                                
                        except subprocess.TimeoutExpired:
                            log_lines.append("ERROR: Timeout (5s)")
                            print("  - Timeout")
                        except Exception as e:
                            log_lines.append(f"ERROR: {e}")
                            print(f"  - Error: {e}")

                except Exception as e:
                    # Generic error catching (parsing, writing etc)
                    log_lines.append(f"Error handling action: {e}")
                    print(f"  - Error: {e}")
            
            # Save Execution Log
            with open(os.path.join(run_dir, "execution.log"), "w") as f:
                f.write("\n".join(log_lines))

            # 3. Handoff to Krax (Sprint1 Task 1)
            try:
                write_krax_job(job_id, job_data, run_dir, result_text, CONFIG)
            except Exception as exc:
                print(f"[TYS] Warning: failed to dispatch Krax job for {job_id}: {exc}")
            
            # Also write standard diagnostic handoff record
            fs.write_handoff(job_id, run_dir)
            
            # 4. Archive Phase
            fs.archive_job(job_id)
            
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "archived"}).encode())
            
        elif self.path == '/job/fail':
            length = int(self.headers.get('content-length'))
            data = json.loads(self.rfile.read(length))
            job_id = data.get("id")
            error = data.get("error")
            
            print(f"[!] Job {job_id} failed: {error}")
            fs.fail_job(job_id)
            
            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "failed"}).encode())
            
        else:
            self._set_headers(404)

def run():
    print(f"[*] Auralis Server running on port {PORT}")
    
    # Custom server class with SO_REUSEADDR to allow immediate port reuse
    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True
    
    with ReusableTCPServer(("", PORT), AuralisHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] Server stopped.")
        finally:
            httpd.server_close()

if __name__ == "__main__":
    run()
