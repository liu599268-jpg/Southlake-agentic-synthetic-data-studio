from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class ScenarioPreset(BaseModel):
    id: str
    name: str
    description: str
    stakeholder: str
    planning_goal: str
    row_multiplier: float
    pressure_notes: list[str]


class DatasetProfile(BaseModel):
    source_name: str
    row_count: int
    column_count: int
    numeric_columns: list[str]
    categorical_columns: list[str]
    missingness: dict[str, float]
    sensitive_columns: list[str]
    preview: list[dict[str, Any]]
    fit_summary: str


class AgentStep(BaseModel):
    id: str
    name: str
    summary: str
    reasoning: str = ""
    status: str = "completed"


class SynthesisPlan(BaseModel):
    model_name: str
    target_rows: int
    scenario_id: str
    stakeholder: str
    goal: str
    constraints: list[str]
    evaluation_focus: list[str]


class ColumnFidelity(BaseModel):
    column: str
    column_type: str  # "numeric" or "categorical"
    score: float
    source_summary: Any = None  # mean for numeric, top-3 frequencies for categorical
    synthetic_summary: Any = None


class DistributionComparison(BaseModel):
    column: str
    categories: list[str]
    source_pct: list[float]
    synthetic_pct: list[float]


class EvalReport(BaseModel):
    fidelity_score: float
    privacy_score: float
    utility_score: float
    exact_match_rate: float
    numeric_similarity: float
    categorical_similarity: float
    highlights: list[str]
    warnings: list[str]
    column_fidelity: list[ColumnFidelity] = []
    distribution_comparisons: list[DistributionComparison] = []


class CautionReport(BaseModel):
    headline: str
    bullets: list[str]
    disclaimer: str


class PitchSummary(BaseModel):
    methodology: list[str]
    features: list[str]
    cautions: list[str]


class PresetInfo(BaseModel):
    id: str
    name: str
    source_name: str
    source_url: str
    documentation_url: str
    notes: str
    columns: list[str]


class RunResponse(BaseModel):
    run_id: str
    status: str
    source: PresetInfo
    scenario: ScenarioPreset
    profile: DatasetProfile
    plan: SynthesisPlan
    timeline: list[AgentStep]
    evaluation: EvalReport
    cautions: CautionReport
    pitch_summary: PitchSummary
    source_preview: list[dict[str, Any]]
    synthetic_preview: list[dict[str, Any]]
    synthetic_row_count: int
    artifacts: dict[str, str]


class DemoRunSummary(BaseModel):
    run_id: str
    label: str
    story_angle: str
    summary: str
    scenario_name: str
    stakeholder: str
    fidelity_score: float
    privacy_score: float
    utility_score: float
    screenshot_path: Optional[str] = None


class PresetLoadRequest(BaseModel):
    preset_id: str = Field(default="nhamcs_ed_2022_curated")


class PresetLoadResponse(BaseModel):
    preset: PresetInfo
    profile: DatasetProfile
    scenarios: list[ScenarioPreset]
    demo_runs: list[DemoRunSummary] = Field(default_factory=list)
