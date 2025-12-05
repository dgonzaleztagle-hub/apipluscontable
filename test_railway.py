import requests
import json

# URL de Railway
url = "https://apipluscontable-production.up.railway.app/api/sync-books"

# Parámetros
params = {
    "rut": "77956294-8",
    "mes": 10,
    "ano": 2025
}

print("====== PETICIÓN A RAILWAY ======")
print(f"URL: {url}")
print(f"Mes: {params['mes']} (Octubre) - Año: {params['ano']}\n")

try:
    response = requests.get(url, params=params, timeout=120)
    
    print(f"HTTP Status: {response.status_code}\n")
    
    if response.status_code == 200:
        data = response.json()
        
        print("✅ SUCCESS")
        
        if data.get("data", {}).get("COMPRAS"):
            compras = data["data"]["COMPRAS"]
            print(f"COMPRAS: {compras.get('cantidad', 0)} registros")
            print(f"  Monto Total: {compras.get('Monto Total', 'N/A')}")
        else:
            print("COMPRAS: None")
            
        if data.get("data", {}).get("VENTAS"):
            ventas = data["data"]["VENTAS"]
            print(f"VENTAS: {ventas.get('cantidad', 0)} registros")
            print(f"  Monto Total: {ventas.get('Monto Total', 'N/A')}")
        else:
            print("VENTAS: None")
        
        print("\nRESPUESTA COMPLETA:")
        print(json.dumps(data, indent=2))
    else:
        print(f"❌ ERROR: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ ERROR: {e}")
