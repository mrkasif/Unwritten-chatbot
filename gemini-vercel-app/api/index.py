import base64
import os
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI(title="Unwritten API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_client = None


class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, Any]] = []
    api_key: Optional[str] = ""
    model: str = "gemini-2.5-flash"
    system_instruction: Optional[str] = "You are a helpful and intelligent AI assistant."
    temperature: float = 0.7
    image_data: Optional[str] = None
    image_mime_type: Optional[str] = None


def get_client(api_key: str):
    global _client
    key = api_key or os.getenv("GEMINI_API_KEY", "")
    if key:
        _client = genai.Client(api_key=key)
    return _client


def generate_stream(req: ChatRequest):
    client = get_client(req.api_key)
    if not client:
        yield "Error: Gemini API key is missing. Set it in the sidebar or in the Vercel environment variables."
        return

    config = types.GenerateContentConfig(
        temperature=req.temperature,
        system_instruction=req.system_instruction if req.system_instruction else None,
    )

    contents = []
    for h in req.history:
        role = "user" if h["role"] == "user" else "model"
        contents.append(
            types.Content(role=role, parts=[types.Part.from_text(text=h["content"])])
        )

    parts = [types.Part.from_text(text=req.message)]
    if req.image_data:
        try:
            parts.insert(
                0,
                types.Part.from_bytes(
                    data=base64.b64decode(req.image_data),
                    mime_type=req.image_mime_type or "image/png",
                ),
            )
        except Exception as e:
            yield f"\n[Image Error: {str(e)}]"
            return

    contents.append(types.Content(role="user", parts=parts))

    try:
        response = client.models.generate_content_stream(
            model=req.model,
            contents=contents,
            config=config,
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        yield f"\n[API Error: {str(e)}]"


@app.get("/api/health")
def health_check():
    return {"status": "online"}


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    return StreamingResponse(generate_stream(request), media_type="text/plain")