"""
Spotify Wrapped - Rating-Based Recommendation Engine
Rate 10 songs and get personalized recommendations
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from utils.api_client import APIClient
from frontend.frontend_config import COLORS

# Page config
st.set_page_config(
    page_title="Recommendations",
    page_icon="🎯",
    layout="wide"
)

from frontend.global_css import apply_global_css
apply_global_css()

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

st.sidebar.markdown(f"# 🎯 Recommendations")
st.sidebar.markdown("### Rate songs & get personalized picks")
st.sidebar.divider()

st.sidebar.markdown("### 🧭 NAVIGATE")
nav_col1, nav_col2, nav_col3 = st.sidebar.columns(3)

with nav_col1:
    if st.button("🏠", help="Home Page", use_container_width=True, key="nav_home_rec"):
        st.switch_page("streamlit_app.py")

with nav_col2:
    if st.button("🎵", help="Your Wrapped", use_container_width=True, key="nav_wrapped_rec"):
        st.switch_page("pages/wrapped_page.py")

with nav_col3:
    if st.button("🎯", help="Recommendations", use_container_width=True, key="nav_rec_rec"):
        st.rerun()

st.sidebar.divider()
st.sidebar.info("⭐ Rate 10 songs to get AI recommendations")
st.sidebar.divider()

if st.sidebar.button("🗑️ CLEAR SESSION", use_container_width=True):
    st.session_state.clear()
    st.rerun()

api = APIClient()

# Initialize session state
if 'rating_phase' not in st.session_state:
    st.session_state.rating_phase = True
if 'current_song_index' not in st.session_state:
    st.session_state.current_song_index = 0
if 'songs_to_rate' not in st.session_state:
    st.session_state.songs_to_rate = None
if 'user_ratings' not in st.session_state:
    st.session_state.user_ratings = {}
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None
if 'current_rating' not in st.session_state:
    st.session_state.current_rating = 0


def reset_session():
    """Reset all session state variables"""
    st.session_state.rating_phase = True
    st.session_state.current_song_index = 0
    st.session_state.songs_to_rate = None
    st.session_state.user_ratings = {}
    st.session_state.recommendations = None
    st.session_state.current_rating = 0


def load_songs_to_rate():
    """Load 10 random songs from API"""
    with st.spinner("🎵 Loading songs..."):
        result = api.start_rating_session()
        
        if result and 'songs' in result:
            songs = result['songs']
            # Normalize field names
            for song in songs:
                song['artists'] = song.get('Artist Name(s)', song.get('artists', 'Unknown'))
                song['track_name'] = song.get('Track Name', song.get('track_name', 'Unknown'))
            
            st.session_state.songs_to_rate = songs
            st.session_state.user_ratings = {}
            st.session_state.current_song_index = 0
            st.session_state.current_rating = 0
            return True
        return False


def render_star_rating(song_id, current_rating):
    """Render interactive star rating"""
    st.markdown("### ⭐ Rate this song (1-5 stars)")
    
    cols = st.columns(5)
    rating = current_rating
    
    for i, col in enumerate(cols, 1):
        with col:
            if st.button(
                "⭐" if i <= current_rating else "☆",
                key=f"star_{song_id}_{i}",
                help=f"Rate {i} star{'s' if i > 1 else ''}"
            ):
                rating = i
                st.session_state.current_rating = i
    
    return rating


def render_rating_phase():
    """Render the rating interface"""
    if not st.session_state.songs_to_rate:
        if not load_songs_to_rate():
            st.error("Failed to load songs. Please try again.")
            return
    
    songs = st.session_state.songs_to_rate
    current_idx = st.session_state.current_song_index
    
    if current_idx >= len(songs):
        st.error("Invalid song index")
        return
    
    current_song = songs[current_idx]
    is_last_song = current_idx == len(songs) - 1
    
    # Song display
    st.markdown(f"""
    <div class='song-card'>
        <h2>{current_song.get('track_name', 'Unknown')}</h2>
        <p><strong>Artist:</strong> {current_song.get('artists', 'Unknown')}</p>
        <p style='color: #b3b3b3;'>Song {current_idx + 1} of {len(songs)}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Rating
    st.markdown("### ⭐ Rate this song")
    st.session_state.current_rating = st.slider("", 1, 5, st.session_state.current_rating, key=f"rating_{current_idx}")
    
    # Navigation
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬅️ Previous", use_container_width=True, disabled=current_idx == 0):
            st.session_state.current_song_index -= 1
            st.rerun()
    
    with col2:
        can_proceed = st.session_state.current_rating > 0
        button_text = "✅ Submit & Get Recommendations" if is_last_song else "Next ➡️"
        
        if st.button(button_text, key="next_btn", use_container_width=True, disabled=not can_proceed):
            st.session_state.user_ratings[current_idx] = {
                'df_index': current_song['df_index'],
                'rating': st.session_state.current_rating
            }
            
            if is_last_song:
                submit_ratings()
            else:
                st.session_state.current_song_index += 1
                if st.session_state.current_song_index in st.session_state.user_ratings:
                    st.session_state.current_rating = st.session_state.user_ratings[st.session_state.current_song_index]['rating']
                else:
                    st.session_state.current_rating = 0
                st.rerun()
    
    with col3:
        if st.button("🔄 Reset", use_container_width=True):
            reset_session()
            st.rerun()
    
    # Show rated songs summary
    if st.session_state.user_ratings:
        with st.expander(f"✅ Rated Songs ({len(st.session_state.user_ratings)}/10)"):
            for idx, rating_data in st.session_state.user_ratings.items():
                if idx < len(songs):
                    song = songs[idx]
                    stars = "⭐" * rating_data['rating']
                    st.markdown(f"**{song['track_name']}** by {song['artists']} - {stars}")


