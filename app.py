from flask import Flask, render_template, redirect, url_for
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, verify_jwt_in_request
from models import db, User, Playlist, Song, Recommendation, SongOfTheDay, Genre, UserSong, UserGenrePreference
from auth_routes import auth
from user_routes import user
from db import init_db
from functools import wraps
import random
from datetime import date

app = Flask(__name__)
app.config.from_object('config')
init_db(app)
jwt = JWTManager(app)

app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(user, url_prefix='/user')

def jwt_optional(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request(optional=True)
            return fn(*args, **kwargs)
        except:
            return fn(*args, **kwargs)
    return wrapper

@app.context_processor
def inject_user():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id) if user_id else None
        return {'current_user': user}
    except:
        return {'current_user': None}

@app.route('/')
@jwt_optional
def home():
    playlists = get_playlists_from_db()
    song_of_the_day = get_song_of_the_day()
    song_data = {'id': song_of_the_day.song.id, 'title': song_of_the_day.song.title, 'artist': song_of_the_day.song.artist} if song_of_the_day else None
    trending_songs = Song.query.order_by(Song.popularity_score.desc()).limit(5).all()
    popular_genres = Genre.query.all()
    return render_template('index.html', playlists=playlists, song_of_the_day=song_data, trending_songs=trending_songs, popular_genres=popular_genres)

@app.route('/songs')
@jwt_optional
def songs():
    genres = Genre.query.all()
    songs = Song.query.all()
    return render_template('songs.html', genres=genres, songs=songs)

@app.route('/first-login')
@jwt_required()
def first_login():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.selected_songs:
        return redirect(url_for('home'))
    songs = Song.query.order_by(Song.popularity_score.desc()).limit(10).all()
    return render_template('first_login.html', songs=songs)

@app.route('/profile')
@jwt_required()
def profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user:
        generate_recommendations(user_id)
        recommendations = Recommendation.query.filter_by(user_id=user_id).all()
        selected_songs = UserSong.query.filter_by(user_id=user_id).all()
        return render_template('profile.html', user=user, recommendations=recommendations, selected_songs=selected_songs)
    return "User not found", 404

@app.route('/song/<int:song_id>')
@jwt_required()
def song(song_id):
    song = Song.query.get(song_id)
    if song:
        song_data = {
            "id": song.id,
            "title": song.title,
            "artist": song.artist,
            "genre": song.genre.name if song.genre else None,
            "release_date": song.release_date,
            "popularity_score": song.popularity_score,
            "recommendation_score": song.recommendation_score
        }
        user_song = UserSong.query.filter_by(user_id=get_jwt_identity(), song_id=song.id).first()
        liked = user_song.liked if user_song else None
        return render_template('song.html', song=song, song_data=song_data, liked=liked)
    return "Song not found", 404

@app.route('/playlist/<int:playlist_id>')
@jwt_optional
def playlist(playlist_id):
    playlist = Playlist.query.get(playlist_id)
    if playlist:
        return render_template('playlist.html', playlist=playlist)
    return "Playlist not found", 404

@app.route('/questionnaire')
@jwt_required()
def questionnaire():
    return render_template('questionnaire.html')

def get_playlists_from_db():
    user_id = get_jwt_identity()
    if user_id:
        return Playlist.query.filter_by(user_id=user_id).all()
    return []

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
    preferences = UserGenrePreference.query.filter_by(user_id=user_id).all()
    if not preferences:
        return
    selected_song_ids = [us.song_id for us in UserSong.query.filter_by(user_id=user_id).all()]
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