#!/bin/bash
# Southlake Agentic Synthetic Data Studio — Setup Script
# Run this on a fresh machine after cloning the repo.

set -e

echo "======================================"
echo "Southlake Studio — Setup"
echo "======================================"
echo ""

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3 is required. Install it first."
    exit 1
fi
echo "✅ Python 3: $(python3 --version)"

# Check Node
if ! command -v node &>/dev/null; then
    echo "❌ Node.js is required. Install it first (v18+ recommended)."
    exit 1
fi
echo "✅ Node.js: $(node --version)"

# Check npm
if ! command -v npm &>/dev/null; then
    echo "❌ npm is required."
    exit 1
fi
echo "✅ npm: $(npm --version)"

echo ""
echo "--- Setting up Python backend ---"

# Create venv
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✅ Created Python virtual environment"
else
    echo "✅ Virtual environment already exists"
fi

# Install Python deps
source .venv/bin/activate
pip install -r services/synth-api/requirements.txt --quiet
echo "✅ Python dependencies installed"

echo ""
echo "--- Setting up Node frontend ---"
cd apps/web
npm install --silent
echo "✅ Node dependencies installed"
cd ../..

echo ""
echo "--- Setting up environment ---"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from example..."
    cp .env.example .env
    echo ""
    echo "🔑 IMPORTANT: Edit .env and add your LLM API key:"
    echo "   ANTHROPIC_API_KEY=sk-ant-..."
    echo ""
    echo "   Without it, the pipeline works but uses pre-built reasoning."
    echo "   With it, the LLM generates real reasoning at every step."
else
    echo "✅ .env file exists"
fi

echo ""
echo "--- Creating artifact directories ---"
mkdir -p artifacts/runs
echo "✅ Artifact directories ready"

echo ""
echo "======================================"
echo "Setup complete!"
echo "======================================"
echo ""
echo "To start the app, run these commands in two separate terminals:"
echo ""
echo "  TERMINAL 1 (Backend):"
echo "    cd $(pwd)"
echo "    source .venv/bin/activate"
echo "    uvicorn --app-dir services/synth-api app.main:app --host 127.0.0.1 --port 8000"
echo ""
echo "  TERMINAL 2 (Frontend):"
echo "    cd $(pwd)/apps/web"
echo "    NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000 npx next dev --hostname 127.0.0.1 --port 3100"
echo ""
echo "  Then open: http://127.0.0.1:3100"
echo ""
echo "⚠️  NOTE: The saved demo runs need to be generated on this machine."
echo "  After both servers are running, run:"
echo "    bash scripts/generate-demo-runs.sh"
echo ""
