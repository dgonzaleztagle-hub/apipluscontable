FROM python:3.12-alpine

WORKDIR /app

# Install system dependencies for Chromium on Alpine
RUN apk add --no-cache \
    ca-certificates \
    libcairo \
    libcups \
    libdbus \
    libexpat \
    libfontconfig \
    libfreetype \
    libgbm \
    libglib \
    libharfbuzz \
    libnss \
    libpango \
    libpixman \
    libx11 \
    libxcb \
    libxcomposite \
    libxcursor \
    libxdamage \
    libxext \
    libxfixes \
    libxi \
    libxinerama \
    libxkbcommon \
    libxrandr \
    libxrender \
    libxss \
    libxtst \
    liberation-fonts \
    xdg-utils \
    && adduser -D nonroot

# Copy backend files
COPY backend/ /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright - it will download and use its own Chromium binary
RUN pip install --no-cache-dir playwright~=1.40.0 && \
    python -m playwright install chromium

EXPOSE 5000

# Run as non-root user
USER nonroot

CMD ["python", "-m", "gunicorn.app.wsgiapp", "app:app", "--bind", "0.0.0.0:5000", "--timeout", "120", "--workers", "1"]CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--timeout", "120", "--workers", "1"]
