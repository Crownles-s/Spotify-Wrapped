"""
Spotify Wrapped — BOLD, EXCITING, Modern Analytics
"""

import streamlit as st
import requests
import pandas as pd
import sys
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Setup project root and paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import global CSS function and config
from frontend.global_css import apply_global_css
from frontend.frontend_config import API_BASE_URL, APP_TITLE, APP_ICON, COLORS

# Page Configuration
st.set_page_config(
    page_title="Your Music Wrapped",
    page_icon="🎯",
    layout="wide"
)

# Apply the global styles from global_css.py
apply_global_css()

# Define the new theme palette for reuse in charts
THEME_PALETTE = ['#8c00ff', '#ff00e5', '#ffffff', '#c8b3ff']

# ============================================================================
# CACHE & HELPERS
# ============================================================================

@st.cache_data(ttl=30)
def check_api_health():
    try:
        resp = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return resp.status_code == 200, resp.json() if resp.ok else None
    except:
        return False, None

def upload_csv_file(uploaded_file):
    try:
        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)
        files = {'file': (uploaded_file.name, uploaded_file)}
        resp = requests.post(f"{API_BASE_URL}/upload", files=files, timeout=30)
        return resp.status_code == 200, resp.json()
    except Exception as e:
        return False, str(e)

@st.cache_data(ttl=20)
def get_mood_distribution():
    try:
        resp = requests.get(f"{API_BASE_URL}/mood-distribution", timeout=10)
        return resp.status_code == 200, resp.json()
    except:
        return False, None

@st.cache_data(ttl=20)
def get_stats():
    try:
        resp = requests.get(f"{API_BASE_URL}/stats", timeout=10)
        return resp.status_code == 200, resp.json()
    except:
        return False, None

@st.cache_data(ttl=20)
def get_top_artists(n=12):
    try:
        resp = requests.get(f"{API_BASE_URL}/top-artists?n={n}", timeout=10)
        return resp.status_code == 200, resp.json()
    except:
        return False, None

@st.cache_data(ttl=20)
def get_top_tracks(n=15):
    try:
        resp = requests.get(f"{API_BASE_URL}/top-tracks?n={n}", timeout=10)
        return resp.status_code == 200, resp.json()
    except:
        return False, None

# ============================================================================
# SIDEBAR — NAVIGATION
# ============================================================================

st.sidebar.markdown(f"# {APP_ICON} {APP_TITLE}")
st.sidebar.markdown("### Your listening story, visualized.")
st.sidebar.divider()

st.sidebar.markdown("### 🧭 NAVIGATE")
nav_col1, nav_col2, nav_col3 = st.sidebar.columns(3)

with nav_col1:
    if st.button("🏠", help="Home Page", use_container_width=True, key="nav_home"):
        st.session_state['current_page'] = 'home'
        st.rerun()

with nav_col2:
    if st.button("🎵", help="Your Wrapped", use_container_width=True, key="nav_wrapped"):
        st.switch_page("pages/wrapped_page.py")

with nav_col3:
    if st.button("🎯", help="Recommendations", use_container_width=True, key="nav_rec"):
        st.switch_page("pages/recommendations_page.py")

st.sidebar.divider()

sample_df = pd.DataFrame({
    "Track Name": ["Song A", "Song B"],
    "Artist Name(s)": ["Artist 1", "Artist 2"],
    "Duration (ms)": [180000, 210000],
    "Popularity": [65, 72]
})
csv_bytes = sample_df.to_csv(index=False).encode("utf-8")
st.sidebar.download_button("📥 Download Sample", csv_bytes, "sample.csv", "text/csv", use_container_width=True)
st.sidebar.info("📋 Export from Spotify & upload CSV")

if st.sidebar.button("🗑️ CLEAR SESSION", use_container_width=True):
    st.session_state.clear()
    st.rerun()

# ============================================================================
# HEADER
# ============================================================================

# Massive Centered Header
st.markdown(f'<div class="main-header">🎵 <span class="header-accent">WRAPPED</span></div>', unsafe_allow_html=True)

api_ok, health = check_api_health()
if not api_ok:
    st.error("❌ Cannot connect to API. Start: `python backend/spotify_api_dynamic.py`")
    st.stop()

st.divider()

# ============================================================================
# UPLOAD
# ============================================================================

