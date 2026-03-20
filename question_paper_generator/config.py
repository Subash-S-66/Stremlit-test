import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

    # Validation constraints
    MAX_TOTAL_QUESTIONS = 50
    MAX_RETRIES = 2

    # Allowed marks in ascending order
    ALLOWED_MARKS = [1, 2, 6, 8, 12, 16]

    # Difficulty levels
    DIFFICULTIES = ["Easy", "Medium", "Hard", "Mix"]
