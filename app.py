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

from hr_analyzer import show_hr_mode
from candidate_mode import show_candidate_mode

# PAGE CONFIG

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# DARK MODE TOGGLE

dark_mode = st.toggle("🌙 Dark Mode")

# CUSTOM CSS

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

*{
    font-family:'Inter',sans-serif;
}

.main{
    padding:1rem 2rem;
    background: linear-gradient(135deg,#EEF2FF,#F8FAFC);
}

/* TOPBAR */

.topbar{
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:18px 30px;
    background:linear-gradient(90deg,#5B5FEF,#3B82F6);
    border-radius:22px;
    margin-bottom:30px;
    box-shadow:0 8px 24px rgba(0,0,0,0.08);
}

.logo-section{
    display:flex;
    align-items:center;
    gap:15px;
}

.logo{
    font-size:40px;
}

.title{
    font-size:30px;
    font-weight:800;
    color:white;
}

.about-btn button{
    background:rgba(255,255,255,0.15);
    border:1px solid rgba(255,255,255,0.3);
    color:white;
    padding:10px 22px;
    border-radius:12px;
    cursor:pointer;
    font-weight:600;
}

/* HERO SECTION */

.hero-section{

    text-align:center;

    padding:90px 40px;

    background: rgba(255,255,255,0.7);

    backdrop-filter: blur(12px);

    border-radius:30px;

    margin-bottom:50px;

    box-shadow:0 8px 32px rgba(31,38,135,0.08);

    border:1px solid rgba(255,255,255,0.3);
}

.hero-section h1{

    font-size:62px;

    font-weight:800;

    background: linear-gradient(90deg,#3B82F6,#7C3AED);

    -webkit-background-clip:text;

    -webkit-text-fill-color:transparent;

    margin-bottom:20px;
}

.hero-section p{
    font-size:22px;
    color:#555;
    max-width:850px;
    margin:auto;
    line-height:1.7;
}

/* MODE CARDS */

.mode-card{

    background: rgba(255,255,255,0.6);

    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);

    border-radius:24px;

    padding:35px;

    border:1px solid rgba(255,255,255,0.3);

    transition:0.3s ease;

    box-shadow:0 8px 32px rgba(31,38,135,0.12);

    text-align:center;

    height:100%;
}

.mode-card:hover{

    transform:translateY(-10px);

    box-shadow:0 20px 50px rgba(59,130,246,0.25);
}

.mode-card h1{
    font-size:55px;
    margin-bottom:10px;
}

.mode-card h2{
    font-size:30px;
    margin-bottom:15px;
    font-weight:700;
}

.mode-card p{
    color:#666;
    line-height:1.7;
    font-size:16px;
}

/* API BOX */

.api-box{
    background:white;
    border-radius:20px;
    padding:25px;
    border:1px solid #E5E7EB;
    margin-bottom:30px;
    box-shadow:0 6px 20px rgba(0,0,0,0.04);
}

/* BUTTONS */

.stButton>button{
    width:100%;
    padding:16px;
    border-radius:16px;
    border:none;
    font-size:18px;
    font-weight:700;
    background:linear-gradient(90deg,#3B82F6,#5B5FEF);
    color:white;
    transition:0.3s ease;
}

.stButton>button:hover{
    transform:scale(1.02);
    box-shadow:0 10px 25px rgba(59,130,246,0.3);
}

/* SCORE STYLES */

.score-high{
    background:linear-gradient(135deg,#11998e,#38ef7d);
    color:white;
    padding:1rem 2rem;
    border-radius:50px;
    text-align:center;
    font-size:1.5rem;
    font-weight:700;
}

.score-mid{
    background:linear-gradient(135deg,#f7971e,#ffd200);
    color:white;
    padding:1rem 2rem;
    border-radius:50px;
    text-align:center;
    font-size:1.5rem;
    font-weight:700;
}

.score-low{
    background:linear-gradient(135deg,#cb2d3e,#ef473a);
    color:white;
    padding:1rem 2rem;
    border-radius:50px;
    text-align:center;
    font-size:1.5rem;
    font-weight:700;
}

/* HIDE STREAMLIT */

#MainMenu{
    visibility:hidden;
}

footer{
    visibility:hidden;
}

[data-testid="stSidebar"]{
    display:none;
}

</style>
""", unsafe_allow_html=True)

# TOPBAR

st.markdown("""
<div class="topbar">

    <div class="logo-section">
        <span class="logo">📄</span>
        <span class="title">AI Resume Analyzer</span>
    </div>

    <div class="about-btn">
        <button>ℹ About</button>
    </div>

</div>
""", unsafe_allow_html=True)

# HERO SECTION

st.markdown("""
<div class="hero-section">

    <h1>Welcome to AI Resume Analyzer</h1>

    <p>
        Your intelligent career assistant that helps you create,
        analyze, optimize, and improve resumes for better job opportunities.
    </p>

</div>
""", unsafe_allow_html=True)

# API KEY

groq_api_key = st.secrets["GROQ_API_KEY"]

# SESSION STATE

if 'mode' not in st.session_state:
    st.session_state['mode'] = None

# HOME SCREEN

if st.session_state['mode'] is None:

    # SETTINGS

    show_settings = st.toggle("⚙️ AI Settings", value=False)

    if show_settings:

        st.markdown("""
        <div class='api-box'>
            <h3 style='color:#3B3FEF;'>
                ⚙️ Configure AI
            </h3>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:

            model_choice = st.radio(
                "🤖 Select AI Model:",
                ["Ollama (Local)", "Groq (Cloud)"],
                horizontal=True
            )

        with col2:

            api_key = None

            if model_choice == "Groq (Cloud)":

                api_key = groq_api_key

                if api_key:
                    st.success("✅ API Key Loaded Successfully!")

                else:
                    st.error("❌ API Key Not Found")

            else:

                st.info("⚡ Ollama runs locally — no API key needed!")
                api_key = None

        st.session_state['model_choice'] = model_choice
        st.session_state['api_key'] = api_key

    else:

        model_choice = st.session_state.get(
            'model_choice',
            'Groq (Cloud)'
        )

        api_key = st.session_state.get(
            'api_key',
            groq_api_key
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # MODE SELECTION

    st.markdown("""
    <h2 style='text-align:center;font-size:42px;'>
        Choose Your Mode
    </h2>
    """, unsafe_allow_html=True)

    st.markdown("""
    <p style='text-align:center;color:gray;font-size:18px;'>
        Select how you want to use the platform
    </p>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,0.15,1])

    # HR MODE

    with col1:

        st.markdown("""
        <div class='mode-card'>

            <h1>👔</h1>

            <h2 style='color:#111827;'>
                HR Mode
            </h2>

            <p>
                Upload multiple resumes, compare candidates,
                generate rankings, SWOT analysis,
                and download screening reports.
            </p>

        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("👔 Enter HR Mode", key="hr_btn"):

            st.session_state['mode'] = 'hr'
            st.rerun()

    # CANDIDATE MODE

    with col3:

        st.markdown("""
        <div class='mode-card'>

            <h1>👤</h1>

            <h2 style='color:#3B3FEF;'>
                Candidate Mode
            </h2>

            <p>
                Upload your resume, get AI analysis,
                improve ATS score,
                optimize for job descriptions,
                and download professional templates.
            </p>

        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("👤 Enter Candidate Mode", key="candidate_btn"):

            st.session_state['mode'] = 'candidate'
            st.rerun()

    # FEATURES

    st.markdown("<br><br><br>", unsafe_allow_html=True)

    st.markdown("""
    <h2 style='text-align:center;'>
        Why Choose AI Resume Analyzer?
    </h2>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4)

    with f1:
        st.info("🧠 AI-Powered Analysis")

    with f2:
        st.success("🛡 ATS Optimization")

    with f3:
        st.warning("📈 Smart Suggestions")

    with f4:
        st.info("📄 Professional Templates")

# INSIDE MODE

else:

    model_choice = st.session_state.get(
        'model_choice',
        'Groq (Cloud)'
    )

    api_key = st.session_state.get(
        'api_key',
        groq_api_key
    )

    col1, col2, col3 = st.columns([1,4,1])

    with col1:

        if st.button("← Back"):

            st.session_state['mode'] = None
            st.session_state.clear()
            st.rerun()

    st.markdown("---")

    if st.session_state['mode'] == 'hr':

        show_hr_mode(api_key, model_choice)

    elif st.session_state['mode'] == 'candidate':

        show_candidate_mode(api_key, model_choice)