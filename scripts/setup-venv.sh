#!/usr/bin/env bash
# Create a Python 3.12+ venv and install the project with dev dependencies.
# After running, activate with: source .venv/bin/activate

set -e
cd "$(dirname "$0")/.."

PYTHON=""
for candidate in python3.12 python3.13 python3; do
  if command -v "$candidate" &>/dev/null; then
    ver=$("$candidate" -c "import sys; print(sys.version_info >= (3, 12))" 2>/dev/null || echo "False")
    if [ "$ver" = "True" ]; then
      PYTHON="$candidate"
      break
    fi
  fi
done

if [ -z "$PYTHON" ]; then
  echo "AskeeDS requires Python 3.12+. Install it (e.g. brew install python@3.12) and re-run this script." >&2
  exit 1
fi

echo "Using: $($PYTHON --version)"
if [ ! -d ".venv" ]; then
  "$PYTHON" -m venv .venv
  echo "Created .venv"
fi
# shellcheck source=/dev/null
. .venv/bin/activate
pip install -q --upgrade pip
pip install -q -e ".[rich,textual,dev]"
echo "Done. Activate with: source .venv/bin/activate"
