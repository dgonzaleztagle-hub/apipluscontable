#!/usr/bin/env python3
"""
Script para inspeccionar el formulario de login en detalle
"""

from playwright.sync_api import sync_playwright

def inspect_login_form():
    """Inspeccionar formulario de login"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            page.goto("https://zeusr.sii.cl/AUT2000/InicioAutenticacion/IngresoRutClave.html", 
                     wait_until="domcontentloaded", timeout=30000)
            
            # Obtener el HTML del formulario
            form_html = page.query_selector("form#myform").inner_html()
            
            print("FORM HTML:")
            print(form_html)
            print("\n" + "="*80 + "\n")
            
            # Obtener todos los hidden inputs
            print("HIDDEN INPUTS:")
            hiddens = page.query_selector_all("input[type='hidden']")
            for h in hiddens:
                name = h.get_attribute("name") or "NO NAME"
                value = h.get_attribute("value") or "(empty)"
                print(f"  {name} = {value}")
            
            print("\n" + "="*80 + "\n")
            
            # Verificar URL de la forma
            form = page.query_selector("form#myform")
            action = form.get_attribute("action")
            method = form.get_attribute("method")
            print(f"FORM ACTION: {action}")
            print(f"FORM METHOD: {method}")
            
        finally:
            browser.close()

if __name__ == "__main__":
    inspect_login_form()
