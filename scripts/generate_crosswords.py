"""Generate crossword runtime JSON files from CSV puzzle definitions.

This script converts row-based crossword definitions
into the runtime JSON contract consumed by CloverKitCrossword frontend:

- acrossClues
- downClues
- answers (grid matrix)
- cluePositions

Usage:
    python scripts/generate_crosswords.py --csv-path /absolute/path/to/puzzle.csv
    python scripts/generate_crosswords.py --csv-dir /absolute/path/to/csv_folder --start-date 2026-03-01
"""

import argparse
import csv
import json
import re
import unicodedata
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple


VALID_DIFFICULTIES = {"easy", "medium", "hard"}


def extract_difficulty_token(value: str) -> Optional[str]:
    """Extract difficulty token from plain text or lightweight HTML content."""
    normalized = normalize_text(value).lower()
    if not normalized:
        return None

    # Strip simple HTML tags (e.g., <div>Medium</div>) before tokenizing.
    normalized = re.sub(r"<[^>]+>", " ", normalized)
    tokenized = re.split(r"[\s,;|:_\-\/]+", normalized)
    for token in tokenized:
        if token in VALID_DIFFICULTIES:
            return token

    return None


def normalize_text(value: str) -> str:
    return (value or "").strip()


def parse_bool(value: str) -> bool:
    normalized = normalize_text(value).lower()
    if normalized in {"true", "1", "yes", "y", "across"}:
        return True
    if normalized in {"false", "0", "no", "n", "down"}:
        return False
    raise ValueError(f"Invalid boolean value for Across Clue: {value!r}")


def parse_int(value: str, field_name: str) -> int:
    try:
        return int(normalize_text(value))
    except Exception as exc:
        raise ValueError(f"Invalid integer for {field_name}: {value!r}") from exc


def normalize_answer_text(value: str) -> str:
    """Normalize answer text to uppercase ASCII letters by stripping diacritics."""
    raw = normalize_text(value)
    if not raw:
        return ""

    decomposed = unicodedata.normalize("NFKD", raw)
    stripped = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return stripped.upper()


def parse_publish_date(value: str) -> str:
    """Return YYYY-MM-DD from mixed publish time formats."""
    raw = normalize_text(value)
    if not raw:
        raise ValueError("Publish Time is required")

    # Try explicit formats first.
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M UTC",
        "%Y-%m-%d %H:%M:%S UTC",
        "%Y-%m-%d %H:%M %Z",
        "%Y-%m-%d %H:%M:%S %Z",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(raw, fmt).date().isoformat()
        except ValueError:
            pass

    # Fallback: pull just the date portion at the beginning.
    date_match = re.match(r"^(\d{4}-\d{2}-\d{2})", raw)
    if date_match:
        return date_match.group(1)

    raise ValueError(f"Unable to parse Publish Time: {value!r}")


def infer_difficulty(row: Dict[str, str], default_difficulty: str) -> str:
    # Priority: Difficulty column -> Tags -> Start Message -> default
    explicit = extract_difficulty_token(row.get("Difficulty", ""))
    if explicit:
        return explicit

    tags = extract_difficulty_token(row.get("Tags", ""))
    if tags:
        return tags

    start_message = extract_difficulty_token(row.get("Start Message", ""))
    if start_message:
        return start_message

    return default_difficulty


def infer_topic(row: Dict[str, str]) -> str:
    tags = normalize_text(row.get("Tags", ""))
    if tags:
        parts = [p.strip().lower() for p in re.split(r"[,;|]", tags) if p.strip()]
        # Prefer first non-difficulty tag.
        for part in parts:
            if part not in VALID_DIFFICULTIES:
                return part
    return "generic"


