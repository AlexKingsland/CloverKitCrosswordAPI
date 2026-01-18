"""
Seed script to populate the database with initial crossword puzzles.
Run this script after creating the database and running migrations.

Usage: python scripts/seed_puzzles.py
"""

import sys
import os
from datetime import date, timedelta

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models import Puzzle


def seed_shopping_puzzle():
    """Seed the shopping-themed crossword puzzle."""
    
    # Check if shopping puzzle already exists for today
    existing_today = Puzzle.query.filter_by(
        topic='shopping',
        publish_date=date.today()
    ).first()
    
    if existing_today:
        print(f"⏭️  Skipped: Shopping puzzle for {date.today()} already exists")
    else:
        # This is the puzzle from the frontend JavaScript
        puzzle_data_today = {
        'title': 'Shopping Crossword',
        'topic': 'shopping',
        'difficulty': 'medium',
        'grid_size': 10,
        'grid_data': [
            ['S', 'H', 'O', 'P', 'I', 'F', 'Y', None, 'C', 'A', 'R', 'T'],
            ['H', None, 'R', None, 'T', None, None, None, 'A', None, 'D', None],
            ['O', None, 'D', None, 'E', None, 'O', 'R', 'D', 'E', 'R', 'S'],
            ['P', 'R', 'O', 'D', 'U', 'C', 'T', None, 'A', None, 'E', None],
            [None, None, None, None, None, None, None, None, 'D', None, 'T', None],
            ['S', 'A', 'L', 'E', 'S', None, 'P', 'R', 'I', 'C', 'Y', None],
            ['A', None, None, None, 'L', None, 'T', None, 'C', None, None, None],
            ['L', None, None, None, 'L', None, 'O', None, 'K', None, None, None],
            ['E', None, None, None, 'S', None, 'R', None, 'O', None, None, None],
            [None, None, 'C', 'H', 'E', 'C', 'K', 'O', 'U', 'T', 'S', None]
        ],
        'across_clues': {
            '1': 'E-commerce platform',
            '8': 'Shopping basket',
            '10': 'Purchase request',
            '11': 'Item for sale',
            '13': 'Discounted items',
            '15': 'Expensive',
            '18': 'Final purchase step'
        },
        'down_clues': {
            '1': 'Online store',
            '2': 'Buyer',
            '3': 'Transaction',
            '4': 'Platform',
            '5': 'Goods',
            '6': 'Design',
            '7': 'Vendor',
            '9': 'Add to',
            '12': 'Price tag',
            '14': 'Store section'
        },
        'clue_positions': {
            '1': {'row': 0, 'col': 0, 'direction': 'across', 'length': 7},
            '2': {'row': 1, 'col': 0, 'direction': 'down', 'length': 4},
            '3': {'row': 2, 'col': 2, 'direction': 'down', 'length': 3},
            '4': {'row': 3, 'col': 0, 'direction': 'down', 'length': 4},
            '5': {'row': 0, 'col': 4, 'direction': 'down', 'length': 9},
            '6': {'row': 4, 'col': 2, 'direction': 'down', 'length': 3},
            '7': {'row': 5, 'col': 0, 'direction': 'down', 'length': 4},
            '8': {'row': 0, 'col': 8, 'direction': 'across', 'length': 4},
            '9': {'row': 1, 'col': 8, 'direction': 'down', 'length': 9},
            '10': {'row': 2, 'col': 6, 'direction': 'across', 'length': 6},
            '11': {'row': 3, 'col': 0, 'direction': 'across', 'length': 7},
            '12': {'row': 3, 'col': 10, 'direction': 'down', 'length': 5},
            '13': {'row': 5, 'col': 0, 'direction': 'across', 'length': 5},
            '14': {'row': 6, 'col': 6, 'direction': 'down', 'length': 3},
            '15': {'row': 5, 'col': 6, 'direction': 'across', 'length': 5},
            '18': {'row': 9, 'col': 2, 'direction': 'across', 'length': 8}
        },
            'publish_date': date.today(),
            'is_active': True
        }
        
        puzzle = Puzzle(**puzzle_data_today)
        db.session.add(puzzle)
        print(f"✓ Created puzzle: {puzzle.title} for {puzzle.publish_date}")
    
    # Check if shopping puzzle already exists for tomorrow
    existing_tomorrow = Puzzle.query.filter_by(
        topic='shopping',
        publish_date=date.today() + timedelta(days=1)
    ).first()
    
    if existing_tomorrow:
        print(f"⏭️  Skipped: Shopping puzzle for {date.today() + timedelta(days=1)} already exists")
    else:
        # Create the same puzzle for tomorrow (for testing)
        puzzle_data_tomorrow = {
            'title': 'Shopping Crossword',
            'topic': 'shopping',
            'difficulty': 'medium',
            'grid_size': 10,
            'grid_data': puzzle_data_today['grid_data'] if not existing_today else None,
            'across_clues': puzzle_data_today['across_clues'] if not existing_today else {},
            'down_clues': puzzle_data_today['down_clues'] if not existing_today else {},
            'clue_positions': puzzle_data_today['clue_positions'] if not existing_today else {},
            'publish_date': date.today() + timedelta(days=1),
            'is_active': True
        }
        
        # If today's puzzle was skipped, we need to define the data
        if existing_today:
            puzzle_data_tomorrow.update({
                'grid_data': existing_today.grid_data,
                'across_clues': existing_today.across_clues,
                'down_clues': existing_today.down_clues,
                'clue_positions': existing_today.clue_positions
            })
        
        tomorrow_puzzle = Puzzle(**puzzle_data_tomorrow)
        db.session.add(tomorrow_puzzle)
        print(f"✓ Created puzzle: {tomorrow_puzzle.title} for {tomorrow_puzzle.publish_date}")


