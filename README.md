# Weatherly

![CI](https://github.com/ThinkAboutRek/Weatherly/actions/workflows/ci.yml/badge.svg)

**Full‑Stack Weather App**

---

## Overview

Weatherly is a professional full‑stack application that fetches real‑time and 7‑day weather forecasts using the Open‑Meteo API. It showcases a modern developer toolchain, including containerization, automated testing, and CI/CD.

### Core Features
- City search (case‑insensitive, normalized display)  
- Geolocation lookup (“Use My Location” button)  
- °C/°F unit toggle  
- Light & Dark (Night) mode  
- Recent searches log  
- Custom error UI for invalid or unknown cities  
- Persistent search logging in PostgreSQL  

---

## Tech Stack

- Python 3.11  
- Django 5.2 + Django REST Framework  
- PostgreSQL  
- Docker & Docker Compose  
- Bootstrap 5  
- Open‑Meteo API  
- Pytest with requests-mock  
- GitHub Actions (CI/CD)  
- WhiteNoise for static asset serving  
- Gunicorn application server  

---

## Getting Started (Local Development)

### 1. Clone the repository
```bash
git clone https://github.com/ThinkAboutRek/Weatherly.git
cd Weatherly
```

### 2. Python virtual environment
```bash
python -m venv .venv
# Activate:
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
Copy example and fill values:
```bash
cp .env.example .env
```
Edit `.env`:
```
SECRET_KEY=your-secret-key
DEBUG=True
POSTGRES_DB=weatherly
POSTGRES_USER=weatherlyuser
POSTGRES_PASSWORD=strongpassword
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
OPEN_METEO_BASE_URL=https://api.open-meteo.com/v1
```

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Start server
```bash
python manage.py runserver
```

### 7. Open in browser
Visit: http://127.0.0.1:8000/

---

## Running with Docker (Development)

Weatherly is containerized with Docker Compose (Postgres + app).

### 1. Ensure `.env` is populated (same as above)

### 2. Build and start services
```bash
docker-compose up --build
```

This will:
- Spin up PostgreSQL
- Apply migrations
- Launch the Django app via Gunicorn with static assets collected

### 3. Visit
http://localhost:8000/

### 4. Tear down
```bash
docker-compose down
```

---

## Testing

Automated tests are written with **Pytest** and use mocks for external HTTP calls.

Run locally:
```bash
pytest --maxfail=1 --disable-warnings -q
```

You should see all tests pass (model, endpoint normal/edge cases, recent searches, case-insensitive behavior).

---

## Continuous Integration

GitHub Actions is configured to:

- Spin up a PostgreSQL service  
- Install dependencies in a virtualenv  
- Run migrations  
- Execute the test suite  

The status badge at the top reflects the current build state.

---

## Environment Variables

Required (see `.env.example`):
- `SECRET_KEY`  
- `DEBUG`  
- `POSTGRES_DB`  
- `POSTGRES_USER`  
- `POSTGRES_PASSWORD`  
- `POSTGRES_HOST`  
- `POSTGRES_PORT`  
- `OPEN_METEO_BASE_URL`

---

## Project Structure

```
Weatherly/
├── weatherly/            # Django project settings
├── weather/              # App: models, views, URLs, tests
├── templates/            # HTML templates
├── static/               # CSS & JavaScript
├── .github/              # CI workflows
├── .env.example          # Env template
├── docker-compose.yml    # Dev container orchestration
├── Dockerfile            # App container build
├── requirements.txt
└── README.md / README_UPDATED.md
```

---

## Next Steps

- **Phase 4: Deployment & Polish**  
  Deploy to a cloud platform (Render, Railway, Vercel with backend proxy, or Heroku) with environment handling, automatic builds, and a real domain.  
- Add test coverage reporting and a coverage badge.  
- Harden secrets for production (no fallback secret, use vault or platform secrets).

---

## Contribution

Feel free to open issues or pull requests. Keep changes small and test before submitting.

---

## License

MIT License — open for educational and portfolio use.  

---

Made with ☕ and curiosity by **Shayan Bagheri (ThinkAboutRek)**
