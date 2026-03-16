"use client";

import { startTransition, useEffect, useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend, Cell,
} from "recharts";

import type {
  ColumnFidelity,
  DatasetProfile,
  DemoRunSummary,
  DistributionComparison,
  PresetLoadResponse,
  RunResponse,
} from "@/lib/types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";
const DEFAULT_PRESET_ID = "nhamcs_ed_2022_curated";
const DEFAULT_SCENARIO_ID = "distributed_campus_routing";
const DEFAULT_STAKEHOLDER = "Network operations team";
const DEFAULT_GOAL =
  "Create a planning-grade synthetic dataset that helps Southlake innovation teams test distributed-campus routing, observation demand, and community handoff assumptions without using real patient records.";

const SOUTHLAKE_FIT_AREAS = [
  {
    title: "Distributed network routing",
    body:
      "Frame where care should stay on campus, move into observation, transfer onward, or resolve through community-connected pathways.",
  },
  {
    title: "Advanced-care-campus thinking",
    body:
      "Test how future-state Southlake capacity could shift once care is delivered through more than one physical setting.",
  },
  {
    title: "Learning-health-system workflow",
    body:
      "Turn one planning question into synthetic data, evaluation metrics, cautions, and exportable artifacts in a single run.",
  },
];

function numberFormat(value: number) {
  return new Intl.NumberFormat("en-CA", {
    maximumFractionDigits: value % 1 === 0 ? 0 : 1,
  }).format(value);
}

