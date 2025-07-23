FROM python:3.11-slim

WORKDIR /app

# Use a working directory that won't be overwritten by GitHub Actions
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy src folder
COPY src/ ./src/

# Entrypoint for GitHub Action
ENTRYPOINT ["python", "/app/src/main.py"]