"""Main application module."""

from flask import Flask
from flask_cors import CORS
from app.routes import init_routes
import os

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # Load configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-please-change')  # Change this in production!
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes
    
    # Enable CORS
    CORS(app)
    
    # Initialize routes
    init_routes(app)
    
    return app 