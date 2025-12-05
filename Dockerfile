FROM python:3.12-slim

WORKDIR /app

# Install all system dependencies required by Playwright/Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libnss3 \
    libxss1 \
    libasound2 \
    libgobject-2.0-0 \
    libglib-2.0-0 \
    libdbus-1-3 \
    libatk-1.0-0 \
    libatk-bridge-2.0-0 \
    libcups2 \
    libgio-2.0-0 \
    libdrm2 \
    libexpat1 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libXcomposite1 \
    libXdamage1 \
    libXfixes3 \
    libXrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy everything from backend
COPY backend/ /app/

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and browsers
RUN pip install playwright && playwright install chromium

EXPOSE 5000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--timeout", "120", "--workers", "1"]
