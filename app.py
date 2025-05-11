from flask import Flask, render_template, redirect, url_for
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, verify_jwt_in_request
from models import db, User, Playlist, Song, Recommendation, SongOfTheDay, Genre, UserSong, UserGenrePreference
from auth_routes import auth
from user_routes import user
from functools import wraps
import random
from datetime import date

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)
jwt = JWTManager(app)

app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(user, url_prefix='/user')

# JWT optional decorator
def jwt_optional(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
            return fn(*args, **kwargs)
        except:
            return fn(*args, **kwargs)
    return wrapper

# Context processor for current_user
@app.context_processor
def inject_user():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id) if user_id else None
        return {'current_user': user}
    except:
        return {'current_user': None}

# Home route
@app.route('/')
@jwt_optional
def home():
    playlists = get_playlists_from_db()
    song_of_the_day = get_song_of_the_day()
    song_data = {'id': song_of_the_day.song.id, 'title': song_of_the_day.song.title, 'artist': song_of_the_day.song.artist} if song_of_the_day else None
    trending_songs = Song.query.order_by(Song.popularity_score.desc()).limit(5).all()
    popular_genres = Genre.query.all()
    return render_template('index.html', playlists=playlists, song_of_the_day=song_data, trending_songs=trending_songs, popular_genres=popular_genres)

# Songs route
@app.route('/songs')
@jwt_optional
def songs():
    genres = Genre.query.all()
    songs = Song.query.all()
    return render_template('songs.html', genres=genres, songs=songs)

# First login song selection
@app.route('/first-login')
@jwt_required()
def first_login():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.selected_songs:  # If user already has selected songs, redirect to home
        return redirect(url_for('home'))
    songs = Song.query.order_by(Song.popularity_score.desc()).limit(10).all()  # Show top 10 popular songs
    return render_template('first_login.html', songs=songs)

# Profile route
@app.route('/profile')
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user:
        generate_recommendations(user_id)  # Generate new recommendations if needed
        recommendations = Recommendation.query.filter_by(user_id=user_id).all()
        selected_songs = UserSong.query.filter_by(user_id=user_id).all()
        return render_template('profile.html', user=user, recommendations=recommendations, selected_songs=selected_songs)
    return "User not found", 404

# Song route
@app.route('/song/<int:song_id>')
@jwt_optional
def song(song_id):
    song = Song.query.get(song_id)
    if song:
        return render_template('song.html', song=song)
    return "Song not found", 404

# Playlist route
@app.route('/playlist/<int:playlist_id>')
@jwt_optional
def playlist(playlist_id):
    playlist = Playlist.query.get(playlist_id)
    if playlist:
        return render_template('playlist.html', playlist=playlist)
    return "Playlist not found", 404

# Helper functions
def get_playlists_from_db():
    return Playlist.query.all()

def get_song_of_the_day():
    today = date.today()
    sotd = SongOfTheDay.query.filter_by(date=today).first()
    if not sotd:
        songs = Song.query.all()
        if songs:
            song = random.choice(songs)
            sotd = SongOfTheDay(date=today, song_id=song.id)
            db.session.add(sotd)
            db.session.commit()
            return sotd
    return sotd

def generate_recommendations(user_id):
    user = User.query.get(user_id)
    if not user:
        return
    # Get user's genre preferences
    preferences = UserGenrePreference.query.filter_by(user_id=user_id).all()
    if not preferences:
        return
    # Get songs the user hasn't selected yet
    selected_song_ids = [us.song_id for us in UserSong.query.filter_by(user_id=user_id).all()]
    # Recommend based on genre preferences and popularity
    for pref in preferences:
        songs = Song.query.filter(
            Song.genre_id == pref.genre_id,
            Song.id.notin_(selected_song_ids)
        ).order_by(Song.popularity_score.desc()).limit(2).all()
        for song in songs:
            existing = Recommendation.query.filter_by(user_id=user_id, song_id=song.id).first()
            if not existing:
                rec = Recommendation(
                    user_id=user_id,
                    song_id=song.id,
                    reason=f"Recommended based on your interest in {pref.genre.name}"
                )
                db.session.add(rec)
    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)