# Dockerfile for social-media-pro
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Set environment variables (optional, for Python output buffering)
ENV PYTHONUNBUFFERED=1

# Entrypoint
CMD ["python", "main.py"]
# Runs at 05:00, 07:00, 13:00, 16:00, 21:00 every day (5 times per day)