def submit_ratings():
    """Submit ratings and get recommendations"""
    with st.spinner("🎵 Generating your personalized recommendations..."):
        # Convert ratings dict to list format required by API
        ratings_list = [
            st.session_state.user_ratings[i] 
            for i in range(len(st.session_state.songs_to_rate))
        ]
        
        # Call API
        result = api.submit_ratings_and_recommend(ratings_list, top_k=10)
        
        if result:
            st.session_state.recommendations = result
            st.session_state.rating_phase = False
            st.rerun()
        else:
            st.error("Failed to get recommendations. Please try again.")


def render_recommendations_phase():
    """Render the recommendations results"""
    st.markdown("<h1 style='text-align: center;'>🎵 Your Personalized Recommendations</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px; color: #b3b3b3;'>Based on your ratings</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    if not st.session_state.recommendations:
        st.error("No recommendations available")
        return
    
    recs = st.session_state.recommendations
    
    # Show summary
    st.success(f"✅ Found {recs['count']} personalized recommendations!")
    st.info(f"📊 {recs['based_on']} • {recs['source']}")
    
    st.markdown("### 🎧 Your Recommended Tracks")
    
    # Display recommendations
    for i, rec in enumerate(recs['recommendations'], 1):
        st.markdown(f"""
        <div class='rec-card'>
            <h3 style='margin: 0 0 10px 0;'>#{i} {rec['track_name']}</h3>
            <p style='margin: 5px 0; font-size: 16px;'><strong>Artist:</strong> {rec['artists']}</p>
            <p style='margin: 5px 0; font-size: 14px; color: #b3b3b3;'><strong>Genre:</strong> {rec.get('track_genre', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Additional info
        col1, col2, col3 = st.columns(3)
        with col1:
            if 'year' in rec:
                st.metric("Year", rec['year'])
        with col2:
            if 'popularity' in rec:
                st.metric("Popularity", f"{rec['popularity']}/100")
        with col3:
            if 'similarity_score' in rec and rec['similarity_score']:
                match_pct = rec['similarity_score'] * 100
                st.metric("Match", f"{match_pct:.1f}%")
        
        st.markdown("---")
    
    # Start over button
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Rate New Songs", key="start_over"):
            reset_session()
            st.rerun()


def main():
    """Main app logic"""
    
    # Check if rating phase or recommendations phase
    if st.session_state.rating_phase:
        render_rating_phase()
    else:
        render_recommendations_phase()


if __name__ == "__main__":
    main()
