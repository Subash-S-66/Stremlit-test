import math

def calculate_difficulty_distribution(total_questions: int, easy_pct: int, medium_pct: int, hard_pct: int) -> dict[str, int]:
    """
    Calculates exact counts for Easy, Medium, and Hard based on percentages and total questions.
    Uses floor division first. The remainder is given to the category with the highest percentage.
    In case of ties for highest percentage, priority is: Hard > Medium > Easy.
    """
    easy_count = math.floor((easy_pct / 100) * total_questions)
    medium_count = math.floor((medium_pct / 100) * total_questions)
    hard_count = math.floor((hard_pct / 100) * total_questions)

    allocated = easy_count + medium_count + hard_count
    remaining = total_questions - allocated

    if remaining > 0:
        # Create a list of tuples to keep track of category, percentage, and priority level.
        # Priority level: Hard (3) > Medium (2) > Easy (1)
        categories = [
            ("Hard", hard_pct, 3),
            ("Medium", medium_pct, 2),
            ("Easy", easy_pct, 1)
        ]

        # Sort based on:
        # 1. Percentage (descending)
        # 2. Priority level (descending)
        categories.sort(key=lambda x: (x[1], x[2]), reverse=True)

        # Distribute remaining questions one by one based on sorted order
        for i in range(remaining):
            category_name = categories[i % len(categories)][0]
            if category_name == "Hard":
                hard_count += 1
            elif category_name == "Medium":
                medium_count += 1
            elif category_name == "Easy":
                easy_count += 1

    return {
        "Easy": easy_count,
        "Medium": medium_count,
        "Hard": hard_count
    }

def calculate_total_marks(distribution: dict[int, int]) -> int:
    """
    Calculates total marks based on a dictionary mapping marks to the number of questions.
    e.g., {1: 5, 2: 3} -> 1*5 + 2*3 = 11
    """
    total = 0
    for mark, count in distribution.items():
        total += mark * count
    return total

def get_section_letter(index: int) -> str:
    """
    Returns an uppercase letter corresponding to the 0-based index.
    0 -> A, 1 -> B, 2 -> C...
    """
    return chr(65 + index)
