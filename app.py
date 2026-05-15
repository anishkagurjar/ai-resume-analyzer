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

    .mode-card {
        background: white;
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border: 2px solid #f0f0f0;
        text-align: center;
        transition: all 0.3s ease;
    }

    .api-box {
        background: #f8f9ff;
        border-radius: 15px;
        padding: 1.5rem;
        border: 2px solid #667eea;
        margin-bottom: 2rem;
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
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 20px rgba(102,126,234,0.4);
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
    [data-testid="stSidebar"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class='header-box'>
        <h1>📄 AI Resume Analyzer</h1>
        <p>Smart Resume Screening & Enhancement System</p>
    </div>
""", unsafe_allow_html=True)

# Get API Key from Streamlit Secrets
groq_api_key = st.secrets["GROQ_API_KEY"]

if 'mode' not in st.session_state:
    st.session_state['mode'] = None

if st.session_state['mode'] is None:

    # AI Settings Toggle
    show_settings = st.toggle("⚙️ AI Settings", value=False)

    if show_settings:
        st.markdown("""
            <div class='api-box'>
                <h3 style='color:#667eea; margin:0 0 1rem 0;'>⚙️ Configure AI</h3>
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
                    st.success("✅ API Key Loaded from Streamlit Secrets!")
                else:
                    st.error("❌ API Key not found in Streamlit Secrets")

            else:
                st.info("⚡ Ollama runs locally — no API key needed!")
                api_key = None

        st.session_state['model_choice'] = model_choice
        st.session_state['api_key'] = api_key

    else:
        model_choice = st.session_state.get('model_choice', 'Groq (Cloud)')
        api_key = st.session_state.get('api_key', groq_api_key)

    st.markdown("---")

    # Mode Selection
    st.markdown("<h2 style='text-align:center;'>Select Mode</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray;'>Who are you?</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 0.2, 1])

    with col1:
        st.markdown("""
            <div class='mode-card'>
                <h1>👔</h1>
                <h2 style='color:#1a1a2e;'>HR Mode</h2>
                <p style='color:gray;'>
                Upload multiple resumes, compare candidates,
                get rankings & SWOT analysis, download screening report!
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("👔 Enter HR Mode", key="hr_btn"):
            st.session_state['mode'] = 'hr'
            st.rerun()

    with col3:
        st.markdown("""
            <div class='mode-card'>
                <h1>👤</h1>
                <h2 style='color:#667eea;'>Candidate Mode</h2>
                <p style='color:gray;'>
                Upload your resume, get AI analysis,
                enhance resume for job description,
                download professional templates!
                </p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("👤 Enter Candidate Mode", key="candidate_btn"):
            st.session_state['mode'] = 'candidate'
            st.rerun()

else:

    # Get Saved Settings
    model_choice = st.session_state.get('model_choice', 'Groq (Cloud)')
    api_key = st.session_state.get('api_key', groq_api_key)

    # Back Button
    col1, col2, col3 = st.columns([1, 4, 1])

    with col1:
        if st.button("← Back"):
            st.session_state['mode'] = None
            st.session_state.clear()
            st.rerun()

    st.markdown("---")

    # Show Selected Mode
    if st.session_state['mode'] == 'hr':
        show_hr_mode(api_key, model_choice)

    elif st.session_state['mode'] == 'candidate':
        show_candidate_mode(api_key, model_choice)