def seed_cars_puzzle():
    """Seed the cars-themed crossword puzzle."""
    
    # Check if cars puzzle already exists for today
    existing_today = Puzzle.query.filter_by(
        topic='cars',
        publish_date=date.today()
    ).first()
    
    if existing_today:
        print(f"⏭️  Skipped: Cars puzzle for {date.today()} already exists")
    else:
        puzzle_data = {
        'title': 'Cars Crossword',
        'topic': 'cars',
        'difficulty': 'medium',
        'grid_size': 10,
        'grid_data': [
            ['E', 'N', 'G', 'I', 'N', 'E', None, 'S', 'E', 'D', 'A', 'N'],
            ['R', None, 'A', None, None, None, None, 'P', None, None, 'I', None],
            ['A', None, 'R', None, 'B', 'R', 'A', 'K', 'E', None, 'R', None],
            ['C', 'L', 'U', 'T', 'C', 'H', None, 'E', None, None, 'E', None],
            ['E', None, 'G', None, None, None, None, 'E', None, None, None, None],
            [None, None, 'E', None, 'W', 'H', 'E', 'E', 'L', 'S', None, None],
            ['M', 'O', 'T', 'O', 'R', None, None, 'D', None, None, 'T', 'I', 'R', 'E'],
            ['I', None, None, None, None, None, None, None, None, None, 'R', None],
            ['R', None, 'S', 'H', 'I', 'F', 'T', None, 'D', 'R', 'I', 'V', 'E'],
            ['R', None, None, None, None, None, None, None, None, None, 'P', None],
        ],
        'across_clues': {
            '1': 'Power source',
            '7': 'Four-door car',
            '9': 'Slow down device',
            '10': 'Manual transmission pedal',
            '13': 'Round rolling parts',
            '15': 'Engine synonym',
            '18': 'Change gears',
            '19': 'Operate a vehicle',
            '21': 'Rubber wheel cover'
        },
        'down_clues': {
            '1': 'Competitive driving',
            '2': 'Auto',
            '3': 'Car storage',
            '4': 'Parking lot',
            '5': 'Need air',
            '8': 'Fast',
            '11': 'Dripping fluid',
            '12': 'Long journey',
            '16': 'Overhead light',
            '17': 'Honk',
            '20': 'Journey'
        },
        'clue_positions': {
            '1': {'row': 0, 'col': 0, 'direction': 'across', 'length': 6},
            '2': {'row': 0, 'col': 0, 'direction': 'down', 'length': 5},
            '3': {'row': 0, 'col': 2, 'direction': 'down', 'length': 5},
            '4': {'row': 3, 'col': 0, 'direction': 'down', 'length': 4},
            '5': {'row': 0, 'col': 10, 'direction': 'down', 'length': 5},
            '7': {'row': 0, 'col': 7, 'direction': 'across', 'length': 5},
            '8': {'row': 0, 'col': 7, 'direction': 'down', 'length': 6},
            '9': {'row': 2, 'col': 4, 'direction': 'across', 'length': 5},
            '10': {'row': 3, 'col': 1, 'direction': 'across', 'length': 6},
            '11': {'row': 2, 'col': 10, 'direction': 'down', 'length': 3},
            '12': {'row': 6, 'col': 10, 'direction': 'down', 'length': 4},
            '13': {'row': 5, 'col': 4, 'direction': 'across', 'length': 6},
            '15': {'row': 6, 'col': 0, 'direction': 'across', 'length': 5},
            '16': {'row': 6, 'col': 0, 'direction': 'down', 'length': 4},
            '18': {'row': 8, 'col': 2, 'direction': 'across', 'length': 5},
            '19': {'row': 8, 'col': 8, 'direction': 'across', 'length': 5},
            '21': {'row': 6, 'col': 11, 'direction': 'across', 'length': 4}
        },
            'publish_date': date.today(),
            'is_active': True
        }
        
        puzzle = Puzzle(**puzzle_data)
        db.session.add(puzzle)
        print(f"✓ Created puzzle: {puzzle.title} for {puzzle.publish_date}")
    
    # Check if cars puzzle already exists for tomorrow
    existing_tomorrow = Puzzle.query.filter_by(
        topic='cars',
        publish_date=date.today() + timedelta(days=1)
    ).first()
    
    if existing_tomorrow:
        print(f"⏭️  Skipped: Cars puzzle for {date.today() + timedelta(days=1)} already exists")
    else:
        # Create the same puzzle for tomorrow (for testing)
        tomorrow_data = puzzle_data if not existing_today else {
            'title': existing_today.title,
            'topic': existing_today.topic,
            'difficulty': existing_today.difficulty,
            'grid_size': existing_today.grid_size,
            'grid_data': existing_today.grid_data,
            'across_clues': existing_today.across_clues,
            'down_clues': existing_today.down_clues,
            'clue_positions': existing_today.clue_positions,
        }
        
        tomorrow_puzzle = Puzzle(
            title=tomorrow_data['title'] if not existing_today else existing_today.title,
            topic=tomorrow_data['topic'] if not existing_today else existing_today.topic,
            difficulty=tomorrow_data['difficulty'] if not existing_today else existing_today.difficulty,
            grid_size=tomorrow_data['grid_size'] if not existing_today else existing_today.grid_size,
            grid_data=tomorrow_data['grid_data'] if not existing_today else existing_today.grid_data,
            across_clues=tomorrow_data['across_clues'] if not existing_today else existing_today.across_clues,
            down_clues=tomorrow_data['down_clues'] if not existing_today else existing_today.down_clues,
            clue_positions=tomorrow_data['clue_positions'] if not existing_today else existing_today.clue_positions,
            publish_date=date.today() + timedelta(days=1),
            is_active=True
        )
        db.session.add(tomorrow_puzzle)
        print(f"✓ Created puzzle: {tomorrow_puzzle.title} for {tomorrow_puzzle.publish_date}")


