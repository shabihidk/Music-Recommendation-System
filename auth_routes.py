from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from yourapp import db  # Import the db object from your main app

# Create a blueprint for authentication-related routes
auth = Blueprint('auth', __name__)

# Route for user registration
@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({"msg": "Missing required fields"}), 400

    # Check if user already exists
    existing_user = User.query.filter_by(email=data.get('email')).first()
    if existing_user:
        return jsonify({"msg": "User already exists"}), 400

    # Create new user
    hashed_password = generate_password_hash(data.get('password'), method='sha256')
    new_user = User(name=data.get('name'), email=data.get('email'), password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "User registered successfully"}), 201

# Route for user login
@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data.get('email') or not data.get('password'):
        return jsonify({"msg": "Missing required fields"}), 400

    # Check if user exists
    user = User.query.filter_by(email=data.get('email')).first()
    if not user or not check_password_hash(user.password, data.get('password')):
        return jsonify({"msg": "Invalid credentials"}), 401

    # Create JWT token
    access_token = create_access_token(identity=user.id)
    return jsonify({"access_token": access_token}), 200

# Route for getting the current user's info (protected route)
@auth.route('/current', methods=['GET'])
@jwt_required()
def current_user():
    user_id = get_jwt_identity()  # Get user ID from the JWT token
    user = User.query.get(user_id)

    if user:
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
        return jsonify(user_data), 200
    return jsonify({"msg": "User not found"}), 404
