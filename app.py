# app.py
import streamlit as st
import tempfile
import os
from utils.recommender import get_recommendation
from utils.vision import analyse_image
from utils.speech import speech_to_text, text_to_speech

st.set_page_config(
    page_title="CineMind — Movie Recommendations",
    page_icon="🎬",
    layout="centered"
)

# ── Custom CSS (light theme) ───────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Page background ── */
.stApp {
    background: #f5f7fa;
}

/* ── Hero header ── */
.hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 20px;
    padding: 36px 32px 28px;
    margin-bottom: 28px;
    text-align: center;
    color: white;
}
.hero h1 { font-size: 2rem; font-weight: 700; margin: 0 0 6px; }
.hero p  { font-size: 0.95rem; opacity: 0.85; margin: 0; }

/* ── Cards ── */
.card {
    background: white;
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
}
.card-title {
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #7c3aed;
}

/* ── Mode selector pills ── */
div[data-testid="stRadio"] > label { display: none; }
div[data-testid="stRadio"] > div {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}
div[data-testid="stRadio"] > div > label {
    background: #f0ebff;
    color: #5b21b6;
    border-radius: 50px;
    padding: 8px 20px;
    font-weight: 500;
    font-size: 0.9rem;
    cursor: pointer;
    border: 2px solid transparent;
    transition: all 0.2s;
}
div[data-testid="stRadio"] > div > label:hover {
    border-color: #7c3aed;
}
div[data-testid="stRadio"] > div > label[data-baseweb="radio"] input:checked + div {
    color: purple;
}

/* ── Primary button ── */
.stButton > button {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white !important;
    border: none;
    border-radius: 12px;
    padding: 12px 28px;
    font-weight: 600;
    font-size: 0.95rem;
    transition: all 0.2s;
    box-shadow: 0 4px 14px rgba(102,126,234,0.35);
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(102,126,234,0.45);
}
.stButton > button:active { transform: translateY(0); }

/* ── Text inputs ── */
.stTextInput > div > div > input {
    border-radius: 10px;
    border: 1.5px solid #e5e7eb;
    font-size: 0.95rem;
    transition: border 0.2s;
    background: white;
}
.stTextInput > div > div > input:focus {
    border-color: #7c3aed;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.1);
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    border: 2px dashed #c4b5fd;
    border-radius: 14px;
    background: #faf5ff;
    padding: 12px;
}

/* ── Recommendation output box ── */
.rec-box {
    background: white;
    border-left: 4px solid #7c3aed;
    border-radius: 14px;
    padding: 24px 28px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    margin-top: 8px;
}

/* ── History expander ── */
[data-testid="stExpander"] {
    background: white;
    border-radius: 12px;
    border: 1px solid #ede9fe;
    margin-bottom: 10px;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: white;
    border-right: 1px solid #f0ebff;
}
.sidebar-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #f5f3ff;
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 8px;
    font-size: 0.88rem;
    font-weight: 500;
    color: #4c1d95;
    width: 100%;
}

