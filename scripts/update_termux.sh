#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."

git pull --ff-only
. .venv/bin/activate
pip install -r requirements.txt
pip install -e .

echo
echo "Update complete."
echo "Run:"
echo "  bash scripts/run_termux.sh"
