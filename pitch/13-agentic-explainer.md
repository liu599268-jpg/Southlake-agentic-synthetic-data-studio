# Agentic Architecture Explainer

This document helps Zhou1, Zhou2, and Huang explain **why this system is agentic** confidently and honestly to judges. This is the #1 question you will be asked.

---

## The 30-Second Answer

If a judge asks "What makes this agentic?", say:

> "Our system doesn't just run a fixed script. It uses Claude — an AI reasoning model — to make decisions at each step. The AI analyzes the dataset, decides how to synthesize it, evaluates its own output, and if the quality isn't good enough, it reasons about why and tries again. Each step produces a visible reasoning trace so you can see what the system thought and why."

That's the core claim. Everything below supports it.

---

## What "Agentic" Actually Means

### The Simple Version

A regular program follows fixed instructions: "do step 1, then step 2, then step 3."

An **agentic** system has an AI that **thinks, decides, and adapts**:
- It looks at the data and **decides** what to do (not just follows a recipe)
- It checks its own work and **adjusts** if something isn't right
- It **explains** its reasoning so a human can understand and trust it

### The Analogy

Think of the difference between a vending machine and a chef:
- A **vending machine** (regular pipeline): you press B4, you get chips. Same input, same output, every time. No thinking.
- A **chef** (agentic system): you say "I want something healthy for lunch." The chef looks at what ingredients are available, considers your preferences, makes a plan, cooks it, tastes it, adjusts the seasoning, and explains what they made and why.

Our system is the chef. It looks at the data, reasons about what synthesis approach fits best, generates the output, checks if it's good, and explains its work.

---

## The Five Agent Steps — What Each One ACTUALLY Does

### 1. Intent Agent
**What it does:** Takes the user's goal and stakeholder choice, and uses Claude to frame it as a specific planning question.

**What to say:** "The Intent Agent doesn't just store a string — it uses AI reasoning to translate the user's goal into a structured planning frame that shapes every downstream decision."

**Example reasoning trace:** *"The user wants to test distributed-campus routing for a network operations team. This means I should emphasize disposition pathways, observation demand, and transfer patterns rather than raw volume metrics."*

### 2. Profile Agent
**What it does:** Analyzes the dataset and uses Claude to identify what's important — not just row counts, but which columns matter most for the planning question, what's missing, and what could be sensitive.

**What to say:** "The Profile Agent doesn't just count rows. It reasons about data quality, identifies which columns are most relevant to the planning question, and flags potential issues before synthesis begins."

### 3. Strategy Agent (previously "Plan Agent")
**What it does:** This is the key agentic step. Claude looks at the data profile, the scenario, and the planning goal, then **decides**:
- How many rows to generate
- Which synthesis approach is best for this specific dataset
- What constraints to apply
- What to watch for during evaluation

**What to say:** "The Strategy Agent is where the real AI decision-making happens. It doesn't use a fixed formula — it reasons about the best approach for each specific run based on the data characteristics and the planning question."

**Why this matters for judges:** This is the difference between "agentic" and "scripted." The system adapts its strategy based on what it sees.

### 4. Evaluate Agent
**What it does:** After synthesis, Claude evaluates the output — not just computing metrics, but **interpreting** them. If fidelity is low, it reasons about why. If there's leakage risk, it explains what to do about it.

**Critical agentic behavior:** If the evaluation shows quality below threshold, the system can **retry with adjusted parameters**. This is a reasoning loop — the agent checks its own work and self-corrects.

**What to say:** "The Evaluate Agent doesn't just compute a score. It interprets the results, explains what they mean for the planning question, and can trigger a retry if the quality isn't sufficient."

### 5. Narrative Agent (previously "Pitch Agent")
**What it does:** Claude takes all the context from previous steps and writes planning-grade methodology, feature, and caution summaries tailored to the specific scenario and audience.

**What to say:** "The Narrative Agent synthesizes everything into plain-English planning output. It's not template-based — it adapts the language to the scenario, the stakeholder, and the evaluation results."

---

## How To Handle "Is This Really An Agent?"

This is the question that can make or break you. Here are the responses:

### If a judge says: "This looks like a regular pipeline with AI labels"

