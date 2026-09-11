# Unwritten — Chatbot App

AI chat assistant powered by Google Gemini, shipped in two flavors:

## Deployments

### 1. `gemini-chatbot-app` — Local App (FastAPI + Streamlit)

Full-featured local chatbot with dark glassmorphism UI, live token streaming, image attachment, and persistent chat sessions.

- **Backend:** FastAPI + `google-genai` (streaming), SQLModel + SQLite session persistence
- **Frontend:** Streamlit
- **Run:** `uvicorn backend.main:app --reload` + `streamlit run frontend/app.py`
- **Docker:** `docker compose up --build`

```
gemini-chatbot-app/
├── backend/
│   ├── main.py               # FastAPI routes, CORS, lifespan, streaming
│   ├── gemini_client.py      # Gemini API wrapper (streaming, images)
│   ├── models.py             # SQLModel: ChatSession + ChatMessage
│   └── database.py           # SQLModel engine + session dependency
└── frontend/
    └── app.py                # Streamlit UI & session manager
```

### 2. `gemini-vercel-app` — Serverless (Next.js + FastAPI Function)

Web-first version for the Vercel platform. Stateless (history via `localStorage`).

- **Frontend:** Next.js (App Router) + Tailwind — streaming chat UI
- **Backend:** FastAPI Python Serverless Function (`api/index.py`)
- **Deploy:** `npx vercel --prod` (set `GEMINI_API_KEY` in Vercel env vars)

```
gemini-vercel-app/
├── api/
│   ├── index.py              # FastAPI serverless function
│   └── requirements.txt
└── app/
    ├── page.tsx              # Chat UI
    ├── layout.tsx
    └── globals.css
```

## Features

- Dark-mode glassmorphism UI with rounded message bubbles and user/bot avatars
- Real-time token streaming with typing cursor (▌)
- Model selection (`gemini-2.5-flash` / `gemini-2.5-pro`), temperature slider, system persona
- Dynamic API key entry (or `GEMINI_API_KEY` env / Vercel env var)
- Image attachment (base64) supported by both backends
- Session/thread persistence (SQLite locally, `localStorage` on Vercel)
- Chat history export (local app)