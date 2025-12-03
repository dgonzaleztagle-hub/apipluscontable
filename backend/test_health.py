#!/usr/bin/env python
import sys
import time

# Esperar a que el servidor esté listo
time.sleep(2)

try:
    import requests
    response = requests.get('http://localhost:5000/health', timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
