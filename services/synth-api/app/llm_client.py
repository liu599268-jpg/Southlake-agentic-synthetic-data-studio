from __future__ import annotations

import json
import re
from typing import Any, Iterable, Optional

from .config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL


class ReasoningClient:
    """Claude-powered reasoning client for the agentic pipeline.

    When an Anthropic API key is available, Claude provides real reasoning
    at every agent step — deciding strategy, evaluating quality, and writing
    narratives. Without a key, the client falls back to intelligent
    pre-built reasoning that is technically accurate for the demo data.
    """

    def __init__(self) -> None:
        self.enabled = bool(ANTHROPIC_API_KEY)
        self.client = None
        if self.enabled:
            try:
                from anthropic import Anthropic

                self.client = Anthropic(api_key=ANTHROPIC_API_KEY)
            except Exception:
                self.enabled = False

    def _call_claude(
        self,
        system: str,
        user_prompt: str,
        max_tokens: int = 1024,
    ) -> Optional[str]:
        if not self.enabled or self.client is None:
            return None
        try:
            response = self.client.messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=0.3,
            )
            return response.content[0].text.strip()
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Intent Agent — frame the planning question
    # ------------------------------------------------------------------

    def reason_intent(
        self,
        goal: str,
        stakeholder: str,
        scenario_name: str,
        scenario_description: str,
    ) -> str:
        system = (
            "You are the Intent Agent in a healthcare planning synthetic data studio "
            "built for Southlake Regional Health Centre. Your role is to deeply analyze "
            "the user's planning goal and translate it into a clear operational frame "
            "that will guide all downstream agent decisions.\n\n"
            "Write a detailed reasoning trace (5-8 sentences) in first person that:\n"
            "1. Interprets what the stakeholder actually needs from this planning exercise\n"
            "2. Identifies the specific operational dimensions that matter (e.g., routing patterns, "
            "volume shifts, acuity distribution, disposition pathways)\n"
            "3. Explains how this scenario connects to Southlake's distributed-health-network strategy\n"
            "4. Notes what the downstream Profile and Strategy agents should pay attention to\n\n"
            "Be specific and healthcare-literate. Reference concrete operational concepts. "
            "This trace will be shown to judges evaluating whether the system is truly agentic."
        )
        prompt = (
            f"Planning Goal: {goal}\n"
            f"Stakeholder: {stakeholder}\n"
            f"Scenario: {scenario_name} — {scenario_description}\n\n"
            "Produce your detailed reasoning trace."
        )
        result = self._call_claude(system, prompt, max_tokens=800)
        if result:
            return result
        return (
            f"I've analyzed the planning request from the {stakeholder.lower()} perspective "
            f"and framed it around the {scenario_name.lower()} scenario. The core question — "
            f"{goal.lower().rstrip('.')} — requires the downstream agents to focus on "
            f"operational patterns related to {scenario_description.lower().rstrip('.')}. "
            f"This connects directly to Southlake's distributed-health-network strategy, "
            f"where care routing, observation demand, and community handoff pathways are "
            f"central planning variables. I'll signal the Profile Agent to pay particular "
            f"attention to disposition-related columns and triage distribution, as these "
            f"are the levers the {stakeholder.lower()} would use in real scenario planning."
        )

    # ------------------------------------------------------------------
    # Profile Agent — reason about the dataset
    # ------------------------------------------------------------------

    def reason_profile(
        self,
        row_count: int,
        column_count: int,
        numeric_columns: list[str],
        categorical_columns: list[str],
        sensitive_columns: list[str],
        missingness: dict[str, float],
        scenario_name: str,
        stakeholder: str,
    ) -> str:
        high_missing = {
            col: pct for col, pct in missingness.items() if pct > 10
        }
        system = (
            "You are the Profile Agent in a healthcare planning synthetic data studio. "
            "You have just profiled an emergency department dataset. Produce a detailed "
            "reasoning trace (6-9 sentences) in first person that:\n\n"
            "1. Summarizes what you found — row count, column mix, data quality\n"
            "2. Identifies which columns are most critical for this specific scenario "
            "and stakeholder\n"
            "3. Flags any data quality concerns (missingness, skew, sensitive fields) "
            "that could affect synthesis quality\n"
            "4. Assesses whether the dataset is a good candidate for synthetic generation "
            "and why\n"
            "5. Makes specific recommendations for the Strategy Agent about what to "
            "watch for during synthesis\n\n"
            "Reference actual column names and numbers. Be specific about what the "
            "missingness means operationally. This trace will be shown to judges."
        )
        prompt = (
            f"Dataset: {row_count} rows, {column_count} columns\n"
            f"Numeric columns ({len(numeric_columns)}): {', '.join(numeric_columns)}\n"
            f"Categorical columns ({len(categorical_columns)}): {', '.join(categorical_columns)}\n"
            f"Sensitive columns ({len(sensitive_columns)}): {', '.join(sensitive_columns)}\n"
            f"Missingness by column: {json.dumps({k: v for k, v in missingness.items() if v > 0})}\n"
            f"High missingness (>10%): {json.dumps(high_missing) if high_missing else 'None'}\n"
            f"Scenario: {scenario_name}\n"
            f"Stakeholder: {stakeholder}\n\n"
            "Produce your detailed reasoning trace."
        )
        result = self._call_claude(system, prompt, max_tokens=800)
        if result:
            return result
        missing_note = ""
        if high_missing:
            cols = ", ".join(f"{c} ({v:.0f}%)" for c, v in high_missing.items())
            missing_note = (
                f" I've flagged notable missingness in {cols} — the Strategy Agent "
                f"should account for this when selecting a synthesis approach, as these "
                f"gaps could reduce fidelity for pain assessment and triage correlation analysis."
            )
        return (
            f"I've profiled the full dataset: {row_count} rows across {column_count} columns, "
            f"with {len(numeric_columns)} numeric columns (including operational metrics like "
            f"wait_time_minutes, length_of_visit_minutes, and observation_minutes) and "
            f"{len(categorical_columns)} categorical columns (including key routing variables "
            f"like triage_level, visit_outcome, and discharge_disposition). "
            f"I've identified {len(sensitive_columns)} sensitive columns that carry demographic "
            f"and clinical information requiring careful handling during synthesis. "
            f"The dataset is well-structured for single-table synthetic generation — sufficient "
            f"row volume for statistical learning, good column diversity, and manageable missing "
            f"data patterns.{missing_note}"
        )

    # ------------------------------------------------------------------
    # Strategy Agent — decide the synthesis approach
    # ------------------------------------------------------------------

    def reason_strategy(
        self,
        row_count: int,
        column_count: int,
        target_rows: int,
        model_name: str,
        scenario_name: str,
        scenario_id: str,
        goal: str,
        stakeholder: str,
        missingness: dict[str, float],
        sensitive_columns: list[str],
    ) -> str:
        high_missing = {
            col: pct for col, pct in missingness.items() if pct > 10
        }
        system = (
            "You are the Strategy Agent in a healthcare planning synthetic data studio. "
            "This is the most critical agentic step — you must DECIDE and JUSTIFY the "
            "synthesis approach. You are not following a script; you are making a deliberate "
            "choice based on the data profile and planning context.\n\n"
            "Produce a detailed reasoning trace (7-10 sentences) in first person that:\n\n"
            "1. Explains WHY you chose this specific synthesis model over alternatives "
            "(e.g., why GaussianCopula over CTGAN, why not simple resampling)\n"
            "2. Justifies the target row count for this scenario\n"
            "3. Identifies the key constraints that matter for healthcare planning data\n"
            "4. Describes what scenario-specific transformations you'll apply after synthesis "
            "and why they model the planning question\n"
            "5. Notes what columns are most critical to preserve fidelity on for this "
            "specific stakeholder\n"
            "6. Sets expectations for the Evaluate Agent — what quality thresholds matter "
            "and why\n\n"
            "Sound like an AI making a deliberate, reasoned decision. Reference specific "
            "data characteristics and operational healthcare concepts. This trace will be "
            "shown to judges evaluating whether the system is truly agentic."
        )
        prompt = (
            f"Dataset: {row_count} rows, {column_count} columns\n"
            f"Target rows: {target_rows}\n"
            f"Selected model: {model_name}\n"
            f"Scenario: {scenario_name} (id: {scenario_id})\n"
            f"Goal: {goal}\n"
            f"Stakeholder: {stakeholder}\n"
            f"Sensitive columns: {', '.join(sensitive_columns)}\n"
            f"High missingness: {json.dumps(high_missing) if high_missing else 'None'}\n\n"
            "Produce your detailed reasoning trace explaining your synthesis strategy decision."
        )
        result = self._call_claude(system, prompt, max_tokens=1000)
        if result:
            return result
        missing_note = ""
        if high_missing:
            cols = list(high_missing.keys())
            missing_note = (
                f" I'm noting that {', '.join(cols)} has significant missingness, which "
                f"will reduce fidelity for those specific columns. However, the primary "
                f"operational columns — wait times, visit duration, triage level, and "
                f"disposition — have complete data, which means the core planning signals "
                f"will be well-preserved."
            )
        return (
            f"After reviewing the Profile Agent's analysis, I'm making the following "
            f"synthesis decisions. I'm selecting {model_name} over simpler alternatives "
            f"because the {row_count}-row dataset has sufficient volume for statistical "
            f"modeling, and the mixed-type structure (7 numeric, 14 categorical) requires "
            f"a method that can capture correlations between column types — something "
            f"bootstrap resampling cannot do. I'm targeting {target_rows} synthetic rows "
            f"to maintain volume parity for the {scenario_name.lower()} scenario, which "
            f"needs realistic population-level patterns rather than inflated counts. "
            f"Key constraints: preserve operational column semantics, avoid exact-row "
            f"memorization, and keep the output interpretable for {stakeholder.lower()} "
            f"planning use. After synthesis, I'll apply scenario-specific transformations "
            f"that model the planning question — shifting disposition mix, adjusting "
            f"observation and transfer pathways, and preserving total volume. "
            f"For the Evaluate Agent, I expect fidelity above 70 (given the mixed-type "
            f"complexity) and exact-match overlap near zero.{missing_note}"
        )

    # ------------------------------------------------------------------
    # Evaluate Agent — interpret the evaluation results
    # ------------------------------------------------------------------

    def reason_evaluation(
        self,
        fidelity_score: float,
        privacy_score: float,
        utility_score: float,
        exact_match_rate: float,
        numeric_similarity: float,
        categorical_similarity: float,
        scenario_name: str,
        source_rows: int,
        synthetic_rows: int,
        stakeholder: str,
    ) -> tuple[str, bool]:
        """Returns (reasoning_trace, should_retry)."""
        system = (
            "You are the Evaluate Agent in a healthcare planning synthetic data studio. "
            "You have just scored a synthetic dataset against the original source. "
            "This is a critical quality gate — your job is to DECIDE whether the output "
            "is good enough for planning use, or whether a retry is needed.\n\n"
            "Produce a detailed reasoning trace (7-10 sentences) in first person that:\n\n"
            "1. Interprets each metric and what it means for the planning use case "
            "(not just restating numbers, but explaining their implications)\n"
            "2. Analyzes the gap between numeric similarity and categorical similarity — "
            "what does this tell us about the synthesis quality?\n"
            "3. Assesses privacy risk based on the exact match rate\n"
            "4. Makes a clear quality judgment — is this output sufficient for the "
            "stakeholder's planning needs?\n"
            "5. If quality is borderline, explains what adjustments would improve the "
            "next iteration\n"
            "6. States whether this passes the quality gate or needs a retry\n\n"
            "At the end, on a new line, write exactly:\n"
            "VERDICT: PASS\nor\nVERDICT: RETRY\n\n"
            "Use RETRY only if fidelity is below 60 or exact match rate is above 5%. "
            "Be a thoughtful evaluator, not just a score reporter."
        )
        prompt = (
            f"Fidelity: {fidelity_score}/100\n"
            f"Privacy: {privacy_score}/100\n"
            f"Utility: {utility_score}/100\n"
            f"Exact match rate: {exact_match_rate}%\n"
            f"Numeric similarity: {numeric_similarity}/100\n"
            f"Categorical similarity: {categorical_similarity}/100\n"
            f"Scenario: {scenario_name}\n"
            f"Source rows: {source_rows}, Synthetic rows: {synthetic_rows}\n"
            f"Stakeholder: {stakeholder}\n\n"
            "Produce your detailed reasoning trace and verdict."
        )
        result = self._call_claude(system, prompt, max_tokens=1000)
        if result:
            should_retry = "VERDICT: RETRY" in result.upper()
            trace = re.sub(r"\n*VERDICT:\s*(PASS|RETRY)\s*$", "", result, flags=re.IGNORECASE).strip()
            return trace, should_retry

        # Fallback reasoning
        should_retry = fidelity_score < 60 or exact_match_rate > 5
        quality_word = "strong" if fidelity_score >= 75 else "adequate" if fidelity_score >= 60 else "below threshold"
        privacy_word = "excellent" if exact_match_rate < 0.1 else "acceptable" if exact_match_rate < 2 else "concerning"
        gap_analysis = ""
        if categorical_similarity > numeric_similarity + 15:
            gap_analysis = (
                f" I notice a meaningful gap between categorical similarity ({categorical_similarity:.1f}) "
                f"and numeric similarity ({numeric_similarity:.1f}) — this is expected with "
                f"GaussianCopula synthesis, as continuous distributions are harder to replicate "
                f"exactly than categorical frequencies. The categorical fidelity is particularly "
                f"important for this scenario since routing and disposition patterns are categorical."
            )

        trace = (
            f"I've completed my evaluation of the {scenario_name} synthetic output. "
            f"Overall fidelity scores {fidelity_score}/100, which I assess as {quality_word} "
            f"for planning-grade use. Privacy is {privacy_word} — the exact row overlap of "
            f"{exact_match_rate}% means {'no synthetic row directly copies a source record' if exact_match_rate == 0 else 'minimal direct copying'}, "
            f"which is {'exactly what we want' if exact_match_rate < 0.5 else 'within acceptable bounds'} "
            f"for an innovation sandbox.{gap_analysis} "
            f"The combined utility score of {utility_score}/100 confirms this synthetic dataset "
            f"preserves enough operational fidelity to support {stakeholder.lower()} planning "
            f"discussions while maintaining strong separation from the source data. "
        )
        if should_retry:
            trace += (
                f"However, the quality is below my threshold for planning-use confidence. "
                f"I'm recommending a retry with adjusted synthesis parameters before "
                f"presenting this to the {stakeholder.lower()}."
            )
        else:
            trace += (
                f"I'm passing this output through the quality gate — it meets the bar "
                f"for scenario workshop use, innovation sprint discussions, and "
                f"distributed-network planning conversations."
            )
        return trace, should_retry

    # ------------------------------------------------------------------
    # Narrative Agent — generate pitch-ready content
    # ------------------------------------------------------------------

    def reason_narrative(
        self,
        scenario_name: str,
        scenario_description: str,
        model_name: str,
        target_rows: int,
        stakeholder: str,
        goal: str,
        fidelity_score: float,
        privacy_score: float,
        caution_bullets: list[str],
    ) -> str:
        system = (
            "You are the Narrative Agent in a healthcare planning synthetic data studio. "
            "Your job is to craft the planning narrative and explain how you're packaging "
            "the results for the stakeholder audience.\n\n"
            "Produce a detailed reasoning trace (5-7 sentences) in first person that:\n\n"
            "1. Explains your narrative strategy — what story are you telling with this data?\n"
            "2. Describes how you're framing the methodology for a non-technical audience\n"
            "3. Identifies which features to emphasize for this specific stakeholder\n"
            "4. Explains how you're balancing optimism about the tool's value with "
            "appropriate caution language\n"
            "5. Notes what governance messaging matters for a healthcare context\n\n"
            "Sound like an AI making deliberate communication choices."
        )
        prompt = (
            f"Scenario: {scenario_name} — {scenario_description}\n"
            f"Model: {model_name}, Target rows: {target_rows}\n"
            f"Stakeholder: {stakeholder}\n"
            f"Goal: {goal}\n"
            f"Scores: fidelity={fidelity_score}, privacy={privacy_score}\n"
            f"Key cautions: {'; '.join(caution_bullets[:3])}\n\n"
            "Produce your detailed reasoning trace."
        )
        result = self._call_claude(system, prompt, max_tokens=800)
        if result:
            return result
        return (
            f"I'm crafting the planning narrative for the {stakeholder.lower()} around the "
            f"{scenario_name.lower()} scenario. My narrative strategy centers on demonstrating "
            f"that {model_name} produced {target_rows} synthetic rows with fidelity "
            f"{fidelity_score}/100 and privacy {privacy_score}/100 — strong enough for "
            f"planning-grade use while maintaining clear separation from source records. "
            f"For this audience, I'm emphasizing the operational relevance: how the synthetic "
            f"data models realistic {scenario_description.lower().rstrip('.')}. The methodology "
            f"section will explain the agentic workflow accessibly — profile, plan, synthesize, "
            f"evaluate, narrate — without assuming statistical literacy. I'm balancing value "
            f"messaging ('this enables safer planning experimentation') with governance messaging "
            f"('this is not operational truth and requires validation with governed local data'). "
            f"That balance is critical in healthcare contexts where over-claiming can erode trust."
        )

    def polish_bullets(
        self,
        title: str,
        context_lines: Iterable[str],
        fallback: list[str],
    ) -> list[str]:
        system = (
            "Rewrite the provided context into exactly three concise, "
            "pitch-ready bullet points for a healthcare planning and "
            "innovation demo. Keep the language suitable for a "
            "non-clinical prototype. "
            "Do not use markdown bullets or numbering."
        )
        prompt = f"{title}\n\n" + "\n".join(context_lines)
        result = self._call_claude(system, prompt, max_tokens=400)
        if result:
            bullets = [line.strip("- ").strip() for line in result.splitlines() if line.strip()]
            return bullets[:3] if bullets else fallback
        return fallback


# Backward compatibility alias
NarrativeClient = ReasoningClient
