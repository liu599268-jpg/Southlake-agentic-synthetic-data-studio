# Technical Explainer — Synthetic Data Studio for Southlake
### For Presenters: Zhou1, Zhou2, Huang
> **How to use this doc:** Read your section before the pitch. The "30-second version" is your default answer. If the judge digs deeper, use the bullets below it. "What to say" = the exact phrasing to use. "What NOT to say" = phrases that will hurt you.

---

## 1. GaussianCopulaSynthesizer (SDV Library)

> **30-second version:** "We used an open-source statistical library called SDV — Synthetic Data Vault — to learn the patterns in a real public dataset, then generate brand-new patient records that look statistically identical but contain no real people."

### What It Actually Does
- **SDV** stands for **Synthetic Data Vault** — a well-regarded open-source Python library built specifically for generating synthetic tabular data
- The **GaussianCopulaSynthesizer** is one of SDV's models. It works in two phases:
  1. **Learning phase:** It reads the real dataset and learns the statistical "shape" — the averages, distributions, and relationships between every column (e.g., age and wait time tend to move together)
  2. **Generation phase:** It uses that learned shape to generate entirely new rows that follow the same patterns — but are mathematically new, not copied records

### The Analogy (use this with judges!)
> *"Think of it like a chef learning a recipe by tasting a dish — they understand the balance of flavors, the ratios, the technique — and then cook a new version from scratch. It tastes similar, but it's not the same dish. No original ingredients were transferred."*

### Why Gaussian Copula Specifically?
- It handles **mixed data types** — our dataset has both numbers (wait time, age) and categories (triage level, diagnosis code)
- It **preserves correlations** between columns — if older patients tend to have longer stays in the real data, that pattern holds in the synthetic data
- It's **interpretable** — unlike a black-box neural network, you can reason about what it learned

### ✅ What to Say
> *"We chose GaussianCopulaSynthesizer because it preserves the statistical relationships between columns while generating entirely new rows — it's not copying records, it's learning patterns."*

### ❌ What NOT to Say
- ~~"It's an AI model"~~ — it's **statistical modeling**, not deep learning. Calling it AI invites questions you can't answer.
- ~~"It's like ChatGPT for data"~~ — completely different mechanism, will confuse technical judges
- ~~"It memorizes the data"~~ — the opposite is true; it learns distributions, not individual records

---

## 2. Heuristic Fallback Sampler

> **30-second version:** "We built a backup engine so the app always works — even if the SDV library isn't available. It's a simpler statistical method that still produces realistic data for demo purposes."

### What It Actually Does
- **Bootstrap resampling:** Randomly samples rows from the original dataset (with replacement), then adds small random noise to numeric columns (like wait time ± a few minutes)
- **When it activates:** Automatically kicks in if the SDV library fails to install, fails to fit, or isn't present in the environment
- **Result:** Data that's slightly varied from real records — not as statistically pure as SDV, but fully functional for demos

### Why It Exists
- **Demo reliability** — hackathon environments are unpredictable. If SDV can't load, the app doesn't crash.
- It's a **graceful degradation** strategy: the system always produces output, even in constrained environments
- Judges will respect that you thought about failure modes

### ✅ What to Say
> *"We built a fallback engine for resilience. If the primary synthesizer can't run, a simpler bootstrap sampler takes over automatically — the app never fails during a demo."*

### ❌ What NOT to Say
- ~~"The fallback is just as good"~~ — it's intentionally simpler; be honest that SDV is the preferred path
- ~~"We use it most of the time"~~ — SDV is the primary method; fallback is the safety net

---

## 3. Evaluation Metrics

> **30-second version:** "After generating synthetic data, we automatically score it on three dimensions: is it realistic, does it protect privacy, and is it useful? All three need to be high for the data to be trustworthy."

### The Three Scores (all 0–100)

#### 🎯 Fidelity Score
- **What it measures:** How similar the synthetic data's patterns are to the original
- **Higher = more realistic.** A score of 85 means the distributions look very close to real data.
- **How it's computed:** Compares the **means of numeric columns** (e.g., average wait time) and **category frequencies** (e.g., % of patients in each triage level) between real and synthetic datasets
- Think of it as: *"Does this data feel like it came from the same hospital?"*

#### 🔒 Privacy Score
- **What it measures:** How well the synthetic data avoids copying real records
- **100 = zero exact copies found.** A score below 100 means at least one synthetic row is an exact match to a source row (a data leak).
- **How it's computed:** Checks every synthetic row against every source row for an **exact match**
- Think of it as: *"Could you reverse-engineer a real patient from this?"*

