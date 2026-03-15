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
            "You are the Intent Agent in a healthcare planning synthetic data studio. "
            "Your job is to take a user's goal and stakeholder lens and produce a "
            "2-3 sentence reasoning trace that explains how you interpreted the planning "
            "question and what it means for downstream synthesis. Be specific to the "
            "scenario. Write in first person as the agent. Keep it concise."
        )
        prompt = (
            f"Goal: {goal}\n"
            f"Stakeholder: {stakeholder}\n"
            f"Scenario: {scenario_name} — {scenario_description}\n\n"
            "Produce your reasoning trace."
        )
        result = self._call_claude(system, prompt)
        if result:
            return result
        return (
            f"Framed the planning run for {stakeholder.lower()} around the "
            f"{scenario_name.lower()} scenario. The core question is: {goal} "
            f"This means downstream synthesis should emphasize the operational "
            f"patterns most relevant to {scenario_description.lower().rstrip('.')}."
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
            "You have just profiled a dataset. Produce a 3-4 sentence reasoning trace "
            "about what you found — what's notable, what might affect synthesis quality, "
            "and what the downstream Strategy Agent should watch for. Be specific about "
            "column names and numbers. Write in first person as the agent."
        )
        prompt = (
            f"Dataset: {row_count} rows, {column_count} columns\n"
            f"Numeric columns ({len(numeric_columns)}): {', '.join(numeric_columns)}\n"
            f"Categorical columns ({len(categorical_columns)}): {', '.join(categorical_columns)}\n"
            f"Sensitive columns ({len(sensitive_columns)}): {', '.join(sensitive_columns)}\n"
            f"High missingness (>10%): {json.dumps(high_missing) if high_missing else 'None'}\n"
            f"Scenario: {scenario_name}\n"
            f"Stakeholder: {stakeholder}\n\n"
            "Produce your reasoning trace."
        )
        result = self._call_claude(system, prompt, max_tokens=512)
        if result:
            return result
        missing_note = ""
        if high_missing:
            cols = ", ".join(f"{c} ({v:.0f}%)" for c, v in high_missing.items())
            missing_note = (
                f" Notable missingness in {cols} — the Strategy Agent should "
                f"account for this when selecting a synthesis approach."
            )
        return (
            f"Profiled {row_count} rows across {column_count} columns. "
            f"Found {len(numeric_columns)} numeric and {len(categorical_columns)} "
            f"categorical columns with {len(sensitive_columns)} flagged as sensitive. "
            f"The dataset is a good candidate for single-table synthesis given its "
            f"size and mixed-type structure.{missing_note}"
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
            "You must decide and justify the synthesis approach. Explain WHY you chose "
            "this model, this row count, and what constraints matter. Reference the "
            "specific data characteristics. Write in first person as the agent. "
            "3-4 sentences. Sound like an AI making a deliberate decision."
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
            "Produce your reasoning trace explaining your synthesis strategy decision."
        )
        result = self._call_claude(system, prompt, max_tokens=512)
        if result:
            return result
        missing_note = ""
        if high_missing:
            cols = list(high_missing.keys())
            missing_note = (
                f" The high missingness in {', '.join(cols)} may reduce fidelity "
                f"for those columns, but the overall dataset quality supports reliable synthesis."
            )
        return (
            f"Given the {row_count}-row dataset with {column_count} columns and "
            f"mixed types, I'm selecting {model_name} as the primary synthesis method. "
            f"The dataset has sufficient size for statistical modeling and the "
            f"{scenario_name.lower()} scenario requires {target_rows} target rows "
            f"to maintain volume parity. Key constraints: preserve operational "
            f"column semantics, avoid exact-row memorization, and keep the output "
            f"interpretable for {stakeholder.lower()} planning use.{missing_note}"
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
            "You have just scored a synthetic dataset. Produce a 3-4 sentence reasoning "
            "trace interpreting the results. Explain what the scores mean for planning "
            "use, flag any concerns, and state whether the quality is sufficient or "
            "whether a retry is recommended. Write in first person as the agent.\n\n"
            "At the end of your trace, add on a new line either:\n"
            "VERDICT: PASS\n"
            "or\n"
            "VERDICT: RETRY\n\n"
            "Use RETRY only if fidelity is below 60 or exact match rate is above 5%."
        )
        prompt = (
            f"Fidelity: {fidelity_score}\n"
            f"Privacy: {privacy_score}\n"
            f"Utility: {utility_score}\n"
            f"Exact match rate: {exact_match_rate}%\n"
            f"Numeric similarity: {numeric_similarity}\n"
            f"Categorical similarity: {categorical_similarity}\n"
            f"Scenario: {scenario_name}\n"
            f"Source rows: {source_rows}, Synthetic rows: {synthetic_rows}\n"
            f"Stakeholder: {stakeholder}\n\n"
            "Produce your reasoning trace and verdict."
        )
        result = self._call_claude(system, prompt, max_tokens=512)
        if result:
            should_retry = "VERDICT: RETRY" in result.upper()
            # Strip the verdict line from the trace
            trace = re.sub(r"\n*VERDICT:\s*(PASS|RETRY)\s*$", "", result, flags=re.IGNORECASE).strip()
            return trace, should_retry

        # Fallback reasoning
        should_retry = fidelity_score < 60 or exact_match_rate > 5
        quality_word = "strong" if fidelity_score >= 75 else "adequate" if fidelity_score >= 60 else "below threshold"
        privacy_word = "excellent" if exact_match_rate < 0.1 else "acceptable" if exact_match_rate < 2 else "concerning"

        trace = (
            f"Evaluated the {scenario_name} output: fidelity {fidelity_score} ({quality_word}), "
            f"privacy {privacy_score} with {exact_match_rate}% exact overlap ({privacy_word}). "
            f"Numeric similarity averaged {numeric_similarity:.1f} and categorical similarity "
            f"averaged {categorical_similarity:.1f}. "
        )
        if should_retry:
            trace += (
                f"Quality is below the planning-use threshold. Recommending a retry "
                f"with adjusted parameters before presenting to {stakeholder.lower()}."
            )
        else:
            trace += (
                f"The output meets the quality threshold for {stakeholder.lower()} "
                f"planning use. The synthetic dataset preserves enough operational "
                f"patterns to support scenario discussion and innovation workshops."
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
            "Produce a 2-3 sentence reasoning trace about how you're crafting the "
            "planning narrative for this specific run. Mention the audience, the scenario "
            "angle, and what you're emphasizing in the output. Write in first person."
        )
        prompt = (
            f"Scenario: {scenario_name} — {scenario_description}\n"
            f"Model: {model_name}, Target rows: {target_rows}\n"
            f"Stakeholder: {stakeholder}\n"
            f"Goal: {goal}\n"
            f"Scores: fidelity={fidelity_score}, privacy={privacy_score}\n"
            f"Key cautions: {'; '.join(caution_bullets[:3])}\n\n"
            "Produce your reasoning trace."
        )
        result = self._call_claude(system, prompt, max_tokens=400)
        if result:
            return result
        return (
            f"Crafting the planning narrative for {stakeholder.lower()} around the "
            f"{scenario_name.lower()} scenario. Emphasizing that {model_name} produced "
            f"{target_rows} synthetic rows with fidelity {fidelity_score} and privacy "
            f"{privacy_score}. The narrative will frame this as a planning artifact "
            f"for innovation use, with clear boundaries about what it is not."
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
