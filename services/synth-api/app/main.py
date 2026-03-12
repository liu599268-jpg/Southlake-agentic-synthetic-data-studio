from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import API_ORIGINS, DEMO_RUN_MANIFEST_PATH, PRESET_ID
from .models import DemoRunSummary, PresetLoadRequest, PresetLoadResponse, PresetInfo, RunResponse
from .pipeline import (
    SCENARIOS,
    build_upload_source_info,
    get_scenario,
    iso_timestamp,
    load_preset_info,
    profile_dataframe,
    run_pipeline,
)
from .storage import init_db, load_run, save_run

app = FastAPI(title="Southlake Agentic Synthetic Data Studio API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=API_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
init_db()


def build_demo_run_summaries() -> list[DemoRunSummary]:
    if not DEMO_RUN_MANIFEST_PATH.exists():
        return []

    try:
        manifest = json.loads(DEMO_RUN_MANIFEST_PATH.read_text())
    except json.JSONDecodeError:
        return []

    summaries: list[DemoRunSummary] = []
    for item in manifest:
        run_id = str(item.get("run_id", "")).strip()
        if not run_id:
            continue

        payload = load_run(run_id)
        if payload is None:
            continue

        run = RunResponse(**payload)
        summaries.append(
            DemoRunSummary(
                run_id=run.run_id,
                label=str(item.get("label", run.scenario.name)),
                story_angle=str(item.get("story_angle", run.scenario.description)),
                summary=str(item.get("summary", "")) or run.cautions.headline,
                scenario_name=run.scenario.name,
                stakeholder=run.plan.stakeholder,
                fidelity_score=run.evaluation.fidelity_score,
                privacy_score=run.evaluation.privacy_score,
                utility_score=run.evaluation.utility_score,
                screenshot_path=item.get("screenshot_path"),
            )
        )
    return summaries


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/presets/load", response_model=PresetLoadResponse)
def load_preset(request: PresetLoadRequest) -> PresetLoadResponse:
    if request.preset_id != PRESET_ID:
        raise HTTPException(status_code=404, detail="Unknown preset")

    dataframe, preset = load_preset_info()
    profile = profile_dataframe(dataframe, preset.name)
    return PresetLoadResponse(
        preset=preset,
        profile=profile,
        scenarios=SCENARIOS,
        demo_runs=build_demo_run_summaries(),
    )


@app.post("/api/runs", response_model=RunResponse)
async def create_run(
    goal: str = Form(...),
    stakeholder: str = Form("Hospital operations lead"),
    scenario_id: str = Form("ed_surge"),
    preset_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(default=None),
) -> RunResponse:
    if not goal.strip():
        raise HTTPException(status_code=400, detail="Goal is required")

    if file is None and preset_id != PRESET_ID:
        raise HTTPException(status_code=400, detail="Provide the default preset or upload a CSV")

    scenario = get_scenario(scenario_id)

    if file is not None:
        if not file.filename or not file.filename.lower().endswith(".csv"):
            raise HTTPException(status_code=400, detail="Only CSV uploads are supported in v1")
        content = await file.read()
        try:
            dataframe = pd.read_csv(pd.io.common.BytesIO(content))
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Unable to read CSV: {exc}") from exc
        source_info = build_upload_source_info(file.filename, dataframe)
        effective_preset_id = None
    else:
        dataframe, source_info = load_preset_info()
        effective_preset_id = preset_id

    response = run_pipeline(
        source_df=dataframe,
        source_info=source_info,
        scenario=scenario,
        goal=goal.strip(),
        stakeholder=stakeholder.strip() or scenario.stakeholder,
    )

    artifact_dir = Path(response.artifacts["artifact_dir"])
    save_run(
        run_id=response.run_id,
        created_at=iso_timestamp(),
        status=response.status,
        preset_id=effective_preset_id,
        scenario_id=scenario.id,
        artifact_dir=artifact_dir,
        payload=response.model_dump(),
    )
    return response


@app.get("/api/runs/{run_id}", response_model=RunResponse)
def get_run(run_id: str) -> RunResponse:
    payload = load_run(run_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunResponse(**payload)


@app.get("/api/runs/{run_id}/download")
def download_run(run_id: str) -> FileResponse:
    payload = load_run(run_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Run not found")
    zip_path = payload["artifacts"]["download_zip"]
    return FileResponse(
        path=zip_path,
        filename=f"southlake-run-{run_id}.zip",
        media_type="application/zip",
    )
