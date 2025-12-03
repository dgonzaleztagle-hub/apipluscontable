#!/usr/bin/env python
"""
Test para el endpoint /api/sync-books
Simula lo que hace el botón "Sinc" de la app Lova
"""
import json
import logging
from app import app

# Configurar logging
logging.basicConfig(level=logging.INFO)

def test_sync_books():
    print("=" * 70)
    print("TEST: Endpoint /api/sync-books (botón Sinc de Lova)")
    print("=" * 70)
    print()
    
    # Crear cliente de test
    client = app.test_client()
    
    # Datos de prueba
    payload = {
        "rut": "77956294-8",
        "password": "Tr7795629.",
        "mes": 10,
        "ano": 2025
    }
    
    print(f"Enviando solicitud a /api/sync-books con:")
    print(f"  RUT: {payload['rut']}")
    print(f"  Mes: {payload['mes']}")
    print(f"  Año: {payload['ano']}")
    print()
    
    # Hacer request
    response = client.post(
        '/api/sync-books',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    print(f"Status Code: {response.status_code}")
    print()
    
    # Parsear respuesta
    data = response.get_json()
    
    print("Response:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print()
    
    # Validar respuesta
    if response.status_code == 200 and data.get('success'):
        compras = data.get('data', {}).get('COMPRAS')
        ventas = data.get('data', {}).get('VENTAS')
        
        print("RESULTADO:")
        if compras and compras.get('registros'):
            print(f"  COMPRAS: {compras['cantidad']} registros OK")
        else:
            print(f"  COMPRAS: No disponibles")
        
        if ventas and ventas.get('registros'):
            print(f"  VENTAS: {ventas['cantidad']} registros OK")
        else:
            print(f"  VENTAS: No disponibles")
        
        print()
        print("TEST EXITOSO")
        return True
    else:
        print("TEST FALLIDO")
        return False

if __name__ == "__main__":
    success = test_sync_books()
    exit(0 if success else 1)
