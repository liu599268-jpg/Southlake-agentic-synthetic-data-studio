# Data Explainer — For Presenters

**Who this is for:** Zhou1, Zhou2, Huang — three presenters who need to speak confidently about the data behind our prototype. You do not need to memorize numbers. You need to understand the story and be able to answer follow-up questions.

Read this once before the pitch. Keep it open during Q&A prep.

---

## 1. The Source: NHAMCS 2022

### What it is

**NHAMCS** stands for the **National Hospital Ambulatory Medical Care Survey**. It is a national survey of emergency department and outpatient visits collected across the United States every year.

**Who runs it:** The **Centers for Disease Control and Prevention (CDC)** — specifically the **National Center for Health Statistics (NCHS)**, which is the U.S. government's principal health statistics agency.

**What it contains:** Records from emergency department visits across hundreds of hospitals. Each row is one patient visit, with information about timing, patient demographics, triage level, reason for visit, payer, and what happened at the end of the visit.

**Why it is public-use:** The CDC deliberately designs NHAMCS so that certain details are aggregated or suppressed before public release. The goal is to allow researchers, analysts, and educators to work with real emergency department patterns without exposing individual patients. The 2022 file was released publicly in July 2024.

**How big it is:** The full public-use file covers tens of thousands of ED visits nationally. Our curated subset — the version used in this project — contains **13,085 rows** and **21 columns**.

### Why we used it

- It is **freely available** from a credible government source, no approval needed
- It covers **emergency department operations** directly — the exact context Southlake cares about
- It is **national in scope**, meaning patterns like wait times, triage levels, and admission rates are meaningful benchmarks
- It allows us to **demonstrate the workflow** without touching any restricted health data

> **If a judge asks:** "Where does the data come from?" Say: "We use the 2022 NHAMCS emergency department public-use file, published by the CDC's National Center for Health Statistics. It is a federal public-use dataset released in July 2024. We chose it because it is credible, freely available, and directly relevant to ED operations."

---

## 2. Why Not Ontario Data

### The short answer

Ontario health data is **restricted**. We could not use it legally or responsibly in a hackathon prototype, even with the best intentions.

### What governs Ontario health data

**PHIPA** — the **Personal Health Information Protection Act** — is the provincial law that governs how personal health information can be collected, used, and disclosed in Ontario. Under PHIPA:

- Patient data can only be used for specific, approved purposes
- Access requires formal approval from health data custodians (like ICES, CIHI, or the hospital itself)
- Even de-identified or aggregated data requires a process review, because de-identification is not automatic or guaranteed

**The Ontario Wait Time Information System** (the provincial dataset closest to what we work with) is explicitly listed as **restricted** in the Ontario Data Catalogue. It is not available for general use.

### Why a hackathon changes the equation

A hackathon produces a prototype, not a production system. If we built our demo on restricted Ontario data:

- We would be using health data outside its approved purpose
- The team could face regulatory exposure under PHIPA
- The data could not be shared, reproduced, or demoed to judges
- We would not be able to publish, open-source, or continue the work post-hackathon

Using a U.S. public-use dataset lets us prove the **workflow and methodology** without any of those risks. The goal here is to show the system, not to claim we already have Southlake-calibrated data.

### What to say if pushed

> **"But Ontario data would be more relevant, right?"**
> "Yes, and that is the logical next step. Our prototype proves the workflow. The path to production would involve a governed data agreement with Southlake or a health data custodian to validate and localize the model with actual Ontario patterns."

> **"Did you consider using Ontario data for the demo?"**
> "We looked at it. The Ontario Wait Time dataset is explicitly restricted under the provincial data catalogue, and PHIPA sets a high bar for any use of personal health information. For a hackathon demo that needs to be shareable and reproducible, a CDC public-use file is the responsible choice."

> **"Isn't U.S. data too different from Ontario to be useful?"**
> "For the purposes of proving the agentic workflow — profiling, generating, evaluating, and presenting synthetic data — the geographic difference does not matter. The methodology is what we are demonstrating, not the specific numbers. We say this explicitly in our caution section."

---

## 3. The 21 Columns Explained

Each row in the dataset is one emergency department visit. Here is what each column captures.

### Timing

| Column | What it means |
|---|---|
| **visit_month** | The calendar month of the ED visit (e.g., "September") |
| **visit_day_of_week** | The day of the week the patient arrived (e.g., "Monday") |
| **arrival_hour** | The hour of the day the patient arrived, as a 24-hour number (e.g., 14 = 2 PM) |

### Flow and Duration

| Column | What it means |
|---|---|
| **wait_time_minutes** | How long the patient waited before being seen by a clinician |
| **length_of_visit_minutes** | The total time the patient spent in the ED from arrival to departure |
| **observation_minutes** | How many minutes the patient spent in an observation bed (0 if not placed in observation) |

### Patient Demographics

| Column | What it means |
|---|---|
| **age_years** | The patient's age in years |
| **sex** | The patient's recorded sex (Male, Female, or Unknown) |
| **race_ethnicity** | The patient's self-reported or recorded racial and ethnic category |

### Arrival and Acuity

