FROM python:3.12-slim

WORKDIR /app

# Install system dependencies that Chromium needs to RUN (not build)
# These are the RUNTIME deps only, not the build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libfreetype6 \
    libgbm1 \
    libgcc-s1 \
    libglib2.0-0 \
    libgobject-2.0-0 \
    libgtk-3-0 \
    libharfbuzz0b \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libpangoft2-1.0-0 \
    libpixman-1-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxinerama1 \
    libxkbcommon0 \
    libxkbcommon-x11-0 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    fonts-liberation \
    xdg-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy backend files
COPY backend/ /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright - it will download and use its own Chromium binary
# Do NOT use --with-deps, just install the browser binary
RUN pip install --no-cache-dir playwright~=1.40.0 && \
    python -m playwright install chromium

# Verify gunicorn is installed
RUN which python && python -m pip list | grep gunicorn

EXPOSE 5000

CMD ["python", "-m", "gunicorn.app.wsgiapp", "app:app", "--bind", "0.0.0.0:5000", "--timeout", "120", "--workers", "1"]CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--timeout", "120", "--workers", "1"]
