"""Authentication and user management functions."""

from functools import wraps
from flask import session, redirect, url_for
import bcrypt
from app.database import execute_query, execute_single_query
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_logged_in():
    """Simple check if user is logged in"""
    return 'user_id' in session and session['user_id'] is not None

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def protected_route(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return protected_route

def verify_user(username, password):
    """Verify user using database function"""
    if not username or not password:
        logger.debug("Empty username or password")
        return None
        
    try:
        logger.debug(f"Attempting to verify user: {username}")
        user = execute_single_query(
            "SELECT * FROM verify_user_login(%s, %s)",
            (username, password)
        )
        logger.debug(f"Database response: {user}")
        
        if user:
            logger.debug(f"User verified successfully: {user.get('user_id')}")
        else:
            logger.debug("No user found with provided credentials")
            
        return user
    except Exception as e:
        logger.error(f"Error verifying user: {str(e)}")
        return None

def check_existing_user(username, email):
    """Check existing user using database function"""
    if not username or not email:
        return None
        
    return execute_single_query(
        "SELECT * FROM check_user_exists(%s, %s)",
        (username, email)
    )

def create_user(username, email, password):
    """Create user using database function"""
    if not username or not email or not password:
        return None
        
    result = execute_single_query(
        "SELECT create_new_user(%s, %s, %s) as user_id",
        (username, email, password)
    )
    return result['user_id'] if result and result['user_id'] is not None else None 