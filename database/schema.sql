-- Create the songs table
CREATE TABLE songs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    artist VARCHAR(255) NOT NULL,
    genre VARCHAR(100) NOT NULL,
    image_path VARCHAR(255) NOT NULL,
    release_date DATE,
    duration INTEGER, -- duration in seconds
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the playlists table
CREATE TABLE playlists (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the playlist_songs table
CREATE TABLE playlist_songs (
    playlist_id INTEGER REFERENCES playlists(id),
    song_id INTEGER REFERENCES songs(id),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (playlist_id, song_id)
);

-- Create the listening_history table
CREATE TABLE listening_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    song_id INTEGER REFERENCES songs(id),
    listened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better search performance
CREATE INDEX idx_songs_title ON songs(title);
CREATE INDEX idx_songs_artist ON songs(artist);
CREATE INDEX idx_songs_genre ON songs(genre);

-- Create a function for full text search across songs
CREATE FUNCTION search_songs(search_query TEXT)
RETURNS TABLE (
    id INTEGER,
    title VARCHAR(255),
    artist VARCHAR(255),
    genre VARCHAR(100),
    image_path VARCHAR(255)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.id,
        s.title,
        s.artist,
        s.genre,
        s.image_path
    FROM songs s
    WHERE 
        s.title ILIKE '%' || search_query || '%'
        OR s.artist ILIKE '%' || search_query || '%'
        OR s.genre ILIKE '%' || search_query || '%'
    ORDER BY 
        CASE 
            WHEN s.title ILIKE search_query || '%' THEN 1
            WHEN s.artist ILIKE search_query || '%' THEN 2
            ELSE 3
        END,
        s.title ASC
    LIMIT 50;
END;
$$ LANGUAGE plpgsql;

-- Create functions for user management
CREATE OR REPLACE FUNCTION create_new_user(
    p_username VARCHAR(50),
    p_email VARCHAR(255),
    p_password VARCHAR(255)
)
RETURNS INTEGER AS $$
DECLARE
    new_user_id INTEGER;
BEGIN
    IF p_username IS NULL OR p_email IS NULL OR p_password IS NULL THEN
        RETURN NULL;
    END IF;

    INSERT INTO users (username, email, password)
    VALUES (p_username, p_email, p_password)
    RETURNING id INTO new_user_id;
    
    RETURN new_user_id;
EXCEPTION
    WHEN unique_violation THEN
        RAISE NOTICE 'Username or email already exists';
        RETURN NULL;
    WHEN OTHERS THEN
        RAISE NOTICE 'Error creating user: %', SQLERRM;
        RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION verify_user_login(
    p_username VARCHAR(50),
    p_password VARCHAR(255)
)
RETURNS TABLE (
    user_id INTEGER,
    username VARCHAR(50),
    user_email VARCHAR(255)
) AS $$
BEGIN
    IF p_username IS NULL OR p_password IS NULL THEN
        RETURN;
    END IF;

    RETURN QUERY
    SELECT 
        u.id AS user_id,
        u.username,
        u.email AS user_email
    FROM users u
    WHERE u.username = p_username 
    AND u.password = p_password
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION check_user_exists(
    p_username VARCHAR(50),
    p_email VARCHAR(255)
)
RETURNS TABLE (
    exists_username VARCHAR(50),
    exists_email VARCHAR(255)
) AS $$
BEGIN
    IF p_username IS NULL OR p_email IS NULL THEN
        RETURN;
    END IF;

    RETURN QUERY
    SELECT 
        u.username,
        u.email
    FROM users u
    WHERE u.username = p_username 
    OR u.email = p_email
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;


-- Create function to add song to listening history
CREATE OR REPLACE FUNCTION add_to_history(
    p_user_id INTEGER,
    p_song_id INTEGER
)
RETURNS BOOLEAN AS $$
BEGIN
    INSERT INTO listening_history (user_id, song_id)
    VALUES (p_user_id, p_song_id);
    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- Create function to get user's listening history
CREATE OR REPLACE FUNCTION get_user_history(
    p_user_id INTEGER
)
RETURNS TABLE (
    song_id INTEGER,
    title VARCHAR(255),
    artist VARCHAR(255),
    genre VARCHAR(100),
    listened_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.id AS song_id,
        s.title,
        s.artist,
        s.genre,
        h.listened_at
    FROM listening_history h
    JOIN songs s ON h.song_id = s.id
    WHERE h.user_id = p_user_id
    ORDER BY h.listened_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Create function to get user's playlists
CREATE OR REPLACE FUNCTION get_user_playlists(
    p_user_id INTEGER
)
RETURNS TABLE (
    playlist_id INTEGER,
    playlist_name VARCHAR(255),
    song_count BIGINT,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id AS playlist_id,
        p.name AS playlist_name,
        COUNT(ps.song_id) AS song_count,
        p.created_at
    FROM playlists p
    LEFT JOIN playlist_songs ps ON p.id = ps.playlist_id
    WHERE p.user_id = p_user_id
    GROUP BY p.id, p.name, p.created_at
    ORDER BY p.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Create function to get songs in a playlist
CREATE OR REPLACE FUNCTION get_playlist_songs(
    p_playlist_id INTEGER
)
RETURNS TABLE (
    song_id INTEGER,
    title VARCHAR(255),
    artist VARCHAR(255),
    genre VARCHAR(100),
    added_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.id AS song_id,
        s.title,
        s.artist,
        s.genre,
        ps.added_at
    FROM playlist_songs ps
    JOIN songs s ON ps.song_id = s.id
    WHERE ps.playlist_id = p_playlist_id
    ORDER BY ps.added_at DESC;
END;
$$ LANGUAGE plpgsql; 