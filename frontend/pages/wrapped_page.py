"""
Spotify Wrapped - Enhanced Sequential Feature Display
Navigate through your personalized music analysis with rich visualizations
"""

import streamlit as st
import sys
from pathlib import Path
import plotly.graph_objects as go

sys.path.append(str(Path(__file__).parent.parent))

from utils.api_client import APIClient
from utils.visualizations import Visualizer
from frontend.frontend_config import WRAPPED_CARD_CSS, COLORS

# Page config
st.set_page_config(
    page_title="Your Wrapped",
    page_icon="🎵",
    layout="wide"
)

from frontend.global_css import apply_global_css
apply_global_css()

# Apply theme
st.markdown(WRAPPED_CARD_CSS, unsafe_allow_html=True)

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

st.sidebar.markdown(f"# 🎵 Spotify Wrapped")
st.sidebar.markdown("### Your listening story, visualized.")
st.sidebar.divider()

st.sidebar.markdown("### 🧭 NAVIGATE")
nav_col1, nav_col2, nav_col3 = st.sidebar.columns(3)

with nav_col1:
    if st.button("🏠", help="Home Page", use_container_width=True, key="nav_home_wrapped"):
        st.switch_page("streamlit_app.py")

with nav_col2:
    if st.button("🎵", help="Your Wrapped", use_container_width=True, key="nav_wrapped_wrapped"):
        st.rerun()

with nav_col3:
    if st.button("🎯", help="Recommendations", use_container_width=True, key="nav_rec_wrapped"):
        st.switch_page("pages/recommendations_page.py")

st.sidebar.divider()
st.sidebar.info("📋 Explore your personalized music analytics")
st.sidebar.divider()

if st.sidebar.button("🗑️ CLEAR SESSION", use_container_width=True):
    st.session_state.clear()
    st.rerun()

api = APIClient()
viz = Visualizer()

# Features to display
FEATURES = [
    {'id': 'top_tracks', 'title': '🎵 Your Top Tracks', 'description': 'Songs you loved most'},
    {'id': 'top_artists', 'title': '🎤 Top Artists', 'description': 'Your favorite creators'},
    {'id': 'temporal', 'title': '📅 Songs Over Time', 'description': 'Your listening journey'},
    {'id': 'audio_features', 'title': '🎛️ Audio Profile', 'description': 'Your sound characteristics'},
    {'id': 'mood_analysis', 'title': '😊 Mood Analysis', 'description': 'Your emotional landscape'},
    {'id': 'popularity', 'title': '⭐ Popularity Style', 'description': 'Mainstream or underground?'},
    {'id': 'mood_radar', 'title': '📊 Mood Radar', 'description': 'Emotional profile at a glance'},
    {'id': 'genre', 'title': '🎸 Genre Explorer', 'description': 'Your musical diversity'},
    {'id': 'explicit', 'title': '🔞 Explicit Content', 'description': 'Rating your playlist'},
]

def safe_api_call(func, *args, **kwargs):
    """Safely call API and handle errors"""
    try:
        result = func(*args, **kwargs)
        return result if result else {}
    except Exception as e:
        st.error(f"⚠️ Error loading data: {str(e)}")
        return None

