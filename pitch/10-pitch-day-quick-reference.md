# Pitch-Day Quick Reference

Use this as the one-page operating sheet on pitch day.

## Local URLs

- App: `http://127.0.0.1:3100`
- API: `http://127.0.0.1:8000`

## Startup Commands

### Backend

```bash
cd /Users/haoranliu/Desktop/southlake-agentic-synthetic-data
source .venv/bin/activate
uvicorn --app-dir services/synth-api app.main:app --host 127.0.0.1 --port 8000
```

### Frontend

```bash
cd /Users/haoranliu/Desktop/southlake-agentic-synthetic-data/apps/web
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000 npm run dev -- --hostname 127.0.0.1 --port 3100
```

## Primary Demo

- Action: click `Load recommended demo run`
- Run ID: `72c9c81912`
- Scenario: `Distributed Campus Routing`
- Fidelity: `81.54`
- Privacy: `100.0`
- Utility: `88.92`

## Backup Demo

- Run ID: `fc0b94e404`
- Scenario: `ED Surge`
- Fidelity: `78.97`
- Privacy: `100.0`
- Utility: `87.38`

## Three Core Claims

- This is an agentic planning studio — Claude reasons at every step, doesn't follow a fixed script.
- The product is relevant to Southlake because it is built around distributed-health-network routing and closer-to-home care questions.
- The value is not only synthetic data generation. The value is AI-powered reasoning plus evaluation plus self-correction plus exportable planning artifacts.

## Three Things Not To Claim

- Do not say this is validated on Southlake data.
- Do not say synthetic data is automatically private or production-safe.
- Do not say this is ready for staffing, reimbursement, or patient-level decisions.

## Fast Recovery Path

If the live app becomes unreliable:

1. Open `pitch/assets/full-run-page.png`
2. Open `pitch/assets/demo-walkthrough.webm`
3. Open `pitch/latest_summary.md`
4. Continue the pitch without apologizing for long

## Files To Keep Open

- `pitch/Southlake-Agentic-Synthetic-Data-Studio-Deck.pptx`
- `pitch/Southlake-Agentic-Synthetic-Data-Studio-Deck.pdf`
- `pitch/assets/full-run-page.png`
- `pitch/assets/demo-walkthrough.webm`
- `pitch/05-judge-qa.md`
- `pitch/11-source-citations.md`

## Best Closing Line

"Our core argument is simple: agentic synthetic data can help health systems test future-state ideas earlier, faster, and more safely. For Southlake, that means a practical first step toward distributed-network experimentation without touching real patient records."
