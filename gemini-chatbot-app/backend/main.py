from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session, delete, select
from typing import Dict, Any

from backend import database
from backend.database import get_session
from backend.gemini_client import GeminiService
from backend.models import ChatMessage, ChatSession, utcnow


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.create_db_and_tables()
    yield


app = FastAPI(title="Unwritten API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

gemini_service = GeminiService()


class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, Any]] = []
    api_key: Optional[str] = ""
    model: str = "gemini-2.5-flash"
    system_instruction: Optional[str] = "You are a helpful and intelligent AI assistant."
    temperature: float = 0.7
    image_data: Optional[str] = None
    image_mime_type: Optional[str] = None
    session_id: Optional[str] = None


class SessionPayload(BaseModel):
    title: Optional[str] = None
    model: str = "gemini-2.5-flash"
    system_instruction: Optional[str] = None
    temperature: float = 0.7


class SessionOut(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    model: str
    system_instruction: Optional[str]
    temperature: float


class MessageOut(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    has_image: bool
    created_at: datetime


@app.get("/api/health")
def health_check():
    return {"status": "online"}


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest, db: Session = Depends(get_session)):
    if request.api_key:
        gemini_service.update_key(request.api_key)

    if request.session_id:
        chat_session = db.get(ChatSession, request.session_id)
        if chat_session is None:
            chat_session = ChatSession(
                id=request.session_id,
                title="New Chat",
                model=request.model,
                system_instruction=request.system_instruction,
                temperature=request.temperature,
            )
            db.add(chat_session)
    else:
        chat_session = ChatSession(
            title="New Chat",
            model=request.model,
            system_instruction=request.system_instruction,
            temperature=request.temperature,
        )
        db.add(chat_session)

    db.commit()
    db.refresh(chat_session)
    session_id = chat_session.id

    chat_session.updated_at = utcnow()
    db.add(
        ChatMessage(
            session_id=session_id,
            role="user",
            content=request.message,
            has_image=bool(request.image_data),
        )
    )
    db.commit()

    async def stream_and_save():
        full_response = ""
        try:
            async for chunk in gemini_service.generate_stream(
                history=request.history,
                message=request.message,
                model=request.model,
                system_instruction=request.system_instruction or "",
                temperature=request.temperature,
                image_data=request.image_data,
                image_mime_type=request.image_mime_type,
            ):
                full_response += chunk
                yield chunk
        except Exception as e:
            error_text = f"\n[Server Error: {str(e)}]"
            full_response += error_text
            yield error_text
        finally:
            with database.db_session() as s:
                s.add(
                    ChatMessage(
                        session_id=session_id,
                        role="assistant",
                        content=full_response,
                        has_image=False,
                    )
                )
                chat_session_row = s.get(ChatSession, session_id)
                if chat_session_row is not None:
                    chat_session_row.updated_at = utcnow()

    return StreamingResponse(stream_and_save(), media_type="text/plain")


@app.post("/api/sessions", response_model=SessionOut)
def create_session(payload: Optional[SessionPayload] = None, db: Session = Depends(get_session)):
    data = payload or SessionPayload()
    chat_session = ChatSession(
        title=data.title or "New Chat",
        model=data.model,
        system_instruction=data.system_instruction,
        temperature=data.temperature,
    )
    db.add(chat_session)
    db.commit()
    db.refresh(chat_session)
    return chat_session


@app.get("/api/sessions", response_model=List[SessionOut])
def list_sessions(db: Session = Depends(get_session)):
    statement = select(ChatSession).order_by(ChatSession.updated_at.desc())
    return db.exec(statement).all()


@app.get("/api/sessions/{session_id}/messages", response_model=List[MessageOut])
def get_session_messages(session_id: str, db: Session = Depends(get_session)):
    statement = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.id)
    )
    return db.exec(statement).all()


@app.delete("/api/sessions/{session_id}/messages")
def clear_session(session_id: str, db: Session = Depends(get_session)):
    chat_session = db.get(ChatSession, session_id)
    if chat_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    db.exec(delete(ChatMessage).where(ChatMessage.session_id == session_id))
    chat_session.updated_at = utcnow()
    db.commit()
    return {"status": "cleared"}


@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_session)):
    chat_session = db.get(ChatSession, session_id)
    if chat_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    db.delete(chat_session)
    db.commit()
    return {"status": "deleted"}