def render_feature(feature_idx):
    """Render individual feature with visualizations"""
    if feature_idx >= len(FEATURES):
        return
    
    feature = FEATURES[feature_idx]
    feature_id = feature['id']
    
    # ---------- TOP TRACKS ----------
    if feature_id == "top_tracks":
        data = safe_api_call(api.get_top_tracks, n=15)
        if data:
            tracks = data.get('top_tracks', [])
            col1, col2 = st.columns([1.5, 1])
            
            with col1:
                fig = viz.plot_top_tracks(tracks)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📍 Track Stats")
                total_tracks = len(tracks)
                avg_popularity = sum([t.get('popularity', 0) for t in tracks]) / total_tracks if tracks else 0
                st.metric("Total Tracks", total_tracks)
                st.metric("Avg Popularity", f"{avg_popularity:.0f}")
        return
    
    # ---------- TOP ARTISTS ----------
    elif feature_id == "top_artists":
        data = safe_api_call(api.get_top_artists, n=12)
        if data:
            artists = data.get('top_artists', [])
            col1, col2 = st.columns([1.5, 1])
            
            with col1:
                fig = viz.plot_top_artists(artists)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("🎤 Artist Stats")
                st.metric("Total Artists", len(artists))
                if artists:
                    st.metric("Top Artist", artists[0].get('artist', 'Unknown'))
                    st.metric("Top Tracks", artists[0].get('track_count', 0))
        return
    
    # ---------- TEMPORAL ANALYSIS ----------
    elif feature_id == "temporal":
        data = safe_api_call(api.get_temporal_analysis)
        if data:
            col1, col2 = st.columns([1.5, 1])
            
            with col1:
                yearly = data.get("yearly_trends", {})
                monthly = data.get("monthly_trends", {})
                fig = viz.plot_temporal_trends(yearly, monthly)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📅 Timeline")
                st.metric("Total Tracks", data.get('total_tracks', 0))
                yearly_count = len(data.get('yearly_trends', {}))
                st.info(f"📊 Spanning {yearly_count} year{'s' if yearly_count != 1 else ''}")
        return
    
    # ---------- AUDIO FEATURES ----------
    elif feature_id == "audio_features":
        data = safe_api_call(api.get_audio_features)
        if data:
            audio = data.get('audio_features') or {}
            
            # Robust normalization: handle case, whitespace for ALL keys
            for k in list(audio.keys()):
                clean_k = k.strip().lower()
                if clean_k not in audio:
                    audio[clean_k] = audio[k]
            
            # Check if audio features are present and non-zero
            has_data = any(float(audio.get(k) or 0) > 0 for k in ['danceability', 'energy', 'valence'])
            
            if not audio or not has_data:
                st.warning("⚠️ Audio features not available")
                st.info("Your data source doesn't contain audio features (Danceability, Energy, Valence).")
                with st.expander("Debug: Available Columns"):
                    st.write(list(audio.keys()))
                return

            col1, col2 = st.columns([1.5, 1])
            
            with col1:
                fig = viz.plot_audio_features_radar({'audio_features': audio})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("🎛️ Sound Profile")
                st.metric("Danceability", f"{audio.get('danceability', 0):.2f}")
                st.metric("Energy", f"{audio.get('energy', 0):.2f}")
                st.metric("Valence", f"{audio.get('valence', 0):.2f}")
        return
    
    # ---------- MOOD ANALYSIS ----------
    elif feature_id == "mood_analysis":
        data = safe_api_call(api.get_mood_distribution)
        if data:
            mood_dist = data.get('mood_distribution', {})
            col1, col2 = st.columns([1.5, 1])
            
            with col1:
                fig = viz.plot_mood_distribution(mood_dist)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("😊 Mood Breakdown")
                for mood, stats in mood_dist.items():
                    pct = stats.get('percentage', 0)
                    st.progress(pct / 100, text=f"{mood}: {pct:.1f}%")
        return
    
    # ---------- POPULARITY STYLE ----------
    elif feature_id == "popularity":
        data = safe_api_call(api.get_popularity_distribution)
        if data:
            dist = data.get('distribution', {})
            col1, col2 = st.columns([1.5, 1])
            
            with col1:
                fig = viz.plot_popularity_distribution(dist)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("⭐ Listener Profile")
                high = dist.get('High', {}).get('count', 0)
                med = dist.get('Medium', {}).get('count', 0)
                low = dist.get('Low', {}).get('count', 0)
                
                if high > med and high > low:
                    st.success("🌟 Mainstream Listener - You love popular hits!")
                elif low > high:
                    st.info("🎧 Underground Explorer - You discover hidden gems!")
                else:
                    st.info("🎵 Balanced Listener - Mix of popular and underground!")
        return
    
    # ---------- MOOD RADAR ----------
    elif feature_id == "mood_radar":
        data = safe_api_call(api.get_mood_distribution)
        if data:
            mood_dist = data.get('mood_distribution', {})
            fig = viz.plot_mood_radar(mood_dist)
            st.plotly_chart(fig, use_container_width=True)
        return
    
    # ---------- GENRE DISTRIBUTION ----------
    elif feature_id == "genre":
        data = safe_api_call(api.get_genre_distribution)  # Use new endpoint
        if data:
            genres = data.get('genre_distribution', {})
            if genres:
                col1, col2 = st.columns([1.5, 1])
                
                with col1:
                    fig = viz.plot_genre_distribution(genres)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.subheader("🎸 Genre Stats")
                    st.metric("Total Genres", len(genres))
                    if genres:
                        top_genre = max(genres.items(), key=lambda x: x[1].get('count', 0))
                        st.metric("Top Genre", top_genre[0])
            else:
                st.info("📊 No genre data available in your playlist.")
        return
    
    # ---------- EXPLICIT CONTENT ----------
    elif feature_id == "explicit":
        data = safe_api_call(api.get_explicit_analysis)
        if data:
            col1, col2 = st.columns([1.5, 1])
            
            with col1:
                fig = viz.plot_explicit_distribution(data)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("🔞 Content Rating")
                st.metric("Explicit Tracks", data.get('explicit_count', 0))
                st.metric("Explicit %", f"{data.get('percentage', 0):.1f}%")
        return


# ============================================================================
# MAIN UI
# ============================================================================

st.title("🎵 Your 2024 Wrapped")

# Check if data is uploaded
if not st.session_state.get('data_uploaded', False):
    st.warning("⚠️ Please upload your playlist data first!")
    st.stop()

# Initialize session state
if "feature_index" not in st.session_state:
    st.session_state.feature_index = 0

# Navigation buttons
col1, col2, col3, col4 = st.columns([1, 2, 2, 1])

with col1:
    if st.button("⬅️ Prev", use_container_width=True):
        if st.session_state.feature_index > 0:
            st.session_state.feature_index -= 1
            st.rerun()

with col2:
    progress = (st.session_state.feature_index + 1) / len(FEATURES)
    st.progress(progress)

with col3:
    st.markdown(
        f"<div style='text-align:center; padding:8px;'><b>{st.session_state.feature_index + 1} / {len(FEATURES)}</b></div>",
        unsafe_allow_html=True
    )

with col4:
    if st.button("Next ➡️", use_container_width=True):
        if st.session_state.feature_index < len(FEATURES) - 1:
            st.session_state.feature_index += 1
            st.rerun()

st.divider()

# Render current feature
render_feature(st.session_state.feature_index)

# Show feature info
current_feature = FEATURES[st.session_state.feature_index]
st.markdown(f"### {current_feature['title']}")
st.caption(current_feature['description'])