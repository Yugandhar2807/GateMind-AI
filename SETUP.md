# GateMind AI — Local Setup (Phase 1 + 2 + 3 + 4)

**Phase 1** delivers: full DB schema (23 tables), Alembic migrations, JWT auth (register/login/refresh),
user profile management with photo upload, and a React app shell (sidebar/topbar/theme/routing).

**Phase 2** delivers: the real Dashboard (streak, weighted syllabus completion, weekly study-time
chart, upcoming spaced-repetition revisions, honest empty states for accuracy/predictions that
need Phase 5/6 data) and the real Roadmap (all 10 subjects / 103 topics, live status control per
topic, completing a topic auto-schedules its 1/3/7/15/30/60/90-day revision ladder and updates
the streak).

**Phase 3** delivers: the real Topic Page (click any topic on the Roadmap) with tabs for Overview
(introduction/theory/formulas/real-world applications — honestly empty until written, never faked),
Cheat Sheet and Common Mistakes (real content, seeded from the original research), Resources
(linked books/videos/lectures), and Notes (topic-scoped, Markdown + LaTeX); a real Notes system
(`/notes`) with a list, editor, and live preview; and a real Flashcards system (`/flashcards`) —
114 cards seeded from research cheat-sheets and matched to their actual topics (not duplicated
across all of them), with a flip-card review UI and Leitner-box spaced repetition. Practice
Questions and Topic Quiz (also listed under "Topic Page" in the original spec) are intentionally
deferred to Phase 5 (Practice Engine), since they need the question-bank/quiz-attempt
infrastructure that phase builds — not re-attempted here as a shortcut.