st.header("📤 UPLOAD YOUR PLAYLIST")
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("**Drag & drop your Spotify export CSV**")

uploaded_file = st.file_uploader("", type=['csv'], label_visibility="collapsed")

if uploaded_file:
    try:
        uploaded_file.seek(0)
        preview_df = pd.read_csv(uploaded_file, nrows=3)
        with st.expander("👀 Preview", expanded=False):
            st.dataframe(preview_df, use_container_width=True)
    except:
        pass

    if st.button("🚀 ANALYZE NOW", use_container_width=True):
        with st.spinner("🎵 Analyzing your music taste..."):
            uploaded_file.seek(0)
            success, result = upload_csv_file(uploaded_file)

        if success:
            st.success(f"✅ Uploaded {result.get('rows', '?')} tracks!")
            st.session_state['data_uploaded'] = True
            st.session_state['upload_info'] = result
            st.rerun()
        else:
            st.error(f"❌ {result}")

st.divider()

# ============================================================================
# DASHBOARD
# ============================================================================

if st.session_state.get('data_uploaded'):
    info = st.session_state.get('upload_info', {})
    
    st.subheader("📊 YOUR STATS")
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    
    with kpi1:
        st.metric("🎵 TRACKS", info.get('rows', '—'))
    with kpi2:
        hrs = (info.get('preview', {}).get('total_duration_ms', 0) / 3.6e6)
        st.metric("⏱️ HOURS", f"{hrs:.1f}" if hrs > 0 else "—")
    with kpi3:
        st.metric("🎤 ARTISTS", info.get('preview', {}).get('unique_artists', '—'))
    with kpi4:
        st.metric("⭐ POP", f"{info.get('preview', {}).get('avg_popularity', 0):.0f}")
    with kpi5:
        st.metric("🔞 EXPLICIT", info.get('preview', {}).get('explicit_count', 0))
    
    st.divider()
    
    st.subheader("🎭 YOUR MOOD SIGNATURE")
    c1, c2 = st.columns([1.2, 1])
    
    with c1:
        ok, mood_data = get_mood_distribution()
        if ok and mood_data:
            mood_dist = mood_data.get('mood_distribution', {})
            mood_rows = [{'Mood': m, 'Pct': d.get('percentage', 0)} for m, d in mood_dist.items()]
            mood_df = pd.DataFrame(mood_rows).sort_values('Pct', ascending=False)
            
            if not mood_df.empty:
                fig = go.Figure(data=[go.Pie(
                    labels=mood_df['Mood'],
                    values=mood_df['Pct'],
                    hole=0.4,
                    marker=dict(colors=THEME_PALETTE,
                               line=dict(color='#040407', width=3))
                )])
                fig.update_layout(
                    showlegend=False, 
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color="white"
                )
                st.plotly_chart(fig, use_container_width=True)

    with c2:
        if ok and mood_data:
            mood_dist = mood_data.get('mood_distribution', {})
            mood_rows = [{'Mood': m, 'Count': d.get('count', 0)} for m, d in mood_dist.items()]
            mood_df = pd.DataFrame(mood_rows).sort_values('Count', ascending=False)
            if not mood_df.empty:
                top_mood = mood_df.iloc[0]['Mood']
                st.markdown(f"## 🎯 TOP: **{top_mood}**")
                st.markdown("Your taste is heavily leaning towards this energy.")

    st.divider()
    
    st.subheader("🎤 TOP ARTISTS")
    ok_a, artists = get_top_artists(12)
    if ok_a and artists:
        artist_list = artists.get('top_artists', [])
        if artist_list:
            artist_df = pd.DataFrame(artist_list).sort_values('track_count', ascending=True).tail(12)
            fig = px.bar(artist_df, x='track_count', y='artist', orientation='h',
                         color_discrete_sequence=['#8c00ff'])
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                font_color="white",
                xaxis=dict(gridcolor='rgba(140, 0, 255, 0.1)'),
                yaxis=dict(gridcolor='rgba(140, 0, 255, 0.1)')
            )
            st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("🏆 YOUR MOST POPULAR TRACKS")
    ok_t, tracks = get_top_tracks(10)
    if ok_t and tracks:
        track_list = tracks.get('top_tracks', [])
        for idx, track in enumerate(track_list[:10], 1):
            st.markdown(f"**{idx}. {track.get('track_name', 'Unknown')}** — {track.get('artist', 'Unknown')}")