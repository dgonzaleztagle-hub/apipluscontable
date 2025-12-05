FROM mcr.microsoft.com/playwright:v1.40.0-focal

WORKDIR /app

# Install Python 3.12 and pip
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.12 \
    python3.12-venv \
    python3-pip \
    python3-setuptools \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy everything from backend
COPY backend/ /app/

# Install Python dependencies
RUN python3.12 -m pip install --no-cache-dir -r requirements.txt

# Ensure Playwright browsers are installed
RUN python3.12 -m pip install --no-cache-dir playwright && \
    python3.12 -m playwright install chromium

EXPOSE 5000

CMD ["python3.12", "-m", "gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--timeout", "120", "--workers", "1"]

EXPOSE 5000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--timeout", "120", "--workers", "1"]