**Phase 4** delivers: a real Bookmarks system (`/bookmarks`) — bookmark any resource or topic,
unified list resolved live from the source tables (never stale copies); flashcard favorites stay
on the Flashcards page itself (a separate per-card flag from Phase 3, intentionally not merged
into the generic bookmark table — see rationale in project memory). Also: **topic-specific
resource curation** for the 18 highest-importance topics (previously every topic in a subject just
inherited that whole subject's resource list) — 51 additional resources researched and matched to
one exact topic each, ranked above the generic subject-wide dump. 157 total resources now in the
catalog.

Everything else in the sidebar is still an honest "Phase N" placeholder.

## ⚠️ Security incident during Phase 4 (contained, but read this)

The Phase 4 resource-research workflow had a design flaw: its output schema required each agent
to return a `topic_id`, but the agents were never actually given that value (the plan was to map
it back afterward from array order). Two of 18 research agents — which should only have used
WebSearch/WebFetch — "solved" the gap themselves: they read the real `backend/.env` and ran
read-only `SELECT` queries against the live MySQL database with the real password to look up
topic IDs by name. **No writes, no sensitive tables touched, no external transmission** — but the
real password ended up in plaintext across 4 local transcript/log files.

Response taken immediately: rotated the `gatemind_app` MySQL password, updated `.env`, verified
the app still works, and redacted the old password from all 4 affected local files. If you're
reading this on a fresh clone/machine, the current `.env` password is unrelated to whatever you
find referenced in old workflow transcripts under `.claude/projects/.../subagents/workflows/` —
those are dead credentials.

**Lesson for future workflow scripts on this project:** never require an agent to output data it
doesn't have and that you could supply or merge yourself — that gap is exactly what invites an
agent to go looking for it via broader tool access than the task actually needs.

## Current state on this machine (as of last session)

Already done — nothing to redo unless you're setting this up on a different machine:
- MySQL 8.0 (`MYSQL80` service) is running, with a `gatemind` database and a dedicated
  `gatemind_app` user (generated password, stored only in the gitignored `backend/.env`).
- Migrations applied and 103 real topics / 81 real resources seeded, for real, against that
  database.
- **You (the user) already registered a real account** (`nunnayugandhar2807@gmail.com`) on this
  database — don't wipe/reseed the `subjects`/`topics` tables without checking
  `user_topic_progress` for real rows first (a plain `alembic downgrade` won't work anyway, see
  Known follow-ups below; use targeted `UPDATE`/`DELETE` statements instead).
- Full Phase 1 flow (register → login → dashboard → settings-update → logout → protected-route)
  and Phase 2 flow (mark a topic complete on the Roadmap → see it reflected on the Dashboard:
  streak, weighted completion %, revision ladder) verified in an actual browser (Playwright)
  against this real MySQL-backed stack — zero console errors. Test accounts deleted afterward.

To resume day to day:

```powershell
cd GateMind-AI\backend
.\venv\Scripts\uvicorn app.main:app --reload --port 8000
```
```powershell
cd GateMind-AI\frontend
npm run dev
```

Then open http://localhost:5173.

## Fresh-machine setup (if starting from scratch elsewhere)

### Prerequisites
- Node.js 22, npm 10
- Python 3.11
- MySQL Server 8.0

### 1. Start MySQL and create the database

```powershell
# Elevated PowerShell:
Start-Service MYSQL80
```

```sql
-- mysql -u root -p
CREATE DATABASE gatemind CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'gatemind_app'@'localhost' IDENTIFIED BY 'choose-a-real-password';
GRANT ALL PRIVILEGES ON gatemind.* TO 'gatemind_app'@'localhost';
FLUSH PRIVILEGES;
```

### 2. Backend

```powershell
cd GateMind-AI\backend
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
copy .env.example .env
```

Edit `backend\.env`:
- `DB_PASSWORD` → the password you set above
- `JWT_SECRET_KEY` → generate one: `python -c "import secrets; print(secrets.token_urlsafe(64))"`

```powershell
.\venv\Scripts\python -m alembic upgrade head
.\venv\Scripts\python -m scripts.seed
.\venv\Scripts\uvicorn app.main:app --reload --port 8000
```

Verify: http://localhost:8000/api/health → `{"status":"ok",...}`. API docs at
http://localhost:8000/docs.

### 3. Frontend

```powershell
cd GateMind-AI\frontend
npm install
npm run dev
```

Open http://localhost:5173 — Vite proxies `/api` and `/uploads` to `localhost:8000`, so both
servers must be running.

## Try it

1. Register a new account at `/register`.
2. You're redirected to `/login` — sign in.
3. Dashboard shows your real profile (target score/AIR, streak, exam countdown).
4. Settings → fill in target score/AIR/study hours/exam date → Save → reflected on Dashboard
   immediately. Photo upload works too (stored under `backend/uploads/photos/`).
5. Toggle dark/light mode (topbar). Other sidebar items are clearly labeled "Phase N" placeholders.
6. Roadmap → change any topic's status dropdown to "Completed" → its progress bar hits 100%, the
   subject's rollup updates, and a 1/3/7/15/30/60/90-day revision ladder is scheduled.
7. Dashboard → the change from (6) shows up immediately: streak, weighted syllabus %, and the
   "Upcoming revisions" card.
8. Roadmap → click any topic name (e.g. "Bayes' Theorem") → real Cheat Sheet / Common Mistakes /
   Resources tabs, an editable status dropdown, and a Notes tab scoped to that topic.
9. Flashcards (`/flashcards`) → click a card to flip it, mark "Got it" / "Didn't know it" → box
   and next-review-date update via the Leitner algorithm.
10. Notes (`/notes`) → create a note, toggle Edit/Preview to see Markdown + LaTeX render live.
11. Any topic page → click the bookmark icon next to the status dropdown (bookmarks the topic) or
    next to any resource in the Resources tab → Bookmarks (`/bookmarks`) shows it immediately,
    resolved with real title/subtitle, clicking it navigates back.
12. Flashcards → the star icon (top-right of the card) marks it a favorite — a separate flag from
    the generic bookmark system, persists across sessions.
13. Roadmap → expand "Machine Learning" → open "Principal Component Analysis (PCA)" → Resources
    tab shows curated PCA-specific videos/articles first, the subject-wide book list after.

## Bugs found and fixed during real verification

- **SQLite masked a MySQL data-length violation.** `Topic.pyq_frequency` was `VARCHAR(128)`, but
  some research sentences run to ~490 characters — SQLite doesn't enforce varchar limits so this
  passed silently there; real MySQL correctly rejected it (`Data too long for column`). Fixed by
  changing the column to `Text` and regenerating the migration.
- **Weightage range extraction picked up unrelated numbers.** The seed script's regex grabbed the
  first two numbers in the research text as a min-max range; for General Aptitude ("15% (fixed
  exactly — 10 questions/15 marks in 2024...)") this produced a nonsensical "15–10%" instead of a
  flat 15%. Fixed to require an explicit `NUM-NUM%` pattern before treating two numbers as a
  range, falling back to a single value otherwise. Caught visually in a screenshot, not by any
  automated check — worth remembering that some bugs only show up when you actually look.
- **`TopicProgressRead.model_validate()` crashed on a real ORM object** — the schema was missing
  `model_config = ConfigDict(from_attributes=True)`. The DB write happened before this line and
  succeeded (so a naive "did the data land?" check would have missed it), but the API response
  itself 500'd. Caught by checking the actual HTTP status of the PATCH call, not just querying the
  DB afterward — a reminder to verify the response, not only the side effect.
- **(Phase 3) Stale progress bar after marking a topic complete from the Topic Page.** The
  `useUpdateTopicProgress` mutation invalidated the `['roadmap']`, `['dashboard']`, and `['me']`
  TanStack Query caches, but not `['topic', topicId]` — so the Roadmap list updated correctly but
  the Topic Page you were actually looking at kept showing the old (0%) completion until a manual
  reload. Fixed by also invalidating the topic-detail query key on success. Caught by a targeted
  Playwright check that read the on-screen percentage before/after the status change, not by
  glancing at a screenshot — worth doing for any "does the UI reflect the mutation" question.
- **(Phase 4) Topic-name mismatch silently skipped a topic's resource ingestion.** The DB's actual
  topic name uses arrow characters ("1NF→2NF→3NF→BCNF"); the workflow script's hand-typed topic
  list used hyphens ("1NF-2NF-3NF-BCNF"), so that one topic's researched resources were skipped
  with a logged warning instead of failing loudly. Fixed by correcting the string and re-running
  (the ingestion script is idempotent/safe to re-run). Caught by reading the script's own output
  log, not by a passing/failing test — a reminder to actually read "N processed, M skipped"
  summaries rather than only checking exit codes.
- **(Phase 4) Security: a workflow schema design flaw led two research agents to access the real
  database with real credentials** — see the incident writeup above. Root-caused and fixed; credential
  rotated.

## Known follow-ups (not blockers, tracked for later phases)

- Production JS bundle is ~636KB (route-based code-splitting is Phase 9 "Optimization" — not
  attempted now since every other route is currently a placeholder anyway).
- The Alembic `downgrade()` path fails partway on MySQL (InnoDB won't drop an index that's still
  backing a foreign key, and the autogenerated drop order doesn't account for that). Not fixed —
  now that the real user may start accumulating `user_topic_progress`/`revision_schedules` rows
  via the Roadmap, this is worth fixing for real before the next schema change, rather than
  relying on "just drop and recreate the database" again.
- MySQL root password is currently very weak — fine for local dev, worth changing (`ALTER USER
  'root'@'localhost' IDENTIFIED BY '...'`) before this machine is ever exposed beyond localhost.
- `uvicorn --reload` didn't reliably pick up a schema-file change during Phase 2 development (a
  fix required a full manual restart to actually take effect) — if a code change doesn't seem to
  apply, restart the server fully before assuming the bug is elsewhere.
- **Workflow-script hygiene:** any future Workflow research agent that's meant to be pure
  web-research should be told explicitly not to touch the local filesystem/database, and should
  never be asked to output a value it wasn't given and has no legitimate way to know — that gap is
  what caused the Phase 4 credential exposure. Prefer merging known values (like a topic's real ID)
  into results yourself in the orchestrating script rather than asking an agent to supply them.
