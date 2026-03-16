# Presenter Handbook

## 1. What This Project Is

Southlake Agentic Synthetic Data Studio is a hackathon prototype for one specific need: helping a health system experiment with data-heavy planning ideas without using real patient records.

The simplest way to explain it is:

- We start from a public emergency-department dataset.
- We use an agent-style workflow to create a synthetic version of that data.
- We score the result for realism, leakage risk, and usefulness.
- We present the output together with clear cautions for healthcare professionals.

This is not a clinical system and not a production privacy guarantee. It is an innovation and planning tool.

## 2. Why Southlake Should Care

Southlake's brief is about becoming a distributed health network. That means care will not be thought of as one building only. It means the organization needs better ways to model:

- where demand shows up
- what care can move closer to home
- what still needs hospital capacity
- how routing, observation, and transfer patterns may change

The problem is that those ideas are data-heavy, while real patient data is highly sensitive. Synthetic data helps create a safer sandbox for early testing.

## 3. What "Synthetic Data" Means

Synthetic data is not copied patient data. It is generated data that tries to preserve useful patterns from a source dataset.

For presenters, the key sentence is:

Synthetic data is fake data that is statistically useful for testing and planning, but should not be treated as the truth about a real hospital population.

## 4. What "Agentic" Means In This Project

In this project, "agentic" means the system does a multi-step workflow instead of one single generation step.

The studio:

- understands the user goal
- profiles the dataset
- decides how many rows to generate and what to evaluate
- creates synthetic data
- checks fidelity and leakage risk
- produces a plain-English caution summary
- drafts pitch-day materials

That is the reason we call it an agentic synthetic data creation service.

## 5. What The Studio Actually Does

The user sees one main interface where they can:

- choose a scenario
- set a stakeholder lens
- enter a goal
- optionally upload a CSV
- generate a run
- inspect metrics and sample rows
- download artifacts

The bundled public dataset is a curated subset of the 2022 CDC/NCHS NHAMCS emergency-department public-use file. It is used as a demo-safe source.

## 6. What The Main Metrics Mean

These metrics matter during the demo:

- `Fidelity`: how well the synthetic output matches the original data patterns
- `Privacy`: how well the output avoids looking like copied source rows
- `Utility`: whether the result is still useful for planning and scenario work
- `Exact row overlap`: the most direct leakage check; lower is better

Important presenter rule:

Do not say the synthetic data is "safe" in an absolute sense. Say the studio performs safety-oriented checks and makes the limitations visible.

## 7. Scenario Presets

The demo currently includes four scenario presets:

- `ED Surge`: more volume, more ambulance arrivals, longer waits, more pressure
- `Community Diversion`: lower-acuity demand shifted away from the ED into community settings
- `Regional Growth`: more visits and more chronic complexity over time
- `Distributed Campus Routing`: more movement across observation, transfer, and distributed care pathways

For pitch day, the best primary scenario is `Distributed Campus Routing` because it aligns most directly with Southlake's distributed-health-network story.

The app now exposes this as a saved demo run on the home screen, so the team can load it instantly instead of depending on live generation.

## 8. Best Current Demo Run

Recommended primary run:

- Run ID: `5248d0e0dd`
- Scenario: `Distributed Campus Routing`
- Fidelity: `81.54`
- Privacy: `100.0`
- Utility: `88.92`
- Synthetic rows: `13,085`
- ✅ Full agentic reasoning traces at all 5 agent steps

Recommended backup run:

- Run ID: `1a900967f5`
- Scenario: `ED Surge`
- Fidelity: `78.97`
- Privacy: `100.0`
- Utility: `87.38`
- Synthetic rows: `17,010`
- ✅ Full agentic reasoning traces at all 5 agent steps

## 9. What Presenters Must Not Claim

Do not claim any of the following:

- that this replaces real Southlake data
- that this is ready for clinical or staffing decisions
- that synthetic data removes all privacy risk
- that a U.S. public-use dataset perfectly represents Ontario patterns
- that this is a finished enterprise platform

## 10. What Presenters Should Claim

These claims are defensible:

- the studio demonstrates a practical workflow for synthetic healthcare planning data
- the system is agentic because it plans, evaluates, and explains its work
- the prototype creates a safer sandbox for experimentation than touching real patient records
- the product is relevant to distributed-care planning, simulation, and innovation
- the next step would be governed validation with local data and privacy review
