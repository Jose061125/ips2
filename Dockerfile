# syntax=docker/dockerfile:1
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

# Optional dev deps (ignored if not present)
COPY requirements-dev.txt ./
RUN if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi

# Copy project
COPY . .

EXPOSE 5000

# Default command (development)
CMD ["python", "run.py"]
