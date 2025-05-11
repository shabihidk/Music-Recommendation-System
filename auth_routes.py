from flask import Blueprint, jsonify, request, render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from models import db, User
from werkzeug.security import check_password_hash, generate_password_hash

auth = Blueprint('auth', __name__)

# Token blacklist for logout
blacklist = set()

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({"msg": "Missing required fields"}), 400

        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            return jsonify({"msg": "Username or email already exists"}), 400

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({"msg": "User registered successfully"}), 201
    return render_template('register.html')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            access_token = create_access_token(identity=user.id)
            return jsonify({"access_token": access_token}), 200
        return jsonify({"msg": "Invalid credentials"}), 401
    return render_template('login.html')

@auth.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    blacklist.add(jti)
    return jsonify({"msg": "Logged out successfully"}), 200

# Check if token is blacklisted
def is_token_blacklisted(jti):
    return jti in blacklist