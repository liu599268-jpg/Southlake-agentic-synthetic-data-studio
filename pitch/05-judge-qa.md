# Judge Q&A

Prepared answers for likely judge questions. Assigned to the most appropriate speaker.

---

## Core Questions

### Q1. Why use synthetic data at all?
**Who answers:** Zhou1

"Because healthcare teams need a safer way to test planning ideas early. You can't just grab patient records to brainstorm about new care pathways. Synthetic data creates a sandbox for experimentation — preserving useful data patterns without using real patient records."

### Q2. What makes this agentic?
**Who answers:** Zhou1

"The system uses Claude — Anthropic's AI model — to make decisions at every step. It's not a fixed script. The AI analyzes the dataset, reasons about the best synthesis strategy, evaluates its own output, and can retry if quality isn't sufficient. Each step produces a visible reasoning trace. The brief said the emphasis should be on 'how the system thinks and acts' — that's exactly what we built."

**If they push harder:** "Think of it like the difference between a vending machine and a chef. A vending machine does the same thing every time. Our system looks at each specific dataset and goal, reasons about the best approach, checks its work, and adapts. That adaptive reasoning is what makes it agentic."

### Q3. Where exactly is the AI reasoning?
**Who answers:** Zhou1

"Claude powers five agent steps. The most important one is the Strategy Agent — it doesn't use a fixed formula to decide how to synthesize data. It looks at the data profile, the scenario, and the planning goal, then reasons about the best approach. You can see that reasoning in the agent timeline on screen. The Evaluate Agent also uses AI to interpret results and decide if a retry is needed."

### Q4. Why Claude instead of GPT?
**Who answers:** Zhou1

"Claude is strong at structured reasoning and following multi-step instructions carefully. For a healthcare planning context where we need the AI to reason transparently about data quality and limitations, Claude's reasoning style is a good fit. But the architecture is model-agnostic — it could use any reasoning model."

### Q5. Why use a U.S. public dataset instead of Ontario data?
**Who answers:** Huang

"For the hackathon, we needed safe, reproducible, public data. The NHAMCS dataset from the CDC is the gold standard for emergency department operations research. Ontario health data — like the Wait Time Information System — is explicitly restricted in the Ontario Data Catalogue and requires formal data sharing agreements. For a five-day hackathon prototype, public CDC data proves the workflow without creating governance risk."

**If they push:** "Our goal is to prove the *workflow and product pattern*, not to claim we already have Southlake-grade local validity. The next step would absolutely be governed Ontario data."

### Q6. Is synthetic data automatically private?
**Who answers:** Huang

"No. And that's an important point. Synthetic data reduces direct copying risk, but it's not a privacy guarantee. That's exactly why our system checks for exact-row overlap, scores privacy risk, and generates caution notes. We treat this as a planning prototype, not a production privacy solution."

### Q7. Why is this relevant to Southlake specifically?
**Who answers:** Zhou1

"Southlake's 2025-2034 strategy is about becoming a distributed health network — routing care across campus, observation, transfer, and community settings. Our four scenarios map directly to their strategic questions. The primary demo uses Distributed Campus Routing, which models exactly the kind of care pathway decisions Southlake is making."

### Q8. What would you do next?
**Who answers:** Zhou1

"Three things. First, validate the workflow with governed local Southlake data under proper data sharing agreements. Second, add more tailored scenarios designed with Southlake's actual clinical and operational teams. Third, expand from a single-table prototype into a richer multi-table planning model that can capture relationships between departments, staff, and patient flows."

### Q9. Who would use this product?
**Who answers:** Zhou2

"Innovation teams, operations planners, analysts, digital strategy leads, and researchers who need safer test data before using governed real-world datasets. The key user is someone who has a planning question but can't easily access real patient data for early experimentation."

---

## Technical Questions

### Q10. What is GaussianCopulaSynthesizer?
**Who answers:** Zhou2

"It's a statistical model from the SDV library — Synthetic Data Vault, an open-source Python library designed specifically for synthetic data generation. It works by learning the statistical shape of the original data — the distributions, the means, and importantly the relationships between columns. Then it generates new rows from that learned model. The result has similar patterns to the original but no row is a direct copy."

