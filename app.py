from flask import Flask, render_template
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required
from flask_sqlalchemy import SQLAlchemy
from config import JWT_SECRET_KEY
from auth_routes import auth  # import auth routes blueprint
from user_routes import user  # import user routes blueprint

# Initialize the Flask application
app = Flask(__name__)

# Configuring JWT and secret key
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/yourdbname'  # Update with actual database info
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

jwt = JWTManager(app)
db = SQLAlchemy(app)

# Register blueprints
app.register_blueprint(auth, url_prefix="/auth")  # Auth routes for login/registration
app.register_blueprint(user)  # User routes for songs

# Define models here
class Playlist(db.Model):
    __tablename__ = 'playlists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    songs = db.relationship('Song', backref='playlist', lazy=True)

class Song(db.Model):
    __tablename__ = 'songs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlists.id'), nullable=False)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    playlists = db.relationship('Playlist', backref='user', lazy=True)

# Helper Functions
def get_playlists_from_db():
    playlists = Playlist.query.all()  # Fetch all playlists from DB
    return [{'id': playlist.id, 'name': playlist.name} for playlist in playlists]

def get_playlist_by_id(playlist_id):
    playlist = Playlist.query.get(playlist_id)  # Fetch playlist by ID
    if playlist:
        songs = [{'title': song.title, 'artist': song.artist} for song in playlist.songs]
        return {'id': playlist.id, 'name': playlist.name, 'songs': songs}
    return None

def get_user_info(user_id):
    user = User.query.get(user_id)  # Fetch user info by user ID (could be session-based or token-based)
    if user:
        return {'id': user.id, 'name': user.name, 'email': user.email}
    return None

# Home route for the main page
@app.route('/')
def home():
    playlists = get_playlists_from_db()  # Fetch playlists from DB
    return render_template('index.html', playlists=playlists)

# Playlist route to display individual playlist details
@app.route('/playlist/<int:playlist_id>')
def playlist(playlist_id):
    playlist = get_playlist_by_id(playlist_id)  # Fetch playlist by ID
    if playlist:
        return render_template('playlist.html', playlist=playlist)
    return "Playlist not found", 404

# Profile route to display user's profile
@app.route('/profile')
@jwt_required()  # Ensure that the user is authenticated before accessing the profile
def profile():
    user_id = get_jwt_identity()  # Fetch the logged-in user's ID from the JWT token
    user_info = get_user_info(user_id)
    if user_info:
        return render_template('profile.html', user=user_info)
    return "User not found", 404

if __name__ == '__main__':
    app.run(debug=True)
