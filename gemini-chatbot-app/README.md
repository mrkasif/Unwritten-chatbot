# Unwritten — Chatbot App

A full-stack streaming chatbot powered by Google Gemini with text, image, and persistent session support.

## Tech Stack

- **Backend:** FastAPI + google-genai
- **Frontend:** Streamlit
- **AI:** Google Gemini (gemini-2.5-flash / gemini-2.5-pro)
- **Persistence:** SQLite (sessions + message history, survives page refreshes)

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create your `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

3. Add your Gemini API key to `.env` (optional — you can also enter it in the UI at runtime):
   ```
   GEMINI_API_KEY=your-api-key-here
   ```

## Run (local)

Start the backend (terminal 1):
```bash
uvicorn backend.main:app --reload
```

Start the frontend (terminal 2):
```bash
streamlit run frontend/app.py
```

Open http://localhost:8501 in your browser.

## Run (Docker)

Set your API key, then start both services:

```bash
export GEMINI_API_KEY=your-api-key-here
docker compose up --build
```

- Backend API: http://localhost:8000
- Streamlit UI: http://localhost:8501

Chat history is persisted to `./data/chat.db` (mounted into the backend container).

## API Endpoints

| Method | Endpoint                          | Description                       |
|--------|-----------------------------------|-----------------------------------|
| POST   | `/api/chat/stream`                | Streaming chat (text/image/base64) |
| GET    | `/api/health`                     | Health check                      |
| POST   | `/api/sessions`                   | Create a new session              |
| GET    | `/api/sessions`                   | List sessions                     |
| GET    | `/api/sessions/{id}/messages`     | Load a session's history          |
| DELETE | `/api/sessions/{id}/messages`     | Clear a session's history         |
| DELETE | `/api/sessions/{id}`              | Delete a session                  |

## Project Structure

```
gemini-chatbot-app/
├── .env.example              # API credentials template
├── requirements.txt          # Python dependencies
├── Dockerfile.backend        # FastAPI container
├── Dockerfile.frontend       # Streamlit container
├── docker-compose.yml        # Run both services together
├── README.md
├── backend/
│   ├── __init__.py
│   ├── main.py               # FastAPI routes, CORS, lifespan, streaming
│   ├── gemini_client.py      # Gemini API wrapper (streaming, images)
│   ├── models.py             # SQLModel: ChatSession + ChatMessage
│   └── database.py           # SQLModel engine, get_session, create_db_and_tables
└── frontend/
    └── app.py                # Streamlit UI & session manager
```