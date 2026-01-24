"""
Frontend Configuration — Red, Black, Grey, White Flat Palette
Modern, sleek, minimal but exciting
"""

# API Configuration
API_BASE_URL = "http://localhost:5000"

# App metadata
APP_TITLE = "Spotify Wrapped"
APP_ICON = "🎵"
PAGE_LAYOUT = "wide"
API_TIMEOUT = 10

# Modern flat color palette
COLORS = {
    'bg_dark': '#0b0b0b',
    'bg_panel': '#0f0f10',
    'bg_hover': '#1a1a1b',
    'accent_red': '#ff3b30',
    'accent_red_dark': '#cc2e26',
    'white': '#f7f7f7',
    'grey_light': '#9aa0a6',
    'grey_muted': '#6f7579',
    'grey_dark': '#2a2a2a',
    'border': '#151515',
    'success': '#34c759',
    'warning': '#ff9500',
    'error': '#ff3b30',
}

# Plotly color scales (red/black/grey theme)
PLOT_COLORS = ['#ff3b30', '#2a2a2a', '#9aa0a6', '#f7f7f7', '#cc2e26', '#151515']
PLOT_SEQUENTIAL = ['#0b0b0b', '#2a2a2a', '#6f7579', '#9aa0a6', '#ff3b30']

# Typography
FONTS = {
    'family': "'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial",
    'mono': "'Fira Code', 'Courier New', monospace",
}

# Wrapped Card Configuration
WRAPPED_CARD_CONFIG = {
    'aspect_ratio': '9:16',  # Portrait mode like Instagram stories
    'width': '450px',  # Adjust as needed
    'height': '800px',  # 16/9 * 450 = 800
    'border_radius': '20px',
    'font_family': 'Dela Gothic One, sans-serif',
    'font_size': '20px',
    'text_align': 'center'
}

# CSS for Wrapped Cards with Custom Background
WRAPPED_CARD_CSS = """
<style>
    /* Import Dela Gothic One font */
    @import url('https://fonts.googleapis.com/css2?family=Dela+Gothic+One&display=swap');
    
    /* Wrapped Card Container */
    .wrapped-card {
        width: 450px;
        height: 800px;
        margin: 20px auto;
        border-radius: 20px;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 40px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        position: relative;
    }
    
    /* Text inside Wrapped Card */
    .wrapped-card h1,
    .wrapped-card h2,
    .wrapped-card h3,
    .wrapped-card p,
    .wrapped-card span {
        font-family: 'Dela Gothic One', sans-serif !important;
        font-size: 20px !important;
        text-align: center !important;
        color: white !important;
        text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.8);
        margin: 10px 0;
    }
    
    /* Title text - larger */
    .wrapped-card .card-title {
        font-size: 32px !important;
        margin-bottom: 20px;
    }
    
    /* Overlay for better text readability */
    .wrapped-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3));
        border-radius: 20px;
        z-index: 1;
    }
    
    /* Ensure content is above overlay */
    .wrapped-card > * {
        position: relative;
        z-index: 2;
    }
</style>
"""