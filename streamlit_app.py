import streamlit as st
import pandas as pd
import pdfplumber
import json
from typing import Dict
import os
# Your custom modules (adjust paths as needed)
from utils.config import GEMINI_API_KEY, USAJOBS_API_KEY
from usajobs_api import USAJobsAPI
from job_hunt_assitant.agents.jd_analyst import JobDescriptionAnalyst
from job_hunt_assitant.agents.resume_cl_agent import ResumeCoverLetterAgent




    
# ────────────────────────────────────────────────
# Page Config + Global Styling
# ────────────────────────────────────────────────
st.set_page_config(
    page_title="Federal Job AI Assistant",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Modern Styling with Better Organization
st.markdown("""
<style>
    /* ═══════════════════════════════════════════════════════════════
       GLOBAL STYLES & FOUNDATION
       ═══════════════════════════════════════════════════════════════ */
    
    /* Main Container */
    .main .block-container { 
        padding-top: 2rem !important; 
        padding-bottom: 3rem !important; 
        max-width: 1400px;
        margin: 0 auto;
    }
    
    /* Typography Base */
    h1, h2, h3, h4, h5, h6 { 
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    /* Smooth Transitions */
    * {
        transition: all 0.2s ease-in-out;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       THEME SYSTEM (Light/Dark Mode Support)
       ═══════════════════════════════════════════════════════════════ */
    
    :root {
        --primary-color: #2563eb;
        --primary-hover: #1d4ed8;
        --secondary-color: #3b82f6;
        --accent-color: #10b981;
        --danger-color: #ef4444;
        --warning-color: #f59e0b;
        --success-color: #10b981;
        
        --text-primary: #111827;
        --text-secondary: #6b7280;
        --text-muted: #9ca3af;
        
        --bg-primary: #ffffff;
        --bg-secondary: #f9fafb;
        --bg-tertiary: #f3f4f6;
        --bg-card: #ffffff;
        
        --border-color: #e5e7eb;
        --border-hover: #d1d5db;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
        
        --radius-sm: 0.5rem;
        --radius-md: 0.75rem;
        --radius-lg: 1rem;
        --radius-xl: 1.5rem;
    }
    
    /* Dark Mode Theme */
    @media (prefers-color-scheme: dark) {
        :root {
            --primary-color: #3b82f6;
            --primary-hover: #60a5fa;
            --secondary-color: #60a5fa;
            --accent-color: #34d399;
            
            --text-primary: #f9fafb;
            --text-secondary: #d1d5db;
            --text-muted: #9ca3af;
            
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-tertiary: #334155;
            --bg-card: #1e293b;
            
            --border-color: #334155;
            --border-hover: #475569;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
            --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.6);
        }
    }
    
    /* Apply Theme Colors */
    [data-testid="stAppViewContainer"] {
        background: var(--bg-secondary);
    }
    
    h1, h2, h3, h4, h5, h6 { 
        color: var(--text-primary) !important;
    }
    
    p, div, span, label {
        color: var(--text-secondary);
    }
    
    /* ═══════════════════════════════════════════════════════════════
       HERO SECTION - Landing Area
       ═══════════════════════════════════════════════════════════════ */
    
    .hero-title {
        font-size: clamp(2.5rem, 5vw, 4rem);
        font-weight: 900;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 1rem;
        line-height: 1.1;
        letter-spacing: -0.03em;
    }
    
    .hero-subtitle {
        font-size: clamp(1.1rem, 2vw, 1.5rem);
        color: var(--text-secondary);
        text-align: center;
        font-weight: 400;
        max-width: 900px;
        margin: 1.5rem auto 2rem;
        line-height: 1.6;
    }
    
    .cta-container {
        display: flex;
        justify-content: center;
        gap: 1rem;
        margin: 2rem 0 3rem;
        flex-wrap: wrap;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       FEATURE CARDS - Landing Page Cards
       ═══════════════════════════════════════════════════════════════ */
    
    .feature-card {
        background: var(--bg-card);
        border-radius: var(--radius-xl);
        padding: 2.5rem 2rem;
        text-align: center;
        border: 2px solid var(--border-color);
        box-shadow: var(--shadow-md);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: var(--shadow-xl);
        border-color: var(--primary-color);
    }
    
    .feature-card:hover::before {
        transform: scaleX(1);
    }
    
    .feature-icon {
        font-size: 3.5rem;
        margin-bottom: 1.5rem;
        display: inline-block;
        filter: grayscale(0.2);
        transition: all 0.3s ease;
    }
    
    .feature-card:hover .feature-icon {
        transform: scale(1.1) rotate(5deg);
        filter: grayscale(0);
    }
    
    .feature-card h3 {
        font-size: 1.3rem;
        margin-bottom: 0.8rem;
        color: var(--text-primary) !important;
    }
    
    .feature-card p {
        color: var(--text-secondary);
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       ANALYSIS CARDS - Result Display Cards
       ═══════════════════════════════════════════════════════════════ */
    
    .analysis-card {
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        padding: 2rem;
        margin-bottom: 1.5rem;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
    }
    
    .analysis-card:hover {
        box-shadow: var(--shadow-md);
        border-color: var(--border-hover);
    }
    
    .section-title {
        color: var(--primary-color) !important;
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        padding-bottom: 0.75rem;
        border-bottom: 3px solid var(--border-color);
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .section-title::before {
        content: '';
        width: 4px;
        height: 1.5rem;
        background: linear-gradient(180deg, var(--primary-color), var(--secondary-color));
        border-radius: 2px;
    }
    
    .bullet-item {
        margin-bottom: 1rem;
        line-height: 1.7;
        font-size: 1rem;
        color: var(--text-secondary);
        padding-left: 1.5rem;
        position: relative;
    }
    
    .bullet-item::before {
        content: '▪';
        position: absolute;
        left: 0;
        color: var(--primary-color);
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       KEYWORD PILLS - Tag Display
       ═══════════════════════════════════════════════════════════════ */
    
    .keyword-pill {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        padding: 0.5rem 1.2rem;
        border-radius: 9999px;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.4rem 0.5rem 0.4rem 0;
        display: inline-block;
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
        border: 1px solid transparent;
    }
    
    .keyword-pill:hover {
        transform: translateY(-2px) scale(1.05);
        box-shadow: var(--shadow-md);
        filter: brightness(1.1);
    }
    
    /* ═══════════════════════════════════════════════════════════════
       TABS SYSTEM - Navigation Tabs
       ═══════════════════════════════════════════════════════════════ */
    
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        padding: 0.5rem;
        gap: 0.5rem;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border-color);
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: var(--radius-md);
        padding: 1rem 2rem;
        font-size: 1rem;
        font-weight: 600;
        color: var(--text-secondary);
        transition: all 0.2s ease;
        border: 1px solid transparent;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: var(--bg-tertiary);
        color: var(--text-primary);
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)) !important;
        color: white !important;
        box-shadow: var(--shadow-md);
        border-color: transparent;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       BUTTONS - All Button Styles
       ═══════════════════════════════════════════════════════════════ */
    
    .stButton > button {
        border-radius: var(--radius-md);
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        box-shadow: var(--shadow-sm);
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.2);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton > button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-lg);
        filter: brightness(1.1);
    }
    
    .stButton > button:active {
        transform: translateY(-1px);
        box-shadow: var(--shadow-sm);
    }
    
    /* ═══════════════════════════════════════════════════════════════
       INPUT FIELDS - Text Inputs, Text Areas
       ═══════════════════════════════════════════════════════════════ */
    
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: var(--radius-md) !important;
        border: 2px solid var(--border-color) !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.2s ease !important;
        background: var(--bg-card) !important;
        color: var(--text-primary) !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       FILE UPLOADER
       ═══════════════════════════════════════════════════════════════ */
    
    [data-testid="stFileUploader"] {
        border-radius: var(--radius-lg);
        border: 2px dashed var(--border-color);
        padding: 2rem;
        background: var(--bg-secondary);
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: var(--primary-color);
        background: var(--bg-card);
    }
    
    /* ═══════════════════════════════════════════════════════════════
       EXPANDER - Collapsible Sections
       ═══════════════════════════════════════════════════════════════ */
    
    .streamlit-expanderHeader {
        background: var(--bg-card);
        border-radius: var(--radius-md);
        padding: 1rem 1.5rem;
        font-weight: 600;
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        transition: all 0.2s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: var(--bg-tertiary);
        border-color: var(--primary-color);
    }
    
    .streamlit-expanderContent {
        border: 1px solid var(--border-color);
        border-top: none;
        border-radius: 0 0 var(--radius-md) var(--radius-md);
        padding: 1.5rem;
        background: var(--bg-card);
    }
    
    /* ═══════════════════════════════════════════════════════════════
       ALERTS & MESSAGES
       ═══════════════════════════════════════════════════════════════ */
    
    .stAlert {
        border-radius: var(--radius-md);
        padding: 1rem 1.5rem;
        border-left: 4px solid;
        font-size: 0.95rem;
    }
    
    /* Success Alert */
    .stSuccess {
        background: rgba(16, 185, 129, 0.1);
        border-left-color: var(--success-color);
        color: var(--text-primary);
    }
    
    /* Info Alert */
    .stInfo {
        background: rgba(59, 130, 246, 0.1);
        border-left-color: var(--primary-color);
        color: var(--text-primary);
    }
    
    /* Warning Alert */
    .stWarning {
        background: rgba(245, 158, 11, 0.1);
        border-left-color: var(--warning-color);
        color: var(--text-primary);
    }
    
    /* Error Alert */
    .stError {
        background: rgba(239, 68, 68, 0.1);
        border-left-color: var(--danger-color);
        color: var(--text-primary);
    }
    
    /* ═══════════════════════════════════════════════════════════════
       PROGRESS BAR
       ═══════════════════════════════════════════════════════════════ */
    
    .stProgress > div > div > div {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        border-radius: 9999px;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       SIDEBAR
       ═══════════════════════════════════════════════════════════════ */
    
    [data-testid="stSidebar"] {
        background: var(--bg-card);
        border-right: 1px solid var(--border-color);
    }
    
    [data-testid="stSidebar"] .element-container {
        margin-bottom: 1rem;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       METRICS - Statistics Display
       ═══════════════════════════════════════════════════════════════ */
    
    [data-testid="stMetric"] {
        background: var(--bg-card);
        padding: 1.5rem;
        border-radius: var(--radius-md);
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
        transition: all 0.2s ease;
    }
    
    [data-testid="stMetric"]:hover {
        box-shadow: var(--shadow-md);
        border-color: var(--primary-color);
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        color: var(--text-secondary);
        font-weight: 500;
    }
    
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary-color);
    }
    
    /* ═══════════════════════════════════════════════════════════════
       DOWNLOAD BUTTON
       ═══════════════════════════════════════════════════════════════ */
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, var(--accent-color), #059669);
        border-radius: var(--radius-md);
        padding: 0.75rem 2rem;
        font-weight: 600;
        color: white;
        border: none;
        box-shadow: var(--shadow-sm);
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        filter: brightness(1.1);
    }
    
    /* ═══════════════════════════════════════════════════════════════
       DIVIDER
       ═══════════════════════════════════════════════════════════════ */
    
    hr {
        margin: 2rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-color), transparent);
    }
    
    /* ═══════════════════════════════════════════════════════════════
       ANIMATIONS & EFFECTS
       ═══════════════════════════════════════════════════════════════ */
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.5;
        }
    }
    
    .feature-card, .analysis-card {
        animation: fadeIn 0.6s ease-out;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       SCROLLBAR STYLING
       ═══════════════════════════════════════════════════════════════ */
    
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-color);
    }
    
    /* ═══════════════════════════════════════════════════════════════
       RESPONSIVE DESIGN
       ═══════════════════════════════════════════════════════════════ */
    
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }
        
        .hero-subtitle {
            font-size: 1.1rem;
        }
        
        .cta-container {
            flex-direction: column;
            align-items: stretch;
        }
        
        .feature-card {
            padding: 1.5rem;
        }
        
        .analysis-card {
            padding: 1.25rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            padding: 0.75rem 1rem;
            font-size: 0.9rem;
        }
    }
    
    /* ═══════════════════════════════════════════════════════════════
       ACCESSIBILITY
       ═══════════════════════════════════════════════════════════════ */
    
    *:focus {
        outline: 2px solid var(--primary-color);
        outline-offset: 2px;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       UTILITY CLASSES
       ═══════════════════════════════════════════════════════════════ */
    
    .glass-effect {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .gradient-text {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Smooth Scrolling */
    html {
        scroll-behavior: smooth;
    }
    
    /* ═══════════════════════════════════════════════════════════════
       SPINNER / LOADING STATES
       ═══════════════════════════════════════════════════════════════ */
    
    .stSpinner > div {
        border-color: var(--primary-color) !important;
    }
</style>
""", unsafe_allow_html=True)

# ────────────────────────────────────────────────
# Session State Initialization (MUST BE FIRST)
# ────────────────────────────────────────────────
def initialize_session_state():
    """Initialize all session state variables with defaults"""
    defaults = {
        'jobs_data': [],
        'selected_job': None,
        'job_analysis': None,
        'resume_text': "",
        'tailored_resume': None,
        'cover_letter': None,
        'resume_analys': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Initialize session state immediately
initialize_session_state()

# ────────────────────────────────────────────────
# Main App
# ────────────────────────────────────────────────
def main():

    # ────────────────────────────────────────────────
    # API Keys Check
    # ────────────────────────────────────────────────
    if not GEMINI_API_KEY:
        st.sidebar.error("⚠️ Gemini API key not found. Some features will be limited.")
        st.sidebar.info("💡 Set GEMINI_API_KEY in utils/config.py")

    if not USAJOBS_API_KEY:
        st.sidebar.error("⚠️ USAJOBS API key not found. Job search will not work.")
        st.sidebar.info("💡 Set USAJOBS_API_KEY in utils/config.py")

    # ────────────────────────────────────────────────
    # Hero Section
    # ────────────────────────────────────────────────
    st.markdown('<h1 class="hero-title">🎯 Sonar Search</h1>', unsafe_allow_html=True)
    st.markdown('<p class="hero-subtitle">AI-Powered Federal Job Application Assistant — Find, Analyze & Apply with Confidence</p>', unsafe_allow_html=True)

    # Quick CTA Buttons
    with st.container():
        st.markdown('<div class="cta-container">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔍 Search Jobs Now", type="primary", use_container_width=True, key="hero_search"):
                pass  # Tab navigation handled by Streamlit
        with col2:
            if st.button("📄 Upload My Resume", use_container_width=True, key="hero_resume"):
                pass  # Tab navigation handled by Streamlit
        st.markdown('</div>', unsafe_allow_html=True)

    # ────────────────────────────────────────────────
    # Feature Cards (shown when no job selected)
    # ────────────────────────────────────────────────
    if not st.session_state.selected_job:
        st.markdown("### 🚀 How It Works – 3 Simple Steps")
        cols = st.columns(3, gap="medium")

        with cols[0]:
            st.markdown("""
                <div class="feature-card">
                    <div class="feature-icon">🔍</div>
                    <h3>Search Federal Jobs</h3>
                    <p>Find open positions using keywords, location or remote filters from the USAJOBS database</p>
                </div>
            """, unsafe_allow_html=True)

        with cols[1]:
            st.markdown("""
                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h3>Deep AI Analysis</h3>
                    <p>Get must-haves, ATS keywords, red flags and strategic positioning recommendations</p>
                </div>
            """, unsafe_allow_html=True)

        with cols[2]:
            st.markdown("""
                <div class="feature-card">
                    <div class="feature-icon">✨</div>
                    <h3>Tailored Documents</h3>
                    <p>Generate perfectly matched resume & cover letter optimized for ATS systems in seconds</p>
                </div>
            """, unsafe_allow_html=True)

    # ────────────────────────────────────────────────
    # Main Tabs
    # ────────────────────────────────────────────────
    tab_search, tab_resume, tab_analysis = st.tabs([
        "🔍  Find Jobs",
        "📄  My Resume",
        "✨  Analyze & Generate"
    ])

    # ════════════════════════════════════════════════════════════════
    # TAB 1: Job Search
    # ════════════════════════════════════════════════════════════════
    with tab_search:
        st.subheader("🎯 Search USA Federal Jobs")
        st.markdown("Search through thousands of federal job openings using the USAJOBS API")

        # Search Form
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            keyword = st.text_input(
                "🔎 Keyword / Position Title", 
                value="Software Engineer",
                help="Enter job title, keywords, or skills you're looking for"
            )
        with col2:
            location = st.text_input(
                "📍 Location / Remote", 
                value="",
                help="Enter city, state, or leave blank for all locations"
            )
        with col3:
            max_results = st.number_input(
                "📊 Max Results", 
                min_value=5, 
                max_value=50, 
                value=15, 
                step=5,
                help="Number of jobs to retrieve"
            )

        # Search Button
        if st.button("🔍 Search USAJOBS", type="primary", use_container_width=True):
            if not USAJOBS_API_KEY:
                st.error("❌ USAJOBS API key missing. Please add it to utils/config.py")
            else:
                with st.spinner("🔄 Searching for opportunities..."):
                    try:
                        api = USAJobsAPI()
                        jobs = api.search_jobs(keyword.strip(), location.strip() or None, max_results)
                        st.session_state.jobs_data = jobs
                    except Exception as e:
                        st.error(f"❌ Search failed: {str(e)}")
                        st.session_state.jobs_data = []

                if jobs:
                    st.success(f"✅ Found **{len(jobs)}** matching positions!")
                else:
                    st.warning("⚠️ No results found. Try broader search terms or different keywords.")

        # Display Results
        if st.session_state.jobs_data:
            st.markdown("---")
            st.markdown("### 📋 Matching Positions")
            
            for idx, job in enumerate(st.session_state.jobs_data):
                with st.expander(
                    f"**{job.get('title', 'Unknown Title')}** — {job.get('agency', 'Unknown Agency')}",
                    expanded=False
                ):
                    # Job Details
                    col_info1, col_info2 = st.columns(2)
                    with col_info1:
                        st.markdown(f"**📍 Location:** {job.get('location', 'Location not specified')}")
                        st.markdown(f"**💰 Salary:** {job.get('salary', 'N/A')}")
                    with col_info2:
                        st.markdown(f"**📅 Posted:** {job.get('posted_date', 'N/A')}")
                        st.markdown(f"**⏰ Closes:** {job.get('closing_date', 'N/A')}")
                    
                    # Action Button
                    if st.button("🎯 Analyze This Position", key=f"select_{idx}", use_container_width=True):
                        st.session_state.selected_job = job
                        st.session_state.job_analysis = None
                        st.rerun()

    # ════════════════════════════════════════════════════════════════
    # TAB 2: Resume Upload
    # ════════════════════════════════════════════════════════════════
    with tab_resume:
        st.subheader("📄 Your Resume")
        st.markdown("Upload your resume in PDF format or paste the text directly")

        # File Upload Section
        st.markdown("#### 📤 Upload Resume")
        uploaded = st.file_uploader(
            "Choose a PDF file",
            type=["pdf"],
            help="Upload your resume in PDF format for best results"
        )
        
        # Text Input Section
        st.markdown("#### ✍️ Or Paste Resume Text")
        pasted = st.text_area(
            "Paste your resume content here",
            height=220,
            help="Copy and paste your resume text if you don't have a PDF"
        )

        # Process Upload
        if uploaded:
            try:
                with pdfplumber.open(uploaded) as pdf:
                    text = "\n".join(p.extract_text() or "" for p in pdf.pages if p.extract_text())
                st.session_state.resume_text = text.strip()
                st.success("✅ Resume uploaded and processed successfully!")
            except Exception as e:
                st.error(f"❌ Error reading PDF: {e}")

        # Process Pasted Text
        elif pasted.strip():
            st.session_state.resume_text = pasted.strip()

        # Display Current Resume
        if st.session_state.resume_text:
            st.markdown("---")
            with st.expander("📝 Current Resume Content", expanded=False):
                st.text_area(
                    "Edit if needed",
                    st.session_state.resume_text,
                    height=380,
                    key="resume_editor",
                    help="You can edit your resume text here before analysis"
                )
            
            # Stats
            word_count = len(st.session_state.resume_text.split())
            char_count = len(st.session_state.resume_text)
            col_stat1, col_stat2 = st.columns(2)
            with col_stat1:
                st.metric("📊 Word Count", f"{word_count:,}")
            with col_stat2:
                st.metric("📊 Character Count", f"{char_count:,}")

    # ════════════════════════════════════════════════════════════════
    # TAB 3: Analysis & Generation
    # ════════════════════════════════════════════════════════════════
    with tab_analysis:
        st.subheader("🎯 Position Analysis & Tailored Documents")

        if not st.session_state.selected_job:
            # No Job Selected Message
            st.info("👈 **Please select a job from the Find Jobs tab to begin analysis**")
            st.markdown("""
            Once you select a position, you'll be able to:
            - 🔍 Get detailed AI analysis of job requirements
            - 📊 View ATS keywords and compatibility scores
            - ✨ Generate tailored resume and cover letter
            - 💡 Receive strategic positioning advice
            """)
        else:
            job = st.session_state.selected_job
            
            # Job Header
            st.markdown(f"### 💼 {job.get('title', 'Unknown Position')}")
            st.caption(f"**{job.get('agency', 'Unknown Agency')}** • 📍 {job.get('location', 'Location not specified')} • [View on USAJOBS]({job.get('url', '#')})")
            
            st.markdown("---")

            # Analyze Button
            if not st.session_state.job_analysis:
                if st.button("🚀 Analyze Job Requirements", type="primary", use_container_width=True):
                    if not GEMINI_API_KEY:
                        st.error("❌ Gemini API key missing. Please add it to utils/config.py")
                    else:
                        with st.spinner("🤖 Analyzing position with AI..."):
                            try:
                                analyst = JobDescriptionAnalyst()
                                full_text = f"{job.get('description', '')}\n\nQualifications:\n{job.get('requirements', '')}"
                                analysis = analyst.analyze_job_description(
                                    full_text,
                                    job.get('title', 'Unknown Position'),
                                    job.get('agency', 'Unknown Agency')
                                )
                                st.session_state.job_analysis = analysis
                                st.success("✅ Analysis complete!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Analysis failed: {str(e)}")
                                st.session_state.job_analysis = {"error": str(e)}

            # Display Analysis Results
            if st.session_state.job_analysis:
                analysis = st.session_state.job_analysis

                if "error" in analysis or "critical_error" in analysis:
                    st.error(f"❌ {analysis.get('error') or analysis.get('critical_error')}")
                else:
                    # Analysis Cards in Two Columns
                    col_left, col_right = st.columns(2, gap="large")

                    # ──────────── LEFT COLUMN ────────────
                    with col_left:
                        # Must-Have Requirements
                        with st.container():
                            st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
                            st.markdown('<div class="section-title">✅ Must-Have Requirements</div>', unsafe_allow_html=True)
                            for req in analysis.get("must_have_requirements", []):
                                st.markdown(f'<div class="bullet-item">{req}</div>', unsafe_allow_html=True)
                            if not analysis.get("must_have_requirements"):
                                st.caption("No must-have requirements identified")
                            st.markdown('</div>', unsafe_allow_html=True)

                        # Preferred Skills
                        with st.container():
                            st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
                            st.markdown('<div class="section-title">⭐ Preferred Skills</div>', unsafe_allow_html=True)
                            for skill in analysis.get("preferred_skills", []):
                                st.markdown(f'<div class="bullet-item">{skill}</div>', unsafe_allow_html=True)
                            if not analysis.get("preferred_skills"):
                                st.caption("No preferred skills identified")
                            st.markdown('</div>', unsafe_allow_html=True)

                        # Key Responsibilities
                        with st.container():
                            st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
                            st.markdown('<div class="section-title">📋 Key Responsibilities</div>', unsafe_allow_html=True)
                            for duty in analysis.get("key_responsibilities", []):
                                st.markdown(f'<div class="bullet-item">{duty}</div>', unsafe_allow_html=True)
                            if not analysis.get("key_responsibilities"):
                                st.caption("No key responsibilities identified")
                            st.markdown('</div>', unsafe_allow_html=True)

                    # ──────────── RIGHT COLUMN ────────────
                    with col_right:
                        # ATS Keywords
                        with st.container():
                            st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
                            st.markdown('<div class="section-title">🔑 ATS Keywords</div>', unsafe_allow_html=True)
                            keywords = analysis.get("keywords_for_ats", [])
                            if keywords:
                                # Show first 15 keywords
                                st.markdown(" ".join(f'<span class="keyword-pill">{k}</span>' for k in keywords[:15]), unsafe_allow_html=True)
                                if len(keywords) > 15:
                                    with st.expander(f"➕ Show all {len(keywords)} keywords"):
                                        st.markdown(" ".join(f'<span class="keyword-pill">{k}</span>' for k in keywords), unsafe_allow_html=True)
                            else:
                                st.caption("No keywords extracted")
                            st.markdown('</div>', unsafe_allow_html=True)

                        # Culture & Work Style
                        with st.container():
                            st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
                            st.markdown('<div class="section-title">🌟 Culture & Work Style</div>', unsafe_allow_html=True)
                            for ind in analysis.get("company_culture_indicators", []):
                                st.markdown(f'<div class="bullet-item">{ind}</div>', unsafe_allow_html=True)
                            if not analysis.get("company_culture_indicators"):
                                st.caption("No culture indicators identified")
                            st.markdown('</div>', unsafe_allow_html=True)

                        # Red Flags
                        with st.container():
                            st.markdown('<div class="analysis-card">', unsafe_allow_html=True)
                            st.markdown('<div class="section-title">⚠️ Red Flags</div>', unsafe_allow_html=True)
                            red_flags = analysis.get("red_flags", [])
                            if red_flags:
                                for flag in red_flags:
                                    st.warning(f"⚠️ {flag}")
                            else:
                                st.caption("✅ No red flags identified")
                            st.markdown('</div>', unsafe_allow_html=True)

                    # Positioning Strategy (Full Width)
                    st.markdown("---")
                    st.markdown("### 🎯 Positioning Strategy")
                    positioning = analysis.get("positioning_strategy", "No strategy provided.")
                    st.info(f"💡 {positioning}")

                    # ════════════════════════════════════════════════════════════════
                    # Document Generation Section
                    # ════════════════════════════════════════════════════════════════
                    if st.session_state.resume_text:
                        st.markdown("---")
                        st.markdown("### ✨ Generate Tailored Documents")

                        # Generate Button
                        if not st.session_state.tailored_resume:
                            if st.button("🚀 Generate Tailored Resume + Cover Letter", type="primary", use_container_width=True):
                                if not GEMINI_API_KEY:
                                    st.error("❌ Gemini API key missing. Cannot generate documents.")
                                else:
                                    with st.spinner("✨ Generating tailored documents with AI..."):
                                        try:
                                            agent = ResumeCoverLetterAgent()
                                            resume_res = agent.customize_resume(st.session_state.resume_text, analysis)
                                            cover_res = agent.generate_cover_letter(st.session_state.resume_text, analysis)
                                            resume_analys = agent.analyze_resume_ats_compatibility(
                                                st.session_state.resume_text,
                                                keywords
                                            )
                                            st.session_state.resume_analys = resume_analys
                                            st.session_state.tailored_resume = resume_res
                                            st.session_state.cover_letter = cover_res
                                            st.success("✅ Documents generated successfully!")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"❌ Generation failed: {str(e)}")

                        # ──────────── ATS Analysis Results ────────────
                        if st.session_state.resume_analys:
                            st.markdown("---")
                            st.markdown("### 📊 ATS Compatibility Analysis")

                            # Safely get values with defaults
                            ats_perct = st.session_state.resume_analys.get("ats_percentage", 0)
                            sugg_needed = st.session_state.resume_analys.get("suggestions", [])
                            keywords_pres = st.session_state.resume_analys.get("keywords_found", [])
                            keywords_missing = st.session_state.resume_analys.get("keywords_missing", [])

                            # ATS Score Display
                            col_score1, col_score2 = st.columns([1, 3])
                            with col_score1:
                                st.metric("🎯 ATS Score", f"{ats_perct}%")
                            with col_score2:
                                st.progress(ats_perct / 100)

                            # Color-coded Feedback
                            if ats_perct >= 85:
                                st.success("✅ **Excellent ATS compatibility!** Your resume should pass most automated screening systems.")
                            elif ats_perct >= 70:
                                st.info("👍 **Good ATS compatibility.** Consider adding a few more keywords for better results.")
                            elif ats_perct >= 50:
                                st.warning("⚠️ **Moderate ATS compatibility.** Some improvements needed to increase your chances.")
                            else:
                                st.error("❌ **Low ATS compatibility.** Significant improvements needed to pass automated screening.")

                            # Keywords Analysis
                            col_kw1, col_kw2 = st.columns(2)

                            with col_kw1:
                                if keywords_pres:
                                    with st.expander(f"✅ **Keywords Found** ({len(keywords_pres)})", expanded=True):
                                        st.markdown("These keywords are present in your resume:")
                                        cols = st.columns(3)
                                        for i, k in enumerate(keywords_pres):
                                            with cols[i % 3]:
                                                st.markdown(f'<span class="keyword-pill">{k}</span>', unsafe_allow_html=True)

                            with col_kw2:
                                if keywords_missing:
                                    with st.expander(f"❌ **Keywords Missing** ({len(keywords_missing)})", expanded=True):
                                        st.markdown("Add these keywords to improve your ATS score:")
                                        cols = st.columns(3)
                                        for i, k in enumerate(keywords_missing):
                                            with cols[i % 3]:
                                                st.markdown(f'<span class="keyword-pill">{k}</span>', unsafe_allow_html=True)

                            # Improvement Suggestions
                            if sugg_needed:
                                with st.expander("💡 **Improvement Suggestions**", expanded=True):
                                    for i, suggestion in enumerate(sugg_needed, 1):
                                        st.markdown(f'<div class="bullet-item">{suggestion}</div>', unsafe_allow_html=True)

                        # ──────────── Tailored Resume Display ────────────
                        if st.session_state.tailored_resume and "customized_resume" in st.session_state.tailored_resume:
                            st.markdown("---")
                            st.markdown("### ✨ Tailored Resume")
                            
                            with st.expander("📄 **View Tailored Resume**", expanded=False):
                                st.markdown(st.session_state.tailored_resume["customized_resume"].replace("\n", "  \n"))
                            
                            st.download_button(
                                "📥 Download Tailored Resume",
                                st.session_state.tailored_resume["customized_resume"],
                                file_name=f"tailored_resume_{job.get('title', 'job').replace(' ', '_')[:50]}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )

                        # ──────────── Cover Letter Display ────────────
                        if st.session_state.cover_letter and "cover_letter" in st.session_state.cover_letter:
                            st.markdown("### 📝 Cover Letter")
                            
                            with st.expander("✉️ **View Cover Letter**", expanded=False):
                                st.markdown(st.session_state.cover_letter["cover_letter"].replace("\n", "  \n"))
                            
                            st.download_button(
                                "📥 Download Cover Letter",
                                st.session_state.cover_letter["cover_letter"],
                                file_name=f"cover_letter_{job.get('agency', 'agency').replace(' ', '_')[:50]}.txt",
                                mime="text/plain",
                                use_container_width=True
                            )

                    else:
                        st.markdown("---")
                        st.warning("⚠️ **Please upload or paste your resume in the My Resume tab first.**")

            # Reset Button
            st.markdown("---")
            if st.button("🔄 Analyze Different Job", use_container_width=True):
                st.session_state.selected_job = None
                st.session_state.job_analysis = None
                st.session_state.tailored_resume = None
                st.session_state.cover_letter = None
                st.session_state.resume_analys = None
                st.rerun()

    # ════════════════════════════════════════════════════════════════
    # Sidebar Configuration
    # ════════════════════════════════════════════════════════════════
    with st.sidebar:
        # Logo & Title
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <div style="font-size: 4rem; margin-bottom: 0.5rem;">💼</div>
            <h2 style="margin: 0; color: var(--primary-color);">Federal Job Assistant</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Current Stats
        st.markdown("### 📊 Current Stats")
        
        # Metrics Display
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.metric("Jobs Found", len(st.session_state.jobs_data))
        with col_s2:
            st.metric("Selected", "✓" if st.session_state.selected_job else "—")
        
        st.metric("Resume Status", "Uploaded ✓" if st.session_state.resume_text else "Not Uploaded")
        
        st.markdown("---")
        
        # Tips Section
        st.markdown("### 💡 Quick Tips")
        st.info("""
        **How to use:**
        1. 🔍 Start by searching for jobs
        2. 📄 Upload your current resume
        3. 🎯 Select a job to analyze
        4. ✨ Generate tailored documents
        
        **Pro Tips:**
        - Use specific keywords in your search
        - Keep your resume updated
        - Review all red flags carefully
        - Customize each application
        """)
        
        st.markdown("---")
        
        # Clear Data Button
        if st.button("🗑️ Clear All Data", type="secondary", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        
        st.markdown("---")
        
        # Footer
        st.caption("Made by Anish")
        

# ════════════════════════════════════════════════════════════════
# Run Application
# ════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    main()