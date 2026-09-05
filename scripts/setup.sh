#!/usr/bin/env bash
# One-time project setup: Python venv + backend deps + frontend deps + demo data.
# Run from the project root: bash scripts/setup.sh
set -euo pipefail

cd "$(dirname "$0")/.."

echo "==> Creating Python virtual environment (.venv)"
python3 -m venv .venv
source .venv/bin/activate

echo "==> Installing Python dependencies"
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Generating demo datasets (replace with real UNSW-NB15/CICIDS2017 for real results)"
python scripts/download_datasets.py

if command -v npm >/dev/null 2>&1; then
  echo "==> Installing frontend dependencies"
  (cd dashboard/frontend && npm install)
else
  echo "==> npm not found, skipping frontend install. Install Node.js to run the dashboard UI."
fi

echo "==> Setup complete."
echo "    Train models:      python pipelines/run_all_experiments.py"
echo "    Start API:         uvicorn dashboard.backend.main:app --reload --port 8000"
echo "    Start dashboard:   (cd dashboard/frontend && npm run dev)"
