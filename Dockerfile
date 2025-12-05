FROM python:3.12-slim

WORKDIR /app

# Install Chromium and its dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium-browser \
    chromium-bsu \
    ca-certificates \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    fonts-liberation \
    libappindicator1 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc-s1 \
    libglib2.0-0 \
    libgobject-2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxinerama1 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    libxkbcommon0 \
    libxkbcommon-x11-0 \
    lsb-release \
    xdg-utils \
    wget \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy everything from backend
COPY backend/ /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright
RUN pip install --no-cache-dir playwright && \
    python -m playwright install chromium

EXPOSE 5000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--timeout", "120", "--workers", "1"]

EXPOSE 5000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--timeout", "120", "--workers", "1"]
