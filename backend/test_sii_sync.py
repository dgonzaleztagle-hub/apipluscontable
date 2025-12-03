#!/usr/bin/env python
"""Test script para sincronización SII"""
import json
import time
import sys

sys.path.insert(0, '.')

try:
    import requests
    
    print("⏳ Esperando respuesta del servidor SII (30-60 segundos)...")
    print("=" * 60)
    
    payload = {
        "rut": "77956294-8",
        "password": "Tr7795629.",
        "mes": 11,
        "ano": 2025
    }
    
    response = requests.post(
        'http://localhost:5000/api/sync-sii',
        json=payload,
        timeout=120  # 2 minutos de timeout
    )
    
    print(f"\n✅ Status Code: {response.status_code}")
    print("\nResponse:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
except requests.exceptions.Timeout:
    print("❌ Timeout - El servidor tardó demasiado")
except requests.exceptions.ConnectionError:
    print("❌ Error de conexión - El servidor no está escuchando")
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    sys.exit(1)
