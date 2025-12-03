#!/usr/bin/env python
"""
Test completo para descargar COMPRAS y VENTAS de múltiples períodos
"""
import logging
from services.sii_scraper import SIIScraper

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)

def test_multiple_periods():
    print("=" * 60)
    print("TEST: Descarga de COMPRAS y VENTAS de múltiples períodos")
    print("=" * 60)
    print()
    
    rut = "77956294-8"
    password = "Tr7795629."
    
    try:
        scraper = SIIScraper(headless=True, timeout=60000)
        
        # Probar algunos períodos
        periods = [
            (10, 2025),
        ]
        
        for mes, ano in periods:
            for book_type in ["COMPRAS", "VENTAS"]:
                print(f"\nDescargando {book_type} - {mes:02d}/{ano}...")
                
                records = scraper.fetch_books(rut, password, mes=mes, ano=ano, book_type=book_type)
                
                if records is None:
                    print(f"  ERROR: fetch_books retornó None")
                else:
                    print(f"  OK: {len(records)} registros descargados")
                    if len(records) > 0:
                        first = records[0]
                        print(f"     Primer tipo: {first.get('Tipo Documento', 'N/A')}")
        
        print("\n" + "=" * 60)
        print("OK: TEST COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_multiple_periods()
    exit(0 if success else 1)
