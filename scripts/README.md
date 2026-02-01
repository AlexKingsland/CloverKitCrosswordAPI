# Crossword Puzzle Migration to Cloudflare R2

This directory contains scripts for migrating from Heroku API to Cloudflare R2 static file storage.

## Overview

The crossword puzzle system has been migrated from a dynamic API to static JSON files stored in Cloudflare R2:

- **Before:** Shopify → Heroku API → PostgreSQL → Daily puzzle
- **After:** Shopify → Cloudflare R2 (CDN) → Static JSON files

## R2 Storage Structure

```
crossword/
└── v1/
    └── generic/
        ├── easy/
        │   ├── 2026-02-01.json
        │   ├── 2026-02-02.json
        │   └── ...
        ├── medium/
        │   ├── 2026-02-01.json
        │   ├── 2026-02-02.json
        │   └── ...
        └── hard/
            ├── 2026-02-01.json
            ├── 2026-02-02.json
            └── ...
```

**Difficulty Mapping (for testing):**
- `easy` → Shopping puzzles
- `medium` → Cars puzzles
- `hard` → Music puzzles

## Scripts

### 1. generate_crosswords.py

Generates daily crossword puzzle JSON files for all three difficulty levels.

**Usage:**
```bash
python scripts/generate_crosswords.py --start-date 2026-02-01 --days 30
```

**Arguments:**
- `--start-date`: Start date in YYYY-MM-DD format (required)
- `--days`: Number of days to generate (required)
- `--output-dir`: Output directory (default: `out`)

**Output:**
Creates JSON files in `out/v1/generic/{difficulty}/{date}.json` format.

**Example:**
```bash
# Generate puzzles for February 2026
python scripts/generate_crosswords.py --start-date 2026-02-01 --days 28
```

### 2. upload_to_r2.py

Uploads generated puzzle files to Cloudflare R2 bucket.

**Prerequisites:**
1. Install boto3: `pip install boto3`
2. Set environment variables:
   ```bash
   export R2_ACCESS_KEY_ID=your_access_key
   export R2_SECRET_ACCESS_KEY=your_secret_key
   export R2_ENDPOINT=https://account-id.r2.cloudflarestorage.com
   export R2_BUCKET=crossword  # optional, defaults to "crossword"
   ```

**Usage:**
```bash
python scripts/upload_to_r2.py
```

**Arguments:**
- `--input-dir`: Input directory with generated files (default: `out`)
- `--bucket`: R2 bucket name (default: from `R2_BUCKET` env var or `crossword`)
- `--dry-run`: Show what would be uploaded without actually uploading

**Example:**
```bash
# Dry run to preview uploads
python scripts/upload_to_r2.py --dry-run

# Actually upload files
python scripts/upload_to_r2.py
```

## Complete Workflow

### Initial Setup

1. **Install dependencies:**
   ```bash
   cd CloverKitCrosswordAPI
   pip install boto3
   ```

2. **Configure R2 credentials:**
   Create a `.env` file or export environment variables:
   ```bash
   export R2_ACCESS_KEY_ID=your_key
   export R2_SECRET_ACCESS_KEY=your_secret
   export R2_ENDPOINT=https://516b34f68738d2ef0040e8efaec9ecfe.r2.cloudflarestorage.com
   export R2_BUCKET=crossword
   ```

3. **Configure R2 bucket:**
   - Bucket name: `crossword`
   - Public access: Enabled
   - CORS configuration:
     ```json
     [
       {
         "AllowedOrigins": ["*"],
         "AllowedMethods": ["GET"],
         "AllowedHeaders": ["*"],
         "MaxAgeSeconds": 3600
       }
     ]
     ```

### Monthly Puzzle Generation

Generate and upload puzzles for the upcoming month:

```bash
# Generate puzzles for March 2026
python scripts/generate_crosswords.py --start-date 2026-03-01 --days 31

# Review generated files
ls -lh out/v1/generic/*/2026-03-*.json

# Upload to R2
python scripts/upload_to_r2.py
```

### Automation (Optional)

Create a monthly cron job or GitHub Action:

```bash
#!/bin/bash
# monthly_puzzle_generation.sh

# Calculate next month's date range
START_DATE=$(date -d "next month" +%Y-%m-01)
DAYS=$(date -d "$START_DATE + 1 month - 1 day" +%d)

# Generate puzzles
python scripts/generate_crosswords.py --start-date $START_DATE --days $DAYS

# Upload to R2
python scripts/upload_to_r2.py
```

## JSON Format

Each puzzle file contains:

```json
{
  "schema_version": 1,
  "difficulty": "medium",
  "date": "2026-02-01",
  "title": "Cars Crossword",
  "topic": "cars",
  "acrossClues": {
    "1": "Power source",
    "7": "Four-door car"
  },
  "downClues": {
    "1": "Competitive driving",
    "2": "Auto"
  },
  "answers": [
    ["E", "N", "G", "I", "N", "E", null, "S", "E", "D", "A", "N"],
    ["R", null, "A", null, null, null, null, "P", null, null, "I", null]
  ],
  "cluePositions": {
    "1": {"row": 0, "col": 0, "direction": "across", "length": 6},
    "2": {"row": 0, "col": 0, "direction": "down", "length": 5}
  }
}
```

## Shopify Extension Changes

The Shopify extension now:

1. Fetches puzzles directly from R2 using UTC dates
2. Uses difficulty-based URLs instead of topic-based
3. Includes fallback to yesterday's puzzle if today's is missing
4. No longer depends on the Heroku API

**Example URL:**
```
https://516b34f68738d2ef0040e8efaec9ecfe.r2.cloudflarestorage.com/crossword/v1/generic/medium/2026-02-01.json
```

## Troubleshooting

### Files Not Uploading

1. Check environment variables are set:
   ```bash
   echo $R2_ACCESS_KEY_ID
   echo $R2_SECRET_ACCESS_KEY
   echo $R2_ENDPOINT
   ```

2. Verify bucket exists and is accessible:
   ```bash
   python scripts/upload_to_r2.py --dry-run
   ```

3. Check IAM permissions for R2 token

### Puzzles Not Loading in Shopify

1. Verify files exist in R2:
   - Check Cloudflare dashboard → R2 → crossword bucket
   - Confirm path: `v1/generic/{difficulty}/{date}.json`

2. Test direct URL in browser:
   ```
   https://YOUR-R2-HOST/crossword/v1/generic/medium/2026-02-01.json
   ```

3. Check browser console for CORS errors

4. Verify R2 bucket has public access enabled

### CORS Issues

Update bucket CORS configuration in Cloudflare dashboard:
- Allow origin: `*` or `*.myshopify.com`
- Allow methods: `GET`
- Allow headers: `*`

## Migration Checklist

- [x] Create `generate_crosswords.py` script
- [x] Create `upload_to_r2.py` script
- [x] Update `requirements.txt` with boto3
- [x] Update `crossword-puzzle.js` to fetch from R2
- [x] Update `crossword-puzzle.liquid` to use difficulty setting
- [ ] Generate initial puzzle batch
- [ ] Upload puzzles to R2
- [ ] Test in Shopify dev store
- [ ] Deploy to production
- [ ] Verify CORS works
- [ ] (Optional) Scale down/remove Heroku app

## Notes

- Puzzles are cached with `max-age=31536000` (1 year) since they're immutable
- UTC dates are used to ensure consistency across timezones
- The same puzzle template is used for all dates in a difficulty level (for testing)
- Future enhancement: Generate unique puzzles using AI or puzzle API
