#!/usr/bin/env python3
"""
Test real del endpoint de sync-sii en Render
Para verificar si realmente funciona con Playwright
"""

import requests
import json
from datetime import datetime

API_URL = "https://apipluscontable.onrender.com"

def test_health():
    """Test health endpoint"""
    print("\n" + "="*60)
    print("TEST 1: Health Check")
    print("="*60)
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

def test_sync_sii():
    """Test sync-sii endpoint con credenciales reales"""
    print("\n" + "="*60)
    print("TEST 2: Sync SII (REAL DATA)")
    print("="*60)
    
    payload = {
        "rut": "77956294-8",
        "password": "Tr7795629.",
        "mes": 11,
        "ano": 2025
    }
    
    print(f"Enviando payload: {json.dumps(payload, indent=2)}")
    print("\nEsperando respuesta del SII... (puede tardar 30+ segundos)")
    
    try:
        response = requests.post(
            f"{API_URL}/api/sync-sii",
            json=payload,
            timeout=120  # 2 minutos de timeout
        )
        print(f"\nStatus: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
        
        # Verificar si es realmente data o mock
        data = response.json()
        if 'data' in data and 'note' in data['data']:
            if 'mock' in data['data']['note'].lower():
                print("\n⚠️  ADVERTENCIA: Retornó MOCK DATA, no datos reales del SII")
                return False
        
        if response.status_code == 200 and data.get('success'):
            compras = len(data.get('data', {}).get('compras', []))
            ventas = len(data.get('data', {}).get('ventas', []))
            print(f"\n✓ SUCCESS: Se obtuvieron {compras} compras y {ventas} ventas")
            return True
        else:
            print(f"\n✗ FAILED: {data.get('error', 'Unknown error')}")
            return False
            
    except requests.Timeout:
        print(f"\n✗ TIMEOUT: SII no respondió en 120 segundos")
        print("   Posible causa: SII está lento o nos bloqueó")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        return False

def test_test_connection():
    """Test endpoint de test-connection"""
    print("\n" + "="*60)
    print("TEST 3: Test Connection")
    print("="*60)
    
    payload = {
        "rut": "77956294-8",
        "password": "Tr7795629."
    }
    
    print(f"Testeando credenciales: {payload['rut']}")
    
    try:
        response = requests.post(
            f"{API_URL}/api/test-connection",
            json=payload,
            timeout=120
        )
        print(f"Status: {response.status_code}")
        print(f"Response:\n{json.dumps(response.json(), indent=2)}")
        return response.status_code in [200, 401]
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False

if __name__ == '__main__':
    print("\n" + "="*60)
    print("TEST DE PRODUCCIÓN - RENDER.COM")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*60)
    
    results = {
        'health': test_health(),
        'test_connection': test_test_connection(),
        'sync_sii': test_sync_sii()
    }
    
    print("\n" + "="*60)
    print("RESUMEN DE RESULTADOS")
    print("="*60)
    for test, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test}: {status}")
    
    all_pass = all(results.values())
    print(f"\nGlobal: {'✓ TODO OK' if all_pass else '✗ PROBLEMAS DETECTADOS'}")
