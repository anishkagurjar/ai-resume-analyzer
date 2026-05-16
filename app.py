import streamlit as st
import os
from dotenv import load_dotenv
from hr_analyzer import show_hr_mode
from candidate_mode import show_candidate_mode

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; margin: 0; padding: 0; }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stSidebar"] {display: none;}
    .block-container { padding: 0 !important; max-width: 100% !important; }

    .navbar {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        padding: 1rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0;
    }
    .navbar-brand {
        color: white;
        font-size: 1.3rem;
        font-weight: 700;
    }
    .navbar-about {
        color: white;
        border: 2px solid white;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 500;
    }
    .hero {
        background: linear-gradient(135deg, #EEF2FF 0%, #F5F3FF 100%);
        padding: 3rem 2rem;
        text-align: center;
    }
    .hero h1 {
        font-size: 2.5rem;
        font-weight: 700;
        color: #4F46E5;
        margin-bottom: 1rem;
    }
    .hero p {
        font-size: 1.1rem;
        color: #6B7280;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.6;
    }
    .mode-section {
        padding: 2rem 2rem 0 2rem;
        background: white;
    }
    .mode-title {
        text-align: center;
        font-size: 1.8rem;
        font-weight: 700;
        color: #1F2937;
        margin-bottom: 0.5rem;
    }
    .mode-underline {
        width: 60px;
        height: 4px;
        background: #4F46E5;
        margin: 0 auto 2rem auto;
        border-radius: 2px;
    }
    .candidate-card {
        background: white;
        border: 2px solid #DBEAFE;
        border-radius: 15px;
        padding: 2rem;
    }
    .hr-card {
        background: white;
        border: 2px solid #D1FAE5;
        border-radius: 15px;
        padding: 2rem;
    }
    .card-title-blue {
        font-size: 1.4rem;
        font-weight: 700;
        color: #3B82F6;
        margin-bottom: 0.8rem;
    }
    .card-title-green {
        font-size: 1.4rem;
        font-weight: 700;
        color: #10B981;
        margin-bottom: 0.8rem;
    }
    .card-desc {
        color: #6B7280;
        font-size: 0.95rem;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.7rem 2rem;
        width: 100%;
        border: none;
        transition: all 0.3s ease;
    }
    .why-section {
        background: #F9FAFB;
        padding: 2.5rem 2rem;
    }
    .why-title {
        text-align: center;
        font-size: 1.8rem;
        font-weight: 700;
        color: #1F2937;
        margin-bottom: 0.5rem;
    }
    .feature-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: left;
        border: 1px solid #E5E7EB;
        height: 100%;
    }
    .feature-desc {
        color: #6B7280;
        font-size: 0.85rem;
        line-height: 1.5;
    }
    .footer {
        background: white;
        text-align: center;
        padding: 1.5rem;
        color: #6B7280;
        font-size: 0.9rem;
        border-top: 1px solid #E5E7EB;
    }
    </style>
