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

## 2026-07-20 — Phase 5: Authentication ✅
**Why:** stand up multi-user auth on the new schema so all later data is per-user and persistent.
**What changed (backend, reused/reworked from the legacy auth layer):**
- `core/security.py` → added `hash_token` (refresh tokens are stored hashed, never raw).
- `schemas/user.py` → `id` is now `UUID`; added `timezone`/`email_verified`.
- `repositories/base.py` → `get()` accepts UUID; `update()` sets provided keys (allows clearing).
- `services/auth_service.py` → register/authenticate + **refresh-token rotation** (persist hashed
  tokens in `refresh_tokens`, single-use, reuse ⇒ 401) + **OAuth get-or-create scaffold**
  (`auth_identities`).
- `api/v1/deps.py` → `get_current_user` parses UUID subject.
- `routers/auth.py` → `/register /login /refresh /logout`; `routers/users.py` → `/me` GET/PATCH +
  local photo upload (Cloudinary swap later). Wired both into `api/v1/router.py`.
- **Frontend:** `types/user.ts` `id: number → string` (UUID). `tsc -b` clean.
**Verified end-to-end on Neon:** register→409 dup / 401 wrong-pass / login / `/me` 200 / no-token 401 /
refresh rotate / **old-refresh reuse ⇒ 401** / PATCH profile 200. Test user cleaned up.

