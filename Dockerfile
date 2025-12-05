FROM python:3.12-slim

WORKDIR /app

# Install system dependencies required by Playwright/Chromium
# Using a comprehensive set of packages for browser automation
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    apt-transport-https \
    ca-certificates \
    curl \
    && curl -sL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get update && apt-get install -y --no-install-recommends \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libgbm1 \
    libglib2.0-0 \
    libgobject-2.0-0 \
    libgtk-3-0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxkbcommon0 \
    libxkbcommon-x11-0 \
    libxinerama1 \
    libxdotool1 \
    fonts-dejavu \
    fonts-liberation \
    fonts-noto-cjk \
    xdg-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy everything from backend
COPY backend/ /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers with system deps handling
RUN pip install --no-cache-dir playwright && \
    playwright install chromium && \
    playwright install-deps chromium

EXPOSE 5000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--timeout", "120", "--workers", "1"]

EXPOSE 5000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--timeout", "120", "--workers", "1"]
