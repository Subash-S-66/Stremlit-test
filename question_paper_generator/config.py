import os
from dotenv import load_dotenv

# Load environment variables from .env file (local dev)
load_dotenv()

def _get_secret(key: str, default: str | None = None) -> str | None:
    """Read from env first, then Streamlit secrets if available."""
    val = os.getenv(key)
    if val:
        return val
    try:
        import streamlit as st
        try:
            secrets = st.secrets
            # st.secrets can raise if not configured on Streamlit Cloud
            if hasattr(secrets, "get"):
                val = secrets.get(key)
                if val:
                    return val
            else:
                if key in secrets:
                    return secrets[key]
        except Exception:
            pass
    except Exception:
        pass
    return default

class Config:
    GEMINI_API_KEY = _get_secret("GEMINI_API_KEY")
    GEMINI_MODEL = _get_secret("GEMINI_MODEL", "gemini-1.5-flash")

    # Validation constraints
    MAX_TOTAL_QUESTIONS = 50
    MAX_RETRIES = 2

    # Allowed marks in ascending order
    ALLOWED_MARKS = [1, 2, 6, 8, 12, 16]

    # Difficulty levels
    DIFFICULTIES = ["Easy", "Medium", "Hard", "Mix"]
