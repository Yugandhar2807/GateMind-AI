"""
Import every model module here so Alembic's autogenerate (via app.db.base)
can discover all tables through Base.metadata.
"""

from app.models.user import User  # noqa: F401
from app.models.content import Subject, Topic, Resource, TopicResource  # noqa: F401
from app.models.course import Course, CourseLesson, UserCourseProgress  # noqa: F401
from app.models.progress import UserTopicProgress, StudySession  # noqa: F401
from app.models.question import Question  # noqa: F401
from app.models.mock import MockTest, MockTestQuestion, QuizAttempt, QuizAnswer  # noqa: F401
from app.models.revision import RevisionSchedule  # noqa: F401
from app.models.bookmark import Bookmark  # noqa: F401
from app.models.flashcard import Flashcard, UserFlashcard  # noqa: F401
from app.models.mistake import Mistake  # noqa: F401
from app.models.note import Note  # noqa: F401
from app.models.reminder import Reminder  # noqa: F401
from app.models.analytics import AnalyticsSnapshot  # noqa: F401
