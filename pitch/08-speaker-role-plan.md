# Speaker Role Plan

## Team

- **Zhou1** — Lead speaker. Opening, problem statement, methodology (Slide 1), closing.
- **Zhou2** — Demo driver. Runs the live app, walks Slide 2 (Features).
- **Huang** — Cautions and credibility. Walks Slide 3 (Cautions), leads Q&A on limitations and governance.

---

## Why This Split

- **Zhou1** is the strongest speaker → owns the opening hook and closing punch. Also explains the agentic methodology because that's the hardest concept to sell.
- **Zhou2** drives the demo → needs to be comfortable clicking through the app and narrating what judges see.
- **Huang** handles cautions → this is a *strength* position, not a weakness. The caution slide builds credibility. The person who delivers it should sound thoughtful and careful, not defensive.

---

## Zhou1's Script

### Opening (0:00 – 1:20)

> "Southlake's challenge is not just a data problem — it's a safe experimentation problem. Healthcare teams need to model new care pathways, test routing ideas, and plan for growth. But they can't casually use real patient records for early-stage testing. We built an agentic synthetic data studio that creates a safer planning sandbox — and makes the limitations visible before anyone over-trusts the output."

### Why Southlake (1:20 – 3:20)

> "Southlake is becoming a distributed health network. Their 2025-2034 strategy is about moving care closer to home — deciding what stays on the main campus, what goes to community clinics, how observation and transfer pathways should evolve. Those questions are data-heavy, but privacy and governance make experimentation hard. Synthetic data unlocks earlier-stage innovation."

### Slide 1 — Methodology (8:10 – 10:30)

> "Our methodology is what the brief calls 'agentic.' Think of the difference between a vending machine and a chef. A vending machine does the same thing every time — press a button, get an output. A chef looks at the ingredients, considers what you asked for, makes a plan, cooks it, tastes it, adjusts, and explains what they made. Our system is the chef."

> "An LLM powers five agent steps. The Intent Agent frames the planning question. The Profile Agent analyzes the dataset. The Strategy Agent — and this is key — uses AI reasoning to *decide* the best synthesis approach for this specific data and scenario. It doesn't use a fixed formula. Then the Evaluate Agent checks its own work — if quality is below threshold, it adjusts and retries. Finally, the Narrative Agent writes planning-grade summaries."

> "The emphasis in the brief was 'how the system thinks and acts, not just the data it produces.' That's exactly what we built. The thinking is visible at every step."

### Closing (15:10 – 16:30)

> "Our core argument is simple: agentic synthetic data can help health systems test future-state ideas earlier, faster, and more safely. For Southlake, that means a practical first step toward distributed-network experimentation without touching real patient records."

> "If this moved beyond the hackathon, the next step would be validation with governed local data, privacy review, and scenario designs tailored to Southlake's actual operating questions."

---

## Zhou2's Script

### Live Demo (3:20 – 6:30)

Open `http://127.0.0.1:3100` in the browser.

> "Here's the studio. Let me show you how it works."

Click **"Load recommended demo run"**.

> "We have pre-saved demo runs so the pitch stays reliable — but the same studio can also generate fresh runs in real time."

While loading:

> "The recommended run uses the Distributed Campus Routing scenario — this directly maps to Southlake's strategy of distributing care across settings."

When results appear, scroll slowly through:

> "At the top you can see the agent timeline — five steps, each showing what the AI reasoned and decided. Below that, the evaluation metrics: fidelity 81.5 — meaning the synthetic data preserves 81.5% of the original statistical patterns. Privacy 100 — zero exact row copies found. Utility 88.9 — a weighted combination."

Scroll to data tables:

> "Here's the source data versus the synthetic output side by side. You can see the patterns are preserved but no row is an exact copy."

Scroll to pitch output:

> "And at the bottom, the system auto-generates methodology, features, and caution summaries. This is the narrative layer — the explanation is as important as the data."

### Slide 2 — Features (10:30 – 12:50)

> "The product is not just a data generator. Three things make it a planning studio."

> "First, Southlake-specific scenarios. Each scenario models a different planning question — ED surge pressure, community diversion, regional growth, and distributed campus routing."

> "Second, visible evaluation. Innovation teams can see fidelity, privacy, and utility scores in one screen. They don't need to trust a black box."

> "Third, export and narrative. Every run produces a downloadable package — synthetic data, evaluation report, and planning summaries ready for workshops or presentations."

---

## Huang's Script

### Slide 3 — Cautions (12:50 – 15:10)

> "We want to be very clear about what this tool is and what it's not."

> "It is safe for planning workshops, innovation sprints, scenario discussions, and early-stage prototyping. It creates a safer starting point than using real patient records for brainstorming."

> "It is NOT ready for clinical decisions, staffing commitments, reimbursement, or any patient-level action."

> "Three specific limitations. First, our demo uses a U.S. public dataset — not Southlake's real data. This is intentional for the hackathon — we needed safe, reproducible data. Real deployment would use governed local data. Second, this is a single-table prototype. A real hospital digital twin would need multi-table relationships and validated local models. Third, synthetic data is not automatically private. Our evaluation checks for exact-row leakage, but that's a necessary check, not a privacy guarantee."

> "We believe showing these limitations openly is a strength. In healthcare, the team that says 'here's what we don't know yet' is more trustworthy than the team that claims everything is solved."

### Q&A Lead

Huang should take first crack at limitation and governance questions. Prepared answers are in `05-judge-qa.md`. Key rule: **be honest, then pivot to what the prototype DOES demonstrate.**

---

## Hand-Off Lines

### Zhou1 → Zhou2
> "That's the problem and the opportunity. Now let me hand over to show the studio itself — how a Southlake planning run actually looks on screen."

### Zhou2 → Zhou1
> "That's the product. Now let me hand back to walk through the methodology that powers it."

### Zhou1 → Zhou2 (Slide 2)
> "That's the agentic workflow. Now let me hand back to walk through the key features."

### Zhou2 → Huang
> "Those are the features. But we also want to be explicit about what this tool is not. I'll hand over for the caution boundary."

### Huang → Zhou1
> "Those limitations are why we position this as a safer front-end to planning, not a final decision system. I'll hand back for the close."

---

## Timing Summary

| Time | Who | What |
|------|-----|------|
| 0:00 – 1:20 | Zhou1 | Opening problem statement |
| 1:20 – 3:20 | Zhou1 | Why Southlake needs this |
| 3:20 – 6:30 | Zhou2 | Live demo |
| 6:30 – 8:10 | Zhou2 | Demo highlights walkthrough |
| 8:10 – 10:30 | Zhou1 | Slide 1 — Methodology |
| 10:30 – 12:50 | Zhou2 | Slide 2 — Features |
| 12:50 – 15:10 | Huang | Slide 3 — Cautions |
| 15:10 – 16:30 | Zhou1 | Closing |
| 16:30 – 20:00 | All | Buffer / Q&A |

---

## Pre-Pitch Checklist

- [ ] All three have read `12-technical-explainer.md`
- [ ] All three have read `13-agentic-explainer.md`
- [ ] All three have read `14-data-explainer.md`
- [ ] Zhou2 has practiced the demo click path 3+ times
- [ ] Hand-off lines rehearsed at least twice
- [ ] One full timed run-through completed
- [ ] Laptop charged, app running, backup screenshots accessible
