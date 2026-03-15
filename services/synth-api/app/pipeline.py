from __future__ import annotations

import json
import hashlib
import math
import random
import re
import warnings
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4
from zipfile import ZIP_DEFLATED, ZipFile

import numpy as np
import pandas as pd

from .config import PITCH_DIR, PRESET_CSV_PATH, PRESET_ID, PRESET_METADATA_PATH, RUNS_DIR
from .llm_client import ReasoningClient
from .models import (
    AgentStep,
    CautionReport,
    DatasetProfile,
    EvalReport,
    PitchSummary,
    PresetInfo,
    RunResponse,
    ScenarioPreset,
    SynthesisPlan,
)

try:
    from sdv.metadata import SingleTableMetadata
    from sdv.single_table import GaussianCopulaSynthesizer

    SDV_AVAILABLE = True
except Exception:
    SDV_AVAILABLE = False


SCENARIOS = [
    ScenarioPreset(
        id="ed_surge",
        name="ED Surge",
        description="Stress-test higher arrivals, ambulance volume, and longer throughput in an innovation sandbox.",
        stakeholder="Emergency operations lead",
        planning_goal="Understand how a Southlake surge scenario reshapes volume, acuity, and visit duration before touching governed local data.",
        row_multiplier=1.3,
        pressure_notes=[
            "Increase visit volume and ambulance arrivals.",
            "Shift triage toward more urgent categories.",
            "Lengthen wait and visit duration.",
        ],
    ),
    ScenarioPreset(
        id="community_diversion",
        name="Community Diversion",
        description="Model lower-acuity demand redirected to community-connected access points and closer-to-home channels.",
        stakeholder="Distributed care planner",
        planning_goal="Show how non-urgent ED demand could move closer to home through community-connected channels in a distributed network.",
        row_multiplier=0.88,
        pressure_notes=[
            "Reduce low-acuity ED visits.",
            "Shorten waits and visit duration.",
            "Increase home/community resolution.",
        ],
    ),
    ScenarioPreset(
        id="regional_growth",
        name="Regional Growth",
        description="Project regional growth with higher chronic disease complexity and future-state capacity pressure.",
        stakeholder="Regional strategy team",
        planning_goal="Demonstrate how regional growth could increase visit count, chronic burden, and future-state capacity pressure.",
        row_multiplier=1.15,
        pressure_notes=[
            "Increase total visits modestly.",
            "Shift age and chronic burden upward.",
            "Raise inpatient conversion slightly.",
        ],
    ),
    ScenarioPreset(
        id="distributed_campus_routing",
        name="Distributed Campus Routing",
        description="Model how a distributed health network shifts care across campus, observation, community, and transfer pathways.",
        stakeholder="Network operations team",
        planning_goal="Create a planning-grade synthetic dataset that helps Southlake innovation teams test distributed-campus routing, observation demand, and community handoff assumptions without using real patient records.",
        row_multiplier=1.0,
        pressure_notes=[
            "Increase observation and transfer pathways.",
            "Preserve total volume while shifting disposition mix.",
            "Use routing-focused caution language.",
        ],
    ),
]

SENSITIVE_KEYWORDS = {
    "age",
    "sex",
    "gender",
    "race",
    "ethnicity",
    "payer",
    "reason",
    "diagnosis",
    "triage",
    "ambulance",
    "admit",
}

NUMERIC_HELPERS = {
    "arrival_hour",
    "wait_time_minutes",
    "length_of_visit_minutes",
    "age_years",
    "pain_scale",
    "chronic_conditions_count",
    "observation_minutes",
}


def load_preset_info() -> tuple[pd.DataFrame, PresetInfo]:
    if not PRESET_CSV_PATH.exists() or not PRESET_METADATA_PATH.exists():
        raise FileNotFoundError(
            "Preset data is missing. Run `python services/synth-api/scripts/bootstrap_nhamcs_preset.py`."
        )

    dataframe = pd.read_csv(PRESET_CSV_PATH)
    metadata = json.loads(PRESET_METADATA_PATH.read_text())
    preset = PresetInfo(**metadata)
    return dataframe, preset


