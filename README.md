# Weatherly

**Full‑Stack Weather App**

---

## Overview

Weatherly is a simple yet professional full‑stack application that fetches real‑time and 7‑day weather forecasts using the Open‑Meteo API. It demonstrates:

- **Backend:** Django & Django REST Framework  
- **Database:** PostgreSQL  
- **Frontend:** Bootstrap, Vanilla JavaScript  
- **Features:**  
  - City search (case‑insensitive, normalized display)  
  - Geolocation lookup (“Use My Location” button)  
  - °C/°F unit toggle  
  - Light & Dark (Night) mode  
  - Recent searches log  
  - Custom error UI for invalid cities  

---

## Tech Stack

- Python 3.11  
- Django 5.2  
- Django REST Framework  
- PostgreSQL  
- Docker (for future phases)  
- Bootstrap 5  
- Open‑Meteo API  
- GitHub Actions (CI/CD)  
- Pytest  

---

## Getting Started

1. **Clone the repository**  
   ```bash
   git clone https://github.com/ThinkAboutRek/Weatherly.git
   cd Weatherly
   ```

2. **Set up a Python virtual environment**  
   ```bash
   python -m venv .venv
   source .venv/bin/activate      # macOS/Linux
   .\.venv\Scripts\Activate.ps1 # Windows PowerShell
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**  
   - Copy `.env.example` to `.env` and fill in your values:  
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

5. **Run migrations**  
   ```bash
   python manage.py migrate
   ```

6. **Start the development server**  
   ```bash
   python manage.py runserver
   ```

7. **Open in your browser**  
   Navigate to http://127.0.0.1:8000/ to use Weatherly.

---

## Project Structure

```
Weatherly/
├── weatherly/        # Django project settings
├── weather/          # Django app (models, views, URLs)
├── templates/        # HTML templates
├── static/           # CSS & JavaScript assets
├── .env.example
├── requirements.txt
└── README.md
```

---

## Next Steps

- **Phase 3:** Dockerize backend & database, add automated tests with Pytest, integrate CI/CD.  
- **Phase 4:** Deploy to a cloud platform (Heroku, Render, or similar).  

---

## 📄 License

Open-source for educational and portfolio use.

---

Made with ☕ and curiosity by **Shayan Bagheri (ThinkAboutRek)**