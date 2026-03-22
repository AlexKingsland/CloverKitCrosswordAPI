# Crossword Puzzle Pipeline

End-to-end pipeline for generating crossword puzzles and deploying them to Cloudflare R2.

## Overview

```
promptList.txt
     ↓
[Step 1] Playwright scrapes PuzzleMe → raw HTML per difficulty
     ↓
[Step 2] parse_crossword.py → structured CSV per puzzle
     ↓
[Step 3] generate_crosswords.py → runtime JSON per puzzle
     ↓
[Step 4] upload_to_r2.py → Cloudflare R2 CDN
     ↓
Shopify extension fetches JSON from R2
```

**Example: 10 prompts × 3 difficulties = 30 puzzles per run**

## Directory Structure

```
scripts/
├── run_pipeline.js               # Orchestrator — Steps 1 & 2
├── parse_crossword.py            # HTML → CSV parser
├── generate_crosswords.py        # CSV → runtime JSON
├── upload_to_r2.py               # JSON → Cloudflare R2
├── seed_puzzles.py               # Legacy DB seeder (deprecated)
├── promptList.txt                # Your puzzle prompts
├── package.json                  # Node.js deps (Playwright)
├── playwright.config.ts          # Playwright configuration
├── playwright/                   # Playwright test specs
│   ├── easycrossword.spec.ts     # 11×11 grid
│   ├── mediumcrossword.spec.ts   # 15×15 grid
│   └── hardcrossword.spec.ts     # 20×20 grid
├── rawhtmls/                     # Generated HTMLs (gitignored)
│   ├── easy/
│   ├── medium/
│   └── hard/
└── parsedCSVs/                   # Parsed CSVs (gitignored)
    ├── easy/
    ├── medium/
    └── hard/
```

## Setup

### Prerequisites

- **Node.js** ≥ 20
- **Python 3** with pip
- Cloudflare R2 credentials (for upload step)

### Install Dependencies

```bash
cd scripts

# Node.js / Playwright
npm install
npx playwright install chromium

# Python
pip install beautifulsoup4 boto3
```

### Configure R2 (for upload step)

```bash
export R2_ACCESS_KEY_ID=your_access_key
export R2_SECRET_ACCESS_KEY=your_secret_key
export R2_ENDPOINT=https://your-account-id.r2.cloudflarestorage.com
export R2_BUCKET=crossword  # optional, defaults to "crossword"
```

## Usage

### Full Pipeline (Steps 1–4)

```bash
cd scripts

# 1. Edit promptList.txt with your puzzle prompts
#    Format: Title, Topic (one per line, # for comments)

# 2. Run Playwright scraping + CSV parsing
node run_pipeline.js

# 3. Generate runtime JSON from CSVs
python3 generate_crosswords.py --csv-dir parsedCSVs --recursive --start-date 2026-03-01

# 4. Upload to R2
python3 upload_to_r2.py
```

### Individual Steps

#### Step 1 & 2: Scrape + Parse (run_pipeline.js)

Reads `promptList.txt`, runs Playwright at 3 difficulty levels for each prompt, then parses the HTML output into CSVs.

```bash
node run_pipeline.js
```

**Input:** `promptList.txt` — one puzzle per line:
```
Space Exploration, Space
Ocean Life, Ocean
Ancient Egypt, Egypt
```

**Output:** CSVs in `parsedCSVs/{easy,medium,hard}/`

#### Step 3: Generate JSON (generate_crosswords.py)

Converts CSVs into the runtime JSON format consumed by the Shopify extension.

```bash
# Single CSV file
python3 generate_crosswords.py --csv-path /path/to/puzzle.csv

# Directory of CSVs (sequential date assignment)
python3 generate_crosswords.py --csv-dir parsedCSVs --recursive --start-date 2026-03-01

# With custom output directory
python3 generate_crosswords.py --csv-dir parsedCSVs --recursive --output-dir out
```

**Arguments:**
| Argument | Description |
|---|---|
| `--csv-path` | Path to a single puzzle CSV file |
| `--csv-dir` | Directory of CSV files (one puzzle per file) |
| `--start-date` | Start date (`YYYY-MM-DD`) for sequential date indexing (default: today) |
| `--recursive` | Recursively search subdirectories for CSVs |
| `--output-dir` | Output directory (default: `out`) |
| `--default-difficulty` | Fallback difficulty: `easy`, `medium`, `hard` (default: `medium`) |

