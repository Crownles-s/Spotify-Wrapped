"""
Spotify Wrapped Analysis API — Complete Working Backend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import os
import pickle
from datetime import datetime
from collections import Counter

import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

df = None

# ============================================================================
# MOOD PREDICTION
# ============================================================================

def predict_mood(row):
    """Predict mood from audio features"""
    try:
        danceability = float(row.get('Danceability', 0.5))
        energy = float(row.get('Energy', 0.5))
        valence = float(row.get('Valence', 0.5))
        acousticness = float(row.get('Acousticness', 0.5))
        tempo = float(row.get('Tempo', 120))
        
        tempo_norm = min(tempo / 200, 1.0)
        
        happy_score = (valence * 0.4) + (energy * 0.3) + (danceability * 0.3)
        sad_score = ((1 - valence) * 0.5) + ((1 - energy) * 0.3) + (acousticness * 0.2)
        energetic_score = (energy * 0.5) + (danceability * 0.3) + (tempo_norm * 0.2)
        chill_score = (acousticness * 0.4) + ((1 - energy) * 0.4) + ((1 - danceability) * 0.2)
        
        scores = {
            'Happy': happy_score,
            'Sad': sad_score,
            'Energetic': energetic_score,
            'Chill': chill_score
        }
        
        return max(scores, key=scores.get)
    except:
        return 'Unknown'

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'data_loaded': df is not None}), 200


@app.route('/upload', methods=['POST'])
def upload():
    global df
    
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file'}), 400
        
        file = request.files['file']
        df = pd.read_csv(file)
        
        if df.empty:
            return jsonify({'error': 'Empty file'}), 400
        
        required = ['Track Name', 'Artist Name(s)', 'Duration (ms)', 'Popularity']
        missing = [col for col in required if col not in df.columns]
        if missing:
            return jsonify({'error': f'Missing: {missing}'}), 400
        
        # Add mood
        df['Mood'] = df.apply(predict_mood, axis=1)
        
        total_ms = df['Duration (ms)'].sum()
        
        return jsonify({
            'message': 'Success',
            'rows': len(df),
            'preview': {
                'total_duration_ms': int(total_ms),
                'unique_artists': int(df['Artist Name(s)'].nunique()),
                'avg_popularity': round(float(df['Popularity'].mean()), 1),
                'explicit_count': int(df['Explicit'].sum()) if 'Explicit' in df.columns else 0
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/stats', methods=['GET'])
def stats():
    global df
    if df is None:
        return jsonify({'error': 'No data'}), 400
    
    try:
        total_ms = df['Duration (ms)'].sum()
        hours = total_ms / 3600000
        days = hours / 24
        
        return jsonify({
            'total_tracks': len(df),
            'unique_artists': int(df['Artist Name(s)'].nunique()),
            'total_duration': {'ms': int(total_ms), 'hours': round(hours, 2), 'days': round(days, 2)},
            'popularity': {
                'average': round(float(df['Popularity'].mean()), 2),
                'median': round(float(df['Popularity'].median()), 2),
                'min': int(df['Popularity'].min()),
                'max': int(df['Popularity'].max())
            },
            'explicit': {
                'count': int(df['Explicit'].sum()) if 'Explicit' in df.columns else 0,
                'percentage': round((df['Explicit'].sum() / len(df) * 100), 2) if 'Explicit' in df.columns else 0
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/top-tracks', methods=['GET'])
def top_tracks():
    global df
    if df is None:
        return jsonify({'error': 'No data'}), 400
    
    try:
        n = request.args.get('n', 15, type=int)
        
        # Sort by Popularity score (highest first), NOT by play count
        df['Popularity'] = pd.to_numeric(df['Popularity'], errors='coerce')
        top = df.nlargest(n, 'Popularity')[['Track Name', 'Artist Name(s)', 'Popularity']]
        
        result = []
        for idx, row in top.iterrows():
            result.append({
                'track_name': str(row['Track Name']),
                'artist': str(row['Artist Name(s)']),
                'popularity': int(row['Popularity'])
            })
        
        return jsonify({'top_tracks': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/top-artists', methods=['GET'])
def top_artists():
    global df
    if df is None:
        return jsonify({'error': 'No data'}), 400
    
    try:
        n = request.args.get('n', 12, type=int)
        top = df['Artist Name(s)'].value_counts().head(n)
        
        result = [
            {'artist': artist, 'track_count': int(count), 'percentage': round((count / len(df)) * 100, 2)}
            for artist, count in top.items()
        ]
        
        return jsonify({'top_artists': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/mood-distribution', methods=['GET'])
def mood_distribution():
    global df
    if df is None:
        return jsonify({'error': 'No data'}), 400
    
    try:
        mood_counts = df['Mood'].value_counts()
        
        result = {
            mood: {'count': int(count), 'percentage': round((count / len(df)) * 100, 2)}
            for mood, count in mood_counts.items()
        }
        
        return jsonify({'mood_distribution': result}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/genre-distribution', methods=['GET'])
def genre_distribution_endpoint():
    """Get genre distribution"""
    global df
    if df is None:
        return jsonify({'error': 'No data'}), 400
    
    try:
        if 'Genres' not in df.columns:
            return jsonify({'genres': {}, 'genre_distribution': {}}), 200
        
        all_genres = []
        for genres_str in df['Genres']:
            if pd.notna(genres_str) and str(genres_str).strip() and str(genres_str) != '':
                genres_list = [g.strip() for g in str(genres_str).split(',') if g.strip()]
                all_genres.extend(genres_list)
        
        if not all_genres:
            return jsonify({'genres': {}, 'genre_distribution': {}}), 200
        
        genre_counts = Counter(all_genres)
        sorted_genres = dict(sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:15])
        
        result = {
            'genres': sorted_genres,  # For homepage
            'genre_distribution': {
                g: {'count': int(c), 'percentage': round((int(c) / len(all_genres) * 100), 2)} 
                for g, c in sorted_genres.items()
            }
        }
        return jsonify(result), 200
    except Exception as e:
        print(f"Genre error: {str(e)}")
        return jsonify({'genres': {}, 'genre_distribution': {}}), 200


@app.route('/temporal-analysis', methods=['GET'])
def temporal_analysis():
    """Yearly and monthly trends"""
    global df
    if df is None:
        return jsonify({'error': 'No data'}), 400
    
    try:
        if 'Added At' not in df.columns:
            return jsonify({'yearly_trends': {}, 'monthly_trends': {}, 'total_tracks': len(df)}), 200
        
        df['Added At'] = pd.to_datetime(df['Added At'], errors='coerce')
        df['Year'] = df['Added At'].dt.year
        df['Month'] = df['Added At'].dt.month
        
        yearly = df['Year'].value_counts().to_dict()
        monthly = df['Month'].value_counts().to_dict()
        
        return jsonify({
            'yearly_trends': {str(k): v for k, v in yearly.items()},
            'monthly_trends': {str(k): v for k, v in monthly.items()},
            'total_tracks': len(df)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/popularity-distribution', methods=['GET'])
def popularity_distribution():
    """Classify by popularity"""
    global df
    if df is None:
        return jsonify({'error': 'No data'}), 400
    
    try:
        def classify(pop):
            if pop < 40:
                return 'Low'
            elif pop < 70:
                return 'Medium'
            else:
                return 'High'
        
        df['Popularity_Class'] = df['Popularity'].apply(classify)
        dist = df['Popularity_Class'].value_counts().to_dict()
        
        return jsonify({
            'distribution': {
                k: {'count': int(v), 'percentage': round((v / len(df)) * 100, 2)}
                for k, v in dist.items()
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/audio-features', methods=['GET'])
def audio_features():
    """Average audio features"""
    global df
    if df is None:
        return jsonify({'error': 'No data'}), 400
    
    try:
        features = {}
        for col in ['Danceability', 'Energy', 'Valence', 'Acousticness', 'Speechiness', 'Instrumentalness', 'Liveness']:
            if col in df.columns:
                features[col.lower()] = round(float(df[col].mean()), 3)
        
        return jsonify({'audio_features': features}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/explicit-analysis', methods=['GET'])
def explicit_analysis():
    """Explicit content analysis"""
    global df
    if df is None:
        return jsonify({'error': 'No data'}), 400
    
    try:
        if 'Explicit' not in df.columns:
            return jsonify({'explicit_count': 0, 'clean_count': len(df), 'percentage': 0}), 200
        
        explicit_count = int(df['Explicit'].sum())
        clean_count = len(df) - explicit_count
        
        return jsonify({
            'explicit_count': explicit_count,
            'clean_count': clean_count,
            'percentage': round((explicit_count / len(df)) * 100, 2)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/start-rating-session', methods=['GET'])
def start_rating_session():
    """Get 10 random songs for rating from the recommender's dataset"""
    global recommender_df
    if recommender_df is None:
        return jsonify({'error': 'Recommender data not loaded'}), 503
    
    try:
        # Get random sample
        sample_size = min(10, len(recommender_df))
        sample_df = recommender_df.sample(n=sample_size)
        
        # Format response
        songs = []
        for idx, row in sample_df.iterrows():
            songs.append({
                'df_index': int(idx),
                'Track Name': str(row.get('track_name', 'Unknown')),
                'Artist Name(s)': str(row.get('artists', 'Unknown')),
                'track_name': str(row.get('track_name', 'Unknown')),
                'artists': str(row.get('artists', 'Unknown')),
                'popularity': int(row.get('popularity', 0)) if pd.notna(row.get('popularity')) else 0,
                'duration_ms': int(row.get('duration_ms', 0)) if pd.notna(row.get('duration_ms')) else 0
            })
        
        return jsonify({'songs': songs}), 200
    except Exception as e:
        print(f"Error in /start-rating-session: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# RECOMMENDATION ENDPOINTS
# ============================================================================
knn_model = None
scaler = None
recommender_data = None
recommender_df = None
scaled_features = None
feature_cols = None

def load_recommender_models():
    """Load all models needed for the recommender"""
    global knn_model, scaler, recommender_data, recommender_df, scaled_features, feature_cols
    try:
        # Assuming the script is run from the project root
        ml_dir = 'ml'
        
        with open(os.path.join(ml_dir, 'recommender_knn.pkl'), 'rb') as f:
            knn_model = pickle.load(f)
            
        with open(os.path.join(ml_dir, 'recommender_scaler.pkl'), 'rb') as f:
            scaler = pickle.load(f)
            
        with open(os.path.join(ml_dir, 'recommender_data.pkl'), 'rb') as f:
            recommender_data = pickle.load(f)
            recommender_df = recommender_data['df']
            # Normalize columns to lower case to avoid issues
            recommender_df.columns = recommender_df.columns.str.lower()
            scaled_features = recommender_data['scaled_features']
            feature_cols = recommender_data['feature_cols']
            
        print("Recommender models loaded successfully.")
        return True
    except FileNotFoundError:
        print("Recommender models not found. Please run backend/train_recommender.py first.")
        return False
    except Exception as e:
        print(f"Error loading recommender models: {e}")
        return False

@app.route('/submit-ratings-and-recommend', methods=['POST'])
def submit_ratings_and_recommend():
    """Generate recommendations based on user ratings"""
    if not all([knn_model, scaler, recommender_df is not None, scaled_features is not None]):
        return jsonify({'error': 'Recommender system not initialized'}), 503

    try:
        data = request.get_json()
        ratings = data.get('ratings', [])
        top_k = data.get('top_k', 10)

        if not ratings:
            return jsonify({'error': 'No ratings provided'}), 400

        # Create a user profile vector
        rated_features = []
        weights = []
        
        for r in ratings:
            df_index = r.get('df_index')
            rating = r.get('rating')
            
            if df_index is not None and rating is not None and df_index in recommender_df.index:
                loc = recommender_df.index.get_loc(df_index)
                rated_features.append(scaled_features[loc])
                weights.append(rating - 3)  # Center ratings (1-5 -> -2-2)

        if not rated_features:
            return jsonify({'error': 'Could not find any of the rated songs in the dataset'}), 400
        
        # Calculate weighted average to get user's taste profile
        user_profile = np.average(rated_features, axis=0, weights=weights).reshape(1, -1)
        
        # Find nearest neighbors
        distances, indices = knn_model.kneighbors(user_profile, n_neighbors=top_k * 2)
        
        # Format recommendations, excluding songs they've already rated
        rated_df_indices = {r['df_index'] for r in ratings}
        recommendations = []
        
        dist_iter = iter(distances.flatten())

        for i in indices.flatten():
            if len(recommendations) >= top_k:
                break
            
            dist = next(dist_iter)
            rec_df_index = recommender_df.index[i]
            if rec_df_index not in rated_df_indices:
                song = recommender_df.iloc[i]
                recommendations.append({
                    'track_name': song.get('track_name', 'Unknown'),
                    'artists': song.get('artists', 'Unknown'),
                    'year': int(song.get('year', 0)),
                    'popularity': int(song.get('popularity', 0)),
                    'track_genre': song.get('track_genre', 'N/A'),
                    'similarity_score': 1 - dist # Convert distance to similarity
                })

        return jsonify({
            'recommendations': recommendations,
            'count': len(recommendations),
            'based_on': f'{len(ratings)} rated songs',
            'source': 'Content-Based KNN Recommender'
        })

    except Exception as e:
        print(f"Error in /submit-ratings-and-recommend: {str(e)}")
        return jsonify({'error': 'Failed to generate recommendations'}), 500


if __name__ == '__main__':
    load_recommender_models()
    print("\n🎵 SPOTIFY WRAPPED API — Starting on http://localhost:5000\n")
    app.run(debug=False, host='0.0.0.0', port=5000)