/* ── Divider ── */
hr { border: none; border-top: 1px solid #ede9fe; margin: 24px 0; }

/* ── Success / info / warning override ── */
[data-testid="stAlert"] { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🎬 CineMind</h1>
    <p>AI-powered movie recommendations via text, voice, or image</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎬 CineMind")
    st.markdown("Your personal AI film curator — describe a mood, speak, or upload a poster.")
    st.markdown("---")
    st.markdown("**Powered by**")
    for badge in [
        ("🧠", "Groq LLaMA 3.3 70B", "Recommendations"),
        ("👁️", "Azure Computer Vision", "Image analysis"),
        ("🎤", "Azure Speech Service", "Voice input / TTS"),
    ]:
        st.markdown(
            f'<div class="sidebar-badge">{badge[0]} <span><b>{badge[1]}</b><br><small style="opacity:0.6">{badge[2]}</small></span></div>',
            unsafe_allow_html=True
        )
    st.markdown("---")
    if "history" in st.session_state:
        st.markdown(f"**Sessions today:** {len(st.session_state.history)}")

# ── Input mode ────────────────────────────────────────────
st.markdown('<div class="card"><div class="card-title">Choose your input method</div>', unsafe_allow_html=True)
mode = st.radio("", ["💬 Text", "🎤 Voice", "🖼️ Image"], horizontal=True)
st.markdown('</div>', unsafe_allow_html=True)

user_text         = ""
image_description = None

# TEXT MODE
if mode == "💬 Text":
    st.markdown('<div class="card"><div class="card-title">Describe your mood</div>', unsafe_allow_html=True)
    user_text = st.text_input(
        "",
        placeholder="e.g. I want something funny and light-hearted tonight",
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# VOICE MODE
elif mode == "🎤 Voice":
    st.markdown('<div class="card"><div class="card-title">Voice input</div>', unsafe_allow_html=True)
    st.info("Record your movie preference below, then click Transcribe.")
    audio_input = st.audio_input("Record your voice")
    if audio_input and st.button("🎤  Transcribe", use_container_width=True):
        with st.spinner("Transcribing..."):
            try:
                recognised = speech_to_text(audio_input.read())
            except RuntimeError as e:
                st.error(str(e))
                recognised = ""
        if recognised:
            st.session_state["voice_text"] = recognised
            st.session_state["auto_recommend"] = True
            st.success(f"Heard: **{recognised}**")
        else:
            st.error("Could not recognise speech. Please try again.")

    if st.session_state.get("voice_text"):
        user_text = st.session_state["voice_text"]
        st.markdown(f"> 🗣️ **You said:** {user_text}")
    st.markdown('</div>', unsafe_allow_html=True)

# IMAGE MODE
elif mode == "🖼️ Image":
    st.markdown('<div class="card"><div class="card-title">Upload an image</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Drop a movie poster, mood board, or any scene",
        type=["jpg", "jpeg", "png"],
        label_visibility="visible"
    )
    user_text = st.text_input(
        "Add a message (optional)",
        placeholder="e.g. recommend something with this kind of vibe"
    )
    if uploaded:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(uploaded.read())
            tmp_path = tmp.name

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image(tmp_path, caption="Your uploaded image", use_container_width=True)

        with st.spinner("Analysing with Azure Vision..."):
            image_description = analyse_image(tmp_path)
        st.success(f"**Azure detected:** {image_description}")
        os.unlink(tmp_path)
        if not user_text:
            user_text = "recommend movies based on this image"
    st.markdown('</div>', unsafe_allow_html=True)

# ── Get recommendation ────────────────────────────────────
auto_trigger = st.session_state.pop("auto_recommend", False)

st.markdown("")
if st.button("🎯  Get Movie Recommendations", use_container_width=True) or auto_trigger:
    if not user_text:
        st.warning("Please enter text, record voice, or upload an image first.")
    else:
        st.markdown("---")
        st.markdown("### 🎬 Your Recommendations")
        st.markdown('<div class="rec-box">', unsafe_allow_html=True)
        response = st.write_stream(get_recommendation(user_text, image_description))
        st.markdown('</div>', unsafe_allow_html=True)

        if "history" not in st.session_state:
            st.session_state.history = []
        st.session_state.history.append({"user": user_text, "bot": response})
        st.session_state["last_response"] = response
        st.session_state.pop("voice_text", None)

# ── Read aloud ────────────────────────────────────────────
if st.session_state.get("last_response"):
    st.markdown("")
    if st.button("🔊  Read Recommendations Aloud", use_container_width=True):
        with st.spinner("Generating audio..."):
            try:
                audio_bytes = text_to_speech(st.session_state["last_response"])
                st.audio(audio_bytes, format="audio/wav", autoplay=True)
            except RuntimeError as e:
                st.error(str(e))

# ── Conversation history ──────────────────────────────────
if "history" in st.session_state and st.session_state.history:
    st.markdown("---")
    st.markdown("### 💬 Conversation History")
    for i, chat in enumerate(reversed(st.session_state.history[-5:])):
        with st.expander(f"Session {len(st.session_state.history) - i}  —  \"{chat['user'][:50]}\""):
            st.markdown(f"**You:** {chat['user']}")
            st.markdown("---")
            st.markdown(chat['bot'])
