from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Playlist, Song
from yourapp import db  # Import the db object from your main app

# Create a blueprint for user-related routes
user = Blueprint('user', __name__)

# Route for getting the user's playlists
@user.route('/playlists', methods=['GET'])
@jwt_required()
def get_playlists():
    user_id = get_jwt_identity()  # Get user ID from the JWT token
    user = User.query.get(user_id)

    if user:
        playlists = [{
            "id": playlist.id,
            "name": playlist.name,
            "description": playlist.description
        } for playlist in user.playlists]

        return jsonify(playlists), 200
    return jsonify({"msg": "User not found"}), 404

# Route for viewing a specific playlist's details
@user.route('/playlist/<int:playlist_id>', methods=['GET'])
@jwt_required()
def get_playlist(playlist_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user:
        playlist = Playlist.query.filter_by(id=playlist_id, user_id=user_id).first()
        if playlist:
            songs = [{"title": song.title, "artist": song.artist} for song in playlist.songs]
            return jsonify({
                "id": playlist.id,
                "name": playlist.name,
                "description": playlist.description,
                "songs": songs
            }), 200
        return jsonify({"msg": "Playlist not found"}), 404
    return jsonify({"msg": "User not found"}), 404

# Route for getting a specific song's details
@user.route('/song/<int:song_id>', methods=['GET'])
@jwt_required()
def get_song(song_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if user:
        song = Song.query.get(song_id)
        if song:
            return jsonify({
                "id": song.id,
                "title": song.title,
                "artist": song.artist
            }), 200
        return jsonify({"msg": "Song not found"}), 404
    return jsonify({"msg": "User not found"}), 404
