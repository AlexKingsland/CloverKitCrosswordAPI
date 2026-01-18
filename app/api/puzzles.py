from datetime import datetime, date
from flask import request, jsonify
from app.api import puzzles_bp
from app.models import Puzzle
from app import db
from app.utils.decorators import require_api_key
from sqlalchemy.exc import IntegrityError


@puzzles_bp.route('/puzzles/daily', methods=['GET'])
def get_daily_puzzle():
    """Get today's puzzle for a specific topic."""
    topic = request.args.get('topic', 'shopping')
    today = date.today()
    
    puzzle = Puzzle.query.filter_by(
        topic=topic,
        publish_date=today,
        is_active=True
    ).first()
    
    if not puzzle:
        # If no puzzle for today, get the most recent active puzzle for this topic
        puzzle = Puzzle.query.filter_by(
            topic=topic,
            is_active=True
        ).filter(
            Puzzle.publish_date <= today
        ).order_by(
            Puzzle.publish_date.desc()
        ).first()
    
    if not puzzle:
        return jsonify({'error': f'No puzzle found for topic: {topic}'}), 404
    
    return jsonify(puzzle.to_dict()), 200


@puzzles_bp.route('/puzzles/date', methods=['GET'])
def get_puzzle_by_date():
    """Get puzzle for a specific date and topic."""
    topic = request.args.get('topic', 'shopping')
    date_str = request.args.get('date')
    
    if not date_str:
        return jsonify({'error': 'Date parameter is required (format: YYYY-MM-DD)'}), 400
    
    try:
        puzzle_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    puzzle = Puzzle.query.filter_by(
        topic=topic,
        publish_date=puzzle_date,
        is_active=True
    ).first()
    
    if not puzzle:
        return jsonify({'error': f'No puzzle found for topic: {topic} on date: {date_str}'}), 404
    
    return jsonify(puzzle.to_dict()), 200


@puzzles_bp.route('/puzzles', methods=['GET'])
@require_api_key
def list_puzzles():
    """List all puzzles with optional filters (admin only)."""
    topic = request.args.get('topic')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    query = Puzzle.query
    
    if topic:
        query = query.filter_by(topic=topic)
    
    # Order by publish date descending
    query = query.order_by(Puzzle.publish_date.desc())
    
    # Paginate results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'puzzles': [puzzle.to_dict() for puzzle in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'total_pages': pagination.pages
    }), 200


@puzzles_bp.route('/puzzles', methods=['POST'])
@require_api_key
def create_puzzle():
    """Create a new puzzle (admin only)."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate required fields
    required_fields = ['title', 'topic', 'grid_size', 'grid_data', 'across_clues', 
                       'down_clues', 'clue_positions', 'publish_date']
    
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({'error': f'Missing required fields: {", ".join(missing_fields)}'}), 400
    
    try:
        # Parse publish_date
        publish_date = datetime.strptime(data['publish_date'], '%Y-%m-%d').date()
        
        # Create new puzzle
        puzzle = Puzzle(
            title=data['title'],
            topic=data['topic'],
            difficulty=data.get('difficulty', 'medium'),
            grid_size=data['grid_size'],
            grid_data=data['grid_data'],
            across_clues=data['across_clues'],
            down_clues=data['down_clues'],
            clue_positions=data['clue_positions'],
            publish_date=publish_date,
            is_active=data.get('is_active', True)
        )
        
        db.session.add(puzzle)
        db.session.commit()
        
        return jsonify(puzzle.to_dict()), 201
        
    except ValueError as e:
        return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': f'A puzzle already exists for topic "{data["topic"]}" on {data["publish_date"]}'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create puzzle: {str(e)}'}), 500


@puzzles_bp.route('/puzzles/<uuid:puzzle_id>', methods=['GET'])
@require_api_key
def get_puzzle(puzzle_id):
    """Get a specific puzzle by ID (admin only)."""
    puzzle = Puzzle.query.get(puzzle_id)
    
    if not puzzle:
        return jsonify({'error': 'Puzzle not found'}), 404
    
    return jsonify(puzzle.to_dict()), 200


@puzzles_bp.route('/puzzles/<uuid:puzzle_id>', methods=['PUT'])
@require_api_key
def update_puzzle(puzzle_id):
    """Update a puzzle (admin only)."""
    puzzle = Puzzle.query.get(puzzle_id)
    
    if not puzzle:
        return jsonify({'error': 'Puzzle not found'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    try:
        # Update fields if provided
        if 'title' in data:
            puzzle.title = data['title']
        if 'topic' in data:
            puzzle.topic = data['topic']
        if 'difficulty' in data:
            puzzle.difficulty = data['difficulty']
        if 'grid_size' in data:
            puzzle.grid_size = data['grid_size']
        if 'grid_data' in data:
            puzzle.grid_data = data['grid_data']
        if 'across_clues' in data:
            puzzle.across_clues = data['across_clues']
        if 'down_clues' in data:
            puzzle.down_clues = data['down_clues']
        if 'clue_positions' in data:
            puzzle.clue_positions = data['clue_positions']
        if 'publish_date' in data:
            puzzle.publish_date = datetime.strptime(data['publish_date'], '%Y-%m-%d').date()
        if 'is_active' in data:
            puzzle.is_active = data['is_active']
        
        puzzle.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(puzzle.to_dict()), 200
        
    except ValueError as e:
        return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'A puzzle already exists for this topic on this date'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update puzzle: {str(e)}'}), 500


@puzzles_bp.route('/puzzles/<uuid:puzzle_id>', methods=['DELETE'])
@require_api_key
def delete_puzzle(puzzle_id):
    """Delete a puzzle (admin only)."""
    puzzle = Puzzle.query.get(puzzle_id)
    
    if not puzzle:
        return jsonify({'error': 'Puzzle not found'}), 404
    
    try:
        db.session.delete(puzzle)
        db.session.commit()
        
        return jsonify({'message': 'Puzzle deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete puzzle: {str(e)}'}), 500
