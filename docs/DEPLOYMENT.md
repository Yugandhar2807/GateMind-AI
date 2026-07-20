# Deploying GateMind AI to Render (one public URL)

One **Docker web service** on Render serves both the React frontend and the FastAPI API from the
same origin, using your existing **Neon** Postgres. You get a single URL like
`https://gatemind-ai.onrender.com` usable from any machine — your login and data are the same
everywhere (they live in Neon, not on any one computer).

## What's in the repo for this
- `Dockerfile` — builds the frontend (Node) and serves it from FastAPI (Python) at `/`, API at `/api`.
- `render.yaml` — Render Blueprint (one web service, health check, env vars).
- `app/main.py` serves the built SPA from `backend/static` when present (prod); local dev is unaffected.

## One-time setup on Render
1. **New → Blueprint** → connect the GitHub repo **Yugandhar2807/GateMind-AI** → select branch
   `main`. Render reads `render.yaml` and proposes the `gatemind-ai` web service. Apply.
   *(Or: New → Web Service → same repo → Render auto-detects the Dockerfile.)*
2. Open the service → **Environment** → add the two secrets (copy the values from your local
   `backend/.env`, they are NOT in git):
   - `DATABASE_URL` = your Neon **pooled** connection string
     (`postgresql://…-pooler.…neon.tech/neondb?sslmode=require`)
   - `JWT_SECRET_KEY` = the value from `backend/.env` (or any new 64+ char secret)
   The rest (`APP_ENV`, `CORS_ORIGINS`, `GATE_EXAM_DATE`) come from `render.yaml`.
3. **Create / Deploy.** First build takes a few minutes (Node build + pip install). The container
   runs `alembic upgrade head` on start, so the schema is applied automatically.
4. Open the service URL. Register/login — it's the **same Neon DB** as local, so your account works.

## Notes
- **Free plan** sleeps after ~15 min idle and cold-starts (~30–60s) on the next request. Fine for
  personal daily use; upgrade the service to avoid sleeping.
- Auto-deploy is on: pushing to `main` redeploys.
- Data lives in Neon (cloud), so it persists across machines/redeploys.
- The AI Mentor stays local-dev-only (needs Ollama); the deployed app runs everything else.
- Photo uploads use the container's ephemeral disk on Render — wire Cloudinary before relying on
  persistent uploads (schema is ready).

## Alternative (Vercel frontend + Render backend)
If you prefer split hosting later: deploy `frontend/` to Vercel (build `npm run build`, output
`dist`, env `VITE_API_URL=<backend-url>`), deploy `backend/` to Render, and set the backend
`CORS_ORIGINS` to the Vercel URL. The single-service Docker path above is simpler for one URL.
