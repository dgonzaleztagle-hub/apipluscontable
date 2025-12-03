#!/usr/bin/env python3
"""
Script para inspeccionar la página después de hacer login y consulta
"""

from playwright.sync_api import sync_playwright
import time

RUT = "77956294-8"
PASSWORD = "Tr7795629."
MES = 10
ANO = 2025

def inspect_spa():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # LOGIN
            print("\n=== PASO 1: LOGIN ===")
            login_url = f"https://zeusr.sii.cl/AUT2000/InicioAutenticacion/IngresoRutClave.html?https://www4.sii.cl/consdcvinternetui/#/index"
            page.goto(login_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_selector("input#rutcntr", timeout=30000)
            page.fill('input#rutcntr', RUT)
            page.fill('input#clave', PASSWORD)
            page.click('button#bt_ingresar')
            page.wait_for_load_state("networkidle", timeout=60000)
            print(f"✓ Login completado. URL: {page.url}")
            
            # WAIT FOR SPA
            print("\n=== PASO 2: ESPERANDO SPA ===")
            time.sleep(5)  # Dar tiempo a que se cargue la SPA
            
            # SCREENSHOT
            page.screenshot(path="spa_page.png")
            print("✓ Screenshot guardado")
            
            # BUTTONS
            print("\n=== BOTONES ===")
            buttons = page.query_selector_all("button")
            print(f"Total de botones: {len(buttons)}")
            for i, btn in enumerate(buttons):
                text = (btn.text_content() or "").strip()
                if text:
                    print(f"  [{i}] {text[:60]}")
            
            # SELECTS
            print("\n=== SELECTS ===")
            selects = page.query_selector_all("select")
            print(f"Total de selects: {len(selects)}")
            for i, sel in enumerate(selects):
                print(f"  SELECT [{i}]:")
                options = sel.query_selector_all("option")
                for j, opt in enumerate(options[:5]):
                    print(f"    - {opt.text_content() or '(empty)'}")
                if len(options) > 5:
                    print(f"    ... y {len(options) - 5} más")
            
            # TABS
            print("\n=== TABS/LINKS ===")
            tabs = page.query_selector_all("a, [role='tab'], [role='tablist'] button")
            print(f"Elementos con rol tab: {len(tabs)}")
            for i, tab in enumerate(tabs[:10]):
                text = (tab.text_content() or "").strip()
                if text:
                    print(f"  [{i}] {text[:40]}")
            
            # WAIT AND INTERACT
            print("\n=== INTERACCIÓN ===")
            input("Presiona Enter para continuar (puedes interactuar con la página en el navegador)...")
            
            # DESPUÉS DE INTERACCIÓN
            print("\nBuscando botones después de interacción...")
            buttons = page.query_selector_all("button")
            for i, btn in enumerate(buttons):
                text = (btn.text_content() or "").strip()
                if "Descargar" in text or "descargar" in text:
                    print(f"  [{i}] ENCONTRADO: {text}")
            
        finally:
            browser.close()

if __name__ == "__main__":
    inspect_spa()
