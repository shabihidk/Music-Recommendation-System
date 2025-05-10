from flask import Flask, render_template, jsonify
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
from flask_sqlalchemy import SQLAlchemy
from config import JWT_SECRET_KEY, DATABASE_URL
from auth_routes import auth
from user_routes import user
from models import db, User, Playlist, Song, Genre, UserSong
import random
from datetime import datetime

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(user, url_prefix='/user')

# Initialize database
with app.app_context():
    db.create_all()

# Helper Functions
def get_playlists_from_db():
    playlists = Playlist.query.all()
    return [{'id': p.id, 'name': p.name, 'description': p.description} for p in playlists]

def get_playlist_by_id(playlist_id):
    playlist = Playlist.query.get(playlist_id)
    if playlist:
        songs = [{'id': s.id, 'title': s.title, 'artist': s.artist} for s in playlist.songs]
        return {'id': playlist.id, 'name': playlist.name, 'description': playlist.description, 'songs': songs}
    return None

def get_user_info(user_id):
    user = User.query.get(user_id)
    if user:
        return {'id': user.id, 'name': user.name, 'email': user.email}
    return None

def get_random_song_of_the_day():
    songs = Song.query.all()
    if songs:
        return random.choice(songs)
    return None

def get_ai_recommendations(user_id):
    # Placeholder for AI API integration (e.g., Spotify API or custom AI model)
    user_songs = UserSong.query.filter_by(user_id=user_id).all()
    genres = set([s.song.genre.name for s in user_songs])
    if not genres:
        genres = ['Pop']  # Default genre
    recommended_songs = Song.query.filter(Song.genre.has(Genre.name.in_(genres))).limit(5).all()
    return [{'id': s.id, 'title': s.title, 'artist': s.artist} for s in recommended_songs]

# Routes
@app.route('/')
def home():
    playlists = get_playlists_from_db()
    song_of_the_day = get_random_song_of_the_day()
    song_data = {'id': song_of_the_day.id, 'title': song_of_the_day.title, 'artist': song_of_the_day.artist} if song_of_the_day else None
    return render_template('index.html', playlists=playlists, song_of_the_day=song_data)

@app.route('/playlist/<int:playlist_id>')
def playlist(playlist_id):
    playlist = get_playlist_by_id(playlist_id)
    if playlist:
        return render_template('playlist.html', playlist=playlist)
    return "Playlist not found", 404

@app.route('/profile')
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user_info = get_user_info(user_id)
    if user_info:
        recommendations = get_ai_recommendations(user_id)
        return render_template('profile.html', user=user_info, recommendations=recommendations)
    return "User not found", 404

@app.route('/songs')
def songs():
    genres = Genre.query.all()
    songs = Song.query.all()
    return render_template('songs.html', genres=genres, songs=songs)

if __name__ == '__main__':
    app.run(debug=True)