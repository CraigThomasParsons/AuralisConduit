#!/bin/bash
# Auralis Server Restart Script
# Kills any existing server and starts a new one

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AURALIS_ROOT="$(dirname "$SCRIPT_DIR")"
SERVER_SCRIPT="$AURALIS_ROOT/bin/auralis_server.py"

echo "=== Auralis Server Restart ==="

# Kill any existing auralis server processes
echo "[*] Stopping existing server(s)..."
pkill -f "auralis_server.py" 2>/dev/null

# Also kill anything on port 3000
fuser -k 3000/tcp 2>/dev/null

# Wait for port to be released
sleep 1

# Start the server
echo "[*] Starting Auralis server..."
cd "$AURALIS_ROOT"
python3 "$SERVER_SCRIPT"
