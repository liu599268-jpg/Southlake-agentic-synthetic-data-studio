#!/bin/zsh
set -euo pipefail

ROOT="/Users/haoranliu/Desktop/southlake-agentic-synthetic-data"

source "$ROOT/.venv/bin/activate"
python "$ROOT/pitch/scripts/build_deck.py"

if [[ -d /Applications/Keynote.app ]]; then
  open -a Keynote
  sleep 3
  python - <<PY
import subprocess
import sys

try:
    subprocess.run(
        ["osascript", "$ROOT/pitch/scripts/export_deck_pdf.applescript"],
        check=True,
        timeout=25,
    )
except subprocess.TimeoutExpired:
    print("Keynote PDF export timed out; keeping the existing PDF backup.", file=sys.stderr)
except subprocess.CalledProcessError as exc:
    print(f"Keynote PDF export failed with exit code {exc.returncode}; keeping the existing PDF backup.", file=sys.stderr)
PY
fi
