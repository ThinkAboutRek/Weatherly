# Weatherly

![CI](https://github.com/ThinkAboutRek/Weatherly/actions/workflows/ci.yml/badge.svg)

**Full‑Stack Weather App**

---

## Overview

Weatherly is a full‑stack Django application that fetches real‑time and 7‑day weather forecasts using the Open‑Meteo API. It features user authentication, a token‑authenticated REST API, paginated search history, CSV data export, and a suite of **44 automated tests** — built to production‑ready standards with Supabase (PostgreSQL), GitHub Actions CI/CD, and WhiteNoise static file serving.

### Core Features

- City search with case‑insensitive input and normalised display name returned from the geocoding API
- Geolocation lookup via the browser Geolocation API ("Use My Location" button)
- °C / °F unit toggle applied to both current conditions and the 7‑day forecast
- Light & Dark (Night) mode toggle with preference persisted in `localStorage`
- User registration, login, and logout (Django session‑based authentication)
- Every search is tied to the authenticated user — anonymous searches are stored separately
- Personal search history page: paginated (10 per page), live city filter, and CSV export
- Token‑authenticated REST API so external clients can authenticate and query history programmatically
- Recent searches widget on the home page — scoped to the logged‑in user's own searches
- Graceful error handling for invalid cities, upstream API failures (502), and missing parameters (400)
- Enhanced Django Admin: searchable by city and username, filterable by user and date, with date hierarchy

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.13 |
| Backend | Django 6.0 + Django REST Framework 3.17 |
| Database | PostgreSQL via Supabase (transaction pooler, SSL) |
| Frontend | Bootstrap 5 (CDN) + Vanilla JavaScript |
| Static files | WhiteNoise (dev: plain storage, prod: compressed + hashed manifest) |
| App server | Gunicorn 25 |
| Containerisation | Docker + Docker Compose |
| Weather data | Open‑Meteo API — forecast + geocoding (no API key required) |
| Reverse geocoding | Nominatim / OpenStreetMap |
| Testing | Pytest 9 + pytest‑django + requests‑mock — **44 tests** |
| CI/CD | GitHub Actions |

---

## Project Structure

```
Weatherly/
├── weatherly/                        # Django project configuration
│   ├── settings.py                   # All settings — env-driven, Supabase-ready
│   ├── urls.py                       # Root URL conf (delegates to weather.urls)
│   ├── wsgi.py                       # WSGI entry point (Gunicorn)
│   └── asgi.py                       # ASGI entry point
│
├── weather/                          # Main Django application
│   ├── models.py                     # Search model (nullable user FK, city, timestamp)
│   ├── views.py                      # Weather API, paginated history, CSV export, history page
│   ├── auth_views.py                 # Register, login, logout HTML views
│   ├── urls.py                       # All URL patterns — HTML pages and /api/* endpoints
│   ├── admin.py                      # Enhanced admin (list_display, search, filter, date hierarchy)
│   ├── migrations/
│   │   ├── 0001_initial.py           # Initial Search model
│   │   └── 0002_alter_search_options_search_user.py  # User FK + Meta ordering
│   └── tests/
│       ├── __init__.py
│       ├── test_models.py            # Model behaviour — 6 tests
│       ├── test_auth.py              # Auth flows — 9 tests
│       ├── test_views.py             # Weather API (city + coords) — 12 tests
│       └── test_views_additional.py  # History, token auth, CSV, pagination — 17 tests
│
├── templates/
│   ├── base.html                     # Shared layout: navbar, messages, Bootstrap, dark-mode toggle
│   ├── index.html                    # Main SPA weather search page
│   ├── history.html                  # Server-rendered paginated search history
│   └── auth/
│       ├── login.html                # Login form (extends base.html)
│       └── register.html             # Registration form (extends base.html)
│
├── static/
│   └── weather/
│       ├── css/styles.css            # Dark mode overrides for Bootstrap components
│       └── js/app.js                 # SPA logic: city search, geolocation, unit/theme toggle
│
├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions: Postgres service, Python 3.13, pytest
│
├── .env.example                      # Environment variable template
├── .env                              # Local secrets — git-ignored
├── .gitignore
├── docker-compose.yml                # Local dev: Postgres 15 container + Django app
├── Dockerfile                        # Production image: python:3.13-slim + Gunicorn
├── pytest.ini                        # DJANGO_SETTINGS_MODULE + --reuse-db
├── requirements.txt                  # Pinned Python dependencies
└── README.md
```

---

## API Reference

All API endpoints return JSON. Authentication is via **session cookie** (browser) or **token** (API clients).

### Public Endpoints

| Method | URL | Query Params | Description |
|--------|-----|-------------|-------------|
| `GET` | `/api/weather/` | `?city=<name>` | Geocode city then return current conditions + 7‑day forecast |
| `GET` | `/api/weather-coords/` | `?lat=<lat>&lon=<lon>` | Fetch forecast by coordinates, reverse-geocode to a place name |
| `GET` | `/api/searches/` | — | Last 5 searches — user‑scoped when authenticated, anonymous otherwise |

**Weather response shape:**
```json
{
  "city": "London",
  "latitude": 51.5,
  "longitude": -0.1,
  "current": {
    "temperature": 14.2,
    "windspeed": 9.4,
    "weathercode": 3
  },
  "daily": {
    "time": ["2026-03-22", "2026-03-23"],
    "temperature_2m_max": [15.1, 13.8],
    "temperature_2m_min": [8.3, 7.9],
    "weathercode": [3, 61]
  }
}
```

### Token Authentication

| Method | URL | Body | Description |
|--------|-----|------|-------------|
| `POST` | `/api/token/` | `{"username": "…", "password": "…"}` | Exchange credentials for an API token |

**Example:**
```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "shayan", "password": "yourpassword"}'
```
```json
{"token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"}
```

### Authenticated API Endpoints

All requests below require the `Authorization: Token <token>` header.

| Method | URL | Query Params | Description |
|--------|-----|-------------|-------------|
| `GET` | `/api/searches/history/` | `?city=<filter>`, `?page=<n>` | Paginated personal search history (10 results per page) |

**Example:**
```bash
curl http://127.0.0.1:8000/api/searches/history/?city=lon&page=1 \
  -H "Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
```
```json
{
  "count": 24,
  "total_pages": 3,
  "page": 1,
  "results": [
    {"city": "London", "searched_at": "2026-03-22T19:04:11.832Z"},
    {"city": "Long Beach", "searched_at": "2026-03-21T08:12:44.001Z"}
  ]
}
```

### HTML Pages

| URL | Auth Required | Description |
|-----|:------------:|-------------|
| `/` | No | Main weather search page (SPA) |
| `/register/` | No | Create a new account |
| `/login/` | No | Log in with username and password |
| `/logout/` | Yes | End session and redirect to home |
| `/history/` | Yes | Paginated personal search history with city filter |
| `/history/export/` | Yes | Download search history as `search_history.csv` (`?city=<filter>` optional) |
| `/admin/` | Staff | Django admin panel |

---

## Getting Started (Local Development)

### 1. Clone the repository
```bash
git clone https://github.com/ThinkAboutRek/Weatherly.git
cd Weatherly
```

### 2. Create and activate a virtual environment
```bash
python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Windows Git Bash
source .venv/Scripts/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment

Copy the example file and fill in your values:
```bash
cp .env.example .env
```

Edit `.env`:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here

# Supabase — Transaction Pooler connection
POSTGRES_DB=postgres
POSTGRES_USER=postgres.<your-project-ref>
POSTGRES_PASSWORD=your-supabase-db-password
POSTGRES_HOST=aws-1-eu-west-1.pooler.supabase.com
POSTGRES_PORT=6543

OPEN_METEO_BASE_URL=https://api.open-meteo.com/v1
```

> **Supabase note:** Always use the **Transaction Pooler** port (`6543`), not the direct connection port (`5432`). The app is pre‑configured with `CONN_MAX_AGE=0` and `sslmode=require` for full PgBouncer compatibility. Session mode (port `5432`) is not supported because it holds persistent connections that conflict with Django's connection lifecycle.

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Start the development server
```bash
python manage.py runserver
```

### 7. Open in browser
Visit: http://127.0.0.1:8000/

### 8. Create a superuser (optional — for Django Admin)
```bash
python manage.py createsuperuser
```
Then visit http://127.0.0.1:8000/admin/

---

## Running with Docker (Local Postgres)

The Docker Compose setup spins up a local PostgreSQL 15 container alongside the app — useful if you prefer not to depend on Supabase for local dev, or for fully offline development.

### 1. Ensure `.env` is populated

You can use any values for the Postgres variables when running locally. Docker Compose overrides `POSTGRES_HOST` to point at the `db` service automatically.

### 2. Build and start services
```bash
docker-compose up --build
```

This will:
- Start a PostgreSQL 15 container with a persistent named volume
- Apply all Django migrations automatically on startup
- Build the app image from `python:3.13-slim`
- Launch Django via Gunicorn on port `8000`
- Serve static files through WhiteNoise

### 3. Visit
http://localhost:8000/

### 4. Tear down
```bash
docker-compose down
```

To also destroy the database volume (wipes all data):
```bash
docker-compose down -v
```

---

## Testing

Automated tests use **Pytest** and **pytest‑django** for database fixtures and the Django test client. All external HTTP calls (Open‑Meteo, Nominatim) are intercepted with **requests‑mock** so no network access is needed. Tests run against a real PostgreSQL test database (created from your `.env` connection).

### Test suite — 44 tests across 4 modules

| Module | Tests | What is covered |
|--------|:-----:|-----------------|
| `test_models.py` | 6 | `__str__` format, anonymous FK, user FK assignment, `SET_NULL` on user delete, `Meta` ordering (newest first), `max_length` boundary |
| `test_auth.py` | 9 | Register page load, successful registration + redirect, mismatched passwords, duplicate username, login page load, valid login, invalid credentials, logout redirect, already‑logged‑in redirect from login page |
| `test_views.py` | 12 | City weather success, missing param (400), city not found (404), search logged anonymously, search logged to authenticated user, upstream 502, case‑insensitive input normalised to geocoded name, coords success, coords missing params (400), coords search logged, reverse geocode failure falls back to "Current Location", coords upstream 502 |
| `test_views_additional.py` | 17 | Recent searches capped at 5, anonymous scoping, authenticated user scoping, paginated history requires token (401), returns 10 per page, user isolation (token A cannot see user B's data), city filter, page 2, CSV requires login, CSV content type, CSV header row (`City,Searched At`), CSV only own data, CSV city filter, history page requires login, history page renders searches, history page city filter, history page total count badge |

### Running tests

Run the full suite:
```bash
pytest --disable-warnings -q
```

Run with full output:
```bash
pytest -v
```

Run a single module:
```bash
pytest weather/tests/test_auth.py -v
pytest weather/tests/test_views.py -v
```

Run a single test by name:
```bash
pytest -k "test_paginated_history_isolates_users" -v
```

> **Why `--reuse-db`?** Supabase uses PgBouncer as a connection pooler. PgBouncer keeps idle connections open, which prevents `DROP DATABASE` from completing at the end of a test run. The `--reuse-db` flag in `pytest.ini` tells pytest‑django to create the test database on first run and reuse it on subsequent runs, skipping the destructive teardown step entirely.

---

## Continuous Integration

GitHub Actions is configured to run on every push and pull request to `main`.

**Pipeline steps:**

1. Checkout repository (`actions/checkout@v4`)
2. Set up Python 3.13 with pip cache (`actions/setup-python@v5`)
3. Spin up PostgreSQL 15 as a service container with a health check
4. Install all dependencies from `requirements.txt` inside a virtualenv
5. Wait for Postgres to be ready (`pg_isready` polling)
6. Run `python manage.py migrate --no-input`
7. Execute `pytest --maxfail=1 --disable-warnings -q`

The CI environment uses a local Postgres container (not Supabase) so there are no PgBouncer constraints — `CREATE DATABASE` and `DROP DATABASE` both work cleanly.

The status badge at the top of this README reflects the latest build on `main`.

---

## Environment Variables

All configuration is loaded from `.env` via `python-dotenv`. No value is hard‑coded in settings.

| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `SECRET_KEY` | Prod only | Dev fallback | Django cryptographic signing key |
| `DEBUG` | No | `False` | Set to `True` in development — enables the dev fallback secret and plain static storage |
| `ALLOWED_HOSTS` | No | `localhost,127.0.0.1,0.0.0.0` | Comma‑separated list of allowed hostnames |
| `POSTGRES_DB` | Yes | `postgres` | Name of the Supabase/Postgres database |
| `POSTGRES_USER` | Yes | — | Database user (e.g. `postgres.<project-ref>` for Supabase) |
| `POSTGRES_PASSWORD` | Yes | — | Database password |
| `POSTGRES_HOST` | Yes | — | Database host (Supabase pooler or `localhost`) |
| `POSTGRES_PORT` | No | `6543` | Database port (`6543` for Supabase transaction pooler) |
| `OPEN_METEO_BASE_URL` | No | `https://api.open-meteo.com/v1` | Override the weather API base URL (useful in tests) |

> **Production guard:** When `DEBUG=False`, a missing `SECRET_KEY` immediately raises `django.core.exceptions.ImproperlyConfigured` — the app will not start with an insecure fallback in production.

> **Static files in production:** When `DEBUG=False`, WhiteNoise uses `CompressedManifestStaticFilesStorage` which requires `python manage.py collectstatic` to have been run. In development (`DEBUG=True`), plain `StaticFilesStorage` is used so `collectstatic` is not needed.

---

## Next Steps

- **Cloud deployment** — Deploy to Render, Railway, or Fly.io with Supabase as the managed database and automatic deploys triggered from `main`.
- **Test coverage reporting** — Add `pytest-cov` and a coverage percentage badge to the README.
- **Rate limiting** — Add `django-ratelimit` to the weather API endpoints to protect against abuse.
- **Email verification** — Extend registration with an email confirmation step using Django's built‑in email framework.
- **Weather icons** — Map WMO `weathercode` values to icons (e.g. WMO Weather Interpretation Codes → emoji or SVG icon set).

---

## Contribution

Feel free to open issues or pull requests. Keep changes focused, ensure all 44 tests pass before submitting, and follow the existing code style.

---

## License

MIT License — open for educational and portfolio use.

---

Made with ☕ and curiosity by **Shayan Bagheri (ThinkAboutRek)**
