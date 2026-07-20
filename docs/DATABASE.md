# GateMind AI — Database Reference (Postgres / Neon)

Greenfield **UUID v2** schema. Provider: **Neon PostgreSQL 17** (pooled endpoint, `ap-southeast-1`).
ORM: SQLAlchemy 2.0 + psycopg 3. Migrations: Alembic (baseline `500dd9cec4a9_uuid_v2_baseline`).

## Conventions (every table)
- **PK:** `id UUID` (client-generated `uuid.uuid4`, `default`).
- **Timestamps:** `created_at`, `updated_at` (`timestamptz`, DB defaults; `updated_at` auto-bumps).
- **Soft delete:** `deleted_at timestamptz NULL` on user-editable content (`users`, `notes`,
  `bookmarks`, `ai_conversations`, `files`).
- **Enums:** stored as VARCHAR + CHECK (`native_enum=False`) — migration-friendly, no native PG enum.
- **FKs:** indexed; `ON DELETE CASCADE` for owned children, `SET NULL` for optional references.
- **Naming:** deterministic (`pk_`, `fk_`, `uq_`, `ix_`, `ck_`) via `MetaData.naming_convention`
  in `app/db/base_class.py`.

## Table groups (30 tables)

**Identity / auth** (`app/models/user.py`)
- `users` — profile, targets (`target_score`, `target_air`, `exam_date`), streak counters, timezone.
- `auth_identities` — external logins (google/github) + local password link. `uq(provider, provider_user_id)`.
- `refresh_tokens` — hashed, `expires_at`/`revoked_at` for rotation.

**Curriculum — global** (`app/models/curriculum.py`)
- `subjects` — 10 GATE DA subjects, weightage, priority, order.
- `topics` — self-referential tree (`parent_topic_id`); rich Markdown content
  (`theory_md`, `formulas_md`, `cheat_sheet_md`, `common_mistakes_md`, `mind_map_json`).
- `topic_prerequisites` — dependency-graph edges (from KNOWLEDGE_DEPENDENCY_MAP).
- `resources`, `topic_resources` — videos/books/etc., curated per topic (`relevance_rank`).

**Learning content — global** (`app/models/content.py`)
- `content_documents` — the GATE-DA-2027 narrative docs made dynamic (category-tagged).
- `questions`, `question_options` — MCQ/MSQ/NAT (NAT via `correct_value`), PYQ/practice/AI/mock.
- `flashcards` — front/back Markdown per topic.
- `mock_templates`, `mock_template_questions` — reusable mock papers.
- `achievements` — badge definitions.

**Per-user progress** (`app/models/progress.py`)
- `user_topic_progress` — status/%/accuracy/time. `uq(user_id, topic_id)`.
- `study_sessions` — logged study time by type.
- `revision_schedules` — 1/3/7/15/30/60/90-day ladder rows. `uq(user_id, topic_id, interval_day)`.
- `user_flashcards` — Leitner box/ease/next_review. `uq(user_id, flashcard_id)`.

**Per-user activity** (`app/models/activity.py`)
- `attempts` + `attempt_answers` — unified practice & mock runs (`attempt_type`), scoring,
  `predicted_gate_score`.
- `notes`, `bookmarks` (polymorphic `target_type`+`target_id`), `mistakes` (error notebook).
- `analytics_snapshots` — daily predicted marks/AIR, per-subject accuracy, weak/strong topics (JSONB).
- `ai_conversations` + `ai_messages` — AI Mentor chats with per-turn `context_snapshot`.
- `files` — Cloudinary refs. `user_achievements`, `reminders`.

## Local workflow
```powershell
cd GateMind-AI\backend
.\venv\Scripts\python -m alembic upgrade head        # apply migrations to Neon
.\venv\Scripts\python -m alembic revision --autogenerate -m "msg"   # after model changes
```
`DATABASE_URL` lives in gitignored `backend/.env`. Use a Neon **dev branch** for local work to keep
prod data clean.
