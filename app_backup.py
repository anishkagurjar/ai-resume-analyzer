import streamlit as st
import os
import re
from utils.parser import extract_text_from_pdf
from utils.analyzer import analyze_resume
from utils.report_generator import (
    generate_modern_template,
    generate_creative_template,
    generate_minimal_template,
    extract_resume_data
)
from dotenv import load_dotenv

load_dotenv()

# Page Config
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    * { font-family: 'Inter', sans-serif; }

    .main { padding: 0rem; }

    .header-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        color: white;
    }
    .header-box h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        color: white;
    }
    .header-box p {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        color: white;
    }

    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 15px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        margin-bottom: 1rem;
    }

    .template-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 2px 15px rgba(0,0,0,0.08);
        border: 2px solid #f0f0f0;
        margin-bottom: 1rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    .template-card:hover {
        border-color: #667eea;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.2);
    }

    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.7rem 2rem;
        border-radius: 25px;
        border: none;
        font-size: 16px;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
        letter-spacing: 0.5px;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }

    .score-high {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        color: white;
        padding: 1rem 2rem;
        border-radius: 50px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: 700;
    }
    .score-mid {
        background: linear-gradient(135deg, #f7971e, #ffd200);
        color: white;
        padding: 1rem 2rem;
        border-radius: 50px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: 700;
    }
    .score-low {
        background: linear-gradient(135deg, #cb2d3e, #ef473a);
        color: white;
        padding: 1rem 2rem;
        border-radius: 50px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: 700;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h2 style='color: #667eea;'>⚙️ Settings</h2>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    model_choice = st.radio(
        "🤖 Select AI Model:",
        ["Ollama (Local)", "Groq (Cloud)"]
    )

    st.markdown("---")

    api_key = None
    if model_choice == "Groq (Cloud)":
        st.markdown("""
            <div style='background: #f0f4ff; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;'>
                <b>🔑 Get Free Groq API Key:</b><br>
                1. Go to console.groq.com<br>
                2. Sign up with Google<br>
                3. Create API Key<br>
                4. Paste below 👇
            </div>
        """, unsafe_allow_html=True)

        api_key = st.text_input(
            "Enter Groq API Key:",
            type="password",
            placeholder="gsk_xxxxxxxxxxxxxxxx"
        )

        if not api_key:
            api_key = os.getenv("GROQ_API_KEY")

        if api_key:
            st.success("✅ API Key Ready!")
        else:
            st.warning("⚠️ Enter API Key to use Groq")

    st.markdown("---")

    if model_choice == "Ollama (Local)":
        st.warning("⚡ Ollama is slow. Switch to Groq for better results!")
    else:
        st.success("🚀 Groq AI — Fast & Powerful!")

    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: gray; font-size: 0.8rem;'>
            Made with ❤️ using Streamlit & Groq
        </div>
    """, unsafe_allow_html=True)

# Header
st.markdown("""
    <div class='header-box'>
        <h1>📄 AI Resume Analyzer</h1>
        <p>ATS-powered Resume Screening System — Get instant AI feedback on your resume!</p>
    </div>
""", unsafe_allow_html=True)

# Stats Row
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown("""
        <div class='card' style='text-align:center;'>
            <h3 style='color:#667eea; margin:0;'>⚡</h3>
            <b>Fast Analysis</b>
            <p style='color:gray; font-size:0.8rem; margin:0;'>Results in seconds</p>
        </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
        <div class='card' style='text-align:center;'>
            <h3 style='color:#667eea; margin:0;'>🎯</h3>
            <b>ATS Score</b>
            <p style='color:gray; font-size:0.8rem; margin:0;'>Match percentage</p>
        </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
        <div class='card' style='text-align:center;'>
            <h3 style='color:#667eea; margin:0;'>💡</h3>
            <b>Smart Tips</b>
            <p style='color:gray; font-size:0.8rem; margin:0;'>AI suggestions</p>
        </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown("""
        <div class='card' style='text-align:center;'>
            <h3 style='color:#667eea; margin:0;'>🎨</h3>
            <b>Templates</b>
            <p style='color:gray; font-size:0.8rem; margin:0;'>Download resume</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Two Columns Layout
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
        <div class='card'>
            <h3>📤 Upload Resume</h3>
        </div>
    """, unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload your Resume (PDF only)",
        type=["pdf"]
    )

with col2:
    st.markdown("""
        <div class='card'>
            <h3>📋 Job Description</h3>
        </div>
    """, unsafe_allow_html=True)
    job_description = st.text_area(
        "Paste Job Description Here",
        height=200,
        placeholder="Paste the job description here..."
    )

st.markdown("<br>", unsafe_allow_html=True)

# Main Logic
if uploaded_file is not None:

    os.makedirs("uploads", exist_ok=True)
    file_path = os.path.join("uploads", uploaded_file.name)

    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("✅ Resume uploaded successfully!")

    resume_text = extract_text_from_pdf(file_path)

    if st.button("🔍 Analyze My Resume"):

        if job_description:

            with st.spinner(f"🤖 AI is analyzing your resume with {model_choice}... Please wait..."):
                result = analyze_resume(
                    resume_text,
                    job_description,
                    model_choice,
                    api_key
                )

            # Save result in session
            st.session_state['result'] = result
            st.session_state['resume_text'] = resume_text

        else:
            st.warning("⚠️ Please paste job description first!")

    # Show result if available
    if 'result' in st.session_state:
        result = st.session_state['result']
        resume_text = st.session_state['resume_text']

        st.markdown("---")
        st.markdown("""
            <div class='card'>
                <h3>🤖 AI Analysis Result</h3>
            </div>
        """, unsafe_allow_html=True)
        st.markdown(result)

        # ATS Score
        match = re.search(r"(\d+)\s*/\s*100", result)
        if match:
            score = int(match.group(1))
            st.markdown("---")
            st.markdown("<h3 style='text-align:center;'>📊 ATS Match Score</h3>", unsafe_allow_html=True)

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.progress(score / 100)
                if score >= 70:
                    st.markdown(f"<div class='score-high'>🎉 Great Match! {score}/100</div>", unsafe_allow_html=True)
                elif score >= 50:
                    st.markdown(f"<div class='score-mid'>⚠️ Average Match! {score}/100</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='score-low'>❌ Low Match! {score}/100</div>", unsafe_allow_html=True)

        # ─── Template Section ───────────────────────────────────────
        st.markdown("---")
        st.markdown("<h2 style='text-align:center;'>🎨 Resume Template Suggestions</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:gray;'>Choose a template and download your resume in a new design!</p>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        t1, t2, t3 = st.columns(3)

        with t1:
            st.markdown("""
                <div class='template-card'>
                    <h2>🔵</h2>
                    <h3 style='color:#3498DB;'>Modern Professional</h3>
                    <p style='color:gray;'>Clean blue design with clear sections. Best for corporate & IT jobs.</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("📥 Download Modern Template"):
                resume_data = extract_resume_data(resume_text, result)
                pdf_buffer = generate_modern_template(resume_data)
                st.download_button(
                    label="⬇️ Click to Download",
                    data=pdf_buffer,
                    file_name="modern_resume.pdf",
                    mime="application/pdf"
                )

        with t2:
            st.markdown("""
                <div class='template-card'>
                    <h2>🟣</h2>
                    <h3 style='color:#6C3483;'>Creative Bold</h3>
                    <p style='color:gray;'>Bold purple design with colored headers. Best for creative & design jobs.</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("📥 Download Creative Template"):
                resume_data = extract_resume_data(resume_text, result)
                pdf_buffer = generate_creative_template(resume_data)
                st.download_button(
                    label="⬇️ Click to Download",
                    data=pdf_buffer,
                    file_name="creative_resume.pdf",
                    mime="application/pdf"
                )

        with t3:
            st.markdown("""
                <div class='template-card'>
                    <h2>⚫</h2>
                    <h3 style='color:#1A1A1A;'>Minimal Clean</h3>
                    <p style='color:gray;'>Simple black & white design. Best for any job — timeless look.</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("📥 Download Minimal Template"):
                resume_data = extract_resume_data(resume_text, result)
                pdf_buffer = generate_minimal_template(resume_data)
                st.download_button(
                    label="⬇️ Click to Download",
                    data=pdf_buffer,
                    file_name="minimal_resume.pdf",
                    mime="application/pdf"
                )

else:
    st.markdown("""
        <div style='text-align:center; padding: 2rem; background: #f8f9ff;
        border-radius: 15px; border: 2px dashed #667eea;'>
            <h3 style='color: #667eea;'>👆 Upload your resume to get started!</h3>
            <p style='color: gray;'>Support PDF format only</p>
        </div>
    """, unsafe_allow_html=True)