#!/usr/bin/env python3
"""
Script para inspeccionar dinámicamente qué elementos existen en la página SPA
"""

from playwright.sync_api import sync_playwright
import time
import json

RUT = "77956294-8"
PASSWORD = "Tr7795629."

def inspect_dynamic():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            # LOGIN
            print("\n=== LOGIN ===")
            login_url = f"https://zeusr.sii.cl/AUT2000/InicioAutenticacion/IngresoRutClave.html?https://www4.sii.cl/consdcvinternetui/#/index"
            page.goto(login_url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_selector("input#rutcntr", timeout=30000)
            page.fill('input#rutcntr', RUT)
            page.fill('input#clave', PASSWORD)
            page.click('button#bt_ingresar')
            page.wait_for_load_state("networkidle", timeout=60000)
            print(f"✓ Login completado")
            
            # ESPERAR A QUE SE CARGUE LA SPA
            print("\n=== ESPERANDO SPA ===")
            time.sleep(5)
            
            # USAR JAVASCRIPT PARA EXTRAER INFO DEL DOM
            print("\n=== INSPECCIONANDO DOM ===")
            
            # Botones con texto "Consultar"
            consultar_buttons = page.eval_on_selector_all(
                "button",
                "buttons => buttons.filter(b => b.textContent.includes('Consultar')).map(b => ({text: b.textContent.trim(), id: b.id, class: b.className}))"
            )
            print(f"Botones 'Consultar': {json.dumps(consultar_buttons, ensure_ascii=False, indent=2)}")
            
            # Botones con texto "Descargar"
            descargar_buttons = page.eval_on_selector_all(
                "button",
                "buttons => buttons.filter(b => b.textContent.toLowerCase().includes('descargar')).map(b => ({text: b.textContent.trim(), id: b.id, class: b.className}))"
            )
            print(f"\nBotones 'Descargar': {json.dumps(descargar_buttons, ensure_ascii=False, indent=2)}")
            
            # Todos los selects
            selects = page.eval_on_selector_all(
                "select",
                "sels => sels.map((s, i) => ({index: i, name: s.name, id: s.id, class: s.className, options: Array.from(s.options).slice(0, 5).map(o => o.textContent)}))"
            )
            print(f"\nSelects: {json.dumps(selects, ensure_ascii=False, indent=2)}")
            
            # Links/buttons con COMPRA/VENTA
            tabs = page.eval_on_selector_all(
                "a, button, [role='tab']",
                "els => els.filter(e => e.textContent.includes('COMPRA') || e.textContent.includes('VENTA')).map(e => ({tag: e.tagName, text: e.textContent.trim(), id: e.id, class: e.className, role: e.getAttribute('role')}))"
            )
            print(f"\nTabs COMPRA/VENTA: {json.dumps(tabs, ensure_ascii=False, indent=2)}")
            
            print("\n" + "="*80)
            print("Presiona Enter para cerrar...")
            input()
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()

if __name__ == "__main__":
    inspect_dynamic()
