#!/bin/bash
# Generate the two demo runs for pitch day.
# Run this AFTER both backend and frontend are running.

set -e

API_BASE="${API_BASE:-http://127.0.0.1:8000}"

echo "Checking API health..."
if ! curl -s "$API_BASE/health" | grep -q '"ok"'; then
    echo "❌ API is not running at $API_BASE"
    echo "   Start the backend first:"
    echo "   source .venv/bin/activate && uvicorn --app-dir services/synth-api app.main:app --host 127.0.0.1 --port 8000"
    exit 1
fi
echo "✅ API is running"

echo ""
echo "--- Generating primary demo run (Distributed Campus Routing) ---"
echo "   This may take 30-60 seconds if LLM API is configured..."

PRIMARY_ID=$(curl -s -X POST "$API_BASE/api/runs" \
  -F "goal=Create a planning-grade synthetic dataset that helps Southlake innovation teams test distributed-campus routing, observation demand, and community handoff assumptions without using real patient records." \
  -F "stakeholder=Network operations team" \
  -F "scenario_id=distributed_campus_routing" \
  -F "preset_id=nhamcs_ed_2022_curated" | python3 -c "import json,sys; print(json.load(sys.stdin)['run_id'])")

echo "✅ Primary run: $PRIMARY_ID"

echo ""
echo "--- Generating backup demo run (ED Surge) ---"

BACKUP_ID=$(curl -s -X POST "$API_BASE/api/runs" \
  -F "goal=Stress-test how Southlake's emergency department would perform under surge conditions with higher arrivals, more ambulance volume, and longer throughput times." \
  -F "stakeholder=Emergency operations lead" \
  -F "scenario_id=ed_surge" \
  -F "preset_id=nhamcs_ed_2022_curated" | python3 -c "import json,sys; print(json.load(sys.stdin)['run_id'])")

echo "✅ Backup run: $BACKUP_ID"

echo ""
echo "--- Updating demo manifest ---"

cat > pitch/backup/demo_runs.json << EOF
[
  {
    "run_id": "$PRIMARY_ID",
    "label": "Primary live demo",
    "story_angle": "Distributed health network",
    "summary": "Best on-stage story for Southlake. Full LLM reasoning traces, per-column fidelity breakdown, and source-vs-synthetic distribution charts.",
    "screenshot_path": null
  },
  {
    "run_id": "$BACKUP_ID",
    "label": "Backup capacity walk-through",
    "story_angle": "ED resilience",
    "summary": "Fallback story with full LLM reasoning and analytical charts. Highlights surge pressure and throughput stress.",
    "screenshot_path": null
  }
]
EOF

echo "✅ Demo manifest updated"

echo ""
echo "======================================"
echo "Demo runs ready!"
echo "======================================"
echo "  Primary: $PRIMARY_ID (Distributed Campus Routing)"
echo "  Backup:  $BACKUP_ID (ED Surge)"
echo ""
echo "  Open http://127.0.0.1:3100 and click 'Load saved run'"
echo ""
