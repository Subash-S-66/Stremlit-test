import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'question_paper_generator'))

from validator import validate_total, validate_mix, validate_inputs
from utils import calculate_difficulty_distribution

print("=== Validation Tests ===")

# Test Input Validator
assert validate_inputs("Math", "Algebra") == (True, "")
assert validate_inputs("", "Algebra")[0] == False
assert validate_inputs("Math", "")[0] == False

# Test Total Validator
assert validate_total(10, 10) == (True, "")
assert validate_total(10, 9)[0] == False
assert validate_total(51, 51)[0] == False # Max total questions is 50

# Test Mix Validator
assert validate_mix(34, 33, 33) == (True, "")
assert validate_mix(34, 34, 34)[0] == False
assert validate_mix(0, 0, 100) == (True, "")

# Test Difficulty Distribution Math
# 10 questions, 33/33/34. Expected: Easy:3, Med:3, Hard:3 + remaining 1 given to Easy (34%) -> 4,3,3
print(calculate_difficulty_distribution(10, 34, 33, 33))
assert calculate_difficulty_distribution(10, 34, 33, 33) == {'Easy': 4, 'Medium': 3, 'Hard': 3}

# 10 questions, 33/34/33. Medium gets the remainder
assert calculate_difficulty_distribution(10, 33, 34, 33) == {'Easy': 3, 'Medium': 4, 'Hard': 3}

# Tie Breaking Test
# 10 questions, 35/35/30
# 3/3/3 = 9. 1 remaining.
# Tie between Easy(35) and Medium(35). Medium > Easy priority. So Medium gets it. -> 3,4,3
print(calculate_difficulty_distribution(10, 35, 35, 30))
assert calculate_difficulty_distribution(10, 35, 35, 30) == {'Easy': 3, 'Medium': 4, 'Hard': 3}

# 10 questions, 35/30/35
# 3/3/3 = 9. 1 remaining.
# Tie between Easy(35) and Hard(35). Hard > Easy priority. So Hard gets it. -> 3,3,4
print(calculate_difficulty_distribution(10, 35, 30, 35))
assert calculate_difficulty_distribution(10, 35, 30, 35) == {'Easy': 3, 'Medium': 3, 'Hard': 4}

print("All tests passed.")
