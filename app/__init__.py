from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name='default'):
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, origins=app.config['ALLOWED_ORIGINS'])
    
    # Register blueprints
    from app.api import puzzles_bp, health_bp
    app.register_blueprint(puzzles_bp, url_prefix='/api/v1')
    app.register_blueprint(health_bp, url_prefix='/api/v1')
    
    return app
