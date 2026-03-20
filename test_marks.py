import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'question_paper_generator'))

from validator import validate_marks_limit

# Test Validation Logic
assert validate_marks_limit(100, 100) == (True, "")
assert validate_marks_limit(100, 90) == (True, "")
assert validate_marks_limit(100, 110)[0] == False
assert "exceeds the allowed total marks (100)" in validate_marks_limit(100, 110)[1]
assert validate_marks_limit(-5, 10)[0] == False
print("Test completed successfully.")