**Output:** JSON files in `out/v1/generic/{difficulty}/{date}.json`

#### Step 4: Upload to R2 (upload_to_r2.py)

Uploads generated JSON files to Cloudflare R2 with immutable cache headers.

```bash
# Dry run (preview uploads)
python3 upload_to_r2.py --dry-run

# Upload
python3 upload_to_r2.py
```

**Arguments:**
| Argument | Description |
|---|---|
| `--input-dir` | Input directory (default: `out`) |
| `--bucket` | R2 bucket name (default: from `R2_BUCKET` env or `crossword`) |
| `--dry-run` | Preview without uploading |

## R2 Storage Structure

```
crossword/
└── v1/
    └── generic/
        ├── easy/
        │   ├── 2026-03-01.json
        │   └── ...
        ├── medium/
        │   ├── 2026-03-01.json
        │   └── ...
        └── hard/
            ├── 2026-03-01.json
            └── ...
```

## JSON Format

Each puzzle file contains:

```json
{
  "schema_version": 1,
  "difficulty": "medium",
  "date": "2026-03-01",
  "title": "Space Exploration",
  "topic": "space",
  "acrossClues": {
    "1": "Earth's satellite",
    "5": "Red planet"
  },
  "downClues": {
    "1": "Milky Way component",
    "2": "Gravity source"
  },
  "answers": [
    ["M", "O", "O", "N", null, "M", "A", "R", "S"],
    ...
  ],
  "cluePositions": {
    "1": {"row": 0, "col": 0, "direction": "across", "length": 4},
    "5": {"row": 0, "col": 5, "direction": "across", "length": 4}
  }
}
```

## CSV Format

Each parsed CSV contains one row per clue with these columns:

`Series, Puzzle ID, Puzzle Type, Title, Publish Time, Author, Tags, Start Message, Notes, Starting X, Starting Y, Clue Number, Across Clue, Answer, Clue, Question Text, Incorrect Options, Correct Option, Explanation, Puzzle Data`

## Automation (Optional)

Create a shell script or GitHub Action for batch runs:

```bash
#!/bin/bash
# generate_and_upload.sh

cd "$(dirname "$0")"

# Scrape and parse
node run_pipeline.js

# Generate JSON
python3 generate_crosswords.py \
  --csv-dir parsedCSVs \
  --recursive \
  --start-date "$(date +%Y-%m-%d)" \
  --output-dir out

# Upload to R2
python3 upload_to_r2.py
```

## Notes

- Only Chromium is used for Playwright — Firefox and WebKit are skipped
- Each puzzle takes ~30–60 seconds due to Playwright load time
- 30 puzzles will take roughly 15–30 minutes
- Lines starting with `#` in `promptList.txt` are treated as comments
- Old files in `rawhtmls/` can be left in place — filenames are timestamped and unique
- Puzzles uploaded to R2 are cached with `max-age=31536000` (1 year, immutable)
- UTC dates are used to ensure consistency across timezones
- Duplicate clue numbers are disambiguated in JSON keys (e.g. `14A`, `14D`)

## Troubleshooting

### Playwright Not Finding Chromium

```bash
npx playwright install chromium
```

### Python Parser Fails

Make sure beautifulsoup4 is installed:
```bash
pip install beautifulsoup4
```

### Files Not Uploading to R2

1. Check environment variables:
   ```bash
   echo $R2_ACCESS_KEY_ID
   echo $R2_SECRET_ACCESS_KEY
   echo $R2_ENDPOINT
   ```
2. Dry run to verify: `python3 upload_to_r2.py --dry-run`
3. Check IAM permissions for R2 token

### Puzzles Not Loading in Shopify

1. Verify files exist in R2 dashboard
2. Test URL: `https://YOUR-R2-HOST/crossword/v1/generic/medium/YYYY-MM-DD.json`
3. Check browser console for CORS errors
4. Ensure R2 bucket has public access enabled
