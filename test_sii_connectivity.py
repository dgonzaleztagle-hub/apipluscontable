#!/usr/bin/env python3
"""
Test simple de conectividad al SII
Verifica si podemos al menos acceder a la página de login
"""

import requests
from datetime import datetime

print("\n" + "="*60)
print("TEST DE CONECTIVIDAD AL SII")
print(f"Timestamp: {datetime.now()}")
print("="*60)

try:
    print("\n1. Testeando acceso a página de login del SII...")
    response = requests.get(
        "https://zeusr.sii.cl/AUT2000/InicioAutenticacion/IngresoRutClave.html",
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    print(f"   Página accesible: {'SÍ' if response.status_code == 200 else 'NO'}")
    
    if response.status_code == 200:
        print(f"   Tamaño: {len(response.content)} bytes")
        print(f"   Primeros 300 chars: {response.text[:300]}")
    
    print("\n2. Testeando acceso a API del SII...")
    response = requests.get(
        "https://www4.sii.cl/consdcvinternetui/services/data/facadeService/getResumen/COMPRAS/11/2025",
        timeout=10
    )
    print(f"   Status: {response.status_code}")
    print(f"   Respuesta: {response.text[:300]}")
    
except requests.exceptions.Timeout:
    print("   ✗ TIMEOUT - SII no responde")
except requests.exceptions.ConnectionError as e:
    print(f"   ✗ ERROR DE CONEXIÓN: {str(e)}")
except Exception as e:
    print(f"   ✗ ERROR: {str(e)}")
