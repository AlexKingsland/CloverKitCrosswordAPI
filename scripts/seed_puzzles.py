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
    
    # This is the puzzle from the frontend JavaScript
    puzzle_data = {
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
    
    puzzle = Puzzle(**puzzle_data)
    db.session.add(puzzle)
    print(f"✓ Created puzzle: {puzzle.title} for {puzzle.publish_date}")
    
    # Create the same puzzle for tomorrow (for testing)
    tomorrow_puzzle = Puzzle(
        title=puzzle_data['title'],
        topic=puzzle_data['topic'],
        difficulty=puzzle_data['difficulty'],
        grid_size=puzzle_data['grid_size'],
        grid_data=puzzle_data['grid_data'],
        across_clues=puzzle_data['across_clues'],
        down_clues=puzzle_data['down_clues'],
        clue_positions=puzzle_data['clue_positions'],
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
            db.session.commit()
            print("\n✅ Database seeding completed successfully!")
            print(f"Total puzzles in database: {Puzzle.query.count()}")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error seeding database: {str(e)}")
            raise


if __name__ == '__main__':
    main()
