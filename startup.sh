#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_DIR="$ROOT_DIR/apps/api"
WEB_DIR="$ROOT_DIR/apps/web"
VENV_DIR="$API_DIR/.venv"

echo "Setting up AutoAce AI..."

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: Python 3 is required." >&2
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "Error: npm is required. Install Node.js and npm first." >&2
  exit 1
fi

echo "Creating Python virtual environment..."
python3 -m venv "$VENV_DIR"

echo "Installing backend dependencies..."
"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -r "$API_DIR/requirements.txt"

echo "Installing frontend dependencies..."
npm --prefix "$WEB_DIR" install

if [[ ! -f "$WEB_DIR/.env.local" ]]; then
  cat > "$WEB_DIR/.env.local" <<'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF
  echo "Created apps/web/.env.local with localhost API configuration."
else
  echo "Keeping existing apps/web/.env.local."
fi

echo "Setup complete."
echo
echo "Start the backend with:"
echo "  cd apps/api && ./.venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo
echo "Start the frontend in another terminal with:"
echo "  cd apps/web && npm run dev"