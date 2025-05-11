from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Playlist, Song, UserSong, Recommendation, UserGenrePreference
from sqlalchemy.sql import func

user = Blueprint('user', __name__)

@user.route('/playlists', methods=['GET'])
@jwt_required()
def get_playlists():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user:
        playlists = [{"id": p.id, "name": p.name, "description": p.description} for p in user.playlists]
        return jsonify(playlists), 200
    return jsonify({"msg": "User not found"}), 404

@user.route('/create-playlist', methods=['POST'])
@jwt_required()
def create_playlist():
    user_id = get_jwt_identity()
    data = request.get_json()
    name = data.get('name')
    description = data.get('description', '')
    if not name:
        return jsonify({"msg": "Playlist name is required"}), 400
    playlist = Playlist(name=name, description=description, user_id=user_id)
    db.session.add(playlist)
    db.session.commit()
    return jsonify({"msg": "Playlist created successfully", "id": playlist.id}), 201

@user.route('/playlist/<int:playlist_id>', methods=['GET'])
@jwt_required()
def get_playlist(playlist_id):
    user_id = get_jwt_identity()
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=user_id).first()
    if playlist:
        songs = [{"id": s.id, "title": s.title, "artist": s.artist} for s in playlist.songs]
        return jsonify({
            "id": playlist.id,
            "name": playlist.name,
            "description": playlist.description,
            "songs": songs
        }), 200
    return jsonify({"msg": "Playlist not found"}), 404

@user.route('/song/<int:song_id>', methods=['GET'])
@jwt_required()
def get_song(song_id):
    song = Song.query.get(song_id)
    if not song:
        return jsonify({"msg": "Song not found"}), 404
    return jsonify({
        "id": song.id,
        "title": song.title,
        "artist": song.artist,
        "genre": song.genre.name if song.genre else None,
        "release_date": song.release_date,
        "popularity_score": song.popularity_score,
        "recommendation_score": song.recommendation_score
    }), 200

@user.route('/select-song', methods=['POST'])
@jwt_required()
def select_song():
    user_id = get_jwt_identity()
    data = request.get_json()
    song_id = data.get('song_id')
    if not Song.query.get(song_id):
        return jsonify({"msg": "Song not found"}), 404
    existing = UserSong.query.filter_by(user_id=user_id, song_id=song_id).first()
    if existing:
        return jsonify({"msg": "Song already selected"}), 400
    user_song = UserSong(user_id=user_id, song_id=song_id)
    db.session.add(user_song)
    db.session.commit()
    return jsonify({"msg": "Song selected successfully"}), 200

@user.route('/like-song', methods=['POST'])
@jwt_required()
def like_song():
    user_id = get_jwt_identity()
    data = request.get_json()
    song_id = data.get('song_id')
    liked = data.get('liked')
    song = Song.query.get(song_id)
    if not song:
        return jsonify({"msg": "Song not found"}), 404
    user_song = UserSong.query.filter_by(user_id=user_id, song_id=song_id).first()
    if not user_song:
        user_song = UserSong(user_id=user_id, song_id=song_id, liked=liked)
        db.session.add(user_song)
    else:
        user_song.liked = liked
    db.session.commit()
    return jsonify({"msg": f"Song {'liked' if liked else 'disliked'} successfully"}), 200

@user.route('/selected-songs', methods=['GET'])
@jwt_required()
def get_selected_songs():
    user_id = get_jwt_identity()
    user_songs = UserSong.query.filter_by(user_id=user_id).all()
    songs = [{"id": s.song.id, "title": s.song.title, "artist": s.song.artist, "liked": s.liked} for s in user_songs]
    return jsonify(songs), 200

@user.route('/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    user_id = get_jwt_identity()
    recommendations = Recommendation.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "song_id": r.song_id,
        "title": r.song.title,
        "artist": r.song.artist,
        "reason": r.reason
    } for r in recommendations]), 200

@user.route('/submit-questionnaire', methods=['POST'])
@jwt_required()
def submit_questionnaire():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    data = request.get_json()
    mood = data.get('mood')
    energy = data.get('energy')
    genre = data.get('genre')
    
    mood_scores = {'happy': 3, 'reflective': 1, 'intense': 2}
    energy_scores = {'high': 3, 'medium': 2, 'low': 1}
    genre_scores = {'pop': 3, 'rock': 2, 'jazz': 1}
    
    total_score = (
        mood_scores.get(mood, 1) +
        energy_scores.get(energy, 1) +
        genre_scores.get(genre, 1)
    )
    
    song = Song.query.order_by(
        func.abs(Song.recommendation_score - total_score)
    ).first()
    
    if song:
        existing_rec = Recommendation.query.filter_by(user_id=user_id, song_id=song.id).first()
        if not existing_rec:
            reason = f"Recommended based on your questionnaire (score: {total_score})"
            rec = Recommendation(user_id=user_id, song_id=song.id, reason=reason)
            db.session.add(rec)
            db.session.commit()
        return jsonify({
            "song_id": song.id,
            "title": song.title,
            "artist": song.artist,
            "reason": f"Recommended based on your questionnaire (score: {total_score})"
        }), 200
    return jsonify({"msg": "No matching song found"}), 404

@user.route('/genre-preferences', methods=['POST'])
@jwt_required()
def set_genre_preference():
    user_id = get_jwt_identity()
    data = request.get_json()
    genre_id = data.get('genre_id')
    weight = data.get('weight', 1)
    preference = UserGenrePreference.query.filter_by(user_id=user_id, genre_id=genre_id).first()
    if preference:
        preference.weight = weight
    else:
        preference = UserGenrePreference(user_id=user_id, genre_id=genre_id, weight=weight)
        db.session.add(preference)
    db.session.commit()
    return jsonify({"msg": "Genre preference updated"}), 200

@user.route('/add-to-playlist', methods=['POST'])
@jwt_required()
def add_to_playlist():
    user_id = get_jwt_identity()
    data = request.get_json()
    playlist_id = data.get('playlist_id')
    song_id = data.get('song_id')
    action = data.get('action', 'add')
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=user_id).first()
    song = Song.query.get(song_id)
    if not playlist or not song:
        return jsonify({"msg": "Playlist or song not found"}), 404
    if action == 'add':
        if song in playlist.songs:
            return jsonify({"msg": "Song already in playlist"}), 400
        playlist.songs.append(song)
        msg = "Song added to playlist"
    else:
        if song not in playlist.songs:
            return jsonify({"msg": "Song not in playlist"}), 400
        playlist.songs.remove(song)
        msg = "Song removed from playlist"
    db.session.commit()
    return jsonify({"msg": msg}), 200