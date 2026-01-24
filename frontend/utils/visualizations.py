"""
Visualization utilities for Spotify Wrapped
Updated Theme: Glowy Purple, Vibrant Pink, and White
"""

import plotly.graph_objects as go
import plotly.express as px

class Visualizer:
    def __init__(self):
        # New Theme Palette
        self.colors = {
            'primary': '#8c00ff',    # Deep Purple
            'secondary': '#ff00e5',  # Vibrant Pink
            'accent': '#c8b3ff',     # Light Purple Glow
            'white': '#ffffff',      # Pure White
            'dark_bg': '#040407'     # Deep Black
        }
        
        # Categorical palette for Pie charts and Multi-bar charts
        self.palette = [self.colors['primary'], self.colors['secondary'], self.colors['white'], self.colors['accent']]
        
        self.base_layout = {
            'paper_bgcolor': 'rgba(0,0,0,0)',
            'plot_bgcolor': 'rgba(0,0,0,0)',
            'font': dict(color='#ffffff', family='Montserrat, sans-serif'),
            'showlegend': False,
            'margin': dict(l=20, r=20, t=60, b=20)
        }

    def _apply_axes_style(self, fig):
        """Helper to apply consistent grid and axis styling"""
        fig.update_xaxes(gridcolor='rgba(140, 0, 255, 0.1)', zeroline=False)
        fig.update_yaxes(gridcolor='rgba(140, 0, 255, 0.1)', zeroline=False)
        return fig

    def plot_top_tracks(self, tracks):
        """Top tracks horizontal bar with Purple Gradient"""
        names = [t.get('track_name', 'Unknown')[:25] for t in tracks[:10]]
        pop = [t.get('popularity', 0) for t in tracks[:10]]
        
        fig = go.Figure(data=[go.Bar(
            y=names, x=pop, orientation='h',
            marker=dict(
                color=pop, 
                colorscale=[[0, '#1a0033'], [1, self.colors['primary']]],
                line=dict(color=self.colors['accent'], width=1)
            ),
            text=pop, textposition='outside'
        )])
        fig.update_layout(**self.base_layout, height=400, title='Top Tracks')
        fig.update_yaxes(autorange='reversed')
        return self._apply_axes_style(fig)
    
    def plot_top_artists(self, artists):
        """Top artists horizontal bar"""
        names = [a.get('artist', 'Unknown')[:25] for a in artists[:10]]
        counts = [a.get('track_count', 0) for a in artists[:10]]
        
        fig = go.Figure(data=[go.Bar(
            y=names, x=counts, orientation='h',
            marker=dict(
                color=counts, 
                colorscale=[[0, '#330066'], [1, self.colors['secondary']]],
                line=dict(color='#ffffff', width=1)
            ),
            text=counts, textposition='outside'
        )])
        fig.update_layout(**self.base_layout, height=400, title='Top Artists')
        fig.update_yaxes(autorange='reversed')
        return self._apply_axes_style(fig)
    
    def plot_mood_distribution(self, mood_dist):
        """Pie chart using the Purple/Pink/White palette"""
        moods = list(mood_dist.keys())
        pcts = [mood_dist[m].get('percentage', 0) for m in moods]
        
        fig = go.Figure(data=[go.Pie(
            labels=moods, values=pcts,
            marker=dict(colors=self.palette, line=dict(color=self.colors['dark_bg'], width=2)),
            textposition='inside', textinfo='label+percent',
            hole=0.4
        )])
        fig.update_layout(**self.base_layout, height=400, title='Mood Distribution')
        return fig
    
    def plot_mood_radar(self, mood_dist):
        """Radar chart with Pink Glow"""
        moods = list(mood_dist.keys())
        values = [mood_dist[m].get('percentage', 0) for m in moods]
        
        fig = go.Figure(data=[go.Scatterpolar(
            r=values, theta=moods,
            fill='toself',
            marker=dict(color=self.colors['secondary']),
            line=dict(color=self.colors['secondary'], width=3),
            fillcolor='rgba(255, 0, 229, 0.3)'
        )])
        fig.update_layout(
            **self.base_layout, 
            height=400, 
            title='Mood Radar', 
            polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(gridcolor='rgba(255,255,255,0.1)'))
        )
        return fig
    
    def plot_genre_distribution(self, genres):
        """Top genres bar chart in Purple"""
        names = list(genres.keys())[:10]
        counts = [genres[g].get('count', 0) for g in names]
        
        fig = go.Figure(data=[go.Bar(
            x=names, y=counts,
            marker=dict(color=self.colors['primary'], line=dict(color=self.colors['accent'], width=1)),
            text=counts, textposition='outside'
        )])
        fig.update_layout(**self.base_layout, height=400, title='Genres', xaxis=dict(tickangle=-45))
        return self._apply_axes_style(fig)
    
    def plot_temporal_trends(self, yearly, monthly):
        """Timeline chart with glowing Pink line"""
        years = sorted([int(y) for y in yearly.keys()])
        counts = [yearly[str(y)] for y in years]
        
        fig = go.Figure(data=[go.Scatter(
            x=years, y=counts, mode='lines+markers',
            line=dict(color=self.colors['secondary'], width=4),
            marker=dict(size=10, color=self.colors['white'], line=dict(color=self.colors['secondary'], width=2))
        )])
        fig.update_layout(**self.base_layout, height=400, title='Listening Over Time')
        return self._apply_axes_style(fig)
    
    def plot_audio_features_radar(self, stats):
        """Radar for audio features with Purple Glow"""
        features = ['danceability', 'energy', 'valence', 'acousticness']
        values = []
        
        audio = stats.get('audio_features', {})
        for f in features:
            val = audio.get(f, 0)
            if val <= 1: val = val * 100
            values.append(val)
        
        fig = go.Figure(data=[go.Scatterpolar(
            r=values, theta=[f.title() for f in features],
            fill='toself',
            marker=dict(color=self.colors['accent'], size=8),
            line=dict(color=self.colors['primary'], width=3),
            fillcolor='rgba(140, 0, 255, 0.4)'
        )])
        fig.update_layout(
            **self.base_layout, 
            height=400, 
            title='Audio Profile',
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], color='#9aa0a6', gridcolor='rgba(255,255,255,0.1)'),
                bgcolor='rgba(0,0,0,0)'
            )
        )
        return fig
    
    def plot_popularity_distribution(self, dist):
        """Popularity breakdown in Theme Colors"""
        cats = list(dist.keys())
        counts = [dist[c].get('count', 0) for c in cats]
        
        fig = go.Figure(data=[go.Bar(
            x=cats, y=counts,
            marker=dict(color=self.palette[:3]),
            text=counts, textposition='outside'
        )])
        fig.update_layout(**self.base_layout, height=400, title='Popularity Preference')
        return self._apply_axes_style(fig)
    
    def plot_explicit_distribution(self, data):
        """Explicit vs clean chart"""
        fig = go.Figure(data=[go.Bar(
            x=['Explicit', 'Clean'],
            y=[data.get('explicit_count', 0), data.get('clean_count', 0)],
            marker=dict(color=[self.colors['secondary'], self.colors['primary']]),
            text=[data.get('explicit_count', 0), data.get('clean_count', 0)],
            textposition='outside'
        )])
        fig.update_layout(**self.base_layout, height=400, title='Explicit Content')
        return self._apply_axes_style(fig)