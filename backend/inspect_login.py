#!/usr/bin/env python3
"""
Script para inspeccionar la estructura HTML de la página de login del SII
"""

import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def inspect_login_page():
    """Inspeccionar la página de login"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-dev-shm-usage',
            '--no-sandbox',
            '--disable-gpu',
        ])
        page = browser.new_page()
        
        try:
            print("\nNaveando a la página de login...")
            page.goto("https://zeusr.sii.cl/AUT2000/InicioAutenticacion/IngresoRutClave.html", 
                     wait_until="domcontentloaded", timeout=30000)
            
            print("✓ Página cargada")
            print(f"URL: {page.url}")
            
            # Esperar un poco para que se cargue el contenido
            page.wait_for_timeout(3000)
            
            # Buscar inputs y buttons
            print("\nSearching for inputs...")
            inputs = page.query_selector_all("input")
            print(f"Found {len(inputs)} inputs:")
            for i, inp in enumerate(inputs):
                name = inp.get_attribute("name") or "NO NAME"
                type_attr = inp.get_attribute("type") or "NO TYPE"
                id_attr = inp.get_attribute("id") or "NO ID"
                placeholder = inp.get_attribute("placeholder") or "NO PLACEHOLDER"
                print(f"  [{i}] name={name}, type={type_attr}, id={id_attr}, placeholder={placeholder}")
            
            print("\nSearching for buttons...")
            buttons = page.query_selector_all("button")
            print(f"Found {len(buttons)} buttons:")
            for i, btn in enumerate(buttons):
                text = btn.text_content() or "NO TEXT"
                type_attr = btn.get_attribute("type") or "NO TYPE"
                id_attr = btn.get_attribute("id") or "NO ID"
                print(f"  [{i}] type={type_attr}, id={id_attr}, text={text[:50]}")
            
            print("\nSearching for forms...")
            forms = page.query_selector_all("form")
            print(f"Found {len(forms)} forms")
            for i, form in enumerate(forms):
                id_attr = form.get_attribute("id") or "NO ID"
                name = form.get_attribute("name") or "NO NAME"
                print(f"  [{i}] id={id_attr}, name={name}")
            
            # Guardar screenshot
            print("\nGuardando screenshot...")
            page.screenshot(path="login_page_inspect.png")
            print("✓ Screenshot guardado como login_page_inspect.png")
            
            # Obtener HTML parcial
            print("\nHTML del formulario (primeros 1500 chars):")
            html = page.content()
            # Buscar form
            form_start = html.find("<form")
            if form_start >= 0:
                form_end = html.find("</form>", form_start) + len("</form>")
                print(html[form_start:min(form_end, form_start + 1500)])
            else:
                print("(form tag not found)")
                
        finally:
            browser.close()

if __name__ == "__main__":
    inspect_login_page()