function TablePreview({
  title,
  rows,
}: {
  title: string;
  rows: Array<Record<string, string | number | null>>;
}) {
  if (!rows.length) {
    return null;
  }

  const columns = Object.keys(rows[0]);

  return (
    <div className="overflow-hidden rounded-[2rem] border border-slate-900/8 bg-white/90">
      <div className="flex items-center justify-between border-b border-slate-900/8 px-5 py-4">
        <h3 className="section-title text-xl font-semibold text-slate-900">
          {title}
        </h3>
        <span className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
          {rows.length} rows shown
        </span>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-950 text-slate-50">
            <tr>
              {columns.map((column) => (
                <th key={column} className="px-4 py-3 font-medium">
                  {column.replaceAll("_", " ")}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, index) => (
              <tr
                key={`${title}-${index}`}
                className="border-b border-slate-900/6 odd:bg-white even:bg-emerald-50/45"
              >
                {columns.map((column) => (
                  <td
                    key={column}
                    className="max-w-[15rem] px-4 py-3 text-slate-700"
                  >
                    {row[column] === null || row[column] === ""
                      ? "—"
                      : String(row[column])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ProfileCard({ profile }: { profile: DatasetProfile }) {
  return (
    <div className="panel rounded-[2rem] p-6">
      <div className="mb-5 flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.16em] text-slate-500">
            Dataset Profile
          </p>
          <h3 className="section-title mt-2 text-2xl font-semibold text-slate-950">
            {profile.source_name}
          </h3>
        </div>
        <div className="rounded-full bg-emerald-100 px-4 py-2 text-sm font-semibold text-emerald-800">
          {profile.fit_summary}
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        <div className="metric-card rounded-[1.4rem] p-4">
          <div className="text-sm text-slate-500">Rows</div>
          <div className="mt-2 text-3xl font-semibold text-slate-950">
            {numberFormat(profile.row_count)}
          </div>
        </div>
        <div className="metric-card rounded-[1.4rem] p-4">
          <div className="text-sm text-slate-500">Columns</div>
          <div className="mt-2 text-3xl font-semibold text-slate-950">
            {numberFormat(profile.column_count)}
          </div>
        </div>
        <div className="metric-card rounded-[1.4rem] p-4">
          <div className="text-sm text-slate-500">Sensitive fields</div>
          <div className="mt-2 text-3xl font-semibold text-slate-950">
            {numberFormat(profile.sensitive_columns.length)}
          </div>
        </div>
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-2">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
            Numeric columns
          </p>
          <p className="mt-2 text-sm leading-7 text-slate-700">
            {profile.numeric_columns.join(", ")}
          </p>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
            Categorical columns
          </p>
          <p className="mt-2 text-sm leading-7 text-slate-700">
            {profile.categorical_columns.join(", ")}
          </p>
        </div>
      </div>
    </div>
  );
}

function DemoRunCard({
  demoRun,
  onLoad,
  loading,
}: {
  demoRun: DemoRunSummary;
  onLoad: (runId: string) => void;
  loading: boolean;
}) {
  return (
    <div className="rounded-[1.8rem] border border-slate-900/8 bg-white/80 p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-emerald-700">
            {demoRun.label}
          </p>
          <h3 className="section-title mt-2 text-2xl font-semibold text-slate-950">
            {demoRun.scenario_name}
          </h3>
        </div>
        <div className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] text-emerald-900">
          {demoRun.story_angle}
        </div>
      </div>
      <p className="mt-3 text-sm leading-6 text-slate-700">{demoRun.summary}</p>
      <div className="mt-4 rounded-[1.4rem] bg-slate-950 px-4 py-3 text-sm text-slate-100">
        Stakeholder: {demoRun.stakeholder}
      </div>
      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <div className="metric-card rounded-[1.3rem] p-3">
          <div className="text-xs uppercase tracking-[0.14em] text-slate-500">
            Fidelity
          </div>
          <div className="mt-1 text-2xl font-semibold text-slate-950">
            {demoRun.fidelity_score}
          </div>
        </div>
        <div className="metric-card rounded-[1.3rem] p-3">
          <div className="text-xs uppercase tracking-[0.14em] text-slate-500">
            Privacy
          </div>
          <div className="mt-1 text-2xl font-semibold text-slate-950">
            {demoRun.privacy_score}
          </div>
        </div>
        <div className="metric-card rounded-[1.3rem] p-3">
          <div className="text-xs uppercase tracking-[0.14em] text-slate-500">
            Utility
          </div>
          <div className="mt-1 text-2xl font-semibold text-slate-950">
            {demoRun.utility_score}
          </div>
        </div>
      </div>
      <div className="mt-4 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() => onLoad(demoRun.run_id)}
          disabled={loading}
          data-testid={`load-demo-${demoRun.run_id}`}
          className="rounded-full bg-slate-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-slate-400"
        >
          {loading ? "Loading saved run..." : "Load saved run"}
        </button>
        {demoRun.screenshot_path && (
          <span className="rounded-full border border-slate-900/10 bg-white px-4 py-3 text-xs font-semibold uppercase tracking-[0.14em] text-slate-500">
            Screenshot ready
          </span>
        )}
      </div>
    </div>
  );
}

function FidelityChart({ data }: { data: ColumnFidelity[] }) {
  if (!data.length) return null;

  const chartData = data.map((item) => ({
    name: item.column.replaceAll("_", " "),
    score: item.score,
    type: item.column_type,
  }));

  return (
    <div className="rounded-[2rem] border border-slate-900/8 bg-white/90 p-6">
      <div className="mb-1 flex items-center justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
            Per-Column Fidelity Breakdown
          </p>
          <h3 className="section-title mt-1 text-xl font-semibold text-slate-950">
            How well each column was preserved
          </h3>
        </div>
        <div className="flex gap-3">
          <div className="flex items-center gap-1.5">
            <div className="h-3 w-3 rounded-sm" style={{ background: "#6366f1" }} />
            <span className="text-xs text-slate-500">Numeric</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="h-3 w-3 rounded-sm" style={{ background: "#f59e0b" }} />
            <span className="text-xs text-slate-500">Categorical</span>
          </div>
        </div>
      </div>
      <p className="mt-2 text-xs leading-5 text-slate-500">
        Numeric scores compare statistical means (normalized by standard deviation). Categorical scores measure distribution overlap (Total Variation Distance). Higher = more faithful to source patterns.
      </p>
      <div className="mt-3" style={{ height: 320 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} layout="vertical" margin={{ left: 120, right: 20, top: 5, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(16,42,67,0.06)" horizontal={false} />
            <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11, fill: "#5a7184" }} />
            <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: "#5a7184" }} width={115} />
            <Tooltip
              contentStyle={{
                background: "#0f2b3c",
                border: "none",
                borderRadius: 12,
                color: "white",
                fontSize: 13,
              }}
              formatter={(value) => [`${Number(value).toFixed(1)}%`, "Fidelity"]}
            />
            <Bar dataKey="score" radius={[0, 6, 6, 0]} maxBarSize={22}>
              {chartData.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={entry.type === "numeric" ? "#6366f1" : "#f59e0b"}
                  fillOpacity={entry.score > 80 ? 1 : entry.score > 60 ? 0.8 : 0.55}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

function DistributionChart({ comparison }: { comparison: DistributionComparison }) {
  const chartData = comparison.categories.map((cat, i) => ({
    name: cat,
    Source: comparison.source_pct[i],
    Synthetic: comparison.synthetic_pct[i],
  }));

  return (
    <div className="rounded-[1.8rem] border border-slate-900/8 bg-white/90 p-5">
      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
        Distribution Comparison
      </p>
      <h3 className="section-title mt-1 text-lg font-semibold text-slate-950">
        {comparison.column.replaceAll("_", " ")}
      </h3>
      <div className="mt-3" style={{ height: 220 }}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ left: 0, right: 0, top: 5, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(16,42,67,0.06)" />
            <XAxis
              dataKey="name"
              tick={{ fontSize: 10, fill: "#5a7184" }}
              angle={-25}
              textAnchor="end"
              height={60}
            />
            <YAxis tick={{ fontSize: 10, fill: "#5a7184" }} unit="%" />
            <Tooltip
              contentStyle={{
                background: "#0f2b3c",
                border: "none",
                borderRadius: 12,
                color: "white",
                fontSize: 12,
              }}
              formatter={(value) => [`${Number(value).toFixed(1)}%`]}
            />
            <Legend wrapperStyle={{ fontSize: 11 }} />
            <Bar dataKey="Source" fill="#334155" radius={[4, 4, 0, 0]} maxBarSize={32} />
            <Bar dataKey="Synthetic" fill="#1bbab1" radius={[4, 4, 0, 0]} maxBarSize={32} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export function Studio() {
  const [presetData, setPresetData] = useState<PresetLoadResponse | null>(null);
  const [selectedScenario, setSelectedScenario] = useState(DEFAULT_SCENARIO_ID);
  const [stakeholder, setStakeholder] = useState(DEFAULT_STAKEHOLDER);
  const [goal, setGoal] = useState(DEFAULT_GOAL);
  const [file, setFile] = useState<File | null>(null);
  const [loadingPreset, setLoadingPreset] = useState(true);
  const [running, setRunning] = useState(false);
  const [loadingRunId, setLoadingRunId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [run, setRun] = useState<RunResponse | null>(null);
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);

  useEffect(() => {
    const loadPreset = async () => {
      setLoadingPreset(true);
      setError(null);

      try {
        const response = await fetch(`${API_BASE}/api/presets/load`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ preset_id: DEFAULT_PRESET_ID }),
        });

        if (!response.ok) {
          throw new Error("Preset load failed");
        }

        const payload = (await response.json()) as PresetLoadResponse;
        const preferredScenario =
          payload.scenarios.find((item) => item.id === DEFAULT_SCENARIO_ID) ??
          payload.scenarios[0];

        setPresetData(payload);
        setSelectedScenario(preferredScenario?.id ?? DEFAULT_SCENARIO_ID);
        setStakeholder(preferredScenario?.stakeholder ?? DEFAULT_STAKEHOLDER);
        setGoal(preferredScenario?.planning_goal ?? DEFAULT_GOAL);
      } catch (loadError) {
        setError(
          `Unable to reach the API at ${API_BASE}. Start the FastAPI service or upload a CSV once the API is running.`,
        );
        console.error(loadError);
      } finally {
        setLoadingPreset(false);
      }
    };

    loadPreset();
  }, []);

  const scenario =
    presetData?.scenarios.find((item) => item.id === selectedScenario) ?? null;
  const recommendedDemoRun = presetData?.demo_runs[0] ?? null;

  async function loadSavedRun(runId: string) {
    setError(null);
    setLoadingRunId(runId);

    try {
      const response = await fetch(`${API_BASE}/api/runs/${runId}`);
      if (!response.ok) {
        throw new Error("Saved run could not be loaded");
      }

      const payload = (await response.json()) as RunResponse;
      startTransition(() => {
        setRun(payload);
        setSelectedScenario(payload.scenario.id);
        setStakeholder(payload.plan.stakeholder);
        setGoal(payload.plan.goal);
        setFile(null);
      });
    } catch (loadError) {
      setError(
        loadError instanceof Error ? loadError.message : "Saved run could not be loaded",
      );
    } finally {
      setLoadingRunId(null);
    }
  }

  function applyScenarioDefaults() {
    if (!scenario) {
      return;
    }

    setStakeholder(scenario.stakeholder);
    setGoal(scenario.planning_goal);
  }

  async function handleRun() {
    setError(null);
    setRunning(true);

    try {
      const formData = new FormData();
      formData.append("goal", goal);
      formData.append("stakeholder", stakeholder);
      formData.append("scenario_id", selectedScenario);

      if (file) {
        formData.append("file", file);
      } else {
        formData.append("preset_id", DEFAULT_PRESET_ID);
      }

      const response = await fetch(`${API_BASE}/api/runs`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => null);
        throw new Error(payload?.detail ?? "Run failed");
      }

      const payload = (await response.json()) as RunResponse;
      startTransition(() => setRun(payload));
    } catch (runError) {
      setError(runError instanceof Error ? runError.message : "Run failed");
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="min-h-screen">
      <div className="mx-auto max-w-[92rem] px-5 py-6 lg:px-8 lg:py-8">
        <header className="soft-grid panel panel-strong overflow-hidden rounded-[2.4rem] px-6 py-7 lg:px-10 lg:py-10">
          <div className="grid gap-10 lg:grid-cols-[1.2fr_0.8fr]">
            <div className="space-y-6">
              <span className="eyebrow">
                Southlake distributed-health-network planning studio
              </span>
              <div className="space-y-4">
                <h1 className="section-title max-w-4xl text-5xl font-semibold tracking-[-0.05em] text-slate-950 sm:text-6xl">
                  Agentic synthetic data for planning, innovation, and future-state design.
                </h1>
                <p className="max-w-3xl text-lg leading-8 text-slate-700">
                  This studio shows how Southlake could test routing, campus,
                  and community-access ideas in a safer sandbox before governed
                  local data is used. It profiles a public ED dataset, creates
                  a synthetic planning run, evaluates the result, and exports a
                  pitch-ready explanation of what is useful and what still needs
                  governance.
                </p>
              </div>

              <div className="flex flex-wrap gap-3">
                {recommendedDemoRun && (
                  <button
                    type="button"
                    onClick={() => void loadSavedRun(recommendedDemoRun.run_id)}
                    disabled={loadingRunId === recommendedDemoRun.run_id}
                    data-testid="load-demo-recommended"
                    className="rounded-full bg-slate-950 px-6 py-3 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-slate-400"
                  >
                    {loadingRunId === recommendedDemoRun.run_id
                      ? "Loading recommended run..."
                      : "Load recommended demo run"}
                  </button>
                )}
                <a
                  href="#builder"
                  className="rounded-full border border-slate-900/10 bg-white/80 px-6 py-3 text-sm font-semibold text-slate-900 transition hover:border-emerald-600 hover:text-emerald-700"
                >
                  Build a fresh planning run
                </a>
              </div>

              <div className="grid gap-3 sm:grid-cols-3">
                <div className="rounded-[1.6rem] border border-slate-900/8 bg-white/70 p-4">
                  <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                    Southlake fit
                  </div>
                  <div className="mt-2 text-sm leading-6 text-slate-700">
                    Built around distributed-campus routing, community
                    diversion, and growth questions that match Southlake&apos;s
                    future-state planning story.
                  </div>
                </div>
                <div className="rounded-[1.6rem] border border-slate-900/8 bg-white/70 p-4">
                  <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                    Product angle
                  </div>
                  <div className="mt-2 text-sm leading-6 text-slate-700">
                    Planning and innovation over clinical record synthesis, with
                    scenario framing, metrics, and cautions visible in one
                    place.
                  </div>
                </div>
                <div className="rounded-[1.6rem] border border-slate-900/8 bg-white/70 p-4">
                  <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                    Guardrail
                  </div>
                  <div className="mt-2 text-sm leading-6 text-slate-700">
                    Innovation and testing only. Not a replacement for governed
                    local patient data, operational truth, or clinical action.
                  </div>
                </div>
              </div>
            </div>

            <div className="rounded-[2rem] border border-slate-900/8 bg-slate-950 p-6 text-slate-50">
              <div className="text-xs font-semibold uppercase tracking-[0.2em] text-emerald-300">
                Prototype contract
              </div>
              <div className="mt-4 space-y-4 text-sm leading-7 text-slate-200">
                <p>
                  Frontend: Next.js studio optimized for pitch-day demo flow,
                  scenario selection, and fast backup run loading.
                </p>
                <p>
                  Backend: FastAPI agentic pipeline with Claude reasoning at
                  every step — profiling, strategy, synthesis, evaluation with
                  retry, and narrative generation.
                </p>
                <p>
                  Source: curated NHAMCS 2022 emergency-department public-use
                  subset positioned as a safe planning stand-in, not as a local
                  Southlake dataset.
                </p>
              </div>
              <div className="mt-6 rounded-[1.5rem] bg-white/10 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-300">
                  Planning use boundary
                </p>
                <p className="mt-2 text-sm leading-6 text-slate-100">
                  Use this studio for innovation workshops, service-design
                  conversations, and pitch-day storytelling. Governed local data
                  is still required before any real operational rollout.
                </p>
              </div>
              <div className="mt-4 rounded-[1.5rem] bg-white/10 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-300">
                  API base
                </p>
                <p className="mt-2 break-all font-mono text-sm text-slate-100">
                  {API_BASE}
                </p>
              </div>
            </div>
          </div>
        </header>

        <div className="mt-6 grid gap-6 xl:grid-cols-[1.08fr_0.92fr]">
          <section className="panel rounded-[2.2rem] p-6 lg:p-8">
            <p className="text-sm font-semibold uppercase tracking-[0.16em] text-slate-500">
              Why Southlake
            </p>
            <h2 className="section-title mt-2 text-3xl font-semibold text-slate-950">
              Built for distributed-health-network planning, not a generic healthcare demo.
            </h2>
            <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-700">
              Southlake&apos;s future-state challenge is deciding how care should be
              routed across campus, observation, transfer, and community
              settings. This studio keeps that planning question visible on the
              screen so judges immediately understand the connection.
            </p>
            <div className="mt-5 grid gap-4 lg:grid-cols-3">
              {SOUTHLAKE_FIT_AREAS.map((area) => (
                <div
                  key={area.title}
                  className="rounded-[1.7rem] border border-slate-900/8 bg-white/80 p-5"
                >
                  <h3 className="section-title text-xl font-semibold text-slate-950">
                    {area.title}
                  </h3>
                  <p className="mt-3 text-sm leading-6 text-slate-700">
                    {area.body}
                  </p>
                </div>
              ))}
            </div>
          </section>

          <section className="panel rounded-[2.2rem] p-6 lg:p-8">
            <div className="flex flex-col gap-3 border-b border-slate-900/8 pb-5">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.16em] text-slate-500">
                  Best demo runs
                </p>
                <h2 className="section-title mt-2 text-3xl font-semibold text-slate-950">
                  Use a saved run if live synthesis is slow.
                </h2>
              </div>
              <p className="text-sm leading-7 text-slate-700">
                These runs are stored locally so the pitch stays reliable even
                without re-running the full pipeline on stage.
              </p>
            </div>

            <div className="mt-5 grid gap-4">
              {presetData?.demo_runs.length ? (
                presetData.demo_runs.map((item) => (
                  <DemoRunCard
                    key={item.run_id}
                    demoRun={item}
                    onLoad={(runId) => void loadSavedRun(runId)}
                    loading={loadingRunId === item.run_id}
                  />
                ))
              ) : (
                <div className="rounded-[1.8rem] border border-dashed border-slate-900/14 bg-white/70 p-5 text-sm leading-6 text-slate-700">
                  Save at least one completed run into the demo manifest to make
                  instant backup loading available in the studio.
                </div>
              )}
            </div>
          </section>
        </div>

        <div className="mt-6 grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
          <section id="builder" className="panel rounded-[2.2rem] p-6 lg:p-8">
            <div className="rounded-[1.7rem] border border-emerald-200 bg-emerald-50/90 px-5 py-4 text-sm leading-6 text-emerald-950">
              This is a planning and innovation sandbox. Use it to rehearse
              distributed-network ideas, then validate with governed local data
              before any operational decision.
            </div>

            <div className="mt-6 flex flex-col gap-4 border-b border-slate-900/8 pb-6 lg:flex-row lg:items-end lg:justify-between">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.16em] text-slate-500">
                  Planning Run Builder
                </p>
                <h2 className="section-title mt-2 text-3xl font-semibold text-slate-950">
                  Choose the Southlake planning story, then synthesize it.
                </h2>
              </div>
              <button
                type="button"
                onClick={handleRun}
                disabled={running || loadingRunId !== null || (!presetData && !file)}
                data-testid="generate-planning-run"
                className="rounded-full bg-slate-950 px-6 py-3 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:bg-slate-400"
              >
                {running ? "Running planning agents..." : "Generate planning run"}
              </button>
            </div>

            <div className="mt-6 grid gap-5">
              <div className="grid gap-5 lg:grid-cols-[1.1fr_0.9fr]">
                <label className="grid gap-2">
                  <span className="text-sm font-semibold text-slate-800">
                    Planning stakeholder
                  </span>
                  <input
                    value={stakeholder}
                    onChange={(event) => setStakeholder(event.target.value)}
                    className="rounded-[1.2rem] border border-slate-900/10 bg-white/80 px-4 py-3 outline-none ring-0 transition focus:border-emerald-500"
                  />
                </label>
                <label className="grid gap-2">
                  <span className="text-sm font-semibold text-slate-800">
                    Scenario
                  </span>
                  <select
                    value={selectedScenario}
                    onChange={(event) => setSelectedScenario(event.target.value)}
                    className="rounded-[1.2rem] border border-slate-900/10 bg-white/80 px-4 py-3 outline-none transition focus:border-emerald-500"
                  >
                    {presetData?.scenarios.map((item) => (
                      <option key={item.id} value={item.id}>
                        {item.name}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              <label className="grid gap-2">
                <span className="text-sm font-semibold text-slate-800">
                  Planning goal
                </span>
                <textarea
                  value={goal}
                  onChange={(event) => setGoal(event.target.value)}
                  rows={5}
                  className="rounded-[1.4rem] border border-slate-900/10 bg-white/80 px-4 py-3 outline-none transition focus:border-emerald-500"
                />
              </label>

              <div className="grid gap-5 lg:grid-cols-2">
                <div className="rounded-[1.8rem] border border-slate-900/8 bg-white/75 p-5">
                  <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                    Default preset
                  </div>
                  <div className="mt-2 text-lg font-semibold text-slate-950">
                    {loadingPreset
                      ? "Loading NHAMCS planning preset..."
                      : presetData?.preset.name ?? "API not connected"}
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-700">
                    {presetData?.preset.notes ??
                      "Start the FastAPI service to load the curated planning preset and scenario set."}
                  </p>
                  {presetData && (
                    <div className="mt-4 flex flex-wrap gap-2">
                      {presetData.preset.columns.slice(0, 6).map((column) => (
                        <span
                          key={column}
                          className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-900"
                        >
                          {column}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="rounded-[1.8rem] border border-dashed border-slate-900/18 bg-[#f2e7cf]/60 p-5">
                  <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                    Optional upload
                  </div>
                  <div className="mt-2 text-lg font-semibold text-slate-950">
                    Replace the preset with your own CSV
                  </div>
                  <p className="mt-3 text-sm leading-6 text-slate-700">
                    Upload a single-table CSV to test the same agent pipeline on
                    custom planning, innovation, or service-design data. The
                    file never leaves this workspace.
                  </p>
                  <label className="mt-4 inline-flex cursor-pointer items-center rounded-full bg-slate-950 px-4 py-2 text-sm font-semibold text-white transition hover:bg-teal-700">
                    {file ? file.name : "Choose CSV"}
                    <input
                      type="file"
                      accept=".csv"
                      className="hidden"
                      onChange={(event) =>
                        setFile(event.target.files?.[0] ?? null)
                      }
                    />
                  </label>
                </div>
              </div>
            </div>

            {error && (
              <div className="mt-6 rounded-[1.4rem] border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            )}

            {scenario && (
              <div className="mt-6 rounded-[1.8rem] border border-slate-900/8 bg-[#dff8ec]/80 p-5">
                <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                  <div>
                    <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                      Scenario framing
                    </div>
                    <h3 className="section-title mt-2 text-2xl font-semibold text-slate-950">
                      {scenario.name}
                    </h3>
                    <p className="mt-2 text-sm leading-6 text-slate-700">
                      {scenario.description}
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-3">
                    <div className="rounded-[1.4rem] bg-white/85 px-4 py-3 text-sm font-semibold text-slate-900">
                      x{scenario.row_multiplier.toFixed(2)} target row multiplier
                    </div>
                    <button
                      type="button"
                      onClick={applyScenarioDefaults}
                      className="rounded-[1.4rem] border border-slate-900/10 bg-white/85 px-4 py-3 text-sm font-semibold text-slate-900 transition hover:border-emerald-600 hover:text-emerald-700"
                    >
                      Use scenario defaults
                    </button>
                  </div>
                </div>
                <div className="mt-4 grid gap-3 sm:grid-cols-3">
                  {scenario.pressure_notes.map((note) => (
                    <div
                      key={note}
                      className="rounded-[1.3rem] bg-white/70 px-4 py-3 text-sm text-slate-700"
                    >
                      {note}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>

          <aside className="space-y-6">
            {presetData ? (
              <>
                <ProfileCard profile={presetData.profile} />
                <TablePreview title="Preset preview" rows={presetData.profile.preview} />
              </>
            ) : (
              <div className="panel rounded-[2rem] p-6">
                <div className="text-sm font-semibold uppercase tracking-[0.16em] text-slate-500">
                  API status
                </div>
                <h2 className="section-title mt-2 text-2xl font-semibold text-slate-950">
                  Waiting for the backend
                </h2>
                <p className="mt-3 text-sm leading-7 text-slate-700">
                  Start the FastAPI service to load the curated planning preset,
                  run the pipeline, load saved demo runs, and enable download
                  artifacts.
                </p>
              </div>
            )}
          </aside>
        </div>

        {run && (
          <section data-testid="run-output" className="mt-6 space-y-6">
            <div className="panel rounded-[2.2rem] p-6 lg:p-8">
              <div className="rounded-[1.7rem] border border-orange-200 bg-orange-50/85 px-5 py-4 text-sm leading-6 text-orange-950">
                Planning and innovation only. This output is designed to support
                scenario discussion, service design, and prototype storytelling.
                It is not operational truth and still requires governed local
                validation.
              </div>

              <div className="mt-6 flex flex-col gap-4 border-b border-slate-900/8 pb-5 lg:flex-row lg:items-end lg:justify-between">
                <div>
                  <p className="text-sm font-semibold uppercase tracking-[0.16em] text-slate-500">
                    Planning run output
                  </p>
                  <h2 className="section-title mt-2 text-3xl font-semibold text-slate-950">
                    {run.scenario.name} completed with {numberFormat(run.synthetic_row_count)} synthetic rows.
                  </h2>
                </div>
                <a
                  href={`${API_BASE}/api/runs/${run.run_id}/download`}
                  className="rounded-full bg-emerald-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-emerald-700"
                >
                  Download run package
                </a>
              </div>

              <div className="mt-6 grid gap-4 lg:grid-cols-4">
                <div className="metric-card rounded-[1.6rem] p-5">
                  <div className="text-sm text-slate-500">Fidelity</div>
                  <div className="mt-2 text-4xl font-semibold text-slate-950">
                    {run.evaluation.fidelity_score}
                  </div>
                </div>
                <div className="metric-card rounded-[1.6rem] p-5">
                  <div className="text-sm text-slate-500">Privacy</div>
                  <div className="mt-2 text-4xl font-semibold text-slate-950">
                    {run.evaluation.privacy_score}
                  </div>
                </div>
                <div className="metric-card rounded-[1.6rem] p-5">
                  <div className="text-sm text-slate-500">Utility</div>
                  <div className="mt-2 text-4xl font-semibold text-slate-950">
                    {run.evaluation.utility_score}
                  </div>
                </div>
                <div className="metric-card rounded-[1.6rem] p-5">
                  <div className="text-sm text-slate-500">Exact row overlap</div>
                  <div className="mt-2 text-4xl font-semibold text-slate-950">
                    {run.evaluation.exact_match_rate}%
                  </div>
                </div>
              </div>

              <div className="mt-6 rounded-[2rem] border border-slate-900/8 bg-slate-950 p-6">
                <div className="mb-5 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="agent-dot h-2.5 w-2.5 rounded-full bg-emerald-400" />
                    <span className="text-sm font-semibold uppercase tracking-[0.16em] text-emerald-300">
                      Agent Reasoning Timeline
                    </span>
                  </div>
                  <span className="rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-xs font-semibold text-slate-400">
                    Powered by Claude · Anthropic
                  </span>
                </div>

                <div className="flex gap-3">
                  {run.timeline.map((step, index) => (
                    <div key={step.id} className="flex flex-1 items-start gap-3">
                      <button
                        type="button"
                        onClick={() => setExpandedAgent(expandedAgent === step.id ? null : step.id)}
                        className="agent-card-glow flex-1 cursor-pointer rounded-[1.4rem] border border-white/8 bg-white/5 p-4 text-left transition hover:bg-white/8"
                      >
                        <div className="flex items-center gap-2">
                          <div className="flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-br from-emerald-400 to-teal-600 text-xs font-bold text-white">
                            {index + 1}
                          </div>
                          <div className="text-xs font-semibold uppercase tracking-[0.12em] text-emerald-300">
                            {step.name}
                          </div>
                        </div>
                        <p className="mt-2 text-xs leading-5 text-slate-400">
                          {step.summary.length > 80 ? step.summary.slice(0, 80) + "..." : step.summary}
                        </p>
                        {step.reasoning && (
                          <div className="mt-2 flex items-center gap-1.5">
                            <div className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                            <span className="text-[0.65rem] font-semibold uppercase tracking-[0.1em] text-emerald-400/70">
                              {expandedAgent === step.id ? "Click to collapse" : "Click to view reasoning"}
                            </span>
                          </div>
                        )}
                        {step.status !== "completed" && (
                          <span className="mt-2 inline-block rounded-full bg-amber-500/20 px-2 py-0.5 text-[0.6rem] font-semibold text-amber-300">
                            {step.status}
                          </span>
                        )}
                      </button>
                      {index < run.timeline.length - 1 && (
                        <div className="mt-8 flex-shrink-0 text-lg text-emerald-500/40">→</div>
                      )}
                    </div>
                  ))}
                </div>

                {expandedAgent && (() => {
                  const step = run.timeline.find((s) => s.id === expandedAgent);
                  if (!step?.reasoning) return null;
                  return (
                    <div className="reasoning-expand mt-4 rounded-[1.4rem] border border-emerald-500/15 bg-emerald-950/30 p-5">
                      <div className="mb-3 flex items-center gap-2">
                        <div className="flex h-6 w-6 items-center justify-center rounded-full bg-gradient-to-br from-emerald-400 to-teal-600 text-[0.6rem] font-bold text-white">
                          AI
                        </div>
                        <span className="text-xs font-semibold uppercase tracking-[0.14em] text-emerald-300">
                          {step.name} — Claude&apos;s Reasoning Trace
                        </span>
                      </div>
                      <p className="text-sm leading-7 text-slate-300">
                        &ldquo;{step.reasoning}&rdquo;
                      </p>
                    </div>
                  );
                })()}
              </div>
            </div>

            {(run.evaluation.column_fidelity?.length > 0 || run.evaluation.distribution_comparisons?.length > 0) && (
              <div className="space-y-6">
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 rounded-full bg-teal-500" />
                  <span className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-500">
                    Analytical evaluation — source vs synthetic comparison
                  </span>
                </div>

                {run.evaluation.column_fidelity?.length > 0 && (
                  <FidelityChart data={run.evaluation.column_fidelity} />
                )}

                {run.evaluation.distribution_comparisons?.length > 0 && (
                  <div className="grid gap-4 xl:grid-cols-3">
                    {run.evaluation.distribution_comparisons.map((comp) => (
                      <DistributionChart key={comp.column} comparison={comp} />
                    ))}
                  </div>
                )}
              </div>
            )}

            <div className="grid gap-6 xl:grid-cols-2">
              <TablePreview title="Source sample" rows={run.source_preview} />
              <TablePreview title="Synthetic planning sample" rows={run.synthetic_preview} />
            </div>

            <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
              <div className="panel rounded-[2.2rem] p-6">
                <p className="text-sm font-semibold uppercase tracking-[0.16em] text-slate-500">
                  Planning evaluation
                </p>
                <div className="mt-4 space-y-4">
                  {run.evaluation.highlights.map((item) => (
                    <div
                      key={item}
                      className="rounded-[1.5rem] border border-slate-900/8 bg-white/80 px-4 py-3 text-sm leading-6 text-slate-700"
                    >
                      {item}
                    </div>
                  ))}
                  {run.evaluation.warnings.map((item) => (
                    <div
                      key={item}
                      className="rounded-[1.5rem] border border-amber-200 bg-amber-50 px-4 py-3 text-sm leading-6 text-amber-900"
                    >
                      {item}
                    </div>
                  ))}
                </div>
              </div>

              <div className="panel rounded-[2.2rem] p-6">
                <p className="text-sm font-semibold uppercase tracking-[0.16em] text-slate-500">
                  Pitch-ready briefing output
                </p>
                <div className="mt-4 grid gap-4 lg:grid-cols-3">
                  <div className="rounded-[1.7rem] bg-white/85 p-4">
                    <h3 className="section-title text-2xl font-semibold text-slate-950">
                      Methodology
                    </h3>
                    <div className="mt-3 space-y-3 text-sm leading-6 text-slate-700">
                      {run.pitch_summary.methodology.map((item) => (
                        <p key={item}>{item}</p>
                      ))}
                    </div>
                  </div>
                  <div className="rounded-[1.7rem] bg-white/85 p-4">
                    <h3 className="section-title text-2xl font-semibold text-slate-950">
                      Features
                    </h3>
                    <div className="mt-3 space-y-3 text-sm leading-6 text-slate-700">
                      {run.pitch_summary.features.map((item) => (
                        <p key={item}>{item}</p>
                      ))}
                    </div>
                  </div>
                  <div className="rounded-[1.7rem] bg-slate-950 p-4 text-slate-50">
                    <h3 className="section-title text-2xl font-semibold">
                      Cautions
                    </h3>
                    <div className="mt-3 space-y-3 text-sm leading-6 text-slate-200">
                      {run.pitch_summary.cautions.map((item) => (
                        <p key={item}>{item}</p>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
              <div className="panel rounded-[2.2rem] border border-orange-200 bg-orange-50/75 p-6">
                <p className="text-sm font-semibold uppercase tracking-[0.16em] text-orange-800">
                  Planning use boundary
                </p>
                <h3 className="section-title mt-2 text-2xl font-semibold text-slate-950">
                  {run.cautions.headline}
                </h3>
                <div className="mt-4 space-y-3 text-sm leading-6 text-slate-700">
                  {run.cautions.bullets.map((item) => (
                    <p key={item}>{item}</p>
                  ))}
                </div>
                <div className="mt-4 rounded-[1.4rem] bg-white/80 px-4 py-3 text-sm font-medium text-orange-900">
                  {run.cautions.disclaimer}
                </div>
              </div>

              <div className="panel rounded-[2.2rem] p-6">
                <p className="text-sm font-semibold uppercase tracking-[0.16em] text-slate-500">
                  Export package and files
                </p>
                <div className="mt-4 grid gap-3">
                  {Object.entries(run.artifacts).map(([key, value]) => (
                    <div
                      key={key}
                      className="rounded-[1.5rem] border border-slate-900/8 bg-white/80 px-4 py-3"
                    >
                      <div className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
                        {key.replaceAll("_", " ")}
                      </div>
                      <div className="mt-2 break-all font-mono text-sm text-slate-700">
                        {value}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
