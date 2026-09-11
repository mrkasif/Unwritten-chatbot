import os
import base64
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Unwritten",
    page_icon="⚡",
    layout="wide",
)

st.markdown("""
<style>
:root {
    --bg: #0E1117;
    --card: #161B22;
    --border: #30363D;
    --user-bubble: #1F2B38;
    --accent: #58A6FF;
    --text: #E6EDF3;
    --muted: #8B949E;
}

[data-testid="stAppViewContainer"] {
    background: var(--bg);
    color: var(--text);
}

[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 920px;
    padding-top: 2rem;
    padding-bottom: 9rem;
}

[data-testid="stSidebar"] {
    background: var(--card);
    border-right: 1px solid var(--border);
    color: var(--text);
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: var(--text);
}

div[data-testid="stMarkdownContainer"] p {
    color: var(--text);
}

div[data-testid="stChatMessage"] {
    background: rgba(22, 27, 34, 0.72);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 10px;
    backdrop-filter: blur(10px);
}

div[data-testid="stChatMessage"]:has([data-testid="stChatMessageUserAvatar"]) {
    background: rgba(31, 43, 56, 0.85);
    border-color: #3A4A5E;
}

[data-testid="stChatInput"] {
    border-radius: 24px;
    border: 1px solid var(--border);
    background: rgba(22, 27, 34, 0.85);
    backdrop-filter: blur(10px);
    padding: 6px 14px;
}

[data-testid="stChatInput"]:focus-within {
    border-color: var(--accent);
    box-shadow: 0 0 0 2px rgba(88, 166, 255, 0.25);
}

[data-testid="stChatInput"] input {
    color: var(--text);
}

.stButton > button {
    border-radius: 8px;
    border: 1px solid var(--border);
    background: #21262D;
    color: var(--text);
}

.stButton > button:hover {
    border-color: var(--accent);
    color: var(--accent);
}

[data-testid="stFileUploader"] {
    border-radius: 12px;
    border: 1px dashed var(--border);
    background: rgba(22, 27, 34, 0.6);
    padding: 8px;
}

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stSelectbox"] > div > div {
    background: #0D1117;
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

BACKEND_BASE = os.getenv("BACKEND_BASE", "http://localhost:8000")
BACKEND_URL = os.getenv("BACKEND_URL", f"{BACKEND_BASE}/api/chat/stream")


def api_get(path):
    try:
        resp = requests.get(f"{BACKEND_BASE}{path}", timeout=5)
        return resp.json() if resp.status_code == 200 else None
    except Exception:
        return None


def api_post(path):
    try:
        resp = requests.post(f"{BACKEND_BASE}{path}", timeout=5)
        return resp.json() if resp.status_code == 200 else None
    except Exception:
        return None


def api_delete(path):
    try:
        requests.delete(f"{BACKEND_BASE}{path}", timeout=5)
    except Exception:
        pass


def refresh_sessions():
    data = api_get("/api/sessions")
    sessions = data or []
    st.session_state.sessions = sessions
    return sessions


if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_image" not in st.session_state:
    st.session_state.pending_image = None

if "session_id" not in st.session_state:
    sessions = refresh_sessions()
    if sessions:
        st.session_state.session_id = sessions[0]["id"]
        st.session_state.messages = api_get(
            f"/api/sessions/{st.session_state.session_id}/messages"
        ) or []
    else:
        created = api_post("/api/sessions")
        st.session_state.session_id = created["id"] if created else None
        st.session_state.messages = []
else:
    refresh_sessions()

with st.sidebar:
    st.title("⚡ Settings & Models")

    user_api_key = st.text_input(
        "Gemini API Key",
        type="password",
        value=os.getenv("GEMINI_API_KEY", ""),
        help="Leave blank to input your key here at runtime.",
    )

    selected_model = st.selectbox(
        "Select Model",
        ["gemini-2.5-flash", "gemini-2.5-pro"],
        index=0,
    )

    temperature = st.slider(
        "Creativity (Temperature)",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.05,
    )

    system_prompt = st.text_area(
        "System Instruction (Persona)",
        value="You are a helpful, expert AI collaborator.",
        height=100,
    )

    st.markdown("---")

    st.markdown("### Conversations")
    session_list = st.session_state.get("sessions", [])
    session_ids = [s["id"] for s in session_list]
    session_labels = {s["id"]: s["title"][:45] for s in session_list}

    if session_ids and st.session_state.get("session_id") not in session_ids:
        st.session_state.session_id = session_ids[0]
        st.session_state.messages = api_get(
            f"/api/sessions/{session_ids[0]}/messages"
        ) or []

    if session_ids:
        current_index = max(session_ids.index(st.session_state["session_id"]), 0)
        selected_session = st.selectbox(
            "Switch Session",
            session_ids,
            index=current_index,
            format_func=lambda sid: session_labels.get(sid, sid),
            key="session_select",
        )
        if selected_session != st.session_state["session_id"]:
            st.session_state.session_id = selected_session
            st.session_state.messages = api_get(
                f"/api/sessions/{selected_session}/messages"
            ) or []
            st.rerun()
    else:
        st.caption("No saved conversations yet.")

    if st.button("➕ New Session"):
        created = api_post("/api/sessions")
        if created:
            st.session_state.session_id = created["id"]
            st.session_state.messages = []
            st.session_state.pending_image = None
            if "image_uploader" in st.session_state:
                del st.session_state["image_uploader"]
            refresh_sessions()
            st.rerun()

    if st.session_state.get("session_id") and st.button("🗑️ Delete Session"):
        api_delete(f"/api/sessions/{st.session_state['session_id']}")
        st.session_state.messages = []
        st.session_state.pending_image = None
        sessions = refresh_sessions()
        if sessions:
            st.session_state.session_id = sessions[0]["id"]
            st.session_state.messages = api_get(
                f"/api/sessions/{sessions[0]['id']}/messages"
            ) or []
        else:
            created = api_post("/api/sessions")
            st.session_state.session_id = created["id"] if created else None
        st.rerun()

    st.markdown("---")

    if st.button("🗑️ Clear Conversation"):
        if st.session_state.get("session_id"):
            api_delete(f"/api/sessions/{st.session_state['session_id']}/messages")
        st.session_state.messages = []
        st.session_state.pending_image = None
        if "image_uploader" in st.session_state:
            del st.session_state["image_uploader"]
        st.rerun()

    if st.session_state.messages:
        transcript = "\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages
        )
        st.download_button(
            label="📥 Export Chat History",
            data=transcript,
            file_name="gemini_chat_history.txt",
            mime="text/plain",
        )

st.title("✨ Unwritten")
st.caption("Chat space powered by FastAPI and Google Gemini")

uploaded_file = st.file_uploader(
    "📎 Attach an image",
    type=["png", "jpg", "jpeg"],
    key="image_uploader",
)

if uploaded_file is not None:
    st.session_state.pending_image = {
        "name": uploaded_file.name,
        "mime": uploaded_file.type or "image/png",
        "data": base64.b64encode(uploaded_file.getvalue()).decode(),
        "raw": uploaded_file.getvalue(),
    }

if st.session_state.pending_image:
    img = st.session_state.pending_image
    thumb_col, info_col = st.columns([1, 5])
    with thumb_col:
        st.image(img["raw"], width=120)
    with info_col:
        st.caption(f"📎 Attached: {img['name']}")
        if st.button("Remove image"):
            st.session_state.pending_image = None
            if "image_uploader" in st.session_state:
                del st.session_state["image_uploader"]
            st.rerun()

for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

if user_input := st.chat_input("Ask anything..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        full_response = ""

        payload = {
            "message": user_input,
            "history": st.session_state.messages[:-1],
            "api_key": user_api_key,
            "model": selected_model,
            "system_instruction": system_prompt,
            "temperature": temperature,
            "session_id": st.session_state.get("session_id"),
        }
        if st.session_state.pending_image:
            payload["image_data"] = st.session_state.pending_image["data"]
            payload["image_mime_type"] = st.session_state.pending_image["mime"]

        try:
            with requests.post(BACKEND_URL, json=payload, stream=True) as response:
                if response.status_code == 200:
                    for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                        if chunk:
                            full_response += chunk
                            placeholder.markdown(full_response + "▌")
                    placeholder.markdown(full_response)
                else:
                    full_response = f"Backend error: {response.status_code}"
                    placeholder.error(full_response)
        except Exception as e:
            full_response = f"Connection failed: {str(e)}"
            placeholder.error(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

    st.session_state.pending_image = None
    if "image_uploader" in st.session_state:
        del st.session_state["image_uploader"]
    st.rerun()