def seed_music_puzzle():
    """Seed the music-themed crossword puzzle."""
    
    # Check if music puzzle already exists for today
    existing_today = Puzzle.query.filter_by(
        topic='music',
        publish_date=date.today()
    ).first()
    
    if existing_today:
        print(f"⏭️  Skipped: Music puzzle for {date.today()} already exists")
    else:
        puzzle_data = {
        'title': 'Music Crossword',
        'topic': 'music',
        'difficulty': 'medium',
        'grid_size': 10,
        'grid_data': [
            ['G', 'U', 'I', 'T', 'A', 'R', None, 'P', 'I', 'A', 'N', 'O'],
            ['E', None, None, None, None, None, None, 'L', None, None, 'O', None],
            ['N', None, 'M', 'E', 'L', 'O', 'D', 'Y', None, None, 'T', None],
            ['R', None, None, None, None, None, None, 'A', None, None, 'E', None],
            ['E', None, 'D', 'R', 'U', 'M', 'S', None, None, None, 'S', None],
            [None, None, None, None, None, None, None, None, None, None, None, None],
            ['C', 'H', 'O', 'R', 'D', None, 'R', 'H', 'Y', 'T', 'H', 'M'],
            ['O', None, None, None, None, None, 'E', None, None, None, None, None],
            ['N', None, 'T', 'E', 'M', 'P', 'O', None, 'B', 'E', 'A', 'T', 'S'],
            ['G', None, None, None, None, None, 'R', None, None, None, None, None],
        ],
        'across_clues': {
            '1': 'Six-string instrument',
            '7': 'Keyboard instrument',
            '9': 'Tune',
            '11': 'Percussion instruments',
            '15': 'Three or more notes',
            '16': 'Musical pattern',
            '18': 'Speed of music',
            '19': 'Pulse of music'
        },
        'down_clues': {
            '1': 'Music style',
            '2': 'Performance',
            '3': 'Musical symbol',
            '4': 'Music book',
            '5': 'Vocal music',
            '6': 'Written music',
            '8': 'Singer group',
            '10': 'Sound quality',
            '12': 'Live show',
            '13': 'Musical collection',
            '14': 'Recorded music',
            '17': 'Tape recorder'
        },
        'clue_positions': {
            '1': {'row': 0, 'col': 0, 'direction': 'across', 'length': 6},
            '2': {'row': 0, 'col': 0, 'direction': 'down', 'length': 5},
            '3': {'row': 2, 'col': 2, 'direction': 'down', 'length': 3},
            '4': {'row': 4, 'col': 2, 'direction': 'down', 'length': 3},
            '5': {'row': 0, 'col': 10, 'direction': 'down', 'length': 5},
            '6': {'row': 6, 'col': 6, 'direction': 'down', 'length': 4},
            '7': {'row': 0, 'col': 7, 'direction': 'across', 'length': 5},
            '8': {'row': 0, 'col': 7, 'direction': 'down', 'length': 4},
            '9': {'row': 2, 'col': 2, 'direction': 'across', 'length': 6},
            '10': {'row': 6, 'col': 0, 'direction': 'down', 'length': 4},
            '11': {'row': 4, 'col': 2, 'direction': 'across', 'length': 5},
            '12': {'row': 6, 'col': 10, 'direction': 'down', 'length': 2},
            '15': {'row': 6, 'col': 0, 'direction': 'across', 'length': 5},
            '16': {'row': 6, 'col': 6, 'direction': 'across', 'length': 6},
            '18': {'row': 8, 'col': 2, 'direction': 'across', 'length': 5},
            '19': {'row': 8, 'col': 8, 'direction': 'across', 'length': 5}
        },
            'publish_date': date.today(),
            'is_active': True
        }
        
        puzzle = Puzzle(**puzzle_data)
        db.session.add(puzzle)
        print(f"✓ Created puzzle: {puzzle.title} for {puzzle.publish_date}")
    
    # Check if music puzzle already exists for tomorrow
    existing_tomorrow = Puzzle.query.filter_by(
        topic='music',
        publish_date=date.today() + timedelta(days=1)
    ).first()
    
    if existing_tomorrow:
        print(f"⏭️  Skipped: Music puzzle for {date.today() + timedelta(days=1)} already exists")
    else:
        # Create the same puzzle for tomorrow (for testing)
        tomorrow_data = puzzle_data if not existing_today else {
            'title': existing_today.title,
            'topic': existing_today.topic,
            'difficulty': existing_today.difficulty,
            'grid_size': existing_today.grid_size,
            'grid_data': existing_today.grid_data,
            'across_clues': existing_today.across_clues,
            'down_clues': existing_today.down_clues,
            'clue_positions': existing_today.clue_positions,
        }
        
        tomorrow_puzzle = Puzzle(
            title=tomorrow_data['title'] if not existing_today else existing_today.title,
            topic=tomorrow_data['topic'] if not existing_today else existing_today.topic,
            difficulty=tomorrow_data['difficulty'] if not existing_today else existing_today.difficulty,
            grid_size=tomorrow_data['grid_size'] if not existing_today else existing_today.grid_size,
            grid_data=tomorrow_data['grid_data'] if not existing_today else existing_today.grid_data,
            across_clues=tomorrow_data['across_clues'] if not existing_today else existing_today.across_clues,
            down_clues=tomorrow_data['down_clues'] if not existing_today else existing_today.down_clues,
            clue_positions=tomorrow_data['clue_positions'] if not existing_today else existing_today.clue_positions,
            publish_date=date.today() + timedelta(days=1),
            is_active=True
        )
        db.session.add(tomorrow_puzzle)
        print(f"✓ Created puzzle: {tomorrow_puzzle.title} for {tomorrow_puzzle.publish_date}")


def main():
    """Main seeding function."""
    app = create_app('development')
    
    with app.app_context():
        print("Starting database seeding...")
        
        # Check if puzzles already exist
        existing_count = Puzzle.query.count()
        if existing_count > 0:
            print(f"\n⚠️  Database already contains {existing_count} puzzle(s).")
            response = input("Do you want to continue and add more puzzles? (y/n): ")
            if response.lower() != 'y':
                print("Seeding cancelled.")
                return
        
        try:
            seed_shopping_puzzle()
            seed_cars_puzzle()
            seed_music_puzzle()
            db.session.commit()
            print("\n✅ Database seeding completed successfully!")
            print(f"Total puzzles in database: {Puzzle.query.count()}")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error seeding database: {str(e)}")
            raise


if __name__ == '__main__':
    main()
