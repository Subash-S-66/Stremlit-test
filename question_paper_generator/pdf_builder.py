import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from utils import get_section_letter, calculate_total_marks

def create_pdf(subject: str, topic: str, questions_data: dict[int, list[str]], output_path: str):
    """
    Creates a professionally formatted PDF for the question paper.
    questions_data: a dictionary mapping mark value -> list of questions.
    Only includes sections that have questions, ordered in ascending mark value.
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=50, leftMargin=50,
        topMargin=50, bottomMargin=50
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=15
    )

    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        alignment=TA_CENTER,
        spaceAfter=25
    )

    section_heading_style = ParagraphStyle(
        'SectionHeadingStyle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        alignment=TA_LEFT,
        spaceAfter=12,
        spaceBefore=20
    )

    question_style = ParagraphStyle(
        'QuestionStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        alignment=TA_LEFT,
        spaceAfter=10,
        leading=16
    )

    story = []

    # Header
    story.append(Paragraph("<b>QUESTION PAPER</b>", title_style))

    # Calculate total marks from questions_data
    distribution_for_marks = {mark: len(qs) for mark, qs in questions_data.items()}
    total_marks = calculate_total_marks(distribution_for_marks)

    meta_info = f"<b>Subject:</b> {subject} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Topic:</b> {topic}<br/><b>Total Marks:</b> {total_marks}"
    story.append(Paragraph(meta_info, meta_style))
    story.append(Spacer(1, 15))

    # Sections (Ascending Order)
    # Filter only marks that have questions generated
    active_marks = sorted([mark for mark in questions_data.keys() if questions_data[mark]])

    for section_idx, mark in enumerate(active_marks):
        section_letter = get_section_letter(section_idx)
        questions = questions_data[mark]

        # Section Heading: e.g., Part A (1 Mark) / Part B (2 Marks)
        mark_label = "Mark" if mark == 1 else "Marks"
        heading_text = f"<b>Part {section_letter} ({mark} {mark_label})</b>"
        story.append(Paragraph(heading_text, section_heading_style))

        # Questions properly formatted with restarted numbering
        for q_idx, question_text in enumerate(questions, start=1):
            # Replacing standard newlines with HTML breaks to preserve formatting in Paragraph
            formatted_text = question_text.replace('\n', '<br/>')
            para_text = f"{q_idx}. {formatted_text}"
            story.append(Paragraph(para_text, question_style))

        story.append(Spacer(1, 10))

    doc.build(story)
    return output_path
