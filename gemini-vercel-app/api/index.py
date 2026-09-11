import os
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from google import genai
from google.genai import types

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "FastAPI is running on Vercel!"}


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[Dict[str, Any]]] = None
    api_key: Optional[str] = None
    model: str = "gemini-2.5-flash"
    temperature: float = 0.7


@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest):
    key = request.api_key or os.getenv("GEMINI_API_KEY")

    async def generate():
        try:
            if not key:
                yield "Error: Gemini API key is missing. Provide one in the request or set GEMINI_API_KEY."
                return

            client = genai.Client(api_key=key)

            contents: List[types.Content] = []
            if request.history:
                for msg in request.history:
                    role = "user" if msg.get("role") == "user" else "model"
                    contents.append(
                        types.Content(
                            role=role,
                            parts=[types.Part.from_text(text=msg.get("content", ""))],
                        )
                    )

            contents.append(
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=request.message)],
                )
            )

            response = client.models.generate_content_stream(
                model=request.model,
                contents=contents,
                config=types.GenerateContentConfig(temperature=request.temperature),
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"\n\n[Error: {e}]"

    return StreamingResponse(generate(), media_type="text/plain")