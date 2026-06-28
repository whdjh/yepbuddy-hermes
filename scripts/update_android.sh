#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

git pull --ff-only

if command -v hermes >/dev/null 2>&1; then
  hermes update || curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
else
  curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
fi

echo
echo "Update complete."
echo "Run:"
echo "  bash scripts/doctor.sh"
echo "  bash scripts/run_hermes.sh"