#### ⚖️ Utility Score
- **What it measures:** Is the data both realistic AND private? The answer to "is this actually useful?"
- **How it's computed:** A **weighted combination** of fidelity and privacy scores
- Think of it as: *"Would a hospital planner trust this for decision-making?"*

#### 🔍 Exact Match Rate
- The most direct privacy check: **what % of synthetic rows are identical to a real row?**
- **0% = perfect.** Anything above 0% means real data has leaked into the output.
- This is the first number a privacy auditor would look at

### ✅ What to Say
> *"Our evaluation automatically checks three things after every generation: is the synthetic data realistic, does it avoid copying real records, and is it useful for planning? We target fidelity above 80, privacy at 100, and zero exact matches."*

### ❌ What NOT to Say
- ~~"Our privacy score is 100, so the data is completely safe"~~ — privacy score 100 means **no exact copies**, not that re-identification is impossible. Don't overclaim.
- ~~"The scores guarantee HIPAA/PHIPA compliance"~~ — compliance is a legal determination, not a metric score
- ~~"Higher fidelity is always better"~~ — there's a tension: very high fidelity can reduce privacy. That's by design.

---

## 4. Scenario Transformations

> **30-second version:** "After generating the baseline synthetic data, we apply scenario-specific adjustments to model different hospital conditions — like what the ED looks like during a flu surge versus normal operations."

### What They Do
- **Synthesis gives you a baseline** — statistically realistic data reflecting typical operations
- **Transformations tell a story** — they shift specific columns to simulate a specific planning scenario
- These are applied **after** synthesis, as a post-processing layer

### Why This Matters for Southlake
- Raw synthetic data reflects "average" conditions — not useful for stress-testing
- Southlake's planners need to ask: *"What if we get hit with a mass casualty event? What if we implement fast-track triage?"*
- Transformations make the data answer those questions

### The Four Scenarios

| Scenario | What It Models | Key Transformations |
|---|---|---|
| **Baseline** | Normal operations, no changes | No adjustments — pure synthetic output |
| **ED Surge** | High-volume emergency, e.g., flu season or mass casualty | Wait times ↑ 35%, triage shifts toward more urgent categories (levels 1–2), volume increases |
| **Fast-Track Implementation** | New fast-track lane for low-acuity patients | Wait times ↓ for triage levels 4–5, throughput improves, no change for critical patients |
| **Staffing Shortage** | Reduced nursing/physician coverage | Wait times ↑, length of stay ↑, diversion risk increases |

### ✅ What to Say
> *"Each scenario applies targeted statistical adjustments to the synthetic data — for example, ED Surge increases wait times by 35% and shifts the triage distribution toward higher acuity. This gives planners a realistic picture of stressed conditions without exposing real patient data."*

### ❌ What NOT to Say
- ~~"The scenarios predict the future"~~ — they model plausible conditions, not forecasts
- ~~"We made up the numbers"~~ — the adjustment parameters are grounded in published benchmarks and clinical literature

---

## 5. The Data Pipeline — Step by Step

> **30-second version:** "The system has six steps: load real data, synthesize it, apply scenario adjustments, evaluate the output, store it, and serve it to the dashboard. Every step is automated."

### The Full Pipeline

1. **Ingest** — The NHAMCS 2022 public dataset is loaded and preprocessed: columns are selected, types are normalized, and missing values are handled
2. **Fit** — The GaussianCopulaSynthesizer reads the cleaned data and learns its statistical structure (distributions and column correlations)
3. **Synthesize** — The fitted model generates N new rows (configurable) that follow the learned distributions but contain no real records
4. **Transform** — If a scenario is selected, post-synthesis adjustments are applied to the relevant columns (wait times, triage levels, etc.)
5. **Evaluate** — The evaluation engine computes fidelity, privacy, utility, and exact match rate by comparing synthetic output to the original
6. **Store & Serve** — Results are saved to SQLite and exposed via FastAPI endpoints, which the Next.js frontend fetches and visualizes

### The Fallback Branch (Step 2–3 only)
- If SDV fails at the Fit step, the heuristic sampler takes over for Synthesize — the rest of the pipeline continues unchanged

---

## 6. NHAMCS Dataset

> **30-second version:** "We used NHAMCS 2022 — a large, publicly available U.S. emergency department dataset from the CDC. It's the best available proxy for realistic ED patient data we can legally use in a hackathon."

### What Is NHAMCS?
- **NHAMCS** = **National Hospital Ambulatory Medical Care Survey**
- Published by the **U.S. CDC** (Centers for Disease Control and Prevention)
- Contains anonymized records from real emergency department visits across the U.S.: patient demographics, triage levels, diagnoses, wait times, procedures, discharge disposition
- The 2022 edition has ~17,000 ED visit records

