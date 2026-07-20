"""
Import every model here so Alembic autogenerate (via app.db.base) discovers all
tables through Base.metadata. Greenfield UUID v2 schema (Postgres).
"""

from app.models.user import User, AuthIdentity, RefreshToken  # noqa: F401
from app.models.curriculum import (  # noqa: F401
    Subject,
    Topic,
    TopicPrerequisite,
    Resource,
    TopicResource,
)
from app.models.content import (  # noqa: F401
    ContentDocument,
    Question,
    QuestionOption,
    Flashcard,
    MockTemplate,
    MockTemplateQuestion,
    Achievement,
)
from app.models.progress import (  # noqa: F401
    UserTopicProgress,
    StudySession,
    RevisionSchedule,
    UserFlashcard,
)
from app.models.activity import (  # noqa: F401
    Attempt,
    AttemptAnswer,
    Note,
    Bookmark,
    Mistake,
    AnalyticsSnapshot,
    AiConversation,
    AiMessage,
    File,
    UserAchievement,
    Reminder,
)