""", unsafe_allow_html=True)

# Session State
if 'mode' not in st.session_state:
    st.session_state['mode'] = None
if 'model_choice' not in st.session_state:
    st.session_state['model_choice'] = 'Groq (Cloud)'
if 'api_key' not in st.session_state:
    st.session_state['api_key'] = GROQ_API_KEY

# HOME PAGE
if st.session_state['mode'] is None:

    # Navbar
    st.markdown("""
        <div class='navbar'>
            <div class='navbar-brand'>📄 AI Resume Analyzer</div>
            <div class='navbar-about'>ⓘ About</div>
        </div>
    """, unsafe_allow_html=True)

    # Hero
    st.markdown("""
        <div class='hero'>
            <h1>Welcome to AI Resume Analyzer</h1>
            <p>Your intelligent career assistant that helps you create, analyze,
            and optimize your resume for better opportunities.</p>
        </div>
    """, unsafe_allow_html=True)

    # AI Settings Toggle — sirf Ollama/Groq switch
    st.markdown("<div style='padding: 1rem 2rem 0 2rem;'>", unsafe_allow_html=True)
    show_settings = st.toggle("⚙️ AI Settings", value=False)

    if show_settings:
        model_choice = st.radio(
            "🤖 Select AI Model:",
            ["Groq (Cloud)", "Ollama (Local)"],
            horizontal=True
        )
        st.session_state['model_choice'] = model_choice

        if model_choice == "Groq (Cloud)":
            st.session_state['api_key'] = GROQ_API_KEY
            st.success("✅ Groq AI Ready!")
        else:
            st.session_state['api_key'] = None
            st.info("⚡ Ollama runs locally — no API key needed!")

    st.markdown("</div>", unsafe_allow_html=True)

    # Mode Selection
    st.markdown("""
        <div class='mode-section'>
            <div class='mode-title'>Choose Your Mode</div>
            <div class='mode-underline'></div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
            <div class='candidate-card'>
                <div style='font-size:2.5rem;'>👤</div>
                <div class='card-title-blue'>Candidate Mode</div>
                <div class='card-desc'>Upload your resume and get AI-powered
                analysis, suggestions, and improvement recommendations.</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("👤 Enter Candidate Mode →", key="candidate_btn"):
            st.session_state['mode'] = 'candidate'
            st.rerun()

    with col2:
        st.markdown("""
            <div class='hr-card'>
                <div style='font-size:2.5rem;'>👔</div>
                <div class='card-title-green'>HR Mode</div>
                <div class='card-desc'>Analyze multiple resumes, compare candidates,
                and get insights to make better hiring decisions.</div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("👔 Enter HR Mode →", key="hr_btn"):
            st.session_state['mode'] = 'hr'
            st.rerun()

    # Why Choose Section
    st.markdown("""
        <div class='why-section'>
            <div class='why-title'>Why Choose AI Resume Analyzer?</div>
            <div class='mode-underline'></div>
        </div>
    """, unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4)
    with f1:
        st.markdown("""
            <div class='feature-card'>
                <div style='font-size:2rem; color:#7C3AED;'>🧠</div>
                <div style='font-weight:700; color:#7C3AED; margin:0.5rem 0;'>AI-Powered Analysis</div>
                <div class='feature-desc'>Advanced AI analyzes your resume and provides detailed insights.</div>
            </div>
        """, unsafe_allow_html=True)
    with f2:
        st.markdown("""
            <div class='feature-card'>
                <div style='font-size:2rem; color:#10B981;'>🛡️</div>
                <div style='font-weight:700; color:#10B981; margin:0.5rem 0;'>ATS Compatibility</div>
                <div class='feature-desc'>Check your resume's ATS score and compatibility.</div>
            </div>
        """, unsafe_allow_html=True)
    with f3:
        st.markdown("""
            <div class='feature-card'>
                <div style='font-size:2rem; color:#F59E0B;'>💡</div>
                <div style='font-weight:700; color:#F59E0B; margin:0.5rem 0;'>Smart Suggestions</div>
                <div class='feature-desc'>Get personalized suggestions to improve your resume.</div>
            </div>
        """, unsafe_allow_html=True)
    with f4:
        st.markdown("""
            <div class='feature-card'>
                <div style='font-size:2rem; color:#3B82F6;'>📄</div>
                <div style='font-weight:700; color:#3B82F6; margin:0.5rem 0;'>Multiple Templates</div>
                <div class='feature-desc'>Choose from professional templates to create a perfect resume.</div>
            </div>
        """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
        <div class='footer'>
            © 2025 AI Resume Analyzer | All rights reserved 💜
        </div>
    """, unsafe_allow_html=True)

# MODE PAGES
else:
    st.markdown("""
        <div class='navbar'>
            <div class='navbar-brand'>📄 AI Resume Analyzer</div>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if st.button("← Back"):
            st.session_state['mode'] = None
            st.rerun()

    st.markdown("---")

    model_choice = st.session_state.get('model_choice', 'Groq (Cloud)')
    api_key = st.session_state.get('api_key') or GROQ_API_KEY

    if st.session_state['mode'] == 'hr':
        show_hr_mode(api_key, model_choice)
    elif st.session_state['mode'] == 'candidate':
        show_candidate_mode(api_key, model_choice)