**Say:** "I understand why it might look that way at first. The key difference is what happens between the steps. In a fixed pipeline, step 2 always does the same thing regardless of step 1's output. In our system, Claude reasons about the output of each step to decide what to do next. The Strategy Agent doesn't use a formula — it reasons about the data profile to choose an approach. The Evaluate Agent can trigger retries. Each step produces a reasoning trace you can inspect."

### If a judge says: "Where's the reasoning loop?"

**Say:** "The evaluation step is our reasoning loop. After synthesis, the system evaluates quality. If fidelity is below threshold or leakage risk is too high, it adjusts parameters and re-runs. You can see this in the agent timeline — each step shows what the AI reasoned and decided."

### If a judge says: "How is this different from just calling an API?"

**Say:** "An API call is one request, one response. Our system makes multiple connected decisions where each step's reasoning influences the next. The Intent Agent's framing shapes the Strategy Agent's choices. The Profile Agent's findings constrain what the Strategy Agent can do. The Evaluate Agent can send the whole thing back for another round. That's what makes it agentic — connected reasoning across steps, not isolated calls."

### If a judge says: "Why not use LangChain or AutoGen?"

**Say:** "We considered agent frameworks, but for a healthcare planning prototype, we wanted full transparency over every reasoning step. Frameworks add abstraction that makes it harder to audit what the AI decided and why. In healthcare, being able to explain every decision matters more than using the trendiest framework."

---

## The Hackathon Brief Connection

The brief says: *"Your service should behave like a smart, goal-driven agent. The emphasis is on how the system thinks and acts, not just the data it produces."*

Map this directly:
- **"Smart"** → Claude reasons at each step, doesn't follow fixed rules
- **"Goal-driven"** → The planning goal shapes every decision from intent framing through evaluation
- **"How the system thinks"** → Visible reasoning traces at each agent step
- **"How it acts"** → Adaptive strategy selection, self-evaluation, retry capability
- **"Not just the data it produces"** → The explanation, caution, and narrative layer is as important as the synthetic rows

### What to say in the opening:

> "We took the brief's emphasis on 'how the system thinks and acts' seriously. Our studio doesn't just generate synthetic rows — it reasons about what to generate, evaluates its own work, and produces visible explanations at every step. The data is important, but the thinking is what makes this agentic."

---

## Visible Reasoning — What Judges Will See

When judges look at a completed run, they'll see an **Agent Timeline** showing 5 steps. Each step has:
- **Agent name** (Intent, Profile, Strategy, Evaluate, Narrative)
- **Summary** of what the agent decided
- **Status** (completed, or retried if quality was insufficient)

The reasoning traces show the AI's actual thought process — not generic descriptions, but specific reasoning about THIS dataset, THIS scenario, THIS planning question.

**Example of what a judge sees:**

> **Strategy Agent:** "Given the 13,085-row ED dataset with 21 columns and moderate missingness in pain_scale (42%), I'm selecting GaussianCopulaSynthesizer as the primary method because the dataset has sufficient size and mixed types. Target: 13,085 rows to match source volume for the distributed campus routing scenario. Key watch: the high missingness in pain_scale and the categorical dominance in visit_outcome may need post-synthesis adjustment."

That's what makes this convincingly agentic — the AI is clearly reasoning about the specific situation, not running a template.

---

## Quick Reference Card

| Question | Answer |
|----------|--------|
| What makes this agentic? | AI reasons and decides at each step, doesn't follow fixed rules |
| Where's the AI? | Claude (Anthropic) powers the reasoning at every agent step |
| Can it self-correct? | Yes — evaluation can trigger retries with adjusted parameters |
| Why not LangChain? | Transparency over abstraction — healthcare needs auditable reasoning |
| What's the reasoning loop? | Evaluate → below threshold → adjust → retry → re-evaluate |
| How is this different from a script? | Scripts do the same thing every time. This adapts to each dataset and goal |

---

## Speaker Assignment for This Topic

**Zhou1** (strongest speaker) should handle the agentic explanation in the opening and Slide 1 walkthrough. The "vending machine vs chef" analogy is your anchor — use it early, then point to the reasoning traces as proof.

**Huang** should handle the "What it's NOT" part during Slide 3 (Cautions). Being honest about limitations actually strengthens the agentic claim — it shows the team understands what "agentic" means and isn't overselling.
