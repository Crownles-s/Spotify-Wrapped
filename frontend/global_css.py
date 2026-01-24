import streamlit as st

def apply_global_css():
    # Define our theme colors
    purple_main = "#8c00ff"
    purple_glow = "#c8b3ff"
    vibrant_pink = "#ff00e5"
    bg_deep_black = "#040407"
    sidebar_black = "#000000"
    text_white = "#ffffff"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&display=swap');

    /* 1. COMPLETELY HIDE DEFAULT NAV & MOVE CONTENT UP */
    [data-testid="stSidebarNav"] {{
        display: none !important;
    }}

    [data-testid="stSidebarContent"] {{
        padding-top: 0rem !important; /* Removes gap at the top */
        background-color: {sidebar_black} !important;
    }}
    
    /* Remove default decoration line at the top */
    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
        color: rgba(0,0,0,0);
    }}

    /* 2. WRAPPED 2024 HEADER - Scaled & Centered */
    .main-header {{
        font-family: 'Montserrat', sans-serif;
        font-size: 5rem;
        font-weight: 900;
        text-align: center;
        margin: 2rem auto;
        color: {text_white};
        line-height: 1.1;
    }}

    .header-accent {{
        color: {purple_main};
        font-size: 8rem;
        display: block;
        text-transform: uppercase;
        filter: drop-shadow(0 0 15px rgba(140, 0, 255, 0.6));
    }}

    /* 3. ALL BUTTONS (SIDEBAR NAV + MAIN) - Glowy Purple */
    div.stButton > button, 
    div.stDownloadButton > button, 
    [data-testid="stSidebar"] button {{
        background: linear-gradient(135deg, {purple_main} 0%, #5e00b3 100%) !important;
        border: 1px solid {purple_glow} !important;
        color: {text_white} !important;
        box-shadow: 0 0 15px rgba(140, 0, 255, 0.5) !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase;
        display: flex;
        justify-content: center;
        align-items: center;
    }}

    div.stButton > button:hover, 
    [data-testid="stSidebar"] button:hover {{
        box-shadow: 0 0 25px rgba(140, 0, 255, 0.9) !important;
        transform: translateY(-2px);
        border-color: white !important;
    }}

    /* 4. SLIDERS - Purple Theme */
    div[data-baseweb="slider"] > div > div {{
        background-color: {purple_main} !important;
    }}
    div[data-testid="stThumbValue"] {{
        color: {purple_glow} !important;
    }}

    /* 5. APP BACKGROUND & SIDEBAR */
    [data-testid="stAppViewContainer"] {{
        background-color: {bg_deep_black} !important;
        background-image: radial-gradient(circle at 15% 25%, rgba(140, 0, 255, 0.12) 0%, transparent 40%),
                          linear-gradient(135deg, rgba(60, 0, 120, 0.08), rgba(10, 0, 30, 0.2)) !important;
    }}

    [data-testid="stSidebar"] {{
        background-color: {sidebar_black} !important;
        border-right: 1px solid rgba(140, 0, 255, 0.2);
    }}

    /* 6. TEXT & METRICS */
    [data-testid="stMetricValue"] {{
        color: {purple_glow} !important;
    }}
    
    h1, h2, h3, p, span, label, [data-testid="stMarkdownContainer"] p {{
        color: {text_white} !important;
    }}

    /* Style for the Navigation Icon Buttons specifically */
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] div.stButton > button {{
        font-size: 1.5rem !important;
        padding: 0.5rem !important;
    }}

    </style>
    """, unsafe_allow_html=True)