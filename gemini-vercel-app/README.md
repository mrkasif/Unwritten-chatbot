# Unwritten — Vercel FastAPI Edition

Serverless FastAPI backend for the Unwritten chatbot. Pure Python, no
frontend build step — runs as a single Vercel Python Serverless Function.

## Structure

```
gemini-vercel-app/
├── api/
│   └── index.py            # FastAPI entry point & routes
├── vercel.json             # @vercel/python builder + routing
└── requirements.txt        # Python dependencies
```

## Endpoints

- `GET /` → `{"status": "FastAPI is running on Vercel!"}`
- `POST /api/chat/stream` → Server-Sent stream of Gemini text chunks

## Request body (`/api/chat/stream`)

```json
{
  "message": "Hello",
  "history": [{"role": "user", "content": "hi"}],
  "api_key": "optional client-supplied key",
  "model": "gemini-2.5-flash",
  "temperature": 0.7
}
```

`api_key` is optional — if omitted, the server falls back to the
`GEMINI_API_KEY` environment variable.

## Run locally

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt   # Windows
# (or: source .venv/bin/activate && pip install -r requirements.txt)

$env:GEMINI_API_KEY = "your key"               # Windows PowerShell
# (or: export GEMINI_API_KEY="your key")

uvicorn api.index:app --reload --port 8000
```

Open http://localhost:8000 and test `/api/chat/stream`.

## Deploy to Vercel

1. Push this folder's contents to a Git repo connected to Vercel, or run
   `npx vercel --prod` from this directory.
2. Set the `GEMINI_API_KEY` environment variable in your Vercel project.