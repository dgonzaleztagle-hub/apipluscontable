import requests
import json
import time

BASE_URL = "https://apipluscontable.onrender.com"

print("=" * 60)
print("TEST 1: Health Check")
print("=" * 60)

response = requests.get(f"{BASE_URL}/health")
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
print()

print("=" * 60)
print("TEST 2: Sync Books (COMPRAS + VENTAS en paralelo)")
print("=" * 60)

payload = {
    "rut": "77956294-8",
    "password": "Tr7795629.",
    "mes": 12,
    "ano": 2025
}

print(f"Request: POST {BASE_URL}/api/sync-books")
print(f"Payload: {json.dumps(payload, indent=2)}")
print("\nEsperando respuesta (puede tardar 30-40 segundos)...")

start_time = time.time()
try:
    response = requests.post(
        f"{BASE_URL}/api/sync-books",
        json=payload,
        timeout=120
    )
    elapsed = time.time() - start_time
    
    print(f"\n✅ Status: {response.status_code}")
    print(f"⏱️  Tiempo total: {elapsed:.1f} segundos")
    
    data = response.json()
    
    if response.status_code == 200:
        print("\n✅ ÉXITO - Respuesta completa:")
        print(json.dumps(data, indent=2))
        
        if "data" in data:
            compras = data["data"].get("COMPRAS", {})
            ventas = data["data"].get("VENTAS", {})
            
            print(f"\n📊 RESUMEN:")
            print(f"   COMPRAS: {len(compras.get('documents', []))} documentos descargados")
            print(f"   VENTAS: {len(ventas.get('documents', []))} documentos descargados")
    else:
        print("\n❌ ERROR - Respuesta:")
        print(json.dumps(data, indent=2))
        
except requests.exceptions.Timeout:
    print(f"❌ TIMEOUT después de 120 segundos")
except Exception as e:
    print(f"❌ ERROR: {str(e)}")

print("\n" + "=" * 60)
