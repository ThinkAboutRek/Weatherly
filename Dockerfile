# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# System dependencies for Postgres client
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static assets
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Start Gunicorn
CMD ["gunicorn", "weatherly.wsgi:application", "--bind", "0.0.0.0:8000"]
