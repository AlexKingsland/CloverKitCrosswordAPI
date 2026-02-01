"""
Generate crossword puzzle JSON files for Cloudflare R2 storage.

This script generates daily crossword puzzles for three difficulty levels:
- Easy: Shopping-themed puzzles
- Medium: Cars-themed puzzles  
- Hard: Music-themed puzzles

Usage:
    python scripts/generate_crosswords.py --start-date 2026-02-01 --days 30
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path


# Puzzle templates (hardcoded for testing)
PUZZLE_TEMPLATES = {
    'easy': {
        'title': 'Shopping Crossword',
        'topic': 'shopping',
        'difficulty': 'easy',
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
        }
    },
    'medium': {
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
        }
    },
    'hard': {
        'title': 'Music Crossword',
        'topic': 'music',
        'difficulty': 'hard',
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
        }
    }
}


def generate_puzzle_json(difficulty: str, date_str: str) -> dict:
    """Generate puzzle JSON for a specific difficulty and date."""
    template = PUZZLE_TEMPLATES[difficulty]
    
    return {
        'schema_version': 1,
        'difficulty': difficulty,
        'date': date_str,
        'title': template['title'],
        'topic': template['topic'],
        'acrossClues': template['across_clues'],
        'downClues': template['down_clues'],
        'answers': template['grid_data'],
        'cluePositions': template['clue_positions']
    }


def main():
    parser = argparse.ArgumentParser(description='Generate crossword puzzle JSON files for R2 storage')
    parser.add_argument('--start-date', required=True, help='Start date in YYYY-MM-DD format')
    parser.add_argument('--days', type=int, required=True, help='Number of days to generate')
    parser.add_argument('--output-dir', default='out', help='Output directory (default: out)')
    
    args = parser.parse_args()
    
    # Parse start date
    try:
        start_date = datetime.strptime(args.start_date, '%Y-%m-%d').date()
    except ValueError:
        print(f"❌ Invalid date format: {args.start_date}. Use YYYY-MM-DD")
        return 1
    
    # Create output directories
    base_path = Path(args.output_dir) / 'v1' / 'generic'
    for difficulty in ['easy', 'medium', 'hard']:
        (base_path / difficulty).mkdir(parents=True, exist_ok=True)
    
    print(f"🎯 Generating {args.days} days of puzzles starting from {start_date}")
    print(f"📁 Output directory: {base_path}")
    print()
    
    generated_count = 0
    
    # Generate puzzles for each day
    for day_offset in range(args.days):
        current_date = start_date + timedelta(days=day_offset)
        date_str = current_date.strftime('%Y-%m-%d')
        
        # Generate puzzle for each difficulty
        for difficulty in ['easy', 'medium', 'hard']:
            puzzle_data = generate_puzzle_json(difficulty, date_str)
            
            # Write to file
            output_file = base_path / difficulty / f'{date_str}.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(puzzle_data, f, indent=2, ensure_ascii=False)
            
            generated_count += 1
            
        print(f"✓ Generated puzzles for {date_str}")
    
    print()
    print(f"✅ Successfully generated {generated_count} puzzle files ({args.days} days × 3 difficulties)")
    print(f"📂 Files saved to: {base_path}")
    print()
    print("Next steps:")
    print("1. Review the generated JSON files")
    print("2. Run: python scripts/upload_to_r2.py")
    
    return 0


if __name__ == '__main__':
    exit(main())
