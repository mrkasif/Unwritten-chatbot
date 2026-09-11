import os
import base64
from typing import AsyncGenerator, List, Dict, Any, Optional
from google import genai
from google.genai import types

class GeminiService:
    def __init__(self, api_key: Optional[str] = None):
        # Fallback to environment variable if api_key is empty string or None
        key = api_key if api_key else os.getenv("GEMINI_API_KEY", "")
        self.client = genai.Client(api_key=key) if key else None

    def update_key(self, api_key: str):
        """Allows dynamic API key injection at runtime."""
        self.client = genai.Client(api_key=api_key)

    async def generate_stream(
        self, 
        history: List[Dict[str, Any]], 
        message: str, 
        model: str = "gemini-2.5-flash",
        system_instruction: str = "",
        temperature: float = 0.7,
        image_data: Optional[str] = None,
        image_mime_type: Optional[str] = None
    ) -> AsyncGenerator[str, None]:
        if not self.client:
            yield "Error: Gemini API key is missing. Please set it in your settings or .env file."
            return

        # Prepare configuration settings
        config = types.GenerateContentConfig(
            temperature=temperature,
            system_instruction=system_instruction if system_instruction else None
        )

        # Convert simple dictionary format to Google SDK content format
        formatted_contents = []
        for h in history:
            role = "user" if h["role"] == "user" else "model"
            formatted_contents.append(
                types.Content(role=role, parts=[types.Part.from_text(text=h["content"])])
            )

        # Build parts for the current message, prepending the attached image
        parts = [types.Part.from_text(text=message)]
        if image_data:
            try:
                image_bytes = base64.b64decode(image_data)
                mime = image_mime_type or "image/png"
                parts.insert(0, types.Part.from_bytes(data=image_bytes, mime_type=mime))
            except Exception as e:
                yield f"\n[Image Error: {str(e)}]"
                return

        # Append current user prompt
        formatted_contents.append(types.Content(role="user", parts=parts))

        try:
            # Stream chunked text from Gemini API
            response = self.client.models.generate_content_stream(
                model=model,
                contents=formatted_contents,
                config=config
            )
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"\n[API Error: {str(e)}]"