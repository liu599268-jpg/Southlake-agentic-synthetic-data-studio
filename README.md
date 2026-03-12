# Southlake Agentic Synthetic Data Studio

Pitch-ready prototype for the Ivey Recruitment Hackathon Southlake brief. The app turns a curated emergency-department public-use dataset into synthetic planning data, evaluation reports, and a three-slide pitch summary focused on methodology, features, and cautions.

## Workspace Layout

- `apps/web`: Next.js frontend
- `services/synth-api`: FastAPI backend and synthesis pipeline
- `data/presets`: curated preset datasets and source metadata
- `artifacts`: generated runs, exports, and SQLite run registry
- `pitch`: slide-ready docs, screenshots, backup packages, and visual assets

## Backend

```bash
cd /Users/haoranliu/Desktop/southlake-agentic-synthetic-data
source .venv/bin/activate
uvicorn --app-dir services/synth-api app.main:app --reload
```

## Frontend

```bash
cd /Users/haoranliu/Desktop/southlake-agentic-synthetic-data/apps/web
npm run dev
```

Set `NEXT_PUBLIC_API_BASE_URL` in `apps/web/.env.local` if the API is not running on `http://127.0.0.1:8000`.

## Bootstrap The Preset

The repo is designed around a curated subset of the 2022 CDC/NCHS NHAMCS emergency department public-use dataset. To rebuild the local preset:

```bash
cd /Users/haoranliu/Desktop/southlake-agentic-synthetic-data
source .venv/bin/activate
python services/synth-api/scripts/bootstrap_nhamcs_preset.py
```

## Notes

- The prototype is for innovation, planning, and testing only.
- It does not accept or require real Southlake patient data.
- The NHAMCS data remains subject to NCHS public-use restrictions; this repo uses a curated operational subset and preserves those cautions in the UI and generated artifacts.
- The app ships with saved demo-run cards backed by `pitch/backup/demo_runs.json` for reliable pitch-day loading.
- Rebuild the screenshots and backup video with `npm run capture:pitch-assets` once the frontend and API are both running locally.
- Rebuild the deck with `python pitch/scripts/build_deck.py`, or use `pitch/scripts/build_and_export_deck.sh` to regenerate both the `.pptx` and Keynote-exported PDF.
- Final pitch-execution materials live in `pitch/08-speaker-role-plan.md`, `pitch/09-timed-run-of-show.md`, `pitch/10-pitch-day-quick-reference.md`, and `pitch/11-source-citations.md`.
