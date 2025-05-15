"""Route handlers for the application."""

from flask import (
    render_template, 
    request, 
    flash, 
    redirect, 
    url_for, 
    jsonify, 
    session,
    send_from_directory
)
from app.auth import verify_user, check_existing_user, create_user, login_required
from app.songs import search_songs, get_songs_paginated
from app.database import execute_query, execute_single_query
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# ----------------------------------------
# Authentication Routes
# ----------------------------------------

def init_auth_routes(app):
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        # Redirect if already logged in
        if 'user_id' in session and session['user_id'] is not None:
            return redirect(url_for('dashboard'))
            
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            
            logger.debug(f"Login attempt for username: {username}")
            
            if not username or not password:
                flash('Please enter both username and password', 'error')
                return render_template('login.html')
            
            user = verify_user(username, password)
            logger.debug(f"Verify user result: {user}")
            
            if user and user.get('user_id'):
                logger.debug(f"Login successful for user_id: {user['user_id']}")
                session['user_id'] = user['user_id']
                session['username'] = user['username']
                return redirect(url_for('dashboard'))
            
            logger.debug("Login failed - invalid credentials")
            flash('Invalid username or password', 'error')
        return render_template('login.html')

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        # Redirect if already logged in
        if 'user_id' in session and session['user_id'] is not None:
            return redirect(url_for('dashboard'))
            
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            
            if not all([username, email, password]):
                flash('All fields are required', 'error')
                return render_template('signup.html')
            
            # Check for existing user
            existing = check_existing_user(username, email)
            if existing:
                if existing['exists_username'] == username:
                    flash('Username already exists', 'error')
                else:
                    flash('Email already registered', 'error')
                return render_template('signup.html')
            
            # Create new user
            user_id = create_user(username, email, password)
            if user_id:
                flash('Account created! Please login.', 'success')
                return redirect(url_for('login'))
            
            flash('Error creating account. Please try again.', 'error')
        return render_template('signup.html')

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))

# ----------------------------------------
# Main Application Routes
# ----------------------------------------

def init_main_routes(app):
    @app.route('/')
    @login_required
    def dashboard():
        if not session.get('user_id'):
            return redirect(url_for('login'))
        return render_template('dashboard.html')

    @app.route('/search')
    @login_required
    def search_page():
        return render_template('searched.html')

    @app.route('/profile')
    @login_required
    def profile():
        return render_template('profile.html')

    @app.route('/playlists')
    @login_required
    def playlists():
        user_id = session.get('user_id')
        playlists = execute_query(
            "SELECT * FROM get_user_playlists(%s)",
            (user_id,)
        )
        return render_template('playlists.html', playlists=playlists)

    @app.route('/history')
    @login_required
    def history():
        user_id = session.get('user_id')
        history = execute_query(
            "SELECT * FROM get_user_history(%s)",
            (user_id,)
        )
        return render_template('history.html', history=history)

# ----------------------------------------
# API Routes
# ----------------------------------------

def init_api_routes(app):
    @app.route('/api/search')
    @login_required
    def search():
        """Search for songs based on query"""
        query = request.args.get('q', '').strip()
        results = search_songs(query)
        return jsonify(results)

    @app.route('/api/songs')
    @login_required
    def get_songs():
        """Get paginated list of songs with optional filtering"""
        page = int(request.args.get('page', 1))
        genre = request.args.get('genre', '').strip()
        sort = request.args.get('sort', 'title')
        
        results = get_songs_paginated(page, genre, sort)
        return jsonify(results)

    @app.route('/api/history/add', methods=['POST'])
    @login_required
    def add_to_history():
        user_id = session.get('user_id')
        song_id = request.json.get('song_id')
        
        if not song_id:
            return jsonify({'error': 'Song ID is required'}), 400
            
        success = execute_single_query(
            "SELECT add_to_history(%s, %s) as success",
            (user_id, song_id)
        )
        
        if success and success['success']:
            return jsonify({'message': 'Added to history'}), 200
        return jsonify({'error': 'Failed to add to history'}), 500

    @app.route('/images/<path:filename>')
    def serve_image(filename):
        """Serve image files"""
        return send_from_directory('images', filename)

def init_routes(app):
    """Initialize all routes"""
    init_auth_routes(app)
    init_main_routes(app)
    init_api_routes(app) 