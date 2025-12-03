#!/usr/bin/env python3
"""
Script para inspeccionar la página de libros después del login
"""

import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Credenciales
RUT = "77956294-8"
PASSWORD = "Tr7795629."

def inspect_after_login():
    """Inspeccionar la página después del login"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-gpu',
        ])
        page = browser.new_page()
        
        try:
            # LOGIN
            print("\n=== PASO 1: LOGIN ===")
            page.goto("https://zeusr.sii.cl/AUT2000/InicioAutenticacion/IngresoRutClave.html", 
                     wait_until="domcontentloaded", timeout=30000)
            print("✓ Página de login cargada")
            
            page.wait_for_selector("input#rutcntr", timeout=30000)
            page.fill('input#rutcntr', RUT)
            page.fill('input#clave', PASSWORD)
            page.click('button#bt_ingresar')
            print("✓ Formulario enviado")
            
            page.wait_for_load_state("networkidle", timeout=60000)
            print(f"✓ Login completado. URL: {page.url}")
            
            # Esperar un poco más
            page.wait_for_timeout(3000)
            
            # INSPECCIONAR PÁGINA DE LIBROS
            print("\n=== PASO 2: INSPECCIONAR PÁGINA DE LIBROS ===")
            print(f"URL actual: {page.url}")
            
            html = page.content()
            print(f"HTML length: {len(html)} chars")
            print(f"¿Contiene 'REGISTRO DE COMPRAS'?: {'REGISTRO DE COMPRAS' in html}")
            print(f"¿Contiene 'consdcvinternetui'?: {'consdcvinternetui' in html}")
            
            # Buscar iframes
            iframes = page.query_selector_all("iframe")
            print(f"\nFound {len(iframes)} iframes")
            
            # Buscar todos los selects
            selects = page.query_selector_all("select")
            print(f"\nFound {len(selects)} selects:")
            for i, sel in enumerate(selects):
                name = sel.get_attribute("name") or "NO NAME"
                id_attr = sel.get_attribute("id") or "NO ID"
                print(f"  [{i}] name={name}, id={id_attr}")
            
            # Buscar todos los botones
            buttons = page.query_selector_all("button")
            print(f"\nFound {len(buttons)} buttons:")
            for i, btn in enumerate(buttons[:10]):  # Primeros 10
                text = btn.text_content() or "NO TEXT"
                type_attr = btn.get_attribute("type") or "NO TYPE"
                print(f"  [{i}] type={type_attr}, text={text[:40]}")
            
            # Buscar "Consultar"
            try:
                consultar_btn = page.query_selector("button:has-text('Consultar')")
                if consultar_btn:
                    print(f"\n✓ Encontré botón 'Consultar'")
                else:
                    print(f"\n✗ NO encontré botón 'Consultar'")
            except:
                print(f"\n✗ Error buscando botón 'Consultar'")
            
            # Buscar "Descargar Detalles"
            try:
                descargar_btn = page.query_selector("button:has-text('Descargar Detalles')")
                if descargar_btn:
                    print(f"✓ Encontré botón 'Descargar Detalles'")
                else:
                    print(f"✗ NO encontré botón 'Descargar Detalles'")
            except:
                print(f"✗ Error buscando botón 'Descargar Detalles'")
            
            # Screenshot
            print("\nGuardando screenshot...")
            page.screenshot(path="after_login.png")
            print("✓ Screenshot guardado")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()

if __name__ == "__main__":
    inspect_after_login()