def load_csv_rows(csv_path: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required_columns = {
            "Puzzle ID",
            "Title",
            "Publish Time",
            "Starting X",
            "Starting Y",
            "Clue Number",
            "Across Clue",
            "Answer",
        }
        missing = required_columns - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV missing required columns: {', '.join(sorted(missing))}")

        for i, row in enumerate(reader, start=2):
            if not any((v or "").strip() for v in row.values()):
                continue
            row["_row_number"] = str(i)
            rows.append(row)

    if not rows:
        raise ValueError("CSV is empty (no puzzle rows found)")
    return rows


def build_puzzle_payload(
    puzzle_rows: List[Dict[str, str]],
    default_difficulty: str,
    forced_date: Optional[str] = None,
    validate_source_dates: bool = True,
) -> dict:
    first = puzzle_rows[0]

    puzzle_id = normalize_text(first.get("Puzzle ID", ""))
    title = normalize_text(first.get("Title", "")) or f"Puzzle {puzzle_id}"
    date_str = forced_date or parse_publish_date(first.get("Publish Time", ""))
    difficulty = infer_difficulty(first, default_difficulty)
    topic = infer_topic(first)

    across_clues: Dict[str, str] = {}
    down_clues: Dict[str, str] = {}
    clue_positions: Dict[str, Dict[str, int]] = {}

    # Build sparse grid in dict form first.
    occupied_cells: Dict[Tuple[int, int], str] = {}
    max_x = 0
    max_y = 0

    clue_number_counts: Dict[str, int] = defaultdict(int)
    for row in puzzle_rows:
        clue_number = normalize_text(row.get("Clue Number", ""))
        if clue_number:
            clue_number_counts[clue_number] += 1

    used_clue_keys = set()

    def resolve_clue_key(raw_clue_number: str, direction: str) -> str:
        # Keep plain numeric key when unique in source data; otherwise disambiguate.
        if clue_number_counts[raw_clue_number] == 1 and raw_clue_number not in used_clue_keys:
            return raw_clue_number

        base = f"{raw_clue_number}{'A' if direction == 'across' else 'D'}"
        key = base
        idx = 2
        while key in used_clue_keys:
            key = f"{base}_{idx}"
            idx += 1
        return key

    for row in puzzle_rows:
        row_num = row["_row_number"]
        clue_number = normalize_text(row.get("Clue Number", ""))
        if not clue_number:
            raise ValueError(f"Row {row_num}: Clue Number is required")

        start_x = parse_int(row.get("Starting X", ""), "Starting X")
        start_y = parse_int(row.get("Starting Y", ""), "Starting Y")
        is_across = parse_bool(row.get("Across Clue", ""))
        direction = "across" if is_across else "down"
        clue_key = resolve_clue_key(clue_number, direction)
        used_clue_keys.add(clue_key)

        if validate_source_dates:
            row_date_str = parse_publish_date(row.get("Publish Time", ""))
            if row_date_str != date_str:
                raise ValueError(
                    f"Row {row_num}: Publish Time date {row_date_str} does not match puzzle date {date_str}"
                )

        answer = normalize_answer_text(row.get("Answer", ""))
        if not answer:
            raise ValueError(f"Row {row_num}: Answer is required")
        if not re.fullmatch(r"[A-Z0-9]+", answer):
            raise ValueError(f"Row {row_num}: Answer must contain only letters A-Z or digits 0-9: {answer!r}")

        clue_text = normalize_text(row.get("Clue", "")) or normalize_text(row.get("Question Text", ""))
        if not clue_text:
            clue_text = "(Clue to be added)"

        if is_across:
            across_clues[clue_key] = clue_text
        else:
            down_clues[clue_key] = clue_text

        clue_positions[clue_key] = {
            "row": start_y,
            "col": start_x,
            "direction": direction,
            "length": len(answer),
        }

        for idx, letter in enumerate(answer):
            x = start_x + idx if is_across else start_x
            y = start_y if is_across else start_y + idx

            key = (y, x)
            if key in occupied_cells and occupied_cells[key] != letter:
                raise ValueError(
                    f"Row {row_num}: Letter conflict at cell (x={x}, y={y}). "
                    f"Existing={occupied_cells[key]!r}, New={letter!r}"
                )
            occupied_cells[key] = letter
            max_x = max(max_x, x)
            max_y = max(max_y, y)

    grid_size = max(max_x + 1, max_y + 1)
    answers: List[List[str]] = [[None for _ in range(grid_size)] for _ in range(grid_size)]
    for (row, col), letter in occupied_cells.items():
        answers[row][col] = letter

    return {
        "puzzle_id": puzzle_id,
        "difficulty": difficulty,
        "date": date_str,
        "payload": {
            "schema_version": 1,
            "difficulty": difficulty,
            "date": date_str,
            "title": title,
            "topic": topic,
            "acrossClues": across_clues,
            "downClues": down_clues,
            "answers": answers,
            "cluePositions": clue_positions,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Generate crossword puzzle JSON files from CSV definitions")
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--csv-path",
        help="Absolute or relative path to a single puzzle CSV file",
    )
    source_group.add_argument(
        "--csv-dir",
        help="Directory containing puzzle CSV files (each file = one puzzle)",
    )
    parser.add_argument(
        "--start-date",
        help="Start date (YYYY-MM-DD) used for date indexing in --csv-dir mode (default: today)",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Recursively search subdirectories for CSV files when using --csv-dir",
    )
    parser.add_argument("--output-dir", default="out", help="Output directory (default: out)")
    parser.add_argument(
        "--default-difficulty",
        default="medium",
        choices=sorted(VALID_DIFFICULTIES),
        help="Fallback difficulty when CSV does not specify one (default: medium)",
    )
    args = parser.parse_args()

    base_path = Path(args.output_dir) / "v1" / "generic"
    base_path.mkdir(parents=True, exist_ok=True)

    generated_count = 0
    emitted_keys = set()

    def write_compiled_payload(puzzle_id: str, compiled: dict, source_name: str) -> int:
        difficulty = compiled["difficulty"]
        date_str = compiled["date"]
        payload = compiled["payload"]

        output_key = (difficulty, date_str)
        if output_key in emitted_keys:
            print(
                f"❌ Output collision: multiple puzzles resolve to "
                f"{difficulty}/{date_str}.json. Ensure unique difficulty/date per puzzle."
            )
            return 1
        emitted_keys.add(output_key)

        output_dir = base_path / difficulty
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{date_str}.json"
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        print(f"✓ {source_name}: puzzle {puzzle_id} -> {difficulty}/{date_str}.json")
        return 0

    if args.csv_path:
        csv_path = Path(args.csv_path)
        if not csv_path.exists():
            print(f"❌ CSV file not found: {csv_path}")
            return 1

        try:
            rows = load_csv_rows(csv_path)
        except Exception as exc:
            print(f"❌ Failed reading CSV: {exc}")
            return 1

        grouped_rows: Dict[str, List[Dict[str, str]]] = defaultdict(list)
        for row in rows:
            puzzle_id = normalize_text(row.get("Puzzle ID", ""))
            if not puzzle_id:
                print(f"❌ Row {row['_row_number']}: Puzzle ID is required")
                return 1
            grouped_rows[puzzle_id].append(row)

        print(f"🎯 Building runtime JSON from CSV: {csv_path}")
        print(f"🧩 Puzzle groups found: {len(grouped_rows)}")
        print(f"📁 Output directory: {base_path}")
        print()

        for puzzle_id, puzzle_rows in grouped_rows.items():
            try:
                compiled = build_puzzle_payload(puzzle_rows, args.default_difficulty)
            except Exception as exc:
                print(f"❌ Puzzle ID {puzzle_id}: {exc}")
                return 1

            result = write_compiled_payload(puzzle_id, compiled, csv_path.name)
            if result != 0:
                return result
            generated_count += 1
    else:
        csv_dir = Path(args.csv_dir)
        if not csv_dir.exists() or not csv_dir.is_dir():
            print(f"❌ CSV directory not found: {csv_dir}")
            return 1

        start_date_str = args.start_date or datetime.today().date().isoformat()

        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            print(f"❌ Invalid start date format: {start_date_str}. Use YYYY-MM-DD")
            return 1

        csv_files = sorted(
            [
                p
                for p in (csv_dir.rglob("*.csv") if args.recursive else csv_dir.glob("*.csv"))
                if p.is_file()
            ],
            key=lambda p: str(p.relative_to(csv_dir)).lower(),
        )
        if not csv_files:
            print(f"❌ No CSV files found in directory: {csv_dir}")
            return 1

        print(f"🎯 Building runtime JSON from CSV directory: {csv_dir}")
        print(f"🗂️  Recursive mode: {'on' if args.recursive else 'off'}")
        print(f"🧩 CSV files found: {len(csv_files)}")
        print(f"📅 Start date index: {start_date.isoformat()}")
        print(f"📁 Output directory: {base_path}")
        print()

        folder_date_offsets: Dict[str, int] = defaultdict(int)

        for csv_file in csv_files:
            try:
                rows = load_csv_rows(csv_file)
            except Exception as exc:
                print(f"❌ Failed reading {csv_file.name}: {exc}")
                return 1

            grouped_rows: Dict[str, List[Dict[str, str]]] = defaultdict(list)
            for row in rows:
                puzzle_id = normalize_text(row.get("Puzzle ID", ""))
                if not puzzle_id:
                    # Auto-generate puzzle ID from title or filename in csv-dir mode
                    title = normalize_text(row.get("Title", ""))
                    if title:
                        puzzle_id = re.sub(r"[^\w\s-]", "", title.lower().strip())
                        puzzle_id = re.sub(r"[\s_]+", "-", puzzle_id).strip("-") or csv_file.stem
                    else:
                        puzzle_id = csv_file.stem
                    # Back-fill all rows with the generated ID
                    for r in rows:
                        if not normalize_text(r.get("Puzzle ID", "")):
                            r["Puzzle ID"] = puzzle_id
                grouped_rows[puzzle_id].append(row)

            if len(grouped_rows) != 1:
                print(
                    f"❌ {csv_file.name}: expected exactly 1 puzzle id per file in --csv-dir mode, "
                    f"found {len(grouped_rows)}"
                )
                return 1

            folder_key = str(csv_file.parent.relative_to(csv_dir))
            folder_offset = folder_date_offsets[folder_key]
            assigned_date = (start_date + timedelta(days=folder_offset)).isoformat()
            folder_date_offsets[folder_key] = folder_offset + 1
            puzzle_id, puzzle_rows = next(iter(grouped_rows.items()))

            # Infer difficulty from parent folder name (e.g., easy/, medium/, hard/)
            parent_folder_name = csv_file.parent.name.lower()
            folder_difficulty = (
                parent_folder_name
                if parent_folder_name in VALID_DIFFICULTIES
                else args.default_difficulty
            )

            try:
                compiled = build_puzzle_payload(
                    puzzle_rows,
                    folder_difficulty,
                    forced_date=assigned_date,
                    validate_source_dates=False,
                )
            except Exception as exc:
                print(f"❌ {csv_file.name} (Puzzle ID {puzzle_id}): {exc}")
                return 1

            result = write_compiled_payload(puzzle_id, compiled, csv_file.name)
            if result != 0:
                return result
            generated_count += 1

    print()
    print(f"✅ Successfully generated {generated_count} puzzle file(s)")
    print(f"📂 Files saved to: {base_path}")
    print()
    print("Next steps:")
    print("1. Review generated JSON files")
    print("2. Run: python scripts/upload_to_r2.py")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
