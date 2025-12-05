FROM python:3.12-slim

WORKDIR /app

# Install only essential system dependencies for Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libnss3 \
    libxss1 \
    libasound2 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy everything from backend
COPY backend/ /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and browsers
RUN pip install playwright && playwright install chromium

EXPOSE 5000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--timeout", "120", "--workers", "1"]
