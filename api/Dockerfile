# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.3
FROM python:${PYTHON_VERSION}-slim

# Prevent .pyc and stdout buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps (if needed) & Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your source code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI with uvicorn
# Assumes you have a file "main.py" with "app = FastAPI()"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]