def get_scenario(scenario_id: str) -> ScenarioPreset:
    for scenario in SCENARIOS:
        if scenario.id == scenario_id:
            return scenario
    return SCENARIOS[0]


def sanitize_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    clean_columns = []
    for column in dataframe.columns:
        clean = re.sub(r"[^a-zA-Z0-9]+", "_", str(column).strip().lower()).strip("_")
        clean_columns.append(clean or f"column_{len(clean_columns) + 1}")
    sanitized = dataframe.copy()
    sanitized.columns = clean_columns
    return sanitized


def _safe_preview(dataframe: pd.DataFrame, limit: int = 8) -> list[dict[str, Any]]:
    preview = dataframe.head(limit).replace({np.nan: None})
    return preview.to_dict(orient="records")


def profile_dataframe(dataframe: pd.DataFrame, source_name: str) -> DatasetProfile:
    numeric_columns = [column for column in dataframe.columns if pd.api.types.is_numeric_dtype(dataframe[column])]
    categorical_columns = [column for column in dataframe.columns if column not in numeric_columns]
    missingness = {
        column: round(float(dataframe[column].isna().mean()) * 100, 2)
        for column in dataframe.columns
    }
    sensitive_columns = [
        column
        for column in dataframe.columns
        if any(keyword in column.lower() for keyword in SENSITIVE_KEYWORDS)
    ]
    fit_summary = (
        "Good candidate for single-table synthetic generation."
        if len(dataframe) >= 100 and len(dataframe.columns) >= 5
        else "Usable, but small sample size may limit fidelity."
    )
    return DatasetProfile(
        source_name=source_name,
        row_count=int(len(dataframe)),
        column_count=int(len(dataframe.columns)),
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        missingness=missingness,
        sensitive_columns=sensitive_columns,
        preview=_safe_preview(dataframe),
        fit_summary=fit_summary,
    )


def build_plan(profile: DatasetProfile, scenario: ScenarioPreset, goal: str, stakeholder: str) -> SynthesisPlan:
    model_name = "GaussianCopulaSynthesizer" if SDV_AVAILABLE else "HeuristicSampler"
    target_rows = max(int(profile.row_count * scenario.row_multiplier), 250)
    constraints = [
        "Preserve operational column semantics and null patterns where practical.",
        "Avoid exact raw-row memorization in the synthetic output.",
        "Apply scenario-specific volume and disposition shifts after synthesis.",
        "Keep the output explainable for planning, innovation, and workshop use.",
    ]
    evaluation_focus = [
        "Schema validity",
        "Distribution fidelity",
        "Exact-match leakage risk",
        "Scenario plausibility",
    ]
    return SynthesisPlan(
        model_name=model_name,
        target_rows=target_rows,
        scenario_id=scenario.id,
        stakeholder=stakeholder,
        goal=goal,
        constraints=constraints,
        evaluation_focus=evaluation_focus,
    )


def _fit_sdv(dataframe: pd.DataFrame, target_rows: int) -> pd.DataFrame:
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="The 'SingleTableMetadata' is deprecated.*",
            category=FutureWarning,
        )
        warnings.filterwarnings(
            "ignore",
            message="We strongly recommend saving the metadata.*",
            category=UserWarning,
        )
        metadata = SingleTableMetadata()
        metadata.detect_from_dataframe(dataframe)
        synthesizer = GaussianCopulaSynthesizer(metadata)
        synthesizer.fit(dataframe)
        return synthesizer.sample(num_rows=target_rows)


