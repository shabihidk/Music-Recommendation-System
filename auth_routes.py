from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Song, UserSong
import random

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not all([data.get('name'), data.get('email'), data.get('password')]):
        return jsonify({"msg": "Missing required fields"}), 400

    existing_user = User.query.filter_by(email=data.get('email')).first()
    if existing_user:
        return jsonify({"msg": "User already exists"}), 400

    hashed_password = generate_password_hash(data.get('password'), method='sha256')
    new_user = User(name=data.get('name'), email=data.get('email'), password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    # Assign initial random songs
    songs = Song.query.all()
    if songs:
        random_songs = random.sample(songs, min(5, len(songs)))
        for song in random_songs:
            user_song = UserSong(user_id=new_user.id, song_id=song.id)
            db.session.add(user_song)
        db.session.commit()

    return jsonify({"msg": "User registered successfully"}), 201

@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not all([data.get('email'), data.get('password')]):
        return jsonify({"msg": "Missing required fields"}), 400

    user = User.query.filter_by(email=data.get('email')).first()
    if not user or not check_password_hash(user.password, data.get('password')):
        return jsonify({"msg": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({"access_token": access_token}), 200

@auth.route('/current', methods=['GET'])
@jwt_required()
def current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user:
        return jsonify({"id": user.id, "name": user.name, "email": user.email}), 200
    return jsonify({"msg": "User not found"}), 404