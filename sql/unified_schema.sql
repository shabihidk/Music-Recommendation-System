-- Drop tables in reverse order to avoid foreign key conflicts
DROP TABLE IF EXISTS user_genre_preferences CASCADE;
DROP TABLE IF EXISTS song_of_the_day CASCADE;
DROP TABLE IF EXISTS recommendations CASCADE;
DROP TABLE IF EXISTS user_songs CASCADE;
DROP TABLE IF EXISTS songs CASCADE;
DROP TABLE IF EXISTS playlists CASCADE;
DROP TABLE IF EXISTS genres CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create genres table
CREATE TABLE IF NOT EXISTS genres (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL
);

-- Create playlists table with unique constraint on (name, user_id)
CREATE TABLE IF NOT EXISTS playlists (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    user_id INTEGER REFERENCES users(id),
    CONSTRAINT unique_playlist_name_user UNIQUE (name, user_id)
);

-- Create songs table with unique constraint on (title, artist)
CREATE TABLE IF NOT EXISTS songs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    artist VARCHAR(100) NOT NULL,
    genre_id INTEGER REFERENCES genres(id),
    playlist_id INTEGER REFERENCES playlists(id),
    release_date DATE,
    popularity_score INTEGER CHECK (popularity_score BETWEEN 0 AND 100),
    CONSTRAINT unique_song_title_artist UNIQUE (title, artist)
);

-- Create user_songs table with unique constraint on (user_id, song_id)
CREATE TABLE IF NOT EXISTS user_songs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    song_id INTEGER REFERENCES songs(id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_user_song UNIQUE (user_id, song_id)
);

-- Create recommendations table with unique constraint on (user_id, song_id)
CREATE TABLE IF NOT EXISTS recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    song_id INTEGER REFERENCES songs(id),
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_recommendation UNIQUE (user_id, song_id)
);

-- Create song_of_the_day table
CREATE TABLE IF NOT EXISTS song_of_the_day (
    date DATE PRIMARY KEY,
    song_id INTEGER REFERENCES songs(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user_genre_preferences table
CREATE TABLE IF NOT EXISTS user_genre_preferences (
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    genre_id INTEGER REFERENCES genres(id),
    weight INTEGER DEFAULT 1,
    PRIMARY KEY (user_id, genre_id)
);

-- Insert unique genres
INSERT INTO genres (name)
VALUES
    ('Pop'),
    ('Rock'),
    ('Hip-Hop'),
    ('Jazz'),
    ('Classical'),
    ('EDM'),
    ('Indie'),
    ('R&B')
ON CONFLICT (name) DO NOTHING;

-- Insert sample users
INSERT INTO users (username, email, password_hash)
VALUES
    ('testuser', 'test@example.com', 'hashed_password_example'),
    ('musicfan', 'fan@example.com', 'hashed_password_example')
ON CONFLICT (username) DO NOTHING;

-- Insert sample playlists
INSERT INTO playlists (name, description, user_id)
VALUES
    ('My Favorites', 'My go-to songs', (SELECT id FROM users WHERE username = 'testuser')),
    ('Chill Vibes', 'Relaxing tunes', (SELECT id FROM users WHERE username = 'musicfan'))
ON CONFLICT ON CONSTRAINT unique_playlist_name_user DO NOTHING;

-- Insert songs
INSERT INTO songs (title, artist, genre_id, release_date, popularity_score)
VALUES
    ('Blinding Lights', 'The Weeknd', (SELECT id FROM genres WHERE name = 'Pop'), '2020-03-20', 95),
    ('Bohemian Rhapsody', 'Queen', (SELECT id FROM genres WHERE name = 'Rock'), '1975-10-31', 98),
    ('Lose Yourself', 'Eminem', (SELECT id FROM genres WHERE name = 'Hip-Hop'), '2002-10-28', 97),
    ('Shape of You', 'Ed Sheeran', (SELECT id FROM genres WHERE name = 'Pop'), NULL, NULL),
    ('Take Five', 'Dave Brubeck', (SELECT id FROM genres WHERE name = 'Jazz'), NULL, NULL),
    ('Moonlight Sonata', 'Beethoven', (SELECT id FROM genres WHERE name = 'Classical'), NULL, NULL)
ON CONFLICT ON CONSTRAINT unique_song_title_artist DO NOTHING;

-- Insert sample user_songs
INSERT INTO user_songs (user_id, song_id)
VALUES
    ((SELECT id FROM users WHERE username = 'testuser'), (SELECT id FROM songs WHERE title = 'Blinding Lights')),
    ((SELECT id FROM users WHERE username = 'musicfan'), (SELECT id FROM songs WHERE title = 'Bohemian Rhapsody'))
ON CONFLICT ON CONSTRAINT unique_user_song DO NOTHING;

-- Insert sample recommendations
INSERT INTO recommendations (user_id, song_id, reason)
VALUES
    ((SELECT id FROM users WHERE username = 'testuser'), (SELECT id FROM songs WHERE title = 'Shape of You'), 'Based on your preference for Pop'),
    ((SELECT id FROM users WHERE username = 'musicfan'), (SELECT id FROM songs WHERE title = 'Lose Yourself'), 'Matches your Hip-Hop interest')
ON CONFLICT ON CONSTRAINT unique_recommendation DO NOTHING;

-- Insert sample song_of_the_day
INSERT INTO song_of_the_day (date, song_id)
VALUES
    (CURRENT_DATE, (SELECT id FROM songs WHERE title = 'Blinding Lights'))
ON CONFLICT (date) DO NOTHING;

-- Insert sample user_genre_preferences
INSERT INTO user_genre_preferences (user_id, genre_id, weight)
VALUES
    ((SELECT id FROM users WHERE username = 'testuser'), (SELECT id FROM genres WHERE name = 'Pop'), 2),
    ((SELECT id FROM users WHERE username = 'musicfan'), (SELECT id FROM genres WHERE name = 'Rock'), 1)
ON CONFLICT ON CONSTRAINT user_genre_preferences_pkey DO NOTHING;