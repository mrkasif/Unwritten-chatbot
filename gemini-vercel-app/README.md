# Unwritten — Vercel Edition

Serverless version of the Unwritten chatbot. Next.js (App Router + Tailwind) frontend talking to a FastAPI Python Serverless Function, with Google Gemini streaming.

## Architecture

Because Vercel Functions are stateless, this variant drops SQLite:

- **Frontend:** Next.js / React chat UI (`app/`) — dark theme, sticky input, streaming `▌`.
- **Backend:** FastAPI wrapped as a Python Serverless Function (`api/index.py`) with `StreamingResponse` (streaming is on by default for the Python runtime).
- **State:** Chat history persists per-browser via `localStorage` (there is no server-side database).

```
gemini-vercel-app/
├── api/
│   ├── index.py              # FastAPI serverless function (/api/chat/stream)
│   └── requirements.txt      # Python deps
├── app/
│   ├── page.tsx              # Chat UI
│   ├── layout.tsx
│   └── globals.css
├── vercel.json               # Routed /api/* -> api/index.py
└── package.json
```

## Run locally

Requires Vercel CLI (runs both Next.js and the Python function):

```bash
npm install
vercel dev
```

Open http://localhost:3000 and add your Gemini key in the sidebar (or set `GEMINI_API_KEY`), then chat.

## Deploy to Vercel

1. Push the folder to a Git repo, or run:
   ```bash
   npx vercel
   npx vercel --prod
   ```

2. Add the environment variable in Vercel (Project → Settings → Environment Variables), or simply paste the key at runtime into the UI sidebar:
   ```
   GEMINI_API_KEY=<your-key>
   ```

3. The app is served from your Vercel URL. API docs are at `/docs`.

## Notes

- Streaming is enabled by default for Python Vercel Functions; `maxDuration: 60` is set in `vercel.json` for long LLM streams.
- The API key entered in the sidebar is sent with each request on the client side (falls back to `GEMINI_API_KEY` on the server). For production, prefer server-side env var only.
- Image payloads (`image_data` base64) are supported by the API but not exposed in the UI.