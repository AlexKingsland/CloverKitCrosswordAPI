from flask import Blueprint

# Create blueprints
puzzles_bp = Blueprint('puzzles', __name__)
health_bp = Blueprint('health', __name__)

# Import routes to register them
from app.api import puzzles, health
