# Southlake Studio Frontend

Next.js frontend for the Southlake Agentic Synthetic Data Studio.

## Run

```bash
cd /Users/haoranliu/Desktop/southlake-agentic-synthetic-data/apps/web
npm run dev
```

The app expects the FastAPI backend at `http://127.0.0.1:8000` by default. Override it with `NEXT_PUBLIC_API_BASE_URL` in `.env.local` if needed.

## Build

```bash
npm run build
```

## Notes

- The page is intentionally demo-first: one screen, fast load, visible metrics, visible cautions.
- The UI reads from the API rather than embedding synthetic results statically.