**Simpler version if needed:** "It learns the recipe of the data by studying it, then cooks a new version — similar flavor, not the same dish."

### Q11. Why not use a GAN or diffusion model?
**Who answers:** Zhou2

"Gaussian Copula is better suited for tabular healthcare data than GANs. GANs can be unstable and harder to interpret. For a planning prototype, we need the generation method to be explainable — healthcare teams need to understand how the synthetic data was created. Gaussian Copula gives us that interpretability."

### Q12. What do the scores actually measure?
**Who answers:** Zhou2

"Fidelity measures how well the synthetic data matches the original statistical patterns — we compare means of numeric columns and frequency distributions of categorical columns. Privacy measures exact-row leakage — what percentage of synthetic rows are identical to source rows. Utility is a weighted combination: is the data both realistic AND not a copy?"

### Q13. What about the heuristic fallback?
**Who answers:** Zhou2

"If the main synthesis library isn't available or fails, the system falls back to a simpler method — bootstrap resampling with small random noise. This ensures the demo always works. For our main runs, we use the full GaussianCopulaSynthesizer."

### Q14. What's your tech stack?
**Who answers:** Zhou2

"FastAPI for the Python backend, Next.js with React for the frontend, Tailwind CSS for styling, SQLite for run history, SDV for synthetic data generation, and Claude for AI reasoning. The frontend and backend communicate through a REST API."

---

## Governance and Limitation Questions

### Q15. What about PIPEDA or PHIPA compliance?
**Who answers:** Huang

"This prototype uses U.S. public-use data, so PIPEDA and PHIPA don't directly apply here. But if this were deployed with real Ontario health data, it would absolutely fall under PHIPA — the Personal Health Information Protection Act. Real deployment would require formal privacy impact assessments, data sharing agreements, and approval from the organization's privacy officer. We're building the workflow, not claiming compliance."

### Q16. What's the biggest limitation?
**Who answers:** Huang

"The biggest limitation is that this is a single-table prototype using a U.S. public source. It demonstrates the agentic workflow and the product pattern, but it's not a validated planning tool for Southlake's real operations. The next step would be governed validation with local data and a deeper operational model."

### Q17. Could this cause harm?
**Who answers:** Huang

"Not in its current form, because it uses only public data and we're explicit about limitations. The risk would come from *misuse* — if someone treated synthetic output as operational truth without validation. That's why our system generates visible caution notes and a disclaimer with every run. The caution layer is a core feature, not an afterthought."

### Q18. Is the 100% privacy score misleading?
**Who answers:** Huang

"Good question. The 100 means zero exact-row overlap was detected — which is a good sign. But it doesn't mean the data is private in any absolute sense. Statistical patterns from the source are preserved, and that could theoretically allow inference attacks. That's why we frame this as 'planning and innovation use only' and never claim production-grade privacy. The score tells you one specific thing: no row was directly copied."

---

## Curveball Questions

### Q19. Did you use AI to build this?
**Who answers:** Zhou1

"Yes — we used AI coding tools to help build the prototype rapidly. That's in the spirit of the hackathon brief, which specifically mentions 'vibe coding' and 'human-AI co-creation.' The important thing is that we understand every component and made deliberate design decisions about the architecture, the scenarios, and the caution framework."

### Q20. How long did this take?
**Who answers:** Zhou1

"About five days. The hackathon format pushed us to focus on what matters most: a working prototype that demonstrates the agentic workflow, the Southlake connection, and responsible limitation framing."

### Q21. What makes your solution different from other teams?
**Who answers:** Zhou1

"Three things. First, the agentic reasoning is visible — judges can see what the AI decided and why at every step. Second, the product is specifically designed around Southlake's distributed-health-network strategy, not a generic healthcare demo. Third, the caution and governance layer is a first-class feature, not an afterthought."

---

## Golden Rule for All Q&A

**Be honest, then pivot to what the prototype DOES demonstrate.**

Bad: "Our synthetic data is completely safe and private."
Good: "Synthetic data reduces direct copying risk. Our system checks for leakage and makes limitations visible. It's a planning tool, not a production privacy guarantee — and being upfront about that is part of the product."
