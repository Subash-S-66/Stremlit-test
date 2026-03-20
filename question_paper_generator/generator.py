import os
import time
import re
import google.generativeai as genai
from config import Config

def init_gemini():
    """Initializes the Gemini API with the key from config."""
    api_key = Config.GEMINI_API_KEY
    if not api_key or api_key == "your_api_key_here":
        raise ValueError("Valid Gemini API Key not found in environment variables. Please check your .env file.")
    genai.configure(api_key=api_key)

def build_prompt(subject: str, topic: str, mark: int, count: int, difficulty_info) -> str:
    """
    Constructs the prompt for Gemini to generate the exact number of questions.
    `difficulty_info` should either be a string (e.g., "Easy") or a dictionary mapping
    difficulty levels to exact counts for this specific mark category.
    """
    prompt = f"You are an expert university-level examiner. Generate EXACTLY {count} distinct questions for the subject '{subject}' focusing on the topic '{topic}'.\n\n"

    prompt += f"Each question is worth {mark} marks.\n"

    if isinstance(difficulty_info, dict):
        prompt += "The difficulty distribution for these specific questions MUST be exactly:\n"
        for diff, diff_count in difficulty_info.items():
            if diff_count > 0:
                prompt += f"- {diff_count} {diff} questions\n"
    else:
        prompt += f"All questions MUST be of {difficulty_info} difficulty.\n"

    prompt += """
STRICT RULES - YOU MUST FOLLOW THESE OR FAIL:
1. Provide ONLY the text of the questions. Absolutely NO answers, NO hints, NO explanations, NO rubrics.
2. Ensure there is NO repetition among the questions.
3. The questions must be of strict exam-level quality. Include conceptual and application-based problems, not just trivial definitions.
4. DO NOT include any introductory greetings, concluding remarks, or metadata (e.g., "Here are the questions:" or "End of paper").
5. Write each individual question strictly on a single continuous line if possible, or format it cleanly.
6. Number the questions sequentially starting from 1 (e.g., "1. ", "2. ", etc.).
"""
    return prompt

def generate_questions_for_mark(subject: str, topic: str, mark: int, count: int, difficulty_info) -> list[str]:
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
            if not response.text:
                raise ValueError("Received empty response from Gemini.")

            # Basic cleanup: split by newlines, filter empty lines
            raw_lines = [line.strip() for line in response.text.split('\n') if line.strip()]

            clean_questions = []
            for line in raw_lines:
                # Use regex to strip leading numbers, dots, dashes, and asterisks.
                # E.g., "1. What is...", "* What is...", "- 1. What is..." -> "What is..."
                # This ensures we don't accidentally strip valid numbers inside the text itself
                # that `lstrip` might if used improperly.
                cleaned = re.sub(r'^[\d\s\.\-\*]+', '', line).strip()
                if cleaned:
                    clean_questions.append(cleaned)

            # If the model groups a single question into multiple lines,
            # this might split them. However, our prompt requests "each individual question strictly on a single continuous line".
            # For robustness, we return exactly what the model gave us cleaned up.

            # If the API returned zero valid questions, raise error to trigger retry
            if not clean_questions:
                raise ValueError("Failed to parse valid questions from the response.")

            # If the model returned more than requested (rare but happens), truncate.
            # If less, we take what we have (retry could be risky if it consistently under-generates).
            if len(clean_questions) > count:
                clean_questions = clean_questions[:count]

            return clean_questions
        except Exception as e:
            if attempt < Config.MAX_RETRIES:
                time.sleep(2)  # Short delay before retry
                continue
            else:
                raise Exception(f"Failed to generate {mark}-mark questions after {Config.MAX_RETRIES + 1} attempts. Last error: {str(e)}")
