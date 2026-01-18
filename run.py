import os
from app import create_app, db
from app.models import Puzzle

# Get environment from ENV variable or default to development
env = os.getenv('FLASK_ENV', 'development')
app = create_app(env)


@app.shell_context_processor
def make_shell_context():
    """Make database and models available in Flask shell."""
    return {'db': db, 'Puzzle': Puzzle}


if __name__ == '__main__':
    port = app.config.get('PORT', 5000)
    host = app.config.get('HOST', '0.0.0.0')
    debug = app.config.get('DEBUG', True)
    
    app.run(host=host, port=port, debug=debug)
