from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Junction table for many-to-many relationship between playlists and songs
playlist_songs = db.Table(
    'playlist_songs',
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlists.id'), primary_key=True),
    db.Column('song_id', db.Integer, db.ForeignKey('songs.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    playlists = db.relationship('Playlist', backref='user', lazy=True)
    selected_songs = db.relationship('UserSong', backref='user', lazy=True)
    recommendations = db.relationship('Recommendation', backref='user', lazy=True)
    genre_preferences = db.relationship('UserGenrePreference', backref='user', lazy=True)

class Genre(db.Model):
    __tablename__ = 'genres'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    songs = db.relationship('Song', backref='genre', lazy=True)

class Playlist(db.Model):
    __tablename__ = 'playlists'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    songs = db.relationship('Song', secondary=playlist_songs, backref='playlists', lazy=True)

class Song(db.Model):
    __tablename__ = 'songs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'))
    release_date = db.Column(db.Date)
    popularity_score = db.Column(db.Integer)  # Constraint handled in DB

class UserSong(db.Model):
    __tablename__ = 'user_songs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    song = db.relationship('Song', backref='user_songs')

class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'))
    reason = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    song = db.relationship('Song', backref='recommendations')

class SongOfTheDay(db.Model):
    __tablename__ = 'song_of_the_day'
    date = db.Column(db.Date, primary_key=True)
    song_id = db.Column(db.Integer, db.ForeignKey('songs.id'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    song = db.relationship('Song', backref='song_of_the_day')

class UserGenrePreference(db.Model):
    __tablename__ = 'user_genre_preferences'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    genre_id = db.Column(db.Integer, db.ForeignKey('genres.id'), primary_key=True)
    weight = db.Column(db.Integer, default=1)
    genre = db.relationship('Genre', backref='user_preferences')