import uuid
from datetime import datetime, timezone
from typing import List, Optional

from sqlmodel import Column, Field, Relationship, SQLModel, Text


def new_uuid() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ChatSession(SQLModel, table=True):
    __tablename__ = "sessions"

    id: str = Field(default_factory=new_uuid, primary_key=True)
    title: str = Field(default="New Chat")
    created_at: datetime = Field(default_factory=utcnow)
    updated_at: datetime = Field(default_factory=utcnow)
    model: str = Field(default="gemini-2.5-flash")
    system_instruction: Optional[str] = Field(default=None)
    temperature: float = Field(default=0.7)

    messages: List["ChatMessage"] = Relationship(
        back_populates="session",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class ChatMessage(SQLModel, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(foreign_key="sessions.id", index=True, ondelete="CASCADE")
    role: str = Field(default="user")
    content: str = Field(sa_column=Column(Text))
    has_image: bool = Field(default=False)
    created_at: datetime = Field(default_factory=utcnow)

    session: Optional[ChatSession] = Relationship(back_populates="messages")