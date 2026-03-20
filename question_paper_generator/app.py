import os
import streamlit as st
from config import Config
from validator import validate_total, validate_mix, validate_inputs, validate_marks_limit
from utils import calculate_difficulty_distribution, calculate_total_marks
from generator import generate_questions_for_mark
from pdf_builder import create_pdf

# Set up page configuration
st.set_page_config(
    page_title="AI Question Paper Generator",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

def init_session_state():
    """Initializes standard session state variables if they don't exist."""
    if "pdf_path" not in st.session_state:
        st.session_state.pdf_path = None
    if "is_generating" not in st.session_state:
        st.session_state.is_generating = False

init_session_state()

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 0px;
    }
    .sub-header {
        text-align: center;
        color: #6B7280;
        margin-bottom: 30px;
        font-size: 1.1rem;
    }
    .step-header {
        color: #2563EB;
        font-weight: 600;
        margin-top: 20px;
        margin-bottom: 15px;
        padding-bottom: 5px;
        border-bottom: 2px solid #E5E7EB;
    }
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
    .stDownloadButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        background-color: #10B981;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🎓 AI Question Paper Generator</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Create professional, university-level exam papers instantly.</p>', unsafe_allow_html=True)

# Main Container
with st.container():
    # --- Step 1: Subject Details ---
    st.markdown('<h3 class="step-header">Step 1: Subject Details</h3>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        subject = st.text_input("Course / Subject Name", placeholder="e.g., Computer Networks")
    with col2:
        topic = st.text_input("Specific Topic", placeholder="e.g., TCP/IP Protocols")

    # --- Step 2: Question Distribution ---
    st.markdown('<h3 class="step-header">Step 2: Question Distribution</h3>', unsafe_allow_html=True)

    col_q, col_m = st.columns(2)
    with col_q:
        total_questions = st.number_input(
            "Total Number of Questions",
            min_value=1,
            max_value=Config.MAX_TOTAL_QUESTIONS,
            value=10,
            step=1,
            help=f"Maximum allowed questions: {Config.MAX_TOTAL_QUESTIONS}"
        )
    with col_m:
        max_total_marks = st.number_input(
            "Maximum Total Marks",
            min_value=1,
            max_value=1000,
            value=100,
            step=1,
            help="The sum of all generated questions' marks must not exceed this value."
        )

    st.write(f"Distribute exactly **{total_questions}** questions across the following mark categories:")

    # Dynamic columns for marks
    cols = st.columns(len(Config.ALLOWED_MARKS))
    distribution = {}

    for idx, mark in enumerate(Config.ALLOWED_MARKS):
        with cols[idx]:
            init_val = total_questions if idx == 0 else 0
            count = st.number_input(
                f"{mark} Mark",
                min_value=0,
                max_value=total_questions,
                value=init_val,
                step=1,
                key=f"mark_{mark}"
            )
            distribution[mark] = count

    # Show real-time distribution warning if it doesn't match
    current_sum = sum(distribution.values())
    if current_sum != total_questions:
        st.warning(f"⚠️ Your current distribution sums to **{current_sum}** questions. It must equal exactly **{total_questions}**.")

    # Show real-time marks warning if it exceeds
    current_marks = calculate_total_marks(distribution)
    if current_marks > max_total_marks:
        st.warning(f"⚠️ The current distributed questions amount to **{current_marks}** marks, which exceeds your maximum of **{max_total_marks}** marks.")

    # --- Step 3: Difficulty Settings ---
    st.markdown('<h3 class="step-header">Step 3: Difficulty Settings</h3>', unsafe_allow_html=True)

    difficulty = st.selectbox("Select Overall Difficulty", Config.DIFFICULTIES)

    easy_pct, medium_pct, hard_pct = 0, 0, 0
    if difficulty == "Mix":
        st.info("Adjust the sliders below to set the difficulty distribution. Total must equal 100%.")
        col_e, col_m, col_h = st.columns(3)
        with col_e:
            easy_pct = st.slider("Easy %", min_value=0, max_value=100, value=34, step=1)
        with col_m:
            medium_pct = st.slider("Medium %", min_value=0, max_value=100, value=33, step=1)
        with col_h:
            hard_pct = st.slider("Hard %", min_value=0, max_value=100, value=33, step=1)

        current_pct = easy_pct + medium_pct + hard_pct
        if current_pct != 100:
            st.warning(f"⚠️ Current sum is **{current_pct}%**. It must equal exactly **100%**.")

    st.markdown("<br>", unsafe_allow_html=True)

# Generate Button
generate_clicked = st.button("🚀 Generate Question Paper", type="primary", use_container_width=True)

if generate_clicked:
    # --- VALIDATION STAGE ---

    # 1. Input Validation
    is_valid_inputs, msg_inputs = validate_inputs(subject, topic)
    if not is_valid_inputs:
        st.error(f"**Validation Error:** {msg_inputs}")
        st.stop()

    # 2. Total/Distribution Validation
    distribution_sum = sum(distribution.values())
    is_valid_total, msg_total = validate_total(total_questions, distribution_sum)
    if not is_valid_total:
        st.error(f"**Validation Error:** {msg_total}")
        st.stop()

    # 3. Marks Limit Validation
    is_valid_marks, msg_marks = validate_marks_limit(max_total_marks, current_marks)
    if not is_valid_marks:
        st.error(f"**Validation Error:** {msg_marks}")
        st.stop()

    # 4. Mix Validation
    if difficulty == "Mix":
        is_valid_mix, msg_mix = validate_mix(easy_pct, medium_pct, hard_pct)
        if not is_valid_mix:
            st.error(f"**Validation Error:** {msg_mix}")
            st.stop()

    # --- GENERATION STAGE ---
    st.session_state.is_generating = True
    st.session_state.pdf_path = None

    questions_data = {}

    # Count active requests
    active_marks = [mark for mark in sorted(Config.ALLOWED_MARKS) if distribution[mark] > 0]

    # Progress indication
    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        for idx, mark in enumerate(active_marks):
            count = distribution[mark]

            status_text.info(f"⏳ Generating {count} questions for {mark} marks...")

            if difficulty == "Mix":
                diff_info = calculate_difficulty_distribution(count, easy_pct, medium_pct, hard_pct)
            else:
                diff_info = difficulty

            questions = generate_questions_for_mark(subject, topic, mark, count, diff_info)
            questions_data[mark] = questions

            # Update progress
            progress_bar.progress((idx + 1) / len(active_marks))

        status_text.info("⏳ Building the professional PDF...")

        # --- PDF CREATION STAGE ---
        output_dir = "assets"
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, "question_paper.pdf")

        pdf_path = create_pdf(subject, topic, questions_data, output_file)
        st.session_state.pdf_path = pdf_path

        status_text.empty()
        progress_bar.empty()

        st.success("✨ Question paper generated successfully!")
        st.balloons()

    except Exception as e:
        status_text.empty()
        progress_bar.empty()
        st.error(f"**Generation Failed:** {str(e)}")
        st.session_state.is_generating = False
        st.stop()

# --- DOWNLOAD & RESET STAGE ---
if st.session_state.pdf_path and os.path.exists(st.session_state.pdf_path):
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("### 🎉 Your paper is ready!")

    col_dl, col_rs = st.columns([3, 1])

    with col_dl:
        with open(st.session_state.pdf_path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()

        st.download_button(
            label="📥 Download PDF",
            data=pdf_bytes,
            file_name=f"{subject.replace(' ', '_')}_Question_Paper.pdf",
            mime="application/pdf"
        )

    with col_rs:
        if st.button("🔄 Reset / Clear", use_container_width=True):
            st.session_state.pdf_path = None
            st.rerun()
