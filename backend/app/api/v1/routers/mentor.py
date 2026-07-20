import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.deps import get_current_user, get_db
from app.models.activity import AiMessage
from app.models.user import User
from app.schemas.mentor import ChatRequest, ChatResponse, ConversationRead, MessageRead
from app.services.llm_provider import LLMUnavailableError
from app.services.mentor_service import MentorService

router = APIRouter(prefix="/mentor", tags=["mentor"])


def _msg(m: AiMessage) -> MessageRead:
    return MessageRead(id=m.id, role=m.role.value, content=m.content, created_at=m.created_at)


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatResponse:
    try:
        conv_id, assistant = MentorService(db).chat(current_user, payload.conversation_id, payload.message)
    except LLMUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI Mentor is offline. It runs on a local Ollama model — start Ollama on your machine. "
            "(The mentor is not available on the deployed server.)",
        ) from exc
    return ChatResponse(conversation_id=conv_id, message=_msg(assistant))


@router.get("/conversations", response_model=list[ConversationRead])
def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ConversationRead]:
    return [
        ConversationRead(id=c.id, title=c.title, updated_at=c.updated_at)
        for c in MentorService(db).list_conversations(current_user)
    ]


@router.get("/conversations/{conversation_id}", response_model=list[MessageRead])
def get_messages(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[MessageRead]:
    msgs = MentorService(db).get_messages(current_user, conversation_id)
    if msgs is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    return [_msg(m) for m in msgs]
