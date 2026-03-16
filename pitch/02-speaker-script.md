# Speaker Script

Total time: 20 minutes. Speakers: Zhou1, Zhou2, Huang.

---

## Zhou1: Opening (0:00 – 1:20)

"Southlake's challenge is not just a data problem — it's a safe experimentation problem.

Healthcare teams need to model new care pathways, test routing ideas, and plan for future growth. But they can't casually use real patient records for early-stage testing. Privacy, governance, and data sharing agreements create a wall between the question and the data.

We built an agentic synthetic data studio that creates a safer planning sandbox — with the reasoning and analysis technically supported by theFinlyApp — and makes the limitations visible before anyone over-trusts the output."

---

## Zhou1: Why Southlake (1:20 – 3:20)

"Southlake is becoming a distributed health network. Their 2025-2034 strategy is about moving care closer to home.

That means asking: what stays on the main campus? What goes to community clinics? How should observation and transfer pathways evolve? What does regional population growth mean for capacity?

Those questions are data-heavy. But privacy and governance make experimentation hard. You can't just grab patient records and start modeling.

Synthetic data solves this. It gives innovation teams a way to test ideas in a safer sandbox — using data that preserves the statistical patterns of real ED operations without containing any real patient records."

---

## Zhou1 → Zhou2 hand-off

"That's the problem and the opportunity. Now let me hand over to show the studio itself — how a Southlake planning run actually looks on screen."

---

## Zhou2: Live Demo (3:20 – 6:30)

*Open browser to http://127.0.0.1:3100*

"Here's the studio. Let me show you how it works."

*Click "Load recommended demo run"*

"We have pre-saved demo runs so the pitch stays reliable, but the studio can also generate fresh runs in real time."

*While loading:*

"The recommended run uses the Distributed Campus Routing scenario. This directly maps to Southlake's strategy of distributing care across campus, observation, community, and transfer settings."

*When results appear, scroll slowly:*

"At the top, the agent timeline — five steps, each showing what the AI reasoned and decided. This is what makes our system agentic: the reasoning engine, technically supported by theFinlyApp, powers every step."

*Point to metrics:*

"Fidelity 87.8 — the synthetic data preserves 87.8% of the original statistical patterns. Privacy 100 — zero exact row copies detected. Utility 92.7 — a weighted score that says this data is both realistic and not a copy."

*Scroll to data tables:*

"Source data versus synthetic output, side by side. Patterns are preserved. No row is identical."

*Scroll to pitch output:*

"And the system auto-generates methodology, features, and caution summaries. The explanation layer is as important as the data itself."

---

## Zhou2: Demo Highlights (6:30 – 8:10)

"Three things to notice. First, the scenario selector. Four Southlake-specific scenarios — each modeling a different planning question.

Second, the evaluation is visible. Innovation teams see quality scores on screen. They don't need to trust a black box.

Third, the export. Every run produces a downloadable package — synthetic data, evaluation report, and planning summaries ready for workshops."

---

## Zhou2 → Zhou1 hand-off

"That's the product. Now let me hand back to walk through the methodology that powers it."

---

## Zhou1: Slide 1 — Methodology (8:10 – 10:30)

"Our methodology is what the hackathon brief calls 'agentic.' Let me explain what that means.

Think of the difference between a vending machine and a chef. A vending machine does the same thing every time — press a button, get an output. No thinking. A chef looks at the ingredients, considers what you asked for, makes a plan, cooks it, tastes it, adjusts the seasoning, and explains what they made and why.

Our system is the chef. The reasoning and analysis that powers the demo is technically supported by theFinlyApp — a financial intelligence platform whose agentic architecture we adapted for healthcare planning.

The engine powers five agent steps. The Intent Agent frames the planning question based on the user's goal. The Profile Agent analyzes the dataset — not just counting rows, but reasoning about what's relevant for the planning question.

