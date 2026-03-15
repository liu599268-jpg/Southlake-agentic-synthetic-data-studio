export type ScenarioPreset = {
  id: string;
  name: string;
  description: string;
  stakeholder: string;
  planning_goal: string;
  row_multiplier: number;
  pressure_notes: string[];
};

export type DatasetProfile = {
  source_name: string;
  row_count: number;
  column_count: number;
  numeric_columns: string[];
  categorical_columns: string[];
  missingness: Record<string, number>;
  sensitive_columns: string[];
  preview: Array<Record<string, string | number | null>>;
  fit_summary: string;
};

export type PresetInfo = {
  id: string;
  name: string;
  source_name: string;
  source_url: string;
  documentation_url: string;
  notes: string;
  columns: string[];
};

export type AgentStep = {
  id: string;
  name: string;
  summary: string;
  reasoning: string;
  status: string;
};

export type SynthesisPlan = {
  model_name: string;
  target_rows: number;
  scenario_id: string;
  stakeholder: string;
  goal: string;
  constraints: string[];
  evaluation_focus: string[];
};

export type EvalReport = {
  fidelity_score: number;
  privacy_score: number;
  utility_score: number;
  exact_match_rate: number;
  numeric_similarity: number;
  categorical_similarity: number;
  highlights: string[];
  warnings: string[];
};

export type CautionReport = {
  headline: string;
  bullets: string[];
  disclaimer: string;
};

export type PitchSummary = {
  methodology: string[];
  features: string[];
  cautions: string[];
};

export type RunResponse = {
  run_id: string;
  status: string;
  source: PresetInfo;
  scenario: ScenarioPreset;
  profile: DatasetProfile;
  plan: SynthesisPlan;
  timeline: AgentStep[];
  evaluation: EvalReport;
  cautions: CautionReport;
  pitch_summary: PitchSummary;
  source_preview: Array<Record<string, string | number | null>>;
  synthetic_preview: Array<Record<string, string | number | null>>;
  synthetic_row_count: number;
  artifacts: Record<string, string>;
};

export type DemoRunSummary = {
  run_id: string;
  label: string;
  story_angle: string;
  summary: string;
  scenario_name: string;
  stakeholder: string;
  fidelity_score: number;
  privacy_score: number;
  utility_score: number;
  screenshot_path?: string | null;
};

export type PresetLoadResponse = {
  preset: PresetInfo;
  profile: DatasetProfile;
  scenarios: ScenarioPreset[];
  demo_runs: DemoRunSummary[];
};