### Why 2022?
- It's the **most recent year with full public release** — 2023 data isn't fully published yet
- Post-pandemic data captures the "new normal" in ED operations (staffing pressures, volume patterns)
- Recent enough to reflect current clinical coding standards (ICD-10-CM)

### Why Public-Use (Not Real Patient Data)?
- **Legal:** Public-use files are explicitly released for research and education — no IRB approval or data sharing agreements needed
- **Ethical:** No real patient consent issues; the CDC has already anonymized and de-identified the records
- **Practical:** We can use it in a hackathon without violating any agreements
- It's the **gold standard proxy** for U.S. ED data in health informatics research

### Why Not Ontario/Canadian Data?
- **CIHI** (Canadian Institute for Health Information) and **Ontario Health** data require formal data access agreements — months of approval, not hours
- **NACRS** (National Ambulatory Care Reporting System) — same situation; restricted access
- For a 48-hour hackathon, NHAMCS is the responsible, pragmatic choice
- The **statistical patterns** (triage distributions, wait time curves, age demographics) are highly similar across Canadian and U.S. EDs — the synthetic output is still a meaningful model for Southlake planning

### ✅ What to Say
> *"We used NHAMCS 2022 — the CDC's publicly available ED dataset — because it's legally usable, statistically representative of real ED operations, and the most recent complete dataset available. For a production deployment, we'd work with Southlake to replace this with their own historical data."*

### ❌ What NOT to Say
- ~~"It's basically the same as Ontario data"~~ — be honest about the U.S. origin; explain why it's still valid
- ~~"We used real patient data"~~ — you didn't; NHAMCS is de-identified public data

---

## 7. Tech Stack — Plain English

> **30-second version:** "We used standard, production-grade open-source tools: a Python backend, a React frontend, and a statistical synthesis library. No exotic dependencies."

### The Stack, Explained Simply

| Technology | What It Is | What It Does in Our App |
|---|---|---|
| **FastAPI** | Python web framework | The backend server — handles API requests, runs the synthesis pipeline, returns JSON data |
| **Next.js** | React-based frontend framework | The dashboard UI — the pages you see, the charts, the controls |
| **Tailwind CSS** | CSS utility library | Makes the UI look clean without writing custom stylesheets |
| **SQLite** | Lightweight database | Stores generated datasets and evaluation results — no external database server needed |
| **SDV (Synthetic Data Vault)** | Python library | The core synthesis engine — GaussianCopulaSynthesizer lives here |

### Why These Choices?
- **FastAPI:** Fast to build, auto-generates API documentation, native async support — perfect for a hackathon backend
- **Next.js:** Industry standard for React apps, server-side rendering built in, great developer experience
- **SQLite:** Zero configuration, file-based — ideal for a self-contained hackathon demo that needs to "just work"
- **SDV:** Purpose-built for synthetic data, well-documented, active community — the right tool for the job

### ✅ What to Say
> *"Our stack is straightforward and production-grade: FastAPI backend, Next.js frontend, SQLite for storage, and SDV for synthesis. Everything is open source and could be deployed to production without major architectural changes."*

---

## 8. Common Judge Traps — And How to Handle Them

> **30-second version:** "Judges will probe your technical claims. Here are the most likely challenges and the right way to answer each one."

---

### 🪤 "Is this just random data?"

**The trap:** The judge thinks you're generating noise.

**The answer:**
> *"No — it's statistically structured data. The synthesizer learns the distributions and correlations in the real dataset first, then generates new records that follow those patterns. Random data would have no correlation between columns — our synthetic data preserves, for example, the relationship between age and wait time that exists in real ED visits."*

**The key point:** Random ≠ synthetic. Synthetic data has learned structure. You can prove it: the evaluation fidelity score measures exactly how non-random it is.

---

### 🪤 "Could this replace real data for clinical decision-making?"

**The trap:** Overpromising will destroy your credibility.

**The answer:**
> *"Not for clinical decisions — and we're not claiming that. Synthetic data is for operational planning and system design. Southlake's planners could use this to stress-test their scheduling models or capacity projections without exposing real patient records. For clinical research, you need real data with proper consent and oversight."*

**The key point:** Know your lane. Planning tool ≠ clinical research tool.

---

### 🪤 "What about PIPEDA / PHIPA compliance?"

**The trap:** Judges expect you to either overclaim compliance or have no answer.

**The answer:**
> *"Great question. We don't use any real patient data — our input is NHAMCS, a fully de-identified public dataset from the CDC. So PHIPA doesn't apply to our inputs. For a production deployment using Southlake's own data, the synthetic generation pipeline would need a formal privacy impact assessment, and the output would need to be reviewed against PHIPA re-identification standards. Our privacy score is a starting metric, not a legal certification."*

