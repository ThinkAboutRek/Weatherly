# Dockerfile
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Install system deps (Postgres client for migrations)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create directory for static files (optional if collecting static later)
RUN mkdir -p /app/staticfiles

# Expose port
EXPOSE 8000

# Default entrypoint for dev
CMD ["gunicorn", "weatherly.wsgi:application", "--bind", "0.0.0.0:8000"]
