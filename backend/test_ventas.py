#!/usr/bin/env python
"""
Test para descargar VENTAS desde SII
"""
import logging
from services.sii_scraper import SIIScraper

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)

def test_ventas():
    print("=" * 60)
    print("TEST: Descarga de VENTAS desde SII")
    print("=" * 60)
    print()
    
    rut = "77956294-8"
    password = "Tr7795629."
    
    try:
        scraper = SIIScraper(headless=True, timeout=60000)
        
        print("Intentando obtener VENTAS...")
        print(f"  RUT: {rut}")
        print(f"  Mes: 10")
        print(f"  Año: 2025")
        print()
        
        records = scraper.fetch_books(rut, password, mes=10, ano=2025, book_type="VENTAS")
        
        if records is None:
            print("❌ ERROR: fetch_books retornó None")
            return False
        
        print(f"✅ ÉXITO: Se descargaron {len(records)} registros de VENTAS")
        
        if len(records) > 0:
            print()
            print("Primer registro:")
            for key, value in list(records[0].items())[:5]:
                print(f"  {key}: {value}")
            print("  ...")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ventas()
    exit(0 if success else 1)
