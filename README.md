# CloverKit Crossword API

Backend API for the CloverKit Crossword Shopify extension. This Flask-based API provides crossword puzzle data dynamically to the storefront extension.

## Tech Stack

- **Python 3.11+**
- **Flask** - Web framework
- **Flask-CORS** - CORS support for Shopify storefronts
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **PostgreSQL** - Database
- **Gunicorn** - Production WSGI server

## Features

- Daily crossword puzzles by topic
- RESTful API endpoints
- Admin API with API key authentication
- JSONB storage for flexible puzzle data
- Automatic database migrations with Alembic
- CORS enabled for Shopify storefronts

## API Endpoints

### Public Endpoints (No auth required)

- `GET /api/v1/puzzles/daily?topic=shopping` - Get today's puzzle for a topic
- `GET /api/v1/puzzles/date?topic=shopping&date=2026-01-17` - Get puzzle for specific date
- `GET /api/v1/health` - Health check

### Admin Endpoints (Requires X-API-Key header)

- `GET /api/v1/puzzles` - List all puzzles (with pagination)
- `POST /api/v1/puzzles` - Create new puzzle
- `GET /api/v1/puzzles/<id>` - Get specific puzzle
- `PUT /api/v1/puzzles/<id>` - Update puzzle
- `DELETE /api/v1/puzzles/<id>` - Delete puzzle

## Local Development Setup

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 14 or higher
- pip (Python package manager)

### 1. Clone the Repository

```bash
cd /path/to/CloverKit
git clone <repository-url> CloverKitCrosswordAPI
cd CloverKitCrosswordAPI
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL Database

```bash
# Create database
psql postgres
CREATE DATABASE crossword_db;
\q
```

### 5. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` file with your settings:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/crossword_db
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this
API_KEY=your-secure-api-key
ALLOWED_ORIGINS=https://your-store.myshopify.com,http://localhost:3000
PORT=5000
HOST=0.0.0.0
```

### 6. Initialize Database

```bash
# Initialize Alembic (first time only)
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

### 7. Seed Database

```bash
python scripts/seed_puzzles.py
```

### 8. Run Development Server

```bash
python run.py
```

The API will be available at `http://localhost:5000`

## Testing the API

### Test Health Endpoint

```bash
curl http://localhost:5000/api/v1/health
```

### Test Daily Puzzle Endpoint

```bash
curl http://localhost:5000/api/v1/puzzles/daily?topic=shopping
```

### Test Admin Endpoints (with API key)

```bash
# List puzzles
curl -H "X-API-Key: your-api-key" http://localhost:5000/api/v1/puzzles

# Create puzzle
curl -X POST \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d @puzzle_data.json \
  http://localhost:5000/api/v1/puzzles
```

## Database Schema

### Puzzles Table

```sql
- id (UUID) - Primary key
- title (VARCHAR) - Puzzle title
- topic (VARCHAR) - Theme/category (e.g., "shopping")
- difficulty (VARCHAR) - easy, medium, hard
- grid_size (INTEGER) - Grid dimensions
- grid_data (JSONB) - 2D array of answers
- across_clues (JSONB) - Across clue objects
- down_clues (JSONB) - Down clue objects
- clue_positions (JSONB) - Clue positioning metadata
- publish_date (DATE) - Publication date
- is_active (BOOLEAN) - Published status
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

UNIQUE CONSTRAINT: (topic, publish_date)
```

## Example Puzzle Data Format

```json
{
  "title": "Shopping Crossword",
  "topic": "shopping",
  "difficulty": "medium",
  "grid_size": 10,
  "grid_data": [
    ["S", "H", "O", "P", "I", "F", "Y", null, "C", "A", "R", "T"],
    ...
  ],
  "across_clues": {
    "1": "E-commerce platform",
    "8": "Shopping basket"
  },
  "down_clues": {
    "1": "Online store",
    "2": "Buyer"
  },
  "clue_positions": {
    "1": {"row": 0, "col": 0, "direction": "across", "length": 7},
    "8": {"row": 0, "col": 8, "direction": "across", "length": 4}
  },
  "publish_date": "2026-01-17"
}
```

## Production Deployment

### Using Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app('production')"
```

### Environment Variables for Production

- Set `FLASK_ENV=production`
- Use strong `SECRET_KEY`
- Use secure `API_KEY`
- Configure `DATABASE_URL` with production database
- Set `ALLOWED_ORIGINS` to your Shopify store domains

## Project Structure

```
CloverKitCrosswordAPI/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # Database models
│   ├── api/
│   │   ├── __init__.py
│   │   ├── puzzles.py       # Puzzle endpoints
│   │   └── health.py        # Health check
│   └── utils/
│       ├── __init__.py
│       └── decorators.py    # Auth decorators
├── migrations/              # Alembic migrations
├── scripts/
│   └── seed_puzzles.py      # Database seeding
├── .env.example
├── .gitignore
├── config.py                # Configuration
├── requirements.txt
├── run.py                   # Entry point
└── README.md
```

## Common Issues

### Database Connection Error

Make sure PostgreSQL is running and connection string is correct in `.env`

```bash
# Check PostgreSQL status
brew services list  # macOS
sudo systemctl status postgresql  # Linux
```

### Migration Issues

If migrations fail, you can reset:

```bash
flask db downgrade
flask db upgrade
```

### CORS Issues

Make sure `ALLOWED_ORIGINS` in `.env` includes your Shopify store domain.

## License

MIT

## Support

For issues or questions, please open an issue in the repository.
