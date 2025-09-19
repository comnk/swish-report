# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.3
FROM python:${PYTHON_VERSION}-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for Playwright Chromium + video processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl unzip gnupg \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libxkbcommon0 \
    libxcomposite1 libxdamage1 libxrandr2 libgbm1 \
    libasound2 libpangocairo-1.0-0 libpango-1.0-0 libcairo2 \
    libx11-xcb1 libxext6 libxfixes3 fonts-liberation libgtk-3-0 \
    ffmpeg \
    python3-opencv \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories for video processing
RUN mkdir -p /app/downloads /app/highlights /app/final_reels

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright + Chromium
RUN pip install playwright \
    && playwright install --with-deps chromium

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
