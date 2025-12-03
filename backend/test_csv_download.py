#!/usr/bin/env python3
"""
Script para testear descarga de CSV de COMPRAS del SII
"""

import sys
import logging
from services.sii_scraper import SIIScraper

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Credenciales de prueba
RUT = "77956294-8"
PASSWORD = "Tr7795629."
MES = 10  # Octubre
ANO = 2025

def test_compras_download():
    """Test descarga de COMPRAS en CSV"""
    
    print("\n" + "="*60)
    print("TEST: Descarga de COMPRAS desde SII")
    print("="*60)
    
    try:
        scraper = SIIScraper(headless=False)  # Ver el navegador para debuggear
        
        print(f"\nIntentando obtener COMPRAS...")
        print(f"  RUT: {RUT}")
        print(f"  Mes: {MES}")
        print(f"  Año: {ANO}")
        
        compras = scraper.fetch_books(RUT, PASSWORD, MES, ANO, book_type="COMPRAS")
        
        if compras is None:
            print("\nERROR: fetch_books retorno None")
            return False
        
        print(f"\nOK: Se descargaron {len(compras)} registros de COMPRAS")
        
        if len(compras) > 0:
            print(f"\nPrimer registro:")
            for key, value in list(compras[0].items())[:5]:
                print(f"  {key}: {value}")
            print("  ...")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_compras_download()
    sys.exit(0 if success else 1)