def _heuristic_sample(dataframe: pd.DataFrame, target_rows: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    sampled = dataframe.sample(
        n=target_rows,
        replace=True,
        random_state=seed % (2**31 - 1),
    ).reset_index(drop=True)
    generated = pd.DataFrame()

    for column in dataframe.columns:
        series = dataframe[column]
        if pd.api.types.is_numeric_dtype(series):
            sample = sampled[column].astype(float)
            std = float(series.dropna().std()) if not series.dropna().empty else 0.0
            noise_scale = std * 0.08 if std and not math.isnan(std) else 0.0
            noise = rng.normal(0, noise_scale, size=len(sample))
            values = sample + noise
            min_value = float(series.min()) if not series.dropna().empty else None
            max_value = float(series.max()) if not series.dropna().empty else None
            if min_value is not None and max_value is not None:
                values = np.clip(values, min_value, max_value)
            if pd.api.types.is_integer_dtype(series.dropna()):
                values = np.rint(values)
            generated[column] = values
        else:
            probabilities = series.value_counts(normalize=True, dropna=False)
            choices = probabilities.index.to_list()
            weights = probabilities.to_numpy()
            generated[column] = rng.choice(choices, size=target_rows, p=weights)

    return generated


def _stable_seed(*parts: str) -> int:
    joined = "||".join(parts)
    digest = hashlib.sha256(joined.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def synthesize_dataframe(dataframe: pd.DataFrame, plan: SynthesisPlan) -> pd.DataFrame:
    seed = _stable_seed(plan.scenario_id, plan.goal, plan.stakeholder, str(plan.target_rows))
    np.random.seed(seed)
    random.seed(seed)

    if SDV_AVAILABLE:
        try:
            return _fit_sdv(dataframe, plan.target_rows)
        except Exception:
            pass
    return _heuristic_sample(dataframe, plan.target_rows, seed)


def _weighted_choice(probabilities: dict[str, float], size: int, seed: int) -> list[str]:
    rng = random.Random(seed)
    population = list(probabilities.keys())
    weights = list(probabilities.values())
    total = sum(weights)
    normalized = [weight / total for weight in weights]
    return rng.choices(population, weights=normalized, k=size)


def apply_scenario_transformations(dataframe: pd.DataFrame, scenario: ScenarioPreset) -> pd.DataFrame:
    transformed = dataframe.copy()

    if "wait_time_minutes" in transformed.columns:
        if scenario.id == "ed_surge":
            transformed["wait_time_minutes"] = (transformed["wait_time_minutes"] * 1.35).round(0)
        elif scenario.id == "community_diversion":
            transformed["wait_time_minutes"] = (transformed["wait_time_minutes"] * 0.72).round(0)
        elif scenario.id == "regional_growth":
            transformed["wait_time_minutes"] = (transformed["wait_time_minutes"] * 1.12).round(0)
        elif scenario.id == "distributed_campus_routing":
            transformed["wait_time_minutes"] = (transformed["wait_time_minutes"] * 0.95).round(0)

    if "length_of_visit_minutes" in transformed.columns:
        if scenario.id == "ed_surge":
            transformed["length_of_visit_minutes"] = (transformed["length_of_visit_minutes"] * 1.22).round(0)
        elif scenario.id == "community_diversion":
            transformed["length_of_visit_minutes"] = (transformed["length_of_visit_minutes"] * 0.84).round(0)
        elif scenario.id == "regional_growth":
            transformed["length_of_visit_minutes"] = (transformed["length_of_visit_minutes"] * 1.08).round(0)

    if "triage_level" in transformed.columns:
        if scenario.id == "ed_surge":
            replacements = {
                "Nonurgent": "Urgent",
                "Semi-urgent": "Urgent",
                "Urgent": "Emergent",
            }
            transformed["triage_level"] = transformed["triage_level"].replace(replacements)
        elif scenario.id == "community_diversion":
            replacements = {
                "Emergent": "Urgent",
                "Urgent": "Semi-urgent",
            }
            transformed["triage_level"] = transformed["triage_level"].replace(replacements)

    if "arrived_by_ambulance" in transformed.columns:
        if scenario.id == "ed_surge":
            transformed["arrived_by_ambulance"] = _weighted_choice(
                {"Yes": 0.32, "No": 0.63, "Unknown": 0.05},
                len(transformed),
                7,
            )
        elif scenario.id == "community_diversion":
            transformed["arrived_by_ambulance"] = _weighted_choice(
                {"Yes": 0.12, "No": 0.83, "Unknown": 0.05},
                len(transformed),
                8,
            )

    if "visit_outcome" in transformed.columns:
        if scenario.id == "distributed_campus_routing":
            transformed["visit_outcome"] = _weighted_choice(
                {
                    "Home or community resolution": 0.58,
                    "Observation pathway": 0.2,
                    "Inpatient admission": 0.14,
                    "Transfer / facility handoff": 0.06,
                    "Left before completion": 0.02,
                },
                len(transformed),
                11,
            )
        elif scenario.id == "community_diversion":
            transformed["visit_outcome"] = _weighted_choice(
                {
                    "Home or community resolution": 0.72,
                    "Observation pathway": 0.11,
                    "Inpatient admission": 0.1,
                    "Transfer / facility handoff": 0.04,
                    "Left before completion": 0.03,
                },
                len(transformed),
                12,
            )

    for column in NUMERIC_HELPERS.intersection(set(transformed.columns)):
        transformed[column] = pd.to_numeric(transformed[column], errors="coerce")
        if "hour" in column:
            transformed[column] = transformed[column].clip(lower=0, upper=23).round(0)
        else:
            transformed[column] = transformed[column].clip(lower=0).round(0)

    return transformed


def evaluate_synthetic(source_df: pd.DataFrame, synthetic_df: pd.DataFrame, scenario: ScenarioPreset) -> EvalReport:
    numeric_scores = []
    categorical_scores = []

    source = source_df.reset_index(drop=True)
    synthetic = synthetic_df.reset_index(drop=True)

    for column in source.columns:
        if column not in synthetic.columns:
            continue
        source_series = source[column].dropna()
        synthetic_series = synthetic[column].dropna()
        if source_series.empty or synthetic_series.empty:
            continue

        if pd.api.types.is_numeric_dtype(source[column]):
            src_mean = float(source_series.mean())
            syn_mean = float(synthetic_series.mean())
            src_std = float(source_series.std()) or 1.0
            delta = min(abs(src_mean - syn_mean) / src_std, 1.5)
            numeric_scores.append(max(0.0, 1.0 - delta))
        else:
            src_freq = source_series.astype(str).value_counts(normalize=True)
            syn_freq = synthetic_series.astype(str).value_counts(normalize=True)
            categories = set(src_freq.index).union(set(syn_freq.index))
            tvd = sum(abs(src_freq.get(cat, 0.0) - syn_freq.get(cat, 0.0)) for cat in categories) / 2
            categorical_scores.append(max(0.0, 1.0 - min(tvd, 1.0)))

    source_rows = set(map(tuple, source.fillna("__NA__").astype(str).to_numpy()))
    synthetic_rows = list(map(tuple, synthetic.fillna("__NA__").astype(str).to_numpy()))
    exact_matches = sum(1 for row in synthetic_rows if row in source_rows)
    exact_match_rate = exact_matches / max(len(synthetic_rows), 1)

    numeric_similarity = float(np.mean(numeric_scores) * 100) if numeric_scores else 0.0
    categorical_similarity = float(np.mean(categorical_scores) * 100) if categorical_scores else 0.0
    fidelity_score = round((numeric_similarity * 0.55) + (categorical_similarity * 0.45), 2)
    privacy_score = round(max(0.0, 100.0 - (exact_match_rate * 250.0)), 2)
    utility_score = round((fidelity_score * 0.6) + (privacy_score * 0.4), 2)

    highlights = [
        f"{scenario.name} scenario generated {len(synthetic_df)} synthetic rows from {len(source_df)} source rows.",
        f"Numeric similarity averaged {numeric_similarity:.1f} and categorical similarity averaged {categorical_similarity:.1f}.",
        "Output preserves a readable planning-and-innovation schema for workshop, demo, and slide use.",
    ]
    warnings = []
    if exact_match_rate > 0.01:
        warnings.append("Exact row overlap exceeded the preferred demo threshold; review before presenting.")
    if fidelity_score < 70:
        warnings.append("Fidelity is directional rather than analytical; position the demo as exploratory.")
    if scenario.id == "distributed_campus_routing":
        warnings.append("Routing shifts are distributed-network planning assumptions, not validated Southlake referral behavior.")
    if not warnings:
        warnings.append("No immediate leakage warning triggered, but synthetic output still requires governance review.")

    return EvalReport(
        fidelity_score=round(fidelity_score, 2),
        privacy_score=round(privacy_score, 2),
        utility_score=round(utility_score, 2),
        exact_match_rate=round(exact_match_rate * 100, 2),
        numeric_similarity=round(numeric_similarity, 2),
        categorical_similarity=round(categorical_similarity, 2),
        highlights=highlights,
        warnings=warnings,
    )


def build_caution_report(
    scenario: ScenarioPreset,
    evaluation: EvalReport,
    source: PresetInfo,
) -> CautionReport:
    bullets = [
        "Use synthetic outputs for planning workshops, innovation sprints, workflow prototyping, and scenario discussion only.",
        "Do not treat this dataset as a substitute for governed Southlake patient data or operational truth.",
        "Rare cohorts and local Ontario care patterns are not faithfully represented in a U.S. national public-use source.",
        "Scenario transformations are directional distributed-network assumptions layered on top of the source distribution.",
        "If this output informs a real project, re-run validation with governed local data, privacy review, and operational owners.",
    ]
    if evaluation.exact_match_rate > 1:
        bullets.insert(1, "Review exact-match leakage before external sharing; the current run preserved too many raw patterns.")

    return CautionReport(
        headline=f"{source.name} is safe for planning demonstrations, not for operational truth claims.",
        bullets=bullets[:5],
        disclaimer="Not for clinical care, staffing commitments, reimbursement, or patient-level action.",
    )


def build_pitch_summary(
    reasoning_client: ReasoningClient,
    scenario: ScenarioPreset,
    plan: SynthesisPlan,
    evaluation: EvalReport,
    cautions: CautionReport,
) -> PitchSummary:
    methodology_fallback = [
        f"Loaded a curated NHAMCS emergency dataset and profiled its operational schema for {scenario.stakeholder.lower()} planning work.",
        f"Used {plan.model_name} to synthesize {plan.target_rows} rows, then applied a {scenario.name.lower()} layer tied to Southlake's distributed-network future state.",
        "Evaluated the result on fidelity, leakage risk, and scenario plausibility before generating pitch-ready planning artifacts.",
    ]
    features_fallback = [
        "Single-click preset loading, upload support, and agent-style planning runs for Southlake-style service design questions.",
        "Synthetic output preview with fidelity, privacy, and utility metrics in one dashboard for innovation teams.",
        "Auto-generated methodology, feature, and caution copy for the 3-slide presentation and backup materials.",
    ]
    caution_fallback = cautions.bullets[:3]

    methodology = reasoning_client.polish_bullets(
        "Methodology",
        [
            f"Scenario: {scenario.name}",
            f"Goal: {plan.goal}",
            f"Model: {plan.model_name}",
            f"Evaluation: fidelity={evaluation.fidelity_score}, privacy={evaluation.privacy_score}",
        ],
        methodology_fallback,
    )
    features = reasoning_client.polish_bullets(
        "Important Features",
        scenario.pressure_notes,
        features_fallback,
    )
    cautions = reasoning_client.polish_bullets(
        "Cautions",
        cautions.bullets,
        caution_fallback,
    )
    return PitchSummary(methodology=methodology, features=features, cautions=cautions)


def build_timeline(
    profile: DatasetProfile,
    plan: SynthesisPlan,
    evaluation: EvalReport,
    reasoning_traces: dict[str, str],
    retry_count: int = 0,
) -> list[AgentStep]:
    steps = [
        AgentStep(
            id="intent",
            name="Intent Agent",
            summary=f"Framed the run for {plan.stakeholder.lower()} with goal: {plan.goal}",
            reasoning=reasoning_traces.get("intent", ""),
        ),
        AgentStep(
            id="profile",
            name="Profile Agent",
            summary=f"Profiled {profile.row_count} rows across {profile.column_count} columns and flagged {len(profile.sensitive_columns)} sensitive columns.",
            reasoning=reasoning_traces.get("profile", ""),
        ),
        AgentStep(
            id="strategy",
            name="Strategy Agent",
            summary=f"Selected {plan.model_name} with a target of {plan.target_rows} synthetic rows.",
            reasoning=reasoning_traces.get("strategy", ""),
        ),
        AgentStep(
            id="evaluate",
            name="Evaluate Agent",
            summary=f"Scored fidelity {evaluation.fidelity_score}, privacy {evaluation.privacy_score}, and utility {evaluation.utility_score}.",
            reasoning=reasoning_traces.get("evaluate", ""),
            status="completed" if retry_count == 0 else f"completed after {retry_count} retry",
        ),
        AgentStep(
            id="narrative",
            name="Narrative Agent",
            summary="Generated planning, feature, and governance copy for the presentation deck.",
            reasoning=reasoning_traces.get("narrative", ""),
        ),
    ]
    return steps


def _json_default(value: Any) -> Any:
    if isinstance(value, (np.integer, np.floating)):
        return value.item()
    if isinstance(value, (datetime, Path)):
        return str(value)
    if pd.isna(value):
        return None
    raise TypeError(f"Object of type {type(value)!r} is not JSON serializable")


def write_artifacts(
    run_id: str,
    source_df: pd.DataFrame,
    synthetic_df: pd.DataFrame,
    payload: dict[str, Any],
) -> dict[str, str]:
    artifact_dir = RUNS_DIR / run_id
    artifact_dir.mkdir(parents=True, exist_ok=True)

    source_path = artifact_dir / "source_preview.csv"
    synthetic_path = artifact_dir / "synthetic_dataset.csv"
    report_path = artifact_dir / "report.json"
    pitch_path = artifact_dir / f"run-{run_id}.md"
    zip_path = artifact_dir / f"{run_id}.zip"

    source_df.head(200).to_csv(source_path, index=False)
    synthetic_df.to_csv(synthetic_path, index=False)
    report_path.write_text(json.dumps(payload, indent=2, default=_json_default))

    pitch_summary = payload["pitch_summary"]
    pitch_markdown = "\n".join(
        [
            f"# Southlake Pitch Draft {run_id}",
            "",
            "## Methodology",
            *[f"- {line}" for line in pitch_summary["methodology"]],
            "",
            "## Features",
            *[f"- {line}" for line in pitch_summary["features"]],
            "",
            "## Cautions",
            *[f"- {line}" for line in pitch_summary["cautions"]],
            "",
        ]
    )
    pitch_path.write_text(pitch_markdown)
    (PITCH_DIR / "latest_summary.md").write_text(pitch_markdown)

    with ZipFile(zip_path, "w", compression=ZIP_DEFLATED) as archive:
        archive.write(source_path, arcname=source_path.name)
        archive.write(synthetic_path, arcname=synthetic_path.name)
        archive.write(report_path, arcname=report_path.name)
        archive.write(pitch_path, arcname=pitch_path.name)

    return {
        "artifact_dir": str(artifact_dir),
        "source_preview_csv": str(source_path),
        "synthetic_csv": str(synthetic_path),
        "report_json": str(report_path),
        "pitch_markdown": str(pitch_path),
        "download_zip": str(zip_path),
    }


MAX_RETRIES = 1


def run_pipeline(
    source_df: pd.DataFrame,
    source_info: PresetInfo,
    scenario: ScenarioPreset,
    goal: str,
    stakeholder: str,
) -> RunResponse:
    reasoning_client = ReasoningClient()
    reasoning_traces: dict[str, str] = {}

    # Step 1: Intent Agent — frame the planning question
    source_df = sanitize_dataframe(source_df)
    reasoning_traces["intent"] = reasoning_client.reason_intent(
        goal=goal,
        stakeholder=stakeholder,
        scenario_name=scenario.name,
        scenario_description=scenario.description,
    )

    # Step 2: Profile Agent — analyze the dataset
    profile = profile_dataframe(source_df, source_info.name)
    reasoning_traces["profile"] = reasoning_client.reason_profile(
        row_count=profile.row_count,
        column_count=profile.column_count,
        numeric_columns=profile.numeric_columns,
        categorical_columns=profile.categorical_columns,
        sensitive_columns=profile.sensitive_columns,
        missingness=profile.missingness,
        scenario_name=scenario.name,
        stakeholder=stakeholder,
    )

    # Step 3: Strategy Agent — decide synthesis approach
    plan = build_plan(profile, scenario, goal, stakeholder)
    reasoning_traces["strategy"] = reasoning_client.reason_strategy(
        row_count=profile.row_count,
        column_count=profile.column_count,
        target_rows=plan.target_rows,
        model_name=plan.model_name,
        scenario_name=scenario.name,
        scenario_id=scenario.id,
        goal=goal,
        stakeholder=stakeholder,
        missingness=profile.missingness,
        sensitive_columns=profile.sensitive_columns,
    )

    # Step 4: Synthesize + Evaluate with retry loop
    retry_count = 0
    for attempt in range(MAX_RETRIES + 1):
        synthetic_df = synthesize_dataframe(source_df, plan)
        synthetic_df = sanitize_dataframe(synthetic_df)
        synthetic_df = apply_scenario_transformations(synthetic_df, scenario)
        evaluation = evaluate_synthetic(source_df, synthetic_df, scenario)

        eval_reasoning, should_retry = reasoning_client.reason_evaluation(
            fidelity_score=evaluation.fidelity_score,
            privacy_score=evaluation.privacy_score,
            utility_score=evaluation.utility_score,
            exact_match_rate=evaluation.exact_match_rate,
            numeric_similarity=evaluation.numeric_similarity,
            categorical_similarity=evaluation.categorical_similarity,
            scenario_name=scenario.name,
            source_rows=profile.row_count,
            synthetic_rows=int(len(synthetic_df)),
            stakeholder=stakeholder,
        )
        reasoning_traces["evaluate"] = eval_reasoning

        if not should_retry or attempt == MAX_RETRIES:
            retry_count = attempt
            break
        retry_count = attempt + 1

    # Step 5: Narrative Agent — generate pitch content
    cautions = build_caution_report(scenario, evaluation, source_info)
    pitch_summary = build_pitch_summary(reasoning_client, scenario, plan, evaluation, cautions)
    reasoning_traces["narrative"] = reasoning_client.reason_narrative(
        scenario_name=scenario.name,
        scenario_description=scenario.description,
        model_name=plan.model_name,
        target_rows=plan.target_rows,
        stakeholder=stakeholder,
        goal=goal,
        fidelity_score=evaluation.fidelity_score,
        privacy_score=evaluation.privacy_score,
        caution_bullets=cautions.bullets,
    )

    # Build timeline with reasoning traces
    timeline = build_timeline(profile, plan, evaluation, reasoning_traces, retry_count)

    run_id = uuid4().hex[:10]
    payload = RunResponse(
        run_id=run_id,
        status="completed",
        source=source_info,
        scenario=scenario,
        profile=profile,
        plan=plan,
        timeline=timeline,
        evaluation=evaluation,
        cautions=cautions,
        pitch_summary=pitch_summary,
        source_preview=_safe_preview(source_df),
        synthetic_preview=_safe_preview(synthetic_df),
        synthetic_row_count=int(len(synthetic_df)),
        artifacts={},
    ).model_dump()

    artifacts = write_artifacts(run_id, source_df, synthetic_df, payload)
    payload["artifacts"] = artifacts
    return RunResponse(**payload)


@dataclass
class UploadContext:
    dataframe: pd.DataFrame
    source_info: PresetInfo
    preset_id: Optional[str]


def build_upload_source_info(filename: str, dataframe: pd.DataFrame) -> PresetInfo:
    return PresetInfo(
        id="uploaded_csv",
        name=f"Uploaded CSV: {filename}",
        source_name=filename,
        source_url="local-upload",
        documentation_url="local-upload",
        notes="User-provided file loaded locally for planning and innovation synthesis.",
        columns=list(dataframe.columns),
    )


def iso_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()
