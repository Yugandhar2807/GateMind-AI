import uuid
from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.activity import AiConversation, AiMessage, Mistake
from app.models.curriculum import Subject, Topic
from app.models.enums import AiRole, ProgressStatus, RevisionStatus
from app.models.progress import RevisionSchedule, UserTopicProgress
from app.models.user import User
from app.services.llm_provider import get_provider

SYSTEM_TEMPLATE = """You are GateMind, {name}'s personal AI mentor for the GATE Data Science & AI (DA) 2027 exam.

Rules:
- Answer using (a) GATE DA syllabus knowledge and (b) THIS student's live data below.
- Be specific, concise, and actionable — reference their ACTUAL topics, weak areas, streak, revisions.
- Never invent their progress or fabricate resources/scores. If asked about data you don't have, say so.
- Prefer short, structured answers (bullets, a clear next step).

=== {name}'s live preparation data (as of {today}) ===
{context}
=== end of data ==="""

MAX_HISTORY = 10


class MentorService:
    def __init__(self, db: Session):
        self.db = db

    def build_context(self, user: User) -> str:
        today = datetime.now(timezone.utc).date()
        topics = {t.id: t for t in self.db.scalars(select(Topic)).all()}
        subjects = {s.id: s for s in self.db.scalars(select(Subject)).all()}
        progress = list(
            self.db.scalars(select(UserTopicProgress).where(UserTopicProgress.user_id == user.id)).all()
        )

        def name_of(tid) -> str:
            t = topics.get(tid)
            return t.name if t else "?"

        exam = user.exam_date or settings.GATE_EXAM_DATE
        days = (exam - today).days if exam else None
        done = [p for p in progress if p.status == ProgressStatus.COMPLETED]
        inprog = [p for p in progress if p.status == ProgressStatus.IN_PROGRESS]

        lines = [
            f"Target: AIR Top {user.target_air or '?'}, score {user.target_score or '?'}/100; "
            f"exam ~{exam} ({days} days left).",
            f"Streak: {user.current_streak_days} days (longest {user.longest_streak_days}).",
            f"Syllabus: {len(done)}/{len(topics)} topics completed, {len(inprog)} in progress.",
        ]
        if inprog:
            lines.append("Currently studying: " + ", ".join(name_of(p.topic_id) for p in inprog[:6]))

        acc = [p for p in progress if p.accuracy_percent is not None]
        if acc:
            weak = sorted(acc, key=lambda p: p.accuracy_percent)[:5]
            strong = sorted(acc, key=lambda p: -p.accuracy_percent)[:3]
            lines.append("Weakest topics: " + ", ".join(f"{name_of(p.topic_id)} ({p.accuracy_percent:.0f}%)" for p in weak))
            lines.append("Strongest topics: " + ", ".join(f"{name_of(p.topic_id)} ({p.accuracy_percent:.0f}%)" for p in strong))
        else:
            lines.append("No practice accuracy yet — hasn't attempted practice questions/mocks.")

        due = list(
            self.db.scalars(
                select(RevisionSchedule).where(
                    RevisionSchedule.user_id == user.id,
                    RevisionSchedule.status == RevisionStatus.PENDING,
                    RevisionSchedule.due_date <= today,
                )
            ).all()
        )
        if due:
            lines.append(f"Revisions due now: {len(due)} — " + ", ".join(name_of(r.topic_id) for r in due[:6]))

        mistakes = list(
            self.db.scalars(
                select(Mistake)
                .where(Mistake.user_id == user.id, Mistake.is_resolved.is_(False))
                .order_by(desc(Mistake.created_at))
                .limit(5)
            ).all()
        )
        if mistakes:
            lines.append(
                "Recent unresolved mistakes: "
                + "; ".join((m.description_md or m.category.value)[:70] for m in mistakes)
            )

        subj_done: dict = {}
        for p in done:
            t = topics.get(p.topic_id)
            if t:
                subj_done[t.subject_id] = subj_done.get(t.subject_id, 0) + 1
        if subj_done:
            lines.append(
                "Completed by subject: "
                + ", ".join(f"{subjects[sid].name}: {n}" for sid, n in subj_done.items() if sid in subjects)
            )
        return "\n".join(lines)

    def chat(self, user: User, conversation_id: uuid.UUID | None, message: str) -> tuple[uuid.UUID, AiMessage]:
        conv = None
        if conversation_id is not None:
            conv = self.db.scalars(
                select(AiConversation).where(
                    AiConversation.id == conversation_id,
                    AiConversation.user_id == user.id,
                    AiConversation.deleted_at.is_(None),
                )
            ).first()
        if conv is None:
            conv = AiConversation(user_id=user.id, title=message[:60])
            self.db.add(conv)
            self.db.flush()

        history = list(
            self.db.scalars(
                select(AiMessage).where(AiMessage.conversation_id == conv.id).order_by(AiMessage.created_at)
            ).all()
        )
        context = self.build_context(user)
        first_name = (user.full_name or "the student").split()[0] if (user.full_name or "").strip() else "the student"
        system = SYSTEM_TEMPLATE.format(
            name=first_name, today=datetime.now(timezone.utc).date(), context=context
        )

        payload = [{"role": "system", "content": system}]
        for m in history[-MAX_HISTORY:]:
            payload.append({"role": m.role.value, "content": m.content})
        payload.append({"role": "user", "content": message})

        self.db.add(AiMessage(conversation_id=conv.id, role=AiRole.USER, content=message))

        reply = get_provider().chat(payload)  # raises LLMUnavailableError if Ollama is down
        if not reply:
            reply = "I couldn't generate a response just now — please try again."

        assistant = AiMessage(
            conversation_id=conv.id,
            role=AiRole.ASSISTANT,
            content=reply,
            context_snapshot={"context": context},
        )
        self.db.add(assistant)
        self.db.commit()
        self.db.refresh(assistant)
        return conv.id, assistant

    def list_conversations(self, user: User) -> list[AiConversation]:
        return list(
            self.db.scalars(
                select(AiConversation)
                .where(AiConversation.user_id == user.id, AiConversation.deleted_at.is_(None))
                .order_by(desc(AiConversation.updated_at))
            ).all()
        )

    def get_messages(self, user: User, conversation_id: uuid.UUID) -> list[AiMessage] | None:
        conv = self.db.scalars(
            select(AiConversation).where(
                AiConversation.id == conversation_id, AiConversation.user_id == user.id
            )
        ).first()
        if conv is None:
            return None
        return list(
            self.db.scalars(
                select(AiMessage).where(AiMessage.conversation_id == conv.id).order_by(AiMessage.created_at)
            ).all()
        )
