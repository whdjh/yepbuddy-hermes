#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

if command -v pkg >/dev/null 2>&1; then
  pkg update
  pkg install -y curl git python clang rust make pkg-config libffi openssl nodejs ripgrep ffmpeg
fi

curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

echo
echo "Install complete."
echo "Next:"
echo "  bash scripts/doctor.sh"
echo "  bash scripts/setup_portal.sh"
echo "  bash scripts/run_hermes.sh"