## 2026-07-20 — Phase 7: Content ingestion + Roadmap Engine ✅
**Why:** normalize the GATE-DA-2027 research into Postgres (single source of truth) and drive the
roadmap dynamically from the DB — no syllabus hardcoded in the frontend.
**Content (scripts/seed_content.py + seed_topic_resources.py, reusing scripts/seed_data/research/*):**
- **10 subjects, 103 topics** (difficulty/importance/pyq-frequency, derived estimated hours +
  revision cadence), **35 prerequisite edges** (dependency graph), **134 resources** (81 subject-wide
  + 53 curated topic-specific; 64 with real URLs), 914 topic↔resource links. Weightages parsed
  (Prob&Stats 16-20%, Programming 14-21%, GA 15%). Idempotent; never fabricates URLs.
**Roadmap Engine (backend):**
- `repositories/roadmap_repository.py`, `services/roadmap_service.py`, `schemas/roadmap.py` +
  `schemas/topic_detail.py`, `routers/roadmap.py` — rewritten for UUID/Postgres, reusing the old
  contract + revision-ladder logic. `services/activity_service.py` (streak + study-session) reworked.
- Endpoints: `GET /roadmap` (subject→topic tree + per-user progress summary),
  `GET /roadmap/topics/{id}` (detail + resources), `PATCH /roadmap/topics/{id}/progress`
  (completing a topic auto-schedules the 1/3/7/15/30/60/90-day revision ladder + updates streak).
- API keeps the frontend's field names (resource_type/platform/theory_markdown…) so the frontend
  only needed id `number → string` (UUID) across all types/hooks/components. `tsc -b` clean.
**Verified on Neon:** roadmap returns 10 subjects/103 topics; topic detail 200 with resources;
mark-complete → 7-rung revision ladder + streak=1 + study_session logged. Frontend type-checks.

**Note:** `/dashboard`, `/notes`, `/flashcards`, `/bookmarks`, `/practice` endpoints are not wired
yet (their pages will error until built) — Dashboard is Phase 6 next.

## 2026-07-20 — Phase 6: Premium Dashboard + Study Session system ✅
**Why:** make the Dashboard the heart of the app (know your status at a glance) and capture real
study time via explicit focus sessions — all from Postgres, no fake data.
**Study Sessions (backend):**
- Migration `db6b859ccb2d`: `study_sessions.interruptions` + `focus_score`.
- `services/study_service.py` + `routers/study.py`: `POST /study/sessions/start` (one active at a
  time, resumes on reload), `POST /study/sessions/{id}/stop` (duration + interruptions + focus +
  notes, updates streak), `GET /study/sessions/active`, `GET /study/sessions` (recent).
- `activity_service.update_streak()` extracted for reuse.
**Dashboard (backend):** `services/dashboard_service.py` rewritten for the new schema + enriched:
greeting, exam countdown (falls back to global GATE date), weighted completion, remaining hours,
predicted completion date (pace-based, needs ≥3 completions), difficulty distribution, per-subject
completion, weekly study series + today/week/month minutes, last session, revision-due-today +
upcoming ladder, today's tasks, weak/strong (onboarding until accuracy exists), honest null
predicted marks/AIR with `has_accuracy_data`/`has_mock_data` flags.
**Frontend (premium UI, Linear/Notion-grade):** rebuilt `DashboardPage` — glass hero (greeting +
days-to-GATE + 4 hero stats), live `StudyTimer` (ticking clock, interruptions, focus-score on
stop), animated SVG progress ring, Recharts weekly-hours bars + difficulty donut, subject-completion
bars, today's plan, upcoming revisions, study forecast, last session, weak/strong. Every card shows
real data or honest onboarding guidance — never "-". `hooks/use-study.ts` + updated dashboard types.
`tsc -b` clean.
**Verified on Neon:** dashboard returns 103 topics / 10 subjects / difficulty mix / 478 remaining
hours; mark-complete → 7-rung upcoming revisions; study start→stop stores duration/interruptions/
focus + updates last-session & streak. Live app restarted on :8000, reachable via Vite proxy.

## 2026-07-20 — Phase 8: Study Engine (Notes + Bookmarks + Flashcards) ✅
**Why:** finish the core study loop so no page errors — Notes, Bookmarks and Flashcards now work.
- **Notes** (`schemas/note` + `note_repository` + `routers/notes`): CRUD on the new `Note` model
  (`content_md`, soft-delete). API keeps `content_markdown` for the frontend.
- **Bookmarks** (`schemas/bookmark` + `bookmark_service` + `routers/bookmarks`): polymorphic
  (`target_type`/`target_id`) toggle + live resolution of title/subtitle/link from resource/topic/
  note/flashcard tables (no relationships → explicit queries).
- **Flashcards** (`schemas/flashcard` + `flashcard_repository` + `flashcard_service` +
  `routers/flashcards`): Leitner boxes (1/3/7/15/30-day), `next_review_at`, favorite + review-later
  on `UserFlashcard`, and `is_bookmarked` reused from the generic bookmark system. Adapted
  `seed_flashcards.py` → **114 flashcards** seeded (matched to real topics). All wired into the router.
**Verified on Neon:** note create/list/patch; 114 flashcards, review advances box + schedules review;
favorite/bookmark state toggles; bookmark toggle + live-resolved list. `tsc -b` clean.

## 2026-07-20 — Phase 9: Practice Engine ✅
**Why:** topic-wise practice with real grading feeds accuracy into progress + the dashboard.
- Backend on the normalized `questions`/`question_options` + `attempts`/`attempt_answers` tables:
  `schemas/practice`, `practice_repository`, `practice_service`, `routers/practice`.
  Endpoints: `GET /practice/topics/{id}/stats`, `POST /practice/start`,
  `POST /practice/attempts/{id}/answer` (MCQ/MSQ/NAT grading + negative marking),
  `POST /practice/attempts/{id}/submit` (score/accuracy → rolls into `user_topic_progress`
  accuracy, powering the dashboard weak/strong widget). Wired into the router.
- **Data:** the referenced `pyq_questions.json` never existed in the repo, so — honoring "no fake
  data" — seeded a **hand-verified 11-question starter set** (`seed_practice_questions.py` +
  `practice_questions.json`), labelled `source=practice` (not claimed official PYQs). A full
  verified PYQ bank is a separate curation effort (needs a product decision).
**Verified on Neon:** start (subject filter) → answer (all types graded) → submit (3/3, 100%) →
topic stats; accuracy rolled into progress. `tsc -b` clean.

**MILESTONE: core study loop is fully functional** (auth · dashboard · study sessions · roadmap ·
topic · notes · flashcards · bookmarks · practice) on Neon Postgres.

## 2026-07-20 — Phase 10: Learning Resources Platform (researched, ranked, admin-managed) ✅
**Why:** make the platform "best-in-class" for resources — every resource researched, verified,
ranked, and fully DB-driven/editable (never hardcoded).
- **Rich schema** (migration `321862e89b84`): `resources` gains category, ranking (gold/silver/
  bronze), instructor, channel, organization, language, year, rating, why_recommended,
  thumbnail_url, confidence_score, last_verified, needs_review, is_approved, is_obsolete; new
  `user_resources` table (favorite/completed/watch_progress/rating/notes). Enums `ResourceRank`,
  `ResourceCategory`.
- **Real web-verified curation:** dispatched 3 expert research subagents (Linear Algebra, Machine
  Learning, Probability & Statistics) that used WebSearch/WebFetch to verify every URL — **102
  gold/silver resources across 38 topics, only 1 needs_review**, written to
  `seed_data/resources_*.json` and imported via `import_resources.py` (**77 new, 52 gold + 25
  silver, dedup by URL, ranked so gold sorts first**). Never fabricated a link.
- **Topic page** now renders rich resource cards: ranking stars, organization/instructor/year,
  duration, "why recommended", needs-review flag, open-on-source. (`topic_detail.ResourceRead`
  enriched; `TopicPage` Resources tab redesigned.)
- **Admin API** (`routers/admin.py`, role-gated by `get_current_admin`): list (filter
  needs_review/approved/obsolete) · create (+link topic) · update · approve · mark obsolete ·
  delete. `scripts/make_admin.py` promotes a user to admin.
**Verified on Neon:** 211 resources (52 gold/25 silver, 77 web-verified); admin 403 for students,
200 for admins; SVD topic shows 3 gold incl. MIT 18.06 Strang. `tsc` clean.

## 2026-07-20 — Phase 10b: Resource curation expanded to 7 subjects ✅
Foreground research agents (network-enabled; background agents are sandboxed and correctly refused
to fabricate) web-verified and curated **Calculus (14), DSA (37), DBMS (29), AI (27) = 108 more
resources across 33 topics**, imported via `import_resources.py`. Platform total: **292 resources,
87 Gold / 71 Silver, 73/103 topics covered, only 8 needs_review** (flagged for admin review — never
fabricated). Integrity-checked (e.g. MIT OCW 18.06 = Strang, confirmed via WebFetch).

**Remaining resource work:** General Aptitude · Deep Learning · Data Science subjects.
**Remaining platform:** full verified PYQ bank · Admin UI + Learning-Path visualization + resource
watch-progress UI · Mock Engine · Analytics · AI Mentor (Ollama) · Gamification ·
Settings/Notifications · Deployment.
