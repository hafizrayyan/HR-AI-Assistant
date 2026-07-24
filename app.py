import streamlit as st
import pandas as pd

# Import modular helper functions
from utils.pdf_text import pdf_text_ext
from utils.sume import resume_summery
from utils.skill_match import skill_match
from utils.match_score import match_score
from utils.recommend import recommendation
# Import your question generation module (Add this line & create function if needed)
from utils.int_question import generate_questions 

# -------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------
st.set_page_config(
    page_title="HR Recruitment AI Assistant",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for layout padding
st.markdown("""
<style>
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        max-width: 99% !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("HR Recruitment AI Assistant")

# -------------------------------------------------------
# SIDEBAR
# -------------------------------------------------------
with st.sidebar:
    st.header("Job Description")
    job_description = st.text_area(
        "Enter Job Description",
        height=250
    )

# -------------------------------------------------------
# FILE UPLOAD
# -------------------------------------------------------
st.header("Candidate Resumes")

pdfs = st.file_uploader(
    "Upload Candidate Resume(s)",
    type=["pdf"],
    accept_multiple_files=True
)

# -------------------------------------------------------
# ANALYZE BUTTON
# -------------------------------------------------------
if st.button("Analyze Resumes", type="primary"):

    if not pdfs:
        st.warning("Please upload at least one resume.")

    elif not job_description.strip():
        st.warning("Please enter a job description.")

    else:
        st.info("Analyzing resumes...")

        candidates_data = []
        progress_bar = st.progress(0)

        for index, pdf in enumerate(pdfs):

            # Extract Resume Text
            raw_text = pdf_text_ext(pdf)

            # Resume Summary
            summary = resume_summery(raw_text)

            # Skill Match
            skill_match_result = skill_match(summary, job_description)

            # Match Score
            score_result = match_score(summary, job_description)

            # Extract numeric score safely
            if isinstance(score_result, dict):
                score = score_result.get("match_percentage", score_result.get("score", 0))
            else:
                score = score_result

            try:
                score = int(float(score))
            except:
                score = 0

            # HR Recommendation
            recommend = recommendation(
                summary,
                job_description,
                skill_match_result,
                score
            )

            # Safely check if decision is 'Hire'
            if isinstance(recommend, dict):
                decision = str(recommend.get("decision", "")).strip().lower()
            else:
                decision = str(recommend).strip().lower()

            # Generate questions IF decision contains "hire"
            questions = []
            if "hire" in decision:
                questions = generate_questions(summary, job_description, skill_match_result , score)

            # Store Candidate Data
            candidate_data = {
                "Candidate": pdf.name,
                "Score": score,
                "Summary": summary,
                "Skill Match": skill_match_result,
                "Recommendation": recommend,
                "Questions": questions  # Stored here
            }

            candidates_data.append(candidate_data)
            progress_bar.progress((index + 1) / len(pdfs))

        st.session_state["candidates"] = candidates_data
        st.success("Analysis Complete!")

# -------------------------------------------------------
# DASHBOARD TABLE & INTERVIEW QUESTIONS
# -------------------------------------------------------
if "candidates" in st.session_state and st.session_state["candidates"]:

    candidates = st.session_state["candidates"]

    st.markdown("---")
    st.subheader("Candidate Ranking Dashboard")

    table_rows = []
    for c in candidates:
        # Extract Recommendation & Justification
        rec = c["Recommendation"]
        if isinstance(rec, dict):
            decision_str = str(rec.get("decision", "N/A")).strip()
            justs = rec.get("justification", [])
            if isinstance(justs, list):
                justification_str = " ".join([str(j).strip() for j in justs])
            else:
                justification_str = str(justs).strip()
        else:
            decision_str = str(rec).strip()
            justification_str = ""

        # Extract Name & Summary
        sum_dict = c["Summary"]
        if isinstance(sum_dict, dict):
            cand_name = str(sum_dict.get("name", c["Candidate"])).strip()
            cand_summary = str(sum_dict.get("summary", "")).strip()
        else:
            cand_name = str(c["Candidate"]).strip()
            cand_summary = str(sum_dict).strip()

        # Extract Matching & Missing Skills
        skills_dict = c["Skill Match"]
        if isinstance(skills_dict, dict):
            m_skills = skills_dict.get("matching_skills", [])
            miss_skills = skills_dict.get("missing_skills", [])
            
            matching_sk = ", ".join([str(s).strip() for s in m_skills]) if isinstance(m_skills, list) else str(m_skills).strip()
            missing_sk = ", ".join([str(s).strip() for s in miss_skills]) if isinstance(miss_skills, list) else str(miss_skills).strip()
        else:
            matching_sk = ""
            missing_sk = ""

        table_rows.append({
            "Candidate Name": " ".join(cand_name.split()),
            "Match Score (%)": c["Score"],
            "Recommendation": " ".join(decision_str.split()),
            "Summary": " ".join(cand_summary.split()),
            "Matching Skills": " ".join(matching_sk.split()),
            "Missing Skills": " ".join(missing_sk.split()),
            "Justification": " ".join(justification_str.split())
        })

    df_display = pd.DataFrame(table_rows)
    df_display = df_display.sort_values(by="Match Score (%)", ascending=False).reset_index(drop=True)

    columns_order = [
        "Candidate Name",
        "Match Score (%)",
        "Recommendation",
        "Summary",
        "Matching Skills",
        "Missing Skills",
        "Justification"
    ]
    df_display = df_display[columns_order]

    # Style Recommendation column
    def style_recommendation(column):
        if column.name == "Recommendation":
            styles = []
            for val in column:
                val_str = str(val).strip().lower()
                if "hire" in val_str:
                    styles.append("background-color: #28a745; color: white; font-weight: bold;")
                elif "reject" in val_str:
                    styles.append("background-color: #dc3545; color: white; font-weight: bold;")
                else:
                    styles.append("")
            return styles
        return [""] * len(column)

    styled_df = df_display.style.apply(style_recommendation, axis=0)

    st.dataframe(
        styled_df,
        column_config={
            "Candidate Name": st.column_config.TextColumn("Candidate Name", width="medium"),
            "Match Score (%)": st.column_config.NumberColumn("Match Score (%)", format="%d%%", width="small"),
            "Recommendation": st.column_config.TextColumn("Recommendation", width="small"),
            "Summary": st.column_config.TextColumn("Summary", width="large"),
            "Matching Skills": st.column_config.TextColumn("Matching Skills", width="medium"),
            "Missing Skills": st.column_config.TextColumn("Missing Skills", width="medium"),
            "Justification": st.column_config.TextColumn("Justification", width="large"),
        },
        use_container_width=True,
        hide_index=True
    )

    # CSV Export
    csv = df_display.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Rankings as CSV",
        csv,
        "candidate_rankings.csv",
        "text/csv"
    )

    # -------------------------------------------------------
    # NEW DISPLAY SECTION: INTERVIEW QUESTIONS FOR "HIRE"
    # -------------------------------------------------------
    has_hire_candidates = any(
    bool(
        c.get("Questions", {}).get("questions") if isinstance(c.get("Questions"), dict) 
        else c.get("Questions")
    ) 
    for c in st.session_state.get("candidates", [])
)

if has_hire_candidates:
    st.markdown("---")
    st.subheader("Custom Interview Questions")

    for candidate in st.session_state["candidates"]:
        raw_questions = candidate.get("Questions", {})
        
        # Safely extract the list of questions
        if isinstance(raw_questions, dict):
            q_list = raw_questions.get("questions", [])
        elif isinstance(raw_questions, list):
            q_list = raw_questions
        else:
            q_list = []

        # SKIP candidate completely if they have no questions (e.g., Rejected candidates)
        if not q_list:
            continue

        # Extract Candidate Name safely
        cand_name = candidate["Candidate"]
        if isinstance(candidate.get("Summary"), dict):
            cand_name = candidate["Summary"].get("name", cand_name)

        # Render expander ONLY for candidates who were recommended for hire
        with st.expander(f"📌 Interview Questions for **{cand_name}**", expanded=True):
            for i, q in enumerate(q_list, 1):
                st.markdown(
                    f"""
                    <div style="
                        background-color: #f8f9fa; 
                        padding: 12px 16px; 
                        border-radius: 8px; 
                        border-left: 4px solid #0d6efd; 
                        margin-bottom: 10px;
                        color: #212529;
                    ">
                        <strong>Q{i}:</strong> {q}
                    </div>
                    """, 
                    unsafe_allow_html=True
                )