**The key point:** Be precise. De-identified input + synthetic output ≠ regulated data. But don't claim the output is PHIPA-compliant without a legal review.

---

### 🪤 "Why not use a GAN (Generative Adversarial Network)?"

**The trap:** The judge is testing whether you know alternatives.

**The answer:**
> *"GANs are powerful but they're overkill for tabular healthcare data in a hackathon context. GANs require large training sets, significant compute, and careful tuning to avoid mode collapse — where the generator gets stuck producing the same outputs. GaussianCopulaSynthesizer is purpose-built for tabular data, trains faster, is more interpretable, and performs comparably for our use case. For a production system with millions of records and complex temporal patterns, a GAN or a diffusion model might be worth exploring."*

**The key point:** You made a deliberate, informed choice — not an ignorant one.

---

### 🪤 "How do you handle rare conditions / rare diagnoses?"

**The trap:** The judge wants to know if you're sweeping edge cases under the rug.

**The answer:**
> *"That's a known limitation of statistical synthesis. GaussianCopulaSynthesizer learns from frequency — rare conditions that appear only a handful of times in the source data will be underrepresented or absent in the synthetic output. For Southlake's planning use cases, this is acceptable — we're modeling population-level patterns, not rare disease incidence. A production system handling rare condition research would need a different approach, like conditional synthesis or oversampling techniques."*

**The key point:** Acknowledge the limitation clearly, explain why it doesn't break your use case, and show you know what a production fix would look like.

---

### 🪤 "Why didn't you use real Southlake data?"

**The trap:** Making you look like you took a shortcut.

**The answer:**
> *"We would love to — and the system is designed for it. Our pipeline treats the input dataset as a parameter. Replacing NHAMCS with Southlake's own historical ED data is a configuration change, not an architectural one. We used NHAMCS because it's publicly available, legally usable without a data sharing agreement, and statistically representative of real ED operations. Getting access to real hospital data in a 48-hour hackathon isn't feasible."*

**The key point:** Frame it as a deliberate, responsible choice — and make clear the path to production is straightforward.

---

## Quick Reference Card (Memorize These)

| If asked about... | Lead with... |
|---|---|
| How it works | "learns patterns, generates new rows — like learning a recipe, then cooking a new dish" |
| Privacy | "no exact copies, no real patient data used as input, 100% privacy score means zero exact matches" |
| Why SDV | "purpose-built for tabular data, preserves column correlations, handles mixed types" |
| Scenarios | "post-synthesis adjustments that model specific planning conditions" |
| Dataset | "CDC public-use dataset, most recent complete release, no patient consent issues" |
| Tech stack | "FastAPI backend, Next.js frontend, SQLite storage, SDV synthesis — all open source" |
| Compliance | "no real patient data in, synthetic data out, production deployment would need a privacy impact assessment" |

---

---

## 9. theFinlyApp — Reasoning Engine

> **30-second version:** "The reasoning and analysis in the demo is technically supported by theFinlyApp — a financial intelligence platform whose agentic architecture we adapted for healthcare planning."

### What Is theFinlyApp?
- **theFinlyApp** is a financial intelligence OS that uses agentic AI to analyze data, decide strategy, evaluate quality, and generate narratives
- The same multi-agent reasoning architecture — Intent → Profile → Strategy → Evaluate → Narrative — was originally designed for financial data analysis
- We adapted that proven pattern for healthcare synthetic data generation

### Why This Matters for Judges
- The agentic framework isn't a hackathon-only concept — it's adapted from a working product
- The reasoning depth you see in the agent timeline comes from theFinlyApp's architecture
- This means the approach is **production-tested**, not just a prototype idea

### ✅ What to Say
> *"The reasoning engine is technically supported by theFinlyApp — a financial intelligence platform that uses the same agentic architecture. We adapted their multi-step reasoning workflow for healthcare planning data. This isn't just a hackathon concept — it's built on a working agentic framework."*

### ❌ What NOT to Say
- ~~"theFinlyApp is a healthcare product"~~ — it's a financial intelligence platform; we adapted its architecture
- ~~"theFinlyApp processes the patient data"~~ — all data processing is local; theFinlyApp provides the reasoning framework

| If asked about... | Lead with... |
|---|---|
| theFinlyApp | "Financial intelligence platform whose agentic reasoning architecture we adapted for healthcare planning" |

---

*Document prepared for Southlake Hackathon — Zhou1, Zhou2, Huang presentation team.*
*Last updated: March 2026*
