#!/usr/bin/env python3
"""
Test local de Playwright contra SII
Para verificar si las credenciales funcionan antes de escalarlas a Render
"""

import logging
from services.sii_scraper import SIIScraper

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_local():
    print("\n" + "="*60)
    print("TEST LOCAL DE PLAYWRIGHT")
    print("="*60)
    
    try:
        scraper = SIIScraper(headless=False)  # False para ver el navegador
        print("\n✓ SIIScraper inicializado correctamente")
        
        # Test 1: Credenciales
        rut = "77956294-8"
        password = "Tr7795629."
        
        print(f"\nTesting credenciales: {rut}")
        result = scraper.test_credentials(rut, password)
        print(f"Resultado: {result}")
        
        if result:
            print("\n✓ Credenciales válidas, intentando fetch de libros...")
            compras, ventas = scraper.fetch_books(rut, password, 11, 2025)
            print(f"Compras: {len(compras) if compras else 0}")
            print(f"Ventas: {len(ventas) if ventas else 0}")
        else:
            print("\n✗ Credenciales inválidas")
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_local()