| Column | What it means |
|---|---|
| **arrived_by_ambulance** | Whether the patient arrived by ambulance (Yes / No / Unknown) |
| **transfer_in** | Whether the patient was transferred in from another facility (Yes / No / Not applicable) |
| **triage_level** | How urgent the visit was, as assigned at triage (e.g., Emergent, Urgent, Semi-urgent, Non-urgent) |
| **pain_scale** | The patient's self-reported pain score from 0 to 10 (blank if not assessed) |
| **chronic_conditions_count** | How many chronic conditions the patient had on record at the time of the visit |

### Clinical and Administrative

| Column | What it means |
|---|---|
| **primary_reason** | The main reason the patient came to the ED, in plain language (e.g., "Chest pain", "Nausea") |
| **primary_payer** | How the patient's visit was expected to be paid for (e.g., Medicare, Private insurance, Self-pay) |

### Outcomes and Disposition

| Column | What it means |
|---|---|
| **admitted_inpatient** | Whether the patient was admitted to the hospital as an inpatient (Yes / No) |
| **admit_unit** | If admitted, which unit the patient was admitted to (e.g., ICU, General floor) |
| **left_against_advice** | Whether the patient left before completing their visit against medical advice (Yes / No) |
| **discharge_disposition** | The official recorded destination at the end of the visit (e.g., "Discharged to home", "Transferred to another facility") |
| **visit_outcome** | A simplified outcome category we derive from the other columns: **Home or community resolution**, **Inpatient admission**, **Observation pathway**, **Transfer / facility handoff**, or **Left before completion** |

> **If a judge asks about visit_outcome:** "That is a column we created ourselves by combining three other columns — admitted_inpatient, observation_minutes, and left_against_advice. It gives the AI agent a clean categorical outcome to use in scenario planning."

---

## 4. The Bootstrap Script

We did not download a spreadsheet off the internet. We wrote a **Python script** that does the following, in order:

1. **Downloads the raw CDC file** directly from the CDC FTP server — a Stata-format file (`.dta`) inside a zip archive
2. **Reads the coded numbers** — the raw NHAMCS file stores almost everything as numeric codes (e.g., `1` = Yes, `2` = No, `1` = January) with a separate label dictionary
3. **Translates the codes into human-readable labels** — using the value-label dictionary embedded in the Stata file, we convert every coded number into plain English
4. **Selects 21 operationally relevant columns** — out of the hundreds of variables in the full survey, we keep the ones that matter for ED operations and planning
5. **Cleans the data** — removes rows missing critical values, clips outliers, fills blanks with safe defaults like "Unknown" or "Not applicable"
6. **Derives the visit_outcome column** — applies a simple logic rule to classify each visit into one of five outcome categories
7. **Saves it as a CSV** — the final output is a clean, portable, human-readable file that loads into the app

The result is **13,085 rows × 21 columns**, stored at `data/presets/nhamcs_ed_2022_curated.csv`.

> **If a judge asks:** "How do we know the data is clean?" Say: "We built the cleaning into the bootstrap script itself. Rows with missing timing or age data are dropped. Values outside valid ranges are clipped. Coded fields are translated to labels using the CDC's own value dictionaries."

---

## 5. What "Sensitive Columns" Means

### What the app flags

When our agent profiles a dataset, it scans every column name for keywords that indicate potentially sensitive content. Nine of our 21 columns are flagged:

| Flagged Column | Reason |
|---|---|
| **age_years** | Contains "age" — a quasi-identifier |
| **sex** | Contains "sex" — a demographic attribute |
| **race_ethnicity** | Contains "race" and "ethnicity" — protected characteristics |
| **triage_level** | Contains "triage" — relates to clinical acuity |
| **arrived_by_ambulance** | Contains "ambulance" — can signal severity |
| **primary_reason** | Contains "reason" — clinical content |
| **primary_payer** | Contains "payer" — financial and insurance information |
| **admitted_inpatient** | Contains "admit" — clinical outcome |
| **admit_unit** | Contains "admit" — clinical destination |

### What the flag actually means

**Flagging is not blocking.** The app does not refuse to generate data for these columns. It means:

- The agent pays extra attention to these columns during synthesis, trying to preserve distribution shapes without copying exact row combinations
- The caution text shown to users explicitly calls out that these fields carry demographic and clinical identifiers
- The **privacy score** in the output reflects how well the synthetic data avoids producing rows that are too similar to specific real rows

### What to say during the demo

> "Our system flags nine columns as sensitive — things like age, sex, race, payer, and clinical outcomes. That flag changes how the synthesizer handles them and shows up in the caution notes we generate. We are not claiming these fields are safe; we are making the sensitivity visible so planners know what to watch."

> **If a judge asks about re-identification risk:** "The privacy metric we display measures exact row overlap between synthetic output and the source. In our best demo run, that score is 100 — meaning no synthetic row is an exact copy of any source row. That is a strong start, but we also say clearly that privacy scoring does not make synthetic data automatically safe for all uses."

---

## 6. The Southlake Connection

### What Southlake is becoming

