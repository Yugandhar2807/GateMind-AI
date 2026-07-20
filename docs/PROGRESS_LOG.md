# GateMind AI — Build Progress Log

Dev-side build log for the production-SaaS rebuild. (Distinct from the study-content
`GATE-DA-2027/PROGRESS_LOG.md`, which is domain data to be ingested, not a dev log.)

Architecture: React (Vercel) → FastAPI (Render) → **Neon PostgreSQL** + Cloudinary + Ollama(dev).
See `docs/DATABASE.md` for the schema. Plan of record: 13 phases.

---

## 2026-07-20 — Phase 0: Recovery & baseline
- Put the migrated codebase under version control (was 0 commits). Corrected git author to
  `Yugandhar <nunnayugandhar2807@gmail.com>` (was the machine's global `rahul` identity); remote
  `origin → github.com/Yugandhar2807/GateMind-AI` (push pending user `gh auth login`).
- Rebuilt the backend Python venv (Python 3.12) — the migrated venv was non-portable.
- Confirmed the local MySQL stack was never present on this machine → clean pivot to cloud Postgres.

## 2026-07-20 — Phase 2: Ran existing GATE-DA-2027 site
- Confirmed static (self-contained `master_report.html` + Markdown). Served at
  `http://localhost:8080/master_report.html`.

## 2026-07-20 — Phase 3: Architecture redesign (approved)
- Decisions locked: Neon Postgres · Cloudinary storage · greenfield UUID v2 schema ·
  AI Mentor = local Ollama (dev only, behind an `LLMProvider` interface; hosted provider deferred).

## 2026-07-20 — Phase 4: Database design ✅
**Why:** move off local MySQL to a production, multi-user, cloud Postgres foundation.
**What changed (backend):**
- `app/core/config.py` → single `DATABASE_URL` (normalised to `postgresql+psycopg://`); added
  Cloudinary/OAuth placeholders.
- `app/db/base_class.py` → UUID `Base` + `created_at/updated_at`, `SoftDeleteMixin`, `enum_col`
  helper, deterministic naming convention.
- `app/db/session.py` → psycopg engine tuned for Neon's pooler.
- `app/models/` → **greenfield 30-table UUID schema** across `user`, `curriculum`, `content`,
  `progress`, `activity` (+ extended `enums`). Old MySQL integer-PK models retired.
- Alembic baseline `500dd9cec4a9_uuid_v2_baseline` generated and **applied to Neon** (30 tables live).
- `requirements.txt` → `pymysql` → `psycopg[binary]`.
- `app/api/v1/router.py` reduced to empty; `/api/health` only. **Legacy feature layer**
  (`services/`, `repositories/`, `schemas/`, `api/v1/routers/*`) retained on disk as reference and
  rewritten on the new schema in Phases 5–12 (not wired into the app yet).
**Verified:** models import + mappers configure (30 tables); `alembic upgrade head` on Neon;
`uvicorn` boots; `GET /api/health` → ok.

**Next:** Phase 5 — Authentication (email/password + JWT + refresh rotation; OAuth scaffold).
