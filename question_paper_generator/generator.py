import os
import time
import google.generativeai as genai
from config import Config

def init_gemini():
    """Initializes the Gemini API with the key from config."""
    api_key = Config.GEMINI_API_KEY
    if not api_key or api_key == "your_api_key_here":
        raise ValueError("Valid Gemini API Key not found in environment variables.")
    genai.configure(api_key=api_key)

def build_prompt(subject: str, topic: str, mark: int, count: int, difficulty_info: dict) -> str:
    """
    Constructs the prompt for Gemini to generate the exact number of questions.
    `difficulty_info` should either be a string (e.g., "Easy") or a dictionary mapping
    difficulty levels to exact counts for this specific mark category.
    """
    prompt = f"You are an expert academic examiner. Generate exactly {count} university-level questions for the subject '{subject}' focusing on the topic '{topic}'.\n\n"

    prompt += f"Each question should be worth {mark} marks.\n"

    if isinstance(difficulty_info, dict):
        prompt += "The difficulty distribution for these questions MUST be exactly:\n"
        for diff, diff_count in difficulty_info.items():
            if diff_count > 0:
                prompt += f"- {diff_count} {diff} questions\n"
    else:
        prompt += f"All questions should be of {difficulty_info} difficulty.\n"

    prompt += """
STRICT RULES:
1. Provide ONLY the questions. Do NOT provide answers, hints, or explanations.
2. Ensure there is no repetition among the questions.
3. The questions must be of exam-level quality, conceptual, and application-based (not just simple definitions).
4. Do NOT include any introductory or concluding text (e.g., "Here are the questions:").
5. Number the questions starting from 1 sequentially (e.g., 1., 2., 3., ...).
6. Format the output cleanly, with each question on a new line.
"""
    return prompt

def generate_questions_for_mark(subject: str, topic: str, mark: int, count: int, difficulty_info: dict) -> list[str]:
    """
    Makes the API call to Gemini to generate questions for a specific mark category.
    Implements retry logic up to Config.MAX_RETRIES.
    """
    init_gemini()
    model = genai.GenerativeModel(Config.GEMINI_MODEL)
    prompt = build_prompt(subject, topic, mark, count, difficulty_info)

    for attempt in range(Config.MAX_RETRIES + 1):
        try:
            response = model.generate_content(prompt)
            # Basic cleanup: split by newlines, filter empty lines
            raw_lines = [line.strip() for line in response.text.split('\n') if line.strip()]

            # Additional cleanup: Remove any markdown bullet points or extra numbers Gemini might add.
            # We want to return a list of raw question strings so the PDF builder can number them properly.
            clean_questions = []
            for line in raw_lines:
                # Remove leading numbers/bullets (e.g., "1.", "-", "*")
                cleaned = line.lstrip("0123456789. -*")
                if cleaned:
                    clean_questions.append(cleaned)

            if not clean_questions:
                raise ValueError("Received empty or improperly formatted response from Gemini.")

            return clean_questions
        except Exception as e:
            if attempt < Config.MAX_RETRIES:
                time.sleep(2)  # Short delay before retry
                continue
            else:
                raise Exception(f"Failed to generate {mark}-mark questions after {Config.MAX_RETRIES + 1} attempts. Error: {str(e)}")
