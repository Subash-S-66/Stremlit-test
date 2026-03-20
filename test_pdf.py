import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'question_paper_generator'))

from pdf_builder import create_pdf

questions_data = {
    1: ["Q1 MCQ", "Q2 MCQ", "Q3 MCQ", "Q4 MCQ", "Q5 MCQ", "Q6 MCQ", "Q7 MCQ", "Q8 MCQ", "Q9 MCQ", "Q10 MCQ"],
    5: ["Long Q1", "Long Q2"]
}

create_pdf("Computer Science", "Networks", questions_data, "test_output.pdf")
print("PDF built successfully. Check test_output.pdf")
