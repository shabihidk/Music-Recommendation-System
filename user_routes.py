from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Playlist, Song, UserSong

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

@user.route('/playlist/<int:playlist_id>', methods=['GET'])
@jwt_required()
def get_playlist(playlist_id):
    user_id = get_jwt_identity()
    playlist = Playlist.query.filter_by(id=playlist_id, user_id=user_id).first()
    if playlist:
        songs = [{"id": s.id, "title": s.title, "artist": s.artist} for s in playlist.songs]
        return jsonify({"id": playlist.id, "name": playlist.name, "description": playlist.description, "songs": songs}), 200
    return jsonify({"msg": "Playlist not found"}), 404

@user.route('/song/<int:song_id>', methods=['GET'])
@jwt_required()
def get_song(song_id):
    song = Song.query.get(song_id)
    if song:
        return jsonify({"id": song.id, "title": song.title, "artist": song.artist}), 200
    return jsonify({"msg": "Song not found"}), 404

@user.route('/select-song', methods=['POST'])
@jwt_required()
def select_song():
    user_id = get_jwt_identity()
    data = request.get_json()
    song_id = data.get('song_id')
    song = Song.query.get(song_id)
    if not song:
        return jsonify({"msg": "Song not found"}), 404

    existing = UserSong.query.filter_by(user_id=user_id, song_id=song_id).first()
    if existing:
        return jsonify({"msg": "Song already selected"}), 400

    user_song = UserSong(user_id=user_id, song_id=song_id)
    db.session.add(user_song)
    db.session.commit()
    return jsonify({"msg": "Song selected successfully"}), 200

@user.route('/selected-songs', methods=['GET'])
@jwt_required()
def get_selected_songs():
    user_id = get_jwt_identity()
    user_songs = UserSong.query.filter_by(user_id=user_id).all()
    songs = [{"id": s.song.id, "title": s.song.title, "artist": s.song.artist} for s in user_songs]
    return jsonify(songs), 200