Southlake Health is one of Ontario's fastest-growing health systems, serving Simcoe County and York Region. Their **2025–2034 strategic plan** is built around a single organizing idea: becoming a **Distributed Health Network**.

That means:
- Care is designed to happen **closer to where people live**, not only at the main Newmarket hospital campus
- New advanced-care campuses (like the planned Innisfil site) will handle some of what used to require a central hospital visit
- Programs like cardiac rehab have already expanded into communities like Georgina as proof of concept
- The organization needs to plan for **routing, capacity, and demand** across multiple sites, not just one building

### Why this creates a data problem

Planning for a distributed network means asking questions like:
- If we open a new campus in Innisfil, how many ED visits could be diverted there?
- What proportion of our observation patients could be handled in a community setting?
- What does chronic-condition load look like if regional population growth continues?
- How does ambulance routing change if there are two campuses instead of one?

These questions are **data-heavy**. But real Southlake patient data is protected and cannot be freely experimented on. Our product is the answer to that gap.

### How our four scenarios map to Southlake's strategy

| Scenario | Strategic Question It Addresses |
|---|---|
| **Distributed Campus Routing** | What does patient flow look like if care is split across multiple campuses? |
| **Community Diversion** | Which lower-acuity visits could move out of the ED into community settings? |
| **ED Surge** | How does the system behave under peak demand, and what buffers are needed? |
| **Regional Growth** | What does rising demand plus increasing chronic complexity look like over time? |

> **If a judge asks:** "Is this actually useful for Southlake?" Say: "Southlake's strategy explicitly names becoming a distributed health network. Each of our four scenarios maps directly to a planning question that distributed-network design forces you to answer. Our tool lets planners explore those scenarios without needing to pull real patient records."

---

## 7. Quick Reference Card

Use this during Q&A if you need to talk about any specific scenario quickly.

---

### Scenario 1 — ED Surge

**What it models:** A high-volume, high-pressure emergency department environment with more ambulance arrivals, longer waits, and more urgent triage cases than baseline.

**Who cares:** Operations leads, capacity planners, staffing teams who need to stress-test the system before a real surge event.

**What changes in the synthetic data:** Higher `arrived_by_ambulance` rate, longer `wait_time_minutes` and `length_of_visit_minutes`, higher proportion of Emergent and Urgent `triage_level` values.

> **One-line pitch:** "We simulate what the data looks like when volume spikes and pressure builds, so planners can think through capacity before the surge hits."

---

### Scenario 2 — Community Diversion

**What it models:** A future state where lower-acuity patients are routed away from the ED into community or primary care settings, reducing load on the main ED.

**Who cares:** Service design teams, community health planners, anyone working on the "closer to home" part of the Southlake strategy.

**What changes in the synthetic data:** Fewer Non-urgent and Semi-urgent visits, lower `chronic_conditions_count` among remaining ED patients, higher proportion of `visit_outcome = Home or community resolution`.

> **One-line pitch:** "We simulate a world where the ED handles only what the community cannot, which is exactly what a distributed health network is supposed to achieve."

---

### Scenario 3 — Regional Growth

**What it models:** Population growth in the region combined with increasing chronic disease burden, driving higher ED volume with more complex patients over a multi-year horizon.

**Who cares:** Strategic planners, capital planning teams, anyone making decisions about new facilities or program expansion over a 5–10 year horizon.

**What changes in the synthetic data:** More rows overall, higher average `age_years`, higher `chronic_conditions_count`, more `admitted_inpatient = Yes` outcomes.

> **One-line pitch:** "We simulate what the demand picture looks like if Simcoe County keeps growing and patients keep getting older, so planners can size capacity ahead of time."

---

### Scenario 4 — Distributed Campus Routing

**What it models:** A multi-site care model where patients are routed across campuses based on acuity and capacity, with more observation, transfer, and handoff activity than a single-hospital model.

**Who cares:** Network design teams, operations planners, anyone building the model for how Southlake's future campuses will divide and share work.

**What changes in the synthetic data:** Higher `observation_minutes`, more `transfer_in = Yes` and `discharge_disposition` values involving facility handoffs, more `visit_outcome = Observation pathway` or `Transfer / facility handoff`.

> **One-line pitch:** "This is the scenario most directly aligned with Southlake's 2025–2034 strategy — it models what patient flow looks like once you have multiple campuses working as one network."

---

## Appendix — Numbers to Know

If you get asked a specific data question:

| Fact | Value |
|---|---|
| Source dataset | CDC/NCHS NHAMCS 2022 Emergency Department Public-Use File |
| Released | July 2024 |
| Rows in our curated subset | 13,085 |
| Columns | 21 |
| Sensitive columns flagged | 9 |
| Governing Ontario privacy law | PHIPA (Personal Health Information Protection Act) |
| Ontario dataset we did NOT use | Ontario Wait Time Information System (restricted) |
| Best demo run scenario | Distributed Campus Routing (Run ID: 72c9c81912) |
| Best demo run fidelity | 81.54 |
| Best demo run privacy | 100.0 (zero exact row overlap) |
| Best demo run utility | 88.92 |

---

*Document prepared for Southlake Agentic Synthetic Data Studio — Ivey Recruitment Hackathon.*
