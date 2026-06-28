#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."

pkg update
pkg install -y python git nano

python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

if [ ! -f .env ]; then
  cp .env.example .env
  echo "created .env"
fi

if [ ! -f config/topic_routes.json ]; then
  cp config/topic_routes.example.json config/topic_routes.json
  echo "created config/topic_routes.json"
fi

mkdir -p data

echo
echo "Install complete."
echo "Next:"
echo "  nano .env"
echo "  nano config/topic_routes.json"
echo "  bash scripts/run_termux.sh"
