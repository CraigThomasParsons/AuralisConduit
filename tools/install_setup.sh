#!/bin/bash
# Auralis Setup & Installation Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AURALIS_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== Auralis Setup ==="

echo "[*] Creating required directories..."
mkdir -p "$AURALIS_ROOT/inbox"
mkdir -p "$AURALIS_ROOT/outbox"
mkdir -p "$AURALIS_ROOT/runs"
mkdir -p "$AURALIS_ROOT/archive"
mkdir -p "$AURALIS_ROOT/failed"
mkdir -p "$AURALIS_ROOT/scratchpad"

echo "[*] Setting up systemd user services..."
mkdir -p ~/.config/systemd/user

# Link systemd unit for the local backend
ln -sf "$AURALIS_ROOT/systemd/auralis-server.service" ~/.config/systemd/user/

# Note: The auralis-proxy.service is considered deprecated by the Chrome extension bridge,
# so we only explicitly enable the auralis-server.service which the extension polls.

# Reload systemd and enable the server
systemctl --user daemon-reload
systemctl --user enable --now auralis-server.service

echo "=== Setup Complete! ==="
echo "The Auralis HTTP server is now running on port 3000 in the background."
echo "You can check its status with: systemctl --user status auralis-server.service"
echo "You can view its logs with: journalctl --user -fu auralis-server.service"
echo ""
echo "Next Steps to test the joke workflow:"
echo "1. Go to chrome://extensions/ and 'Load unpacked' the chrome_extension/ directory."
echo "2. Keep a chatgpt.com tab open."
echo "3. Run: mkdir -p inbox/joke_test && echo 'Tell me a short two-line joke.' > inbox/joke_test/briefing.md"
