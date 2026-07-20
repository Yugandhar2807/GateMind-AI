import enum


class PreferredStudyTime(str, enum.Enum):
    EARLY_MORNING = "early_morning"
    MORNING = "morning"
    EVENING = "evening"
    NIGHT = "night"
    LATE_NIGHT = "late_night"


class NodeLevel(str, enum.Enum):
    """Depth marker for the self-referential content tree under a Subject."""

    TOPIC = "topic"
    SUBTOPIC = "subtopic"
    CONCEPT = "concept"


class Difficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    VERY_HARD = "very_hard"


class PriorityLevel(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ProgressStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    NEEDS_REVISION = "needs_revision"


class ResourceType(str, enum.Enum):
    VIDEO = "video"
    BOOK = "book"
    BLOG = "blog"
    DOCUMENTATION = "documentation"
    RESEARCH_PAPER = "research_paper"
    GITHUB_REPO = "github_repo"
    ARTICLE = "article"
    LECTURE_SERIES = "lecture_series"


class ResourceLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    RESEARCH = "research"


class SessionType(str, enum.Enum):
    LEARNING = "learning"
    REVISION = "revision"
    PRACTICE = "practice"
    MOCK = "mock"
    FLASHCARDS = "flashcards"


class QuestionType(str, enum.Enum):
    MCQ = "mcq"
    MSQ = "msq"
    NAT = "nat"
    CODING = "coding"


class QuestionSource(str, enum.Enum):
    PYQ = "pyq"
    PRACTICE = "practice"
    AI_GENERATED = "ai_generated"
    MOCK = "mock"


class MockType(str, enum.Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    FULL_SYLLABUS = "full_syllabus"
    TOPIC = "topic"
    MIXED = "mixed"


class MockStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    MISSED = "missed"


class RevisionInterval(int, enum.Enum):
    DAY_1 = 1
    DAY_3 = 3
    DAY_7 = 7
    DAY_15 = 15
    DAY_30 = 30
    DAY_60 = 60
    DAY_90 = 90


class RevisionStatus(str, enum.Enum):
    PENDING = "pending"
    DUE = "due"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class BookmarkType(str, enum.Enum):
    RESOURCE = "resource"
    QUESTION = "question"
    TOPIC = "topic"
    FORMULA = "formula"
    NOTE = "note"
    FLASHCARD = "flashcard"


class MistakeCategory(str, enum.Enum):
    CONCEPTUAL_GAP = "conceptual_gap"
    CARELESS_SLIP = "careless_slip"
    TIME_PRESSURE = "time_pressure"
    GUESSING = "guessing"
    FORMULA_FORGOTTEN = "formula_forgotten"
    REVISION_DECAY = "revision_decay"


class ReminderType(str, enum.Enum):
    STUDY = "study"
    REVISION = "revision"
    MOCK = "mock"
    WEAK_TOPIC = "weak_topic"


class UserRole(str, enum.Enum):
    STUDENT = "student"
    ADMIN = "admin"


class AuthProvider(str, enum.Enum):
    PASSWORD = "password"
    GOOGLE = "google"
    GITHUB = "github"


class AttemptType(str, enum.Enum):
    PRACTICE = "practice"
    MOCK = "mock"


class AttemptStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    ABANDONED = "abandoned"


class AiRole(str, enum.Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class FileKind(str, enum.Enum):
    AVATAR = "avatar"
    ATTACHMENT = "attachment"
    AI_NOTE = "ai_note"
    IMPORT = "import"


class ContentCategory(str, enum.Enum):
    """Which GATE-DA-2027 source doc a `content_documents` row was ingested from."""

    ROADMAP = "roadmap"
    SUBJECT_ANALYSIS = "subject_analysis"
    TREND_ANALYSIS = "trend_analysis"
    DEPENDENCY_MAP = "dependency_map"
    SOURCE_RESEARCH = "source_research"
    ERROR_NOTEBOOK = "error_notebook"
    PROGRESS_LOG = "progress_log"
    OTHER = "other"


class ResourceRank(str, enum.Enum):
    GOLD = "gold"
    SILVER = "silver"
    BRONZE = "bronze"


class ResourceCategory(str, enum.Enum):
    """Fine-grained learning-resource category (curation buckets)."""

    BEST_PLAYLIST = "best_playlist"
    BEST_SINGLE_VIDEO = "best_single_video"
    NPTEL = "nptel"
    IIT_LECTURE = "iit_lecture"
    MIT_OCW = "mit_ocw"
    STANFORD = "stanford"
    HARVARD = "harvard"
    COURSERA = "coursera"
    EDX = "edx"
    DOCUMENTATION = "documentation"
    REFERENCE_BOOK = "reference_book"
    PRACTICE_WEBSITE = "practice_website"
    PYQ_EXPLANATION = "pyq_explanation"
    CHEAT_SHEET = "cheat_sheet"
    FORMULA_NOTES = "formula_notes"
    GITHUB = "github"
    VISUALIZATION = "visualization"
    RESEARCH_PAPER = "research_paper"
    OTHER = "other"
