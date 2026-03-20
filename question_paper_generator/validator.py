from config import Config

def validate_total(total_questions: int, distribution_sum: int) -> tuple[bool, str]:
    """
    Validates the total number of questions and checks if the distribution matches the total.
    """
    if total_questions <= 0:
        return False, "Total questions must be greater than 0."

    if total_questions > Config.MAX_TOTAL_QUESTIONS:
        return False, f"Total questions cannot exceed {Config.MAX_TOTAL_QUESTIONS}."

    if distribution_sum != total_questions:
        return False, f"Sum of distributed questions ({distribution_sum}) must exactly equal the total questions ({total_questions})."

    return True, ""

def validate_mix(easy_pct: int, medium_pct: int, hard_pct: int) -> tuple[bool, str]:
    """
    Validates if the sum of percentages for mix difficulty equals 100.
    """
    total_pct = easy_pct + medium_pct + hard_pct
    if total_pct != 100:
        return False, f"Sum of difficulty percentages must equal 100%. Current sum: {total_pct}%."

    return True, ""

def validate_inputs(subject: str, topic: str) -> tuple[bool, str]:
    """
    Validates that basic string inputs are not empty.
    """
    if not subject.strip():
        return False, "Subject cannot be empty."
    if not topic.strip():
        return False, "Topic cannot be empty."

    return True, ""
