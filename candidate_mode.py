import streamlit as st
import os
import re
from utils.parser import extract_text_from_pdf
from utils.analyzer import analyze_resume
from utils.report_generator import (
    extract_resume_data,
    generate_modern_template,
    generate_creative_template,
    generate_minimal_template
)
from dotenv import load_dotenv

load_dotenv()


def enhance_resume_with_ai(resume_text, job_description, model_choice, api_key):
    from groq import Groq
    import ollama

    prompt = f"""
You are an expert resume writer and career coach.

Your task is to ENHANCE and REWRITE the given resume to perfectly match the job description.

RULES:
- Keep all real information from the original resume
- Rewrite in a professional tone
- Add relevant keywords from job description
- Improve bullet points to be more impactful
- Use action verbs
- Make it ATS-friendly
- Format it clearly with sections:
  * Career Objective
  * Education
  * Skills
  * Projects
  * Achievements

ORIGINAL RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Write the enhanced resume now:
"""

    if model_choice == "Groq (Cloud)":
        if not api_key:
            return "❌ Please enter Groq API Key"
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert resume writer."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content
    else:
        response = ollama.chat(
            model="tinyllama",
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"]


def show_candidate_mode(api_key, model_choice):

    st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 2rem; border-radius: 15px; text-align: center; margin-bottom: 2rem;'>
            <h1 style='color: white; margin:0;'>👤 Candidate Mode</h1>
            <p style='color: #e0e0ff; margin:0.5rem 0 0 0;'>
                Enhance your resume for your dream job!
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Two columns
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📤 Upload Your Resume")
        uploaded_file = st.file_uploader(
            "Upload Resume (PDF only)",
            type=["pdf"],
            key="candidate_resume"
        )

    with col2:
        st.subheader("📋 Target Job Description")
        job_description = st.text_area(
            "Paste Job Description Here",
            height=200,
            placeholder="Paste the job you want to apply for...",
            key="candidate_job"
        )

    st.markdown("---")

    if uploaded_file is not None:

        os.makedirs("uploads", exist_ok=True)
        file_path = os.path.join("uploads", uploaded_file.name)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success("✅ Resume uploaded successfully!")
        resume_text = extract_text_from_pdf(file_path)

        # Two buttons
        col1, col2 = st.columns(2)

        with col1:
            analyze_btn = st.button("🔍 Analyze My Resume", key="candidate_analyze")

        with col2:
            enhance_btn = st.button("✨ Enhance My Resume with AI", key="candidate_enhance")

        # Analyze
        if analyze_btn:
            if job_description:
                with st.spinner("🤖 Analyzing your resume..."):
                    result = analyze_resume(
                        resume_text,
                        job_description,
                        model_choice,
                        api_key
                    )
                st.session_state['candidate_result'] = result
                st.session_state['candidate_resume_text'] = resume_text
            else:
                st.warning("⚠️ Please paste job description!")

        # Enhance
        if enhance_btn:
            if job_description:
                with st.spinner("✨ AI is enhancing your resume... Please wait..."):
                    enhanced = enhance_resume_with_ai(
                        resume_text,
                        job_description,
                        model_choice,
                        api_key
                    )
                st.session_state['enhanced_resume'] = enhanced
                st.session_state['candidate_resume_text'] = resume_text
            else:
                st.warning("⚠️ Please paste job description!")

        # Show Analysis
        if 'candidate_result' in st.session_state:
            result = st.session_state['candidate_result']

            st.markdown("---")
            st.subheader("🤖 AI Analysis Result")
            st.markdown(result)

            # ATS Score
            match = re.search(r"(\d+)\s*/\s*100", result)
            if match:
                score = int(match.group(1))
                st.markdown("---")
                st.subheader("📊 ATS Match Score")
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.progress(score / 100)
                    if score >= 70:
                        st.success(f"🎉 Great Match! {score}/100")
                    elif score >= 50:
                        st.warning(f"⚠️ Average Match! {score}/100")
                    else:
                        st.error(f"❌ Low Match! {score}/100")

        # Show Enhanced Resume
        if 'enhanced_resume' in st.session_state:
            enhanced = st.session_state['enhanced_resume']
            resume_text = st.session_state['candidate_resume_text']

            st.markdown("---")
            st.markdown("""
                <div style='background: linear-gradient(135deg, #667eea, #764ba2);
                padding: 1rem; border-radius: 10px; text-align: center; color: white;'>
                    <h3>✨ AI Enhanced Resume</h3>
                </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(enhanced)

            # Template Download
            st.markdown("---")
            st.markdown("<h3 style='text-align:center;'>🎨 Download Enhanced Resume</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center; color:gray;'>Choose a template to download!</p>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            t1, t2, t3 = st.columns(3)

            resume_data = extract_resume_data(enhanced, "")

            with t1:
                st.markdown("""
                    <div style='background:white; border-radius:12px; padding:1.5rem;
                    box-shadow: 0 2px 15px rgba(0,0,0,0.08); text-align:center;'>
                        <h2>🔵</h2>
                        <h3 style='color:#3498DB;'>Modern</h3>
                        <p style='color:gray;'>Corporate & IT jobs</p>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                pdf = generate_modern_template(resume_data)
                st.download_button(
                    "📥 Download Modern",
                    data=pdf,
                    file_name="enhanced_modern.pdf",
                    mime="application/pdf",
                    key="enh_modern"
                )

            with t2:
                st.markdown("""
                    <div style='background:white; border-radius:12px; padding:1.5rem;
                    box-shadow: 0 2px 15px rgba(0,0,0,0.08); text-align:center;'>
                        <h2>🟣</h2>
                        <h3 style='color:#6C3483;'>Creative</h3>
                        <p style='color:gray;'>Design & creative jobs</p>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                pdf = generate_creative_template(resume_data)
                st.download_button(
                    "📥 Download Creative",
                    data=pdf,
                    file_name="enhanced_creative.pdf",
                    mime="application/pdf",
                    key="enh_creative"
                )

            with t3:
                st.markdown("""
                    <div style='background:white; border-radius:12px; padding:1.5rem;
                    box-shadow: 0 2px 15px rgba(0,0,0,0.08); text-align:center;'>
                        <h2>⚫</h2>
                        <h3 style='color:#1A1A1A;'>Minimal</h3>
                        <p style='color:gray;'>Any job — timeless</p>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                pdf = generate_minimal_template(resume_data)
                st.download_button(
                    "📥 Download Minimal",
                    data=pdf,
                    file_name="enhanced_minimal.pdf",
                    mime="application/pdf",
                    key="enh_minimal"
                )
    else:
        st.markdown("""
            <div style='text-align:center; padding: 2rem; background: #f8f9ff;
            border-radius: 15px; border: 2px dashed #667eea;'>
                <h3 style='color: #667eea;'>👆 Upload your resume to get started!</h3>
                <p style='color: gray;'>PDF format only</p>
            </div>
        """, unsafe_allow_html=True)