from __future__ import annotations

import os
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
PRESETS_DIR = WORKSPACE_ROOT / "data" / "presets"
ARTIFACTS_ROOT = WORKSPACE_ROOT / "artifacts"
RUNS_DIR = ARTIFACTS_ROOT / "runs"
PITCH_DIR = WORKSPACE_ROOT / "pitch"
PITCH_ASSETS_DIR = PITCH_DIR / "assets"
PITCH_BACKUP_DIR = PITCH_DIR / "backup"
DEMO_RUN_MANIFEST_PATH = PITCH_BACKUP_DIR / "demo_runs.json"
DATABASE_PATH = ARTIFACTS_ROOT / "runs.sqlite3"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
API_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "API_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3100,http://127.0.0.1:3100",
    ).split(",")
    if origin.strip()
]

PRESET_ID = "nhamcs_ed_2022_curated"
PRESET_CSV_PATH = PRESETS_DIR / f"{PRESET_ID}.csv"
PRESET_METADATA_PATH = PRESETS_DIR / f"{PRESET_ID}.metadata.json"

for path in (PRESETS_DIR, ARTIFACTS_ROOT, RUNS_DIR, PITCH_DIR, PITCH_ASSETS_DIR, PITCH_BACKUP_DIR):
    path.mkdir(parents=True, exist_ok=True)