The Strategy Agent is where the real decision-making happens. It uses AI reasoning to decide the best synthesis approach for this specific data and scenario. Not a fixed formula — actual reasoning.

Then the Evaluate Agent checks its own work. If quality is below threshold, it reasons about why and adjusts parameters for a retry. That self-correction loop is a core part of what makes this agentic.

Finally, the Narrative Agent writes planning-grade summaries tailored to the audience and scenario.

The brief said: 'the emphasis is on how the system thinks and acts, not just the data it produces.' That's exactly what we built. The thinking is visible at every step."

---

## Zhou1 → Zhou2 hand-off

"That's the agentic workflow. Now let me hand back to walk through the key features."

---

## Zhou2: Slide 2 — Features (10:30 – 12:50)

"The product is not just a data generator. It's a planning and innovation studio. Three things make it practical.

First: Southlake-specific scenarios. Each scenario models a different planning question. ED surge for pressure testing. Community diversion for shifting low-acuity demand closer to home. Regional growth for population projections. And distributed campus routing — our primary demo — for modeling how care should be routed across settings.

Second: visible evaluation. Fidelity, privacy, and utility scores are on screen. The agent timeline shows what the AI decided at each step. Innovation teams can see the reasoning, not just the output.

Third: export and narrative. Every run produces a downloadable package with the synthetic dataset, evaluation report, and pitch-ready summaries. This means an innovation team can go from a planning question to a testable artifact in minutes."

---

## Zhou2 → Huang hand-off

"Those are the features. But we also want to be explicit about what this tool is not. I'll hand over for the caution boundary."

---

## Huang: Slide 3 — Cautions (12:50 – 15:10)

"We want to be very clear about what this tool is and what it's not.

It is safe for planning workshops, innovation sprints, scenario discussions, and early-stage prototyping. It creates a safer starting point than using real patient records for brainstorming.

It is NOT ready for clinical decisions, staffing commitments, reimbursement, or any patient-level action.

Three specific limitations.

First: our demo uses a U.S. public dataset, not Southlake's real data. This is intentional. For the hackathon, we needed safe, reproducible data that we could freely share and demo. The NHAMCS dataset from the CDC is the gold standard for ED operations research. Real deployment would use governed local data under proper data sharing agreements.

Second: this is a single-table prototype. A real hospital digital twin would need multi-table relationships, validated local models, and integration with hospital information systems. We're not claiming to have built that — we're showing the workflow.

Third: synthetic data is not automatically private. Our evaluation checks for exact-row leakage, but that's a necessary check, not a privacy guarantee. The system makes these limitations visible on purpose. In healthcare, the explanation of what you DON'T know is as important as the data you produce.

We believe showing these limitations openly is a strength. In healthcare, the team that says 'here's what we don't know yet' is more trustworthy than the team that claims everything is solved."

---

## Huang → Zhou1 hand-off

"Those limitations are why we position this as a safer front-end to planning, not a final decision system. I'll hand back for the close."

---

## Zhou1: Closing (15:10 – 16:30)

"Our core argument is simple: agentic synthetic data can help health systems test future-state ideas earlier, faster, and more safely.

For Southlake, that means a practical first step toward distributed-network experimentation without touching real patient records. The reasoning and analysis engine is technically supported by theFinlyApp, demonstrating that agentic intelligence built for one domain can be adapted for healthcare planning.

If this moved beyond the hackathon, the next step would be validation with governed local data, privacy review, and scenario designs tailored to Southlake's actual operating questions.

Thank you."

---

## All: Q&A Buffer (16:30 – 20:00)

- Huang takes limitation/governance/privacy questions first
- Zhou1 takes methodology/agentic/strategy questions
- Zhou2 takes demo/product/feature questions
- See `05-judge-qa.md` for prepared answers
- See `12-technical-explainer.md` for deep technical answers
- See `13-agentic-explainer.md` for "is this really an agent?" responses
