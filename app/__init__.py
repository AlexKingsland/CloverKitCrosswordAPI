from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import config
import re

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name='default'):
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Handle CORS with wildcard support
    allowed_origins = app.config.get('ALLOWED_ORIGINS', [])
    cors_origins = []
    
    for origin in allowed_origins:
        if origin == '*.myshopify.com':
            # Convert wildcard to regex pattern
            cors_origins.append(r'https://.*\.myshopify\.com$')
        else:
            cors_origins.append(origin)
    
    CORS(app, origins=cors_origins, supports_credentials=True)
    
    # Register blueprints
    from app.api import puzzles_bp, health_bp
    app.register_blueprint(puzzles_bp, url_prefix='/api/v1')
    app.register_blueprint(health_bp, url_prefix='/api/v1')
    
    return app
