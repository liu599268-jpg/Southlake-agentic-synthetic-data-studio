#!/bin/zsh
set -euo pipefail

ROOT="/Users/haoranliu/Desktop/southlake-agentic-synthetic-data"

source "$ROOT/.venv/bin/activate"
python "$ROOT/pitch/scripts/build_deck.py"
open -a Keynote
osascript "$ROOT/pitch/scripts/export_deck_pdf.applescript"
