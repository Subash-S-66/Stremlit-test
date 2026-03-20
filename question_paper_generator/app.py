import os
import streamlit as st
from config import Config
from validator import validate_total, validate_mix, validate_inputs
from utils import calculate_difficulty_distribution
from generator import generate_questions_for_mark
from pdf_builder import create_pdf

# Set up page configuration
st.set_page_config(page_title="AI Question Paper Generator", layout="centered")

def init_session_state():
    """Initializes standard session state variables if they don't exist."""
    if "pdf_path" not in st.session_state:
        st.session_state.pdf_path = None
    if "is_generating" not in st.session_state:
        st.session_state.is_generating = False

init_session_state()

st.title("🎓 AI Question Paper Generator")

# Optional Reset Button
if st.button("Reset Generated Paper"):
    st.session_state.pdf_path = None
    st.rerun()

with st.form("generator_form"):
    st.header("1. Subject Info")
    subject = st.text_input("Subject")
    topic = st.text_input("Topic")

    st.header("2. Total Questions")
    total_questions = st.number_input("Total Questions", min_value=1, max_value=Config.MAX_TOTAL_QUESTIONS, value=10, step=1)

    st.header("3. Question Distribution (Marks)")
    st.write(f"Distribute exactly {total_questions} questions across the allowed marks.")

    cols = st.columns(len(Config.ALLOWED_MARKS))
    distribution = {}
    for idx, mark in enumerate(Config.ALLOWED_MARKS):
        with cols[idx]:
            # Initial value is total_questions for the first box just to be helpful, 0 for rest
            init_val = total_questions if idx == 0 else 0
            count = st.number_input(f"{mark} Mark", min_value=0, max_value=total_questions, value=init_val, step=1, key=f"mark_{mark}")
            distribution[mark] = count

    st.header("4. Difficulty Level")
    difficulty = st.selectbox("Select Difficulty", Config.DIFFICULTIES)

    # Variables for Mix difficulty
    easy_pct, medium_pct, hard_pct = 0, 0, 0

    # Because we are inside a form, we cannot use a dynamic `if difficulty == "Mix"` to show/hide other fields interactively.
    # So we show the Mix percentages always but note that they are only used if "Mix" is selected.
    st.subheader("Mix Distribution (%) (Only applies if 'Mix' difficulty is selected)")
    st.write("Sum must equal 100%")
    col_e, col_m, col_h = st.columns(3)
    with col_e:
        easy_pct = st.number_input("Easy %", min_value=0, max_value=100, value=34, step=1)
    with col_m:
        medium_pct = st.number_input("Medium %", min_value=0, max_value=100, value=33, step=1)
    with col_h:
        hard_pct = st.number_input("Hard %", min_value=0, max_value=100, value=33, step=1)

    submitted = st.form_submit_button("Generate Question Paper")

if submitted:
    # --- VALIDATION STAGE ---

    # 1. Input Validation
    is_valid_inputs, msg_inputs = validate_inputs(subject, topic)
    if not is_valid_inputs:
        st.error(msg_inputs)
        st.stop()

    # 2. Total/Distribution Validation
    distribution_sum = sum(distribution.values())
    is_valid_total, msg_total = validate_total(total_questions, distribution_sum)
    if not is_valid_total:
        st.error(msg_total)
        st.stop()

    # 3. Mix Validation (if applicable)
    if difficulty == "Mix":
        is_valid_mix, msg_mix = validate_mix(easy_pct, medium_pct, hard_pct)
        if not is_valid_mix:
            st.error(msg_mix)
            st.stop()

    # --- GENERATION STAGE ---
    st.session_state.is_generating = True
    st.session_state.pdf_path = None

    questions_data = {}

    with st.spinner("Generating question paper using Gemini... Please wait."):
        try:
            for mark in sorted(Config.ALLOWED_MARKS):
                count = distribution[mark]
                if count > 0:
                    st.toast(f"Generating {count} questions for {mark} marks...")

                    if difficulty == "Mix":
                        # Calculate exact counts for this specific mark category based on percentages
                        diff_info = calculate_difficulty_distribution(count, easy_pct, medium_pct, hard_pct)
                    else:
                        diff_info = difficulty

                    questions = generate_questions_for_mark(subject, topic, mark, count, diff_info)

                    # Store generated questions
                    questions_data[mark] = questions

            # --- PDF CREATION STAGE ---
            output_dir = "assets"
            os.makedirs(output_dir, exist_ok=True)
            output_file = os.path.join(output_dir, "question_paper.pdf")

            # Build the PDF
            pdf_path = create_pdf(subject, topic, questions_data, output_file)
            st.session_state.pdf_path = pdf_path

            st.success("Question paper generated successfully!")

        except Exception as e:
            st.error(f"An error occurred during generation: {str(e)}")
            st.session_state.is_generating = False
            st.stop()

# --- DOWNLOAD STAGE ---
if st.session_state.pdf_path and os.path.exists(st.session_state.pdf_path):
    with open(st.session_state.pdf_path, "rb") as pdf_file:
        pdf_bytes = pdf_file.read()

    st.download_button(
        label="Download Question Paper PDF",
        data=pdf_bytes,
        file_name="question_paper.pdf",
        mime="application/pdf",
        type="primary"
    )
