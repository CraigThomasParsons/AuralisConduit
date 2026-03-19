#!/bin/bash
# Auralis Systemd Setup Script
# Installs the Auralis server as a user systemd service

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AURALIS_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=== auralis Systemd Setup ==="

# Create user systemd directory if it doesn't exist
mkdir -p ~/.config/systemd/user

# Copy service file
cp "$AURALIS_ROOT/systemd/auralis-server.service" ~/.config/systemd/user/

# Reload systemd
systemctl --user daemon-reload

echo "[*] Service installed. Usage:"
echo ""
echo "  Start:   systemctl --user start auralis-server"
echo "  Stop:    systemctl --user stop auralis-server"
echo "  Status:  systemctl --user status auralis-server"
echo "  Logs:    journalctl --user -u auralis-server -f"
echo "  Enable:  systemctl --user enable auralis-server  (start on login)"
echo ""
