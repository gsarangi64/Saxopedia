> CSC 210 Project 2 — Gaurav Sarangi, Austin Shilling

# Saxopedia

## Purpose
Saxopedia is an encyclopedia of standard classical saxophone repertoire. Users can browse pieces, view composer information, track repertoire they've studied, and build performance programs.

## Navigation

| Page | URL | Auth Required |
|---|---|---|
| Home | `/` | No |
| Repertoire | `/repertoire` | Yes |
| My Programs | `/programs` | Yes |
| Studied List | `/studied` | Yes |
| Composer Info | `/composer/<name>` | No |
| Register | `/register` | No |
| Login | `/login` | No |
| Logout | `/logout` | Yes |

## Key Features

### User Authentication
Users can register and log in to access personalized data. Passwords are hashed via Werkzeug. Sessions are managed with Flask-Login.

### Repertoire Tracking
Logged-in users can mark any piece from the repertoire as studied, add optional performance notes, and view their full studied list on the Studied List page.

### Programs
Users can create named performance programs and add any number of pieces to them from the Repertoire page. Programs and their pieces are viewable and manageable on the My Programs page.

### Filtering and Search (Front-End)
The repertoire page has a fully client-side filter system written in JavaScript (filters.js). Features include:
- **Live search** — filters by title or composer as you type, with no page reload
- **Epoch toggle buttons** — built dynamically from the data at page load; multiple epochs can be active simultaneously (OR logic)
- **Sort** — by year ascending/descending, title A-Z, or composer A-Z, applied to the filtered subset
- **Active filter tags** — each active filter displays as a removable tag; filters can be cleared individually or all at once
- **Live piece count** — updates to show how many pieces match the current filters out of the total

### Data Sources
- **sax-repertoire** — a personal JSON file of saxophone repertoire hosted on GitHub, fetched via raw URL
- **OpenOpus** — an open-source REST API of classical composers, returning JSON with birth/death dates, epoch, and full name

## Project Structure

```
Saxopedia/
├── app/
│   ├── app.py          # Flask application, routes
│   ├── models.py       # SQLAlchemy models and DB helpers
│   ├── forms.py        # Flask-WTF form definitions
│   ├── services.py     # External API/data fetching logic
│   ├── templates/      # Jinja2 HTML templates
│   └── static/
│       ├── css/
│       │   └── styles.css
│       └── js/
│           └── filters.js
├── venv/
├── requirements.txt
└── README.md
```

## Setup Instructions

```bash
# 1. Clone the repository
git clone https://github.com/gsarangi64/Saxopedia.git
cd Saxopedia

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the app
python app/app.py
```

The app runs at `http://127.0.0.1:5000` by default.