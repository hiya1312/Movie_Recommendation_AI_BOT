# config.py
import os

try:
    import streamlit as st
    _secrets = st.secrets
except Exception:
    _secrets = {}

def _get(key):
    if _secrets and key in _secrets:
        return _secrets[key]
    return os.environ.get(key, "")

GROQ_API_KEY    = _get("GROQ_API_KEY")
VISION_KEY      = _get("VISION_KEY")
VISION_ENDPOINT = _get("VISION_ENDPOINT")
SPEECH_KEY      = _get("SPEECH_KEY")
SPEECH_REGION   = _get("SPEECH_REGION")
