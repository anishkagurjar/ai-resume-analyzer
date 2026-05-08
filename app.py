import streamlit as st
import os
import re

from utils.parser import extract_text_from_pdf
from utils.analyzer import analyze_resume

# Page Config
st.set_page_config(
    page_title="AI Resume Analyzer",
    layout="wide"
)

# Main Title
st.title("AI Resume Analyzer")

# Sidebar
st.sidebar.title("Resume Analyzer")

st.sidebar.write(
    "AI-powered ATS Resume Screening System"
)

st.sidebar.info(
    "Upload your resume and compare it with a job description."
)

# Description
st.write(
    "Upload your resume and compare with job description."
)

# Upload Resume
uploaded_file = st.file_uploader(
    "Upload Resume",
    type=["pdf"]
)

# Job Description
job_description = st.text_area(
    "Paste Job Description Here"
)

# Main Logic
if uploaded_file is not None:

    # Create uploads folder
    os.makedirs("uploads", exist_ok=True)

    # Save uploaded file
    file_path = os.path.join(
        "uploads",
        uploaded_file.name
    )

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("Resume uploaded successfully!")

    # Extract text from PDF
    resume_text = extract_text_from_pdf(file_path)

    st.info(
        "Resume text extracted successfully."
    )

    # Resume Section
    st.markdown("---")

    st.subheader("📄 Resume Text")

    st.write(resume_text)

    # Analyze Button
    if st.button("Analyze Resume"):

        # Check Job Description
        if job_description:

            with st.spinner("Analyzing Resume..."):

                # AI Analysis
                result = analyze_resume(
                    resume_text,
                    job_description
                )

                st.success(
                    "AI analysis completed successfully!"
                )

                # AI Analysis Section
                st.markdown("---")

                st.subheader("🤖 AI Analysis")

                st.write(result)

                # ATS Score
                match = re.search(r"(\d+)\s*/\s*100", result)

                if match:

                    score = int(match.group(1))

                    st.markdown("---")

                    st.subheader("📊 ATS Match Score")

                    st.progress(score)

                    st.metric(
                        label="ATS Match Score",
                        value=f"{score}%"
                    )

        else:

            st.warning(
                "Please paste job description."
            )