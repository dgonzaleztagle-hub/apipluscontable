#!/usr/bin/env python3
"""
Script para capturar clicks y eventos del usuario para replicarlos después
"""

from playwright.sync_api import sync_playwright
import time
import json

RUT = "77956294-8"
PASSWORD = "Tr7795629."

def capture_user_interaction():
    """Captura interacciones del usuario para replicarlas"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Listener para capturar clicks
        clicks = []
        def handle_click(element):
            clicks.append({
                'type': 'click',
                'selector': element,
                'timestamp': time.time()
            })
        
        page.on("console", lambda msg: print(f"[CONSOLE] {msg.text}"))
        
        try:
            # LOGIN
            print("\n" + "="*80)
            print("PASO 1: HACIENDO LOGIN")
            print("="*80)
            
            login_url = f"https://zeusr.sii.cl/AUT2000/InicioAutenticacion/IngresoRutClave.html?https://www4.sii.cl/consdcvinternetui/#/index"
            page.goto(login_url, wait_until="domcontentloaded", timeout=30000)
            
            page.wait_for_selector("input#rutcntr", timeout=30000)
            print("✓ Formulario de login visible")
            
            page.fill('input#rutcntr', RUT)
            print(f"✓ RUT ingresado: {RUT}")
            
            page.fill('input#clave', PASSWORD)
            print(f"✓ Contraseña ingresada")
            
            page.click('button#bt_ingresar')
            print("✓ Botón de login clickeado")
            
            page.wait_for_load_state("networkidle", timeout=60000)
            print(f"✓ Login completado. URL: {page.url}")
            
            # ESPERAR A SPA
            print("\n" + "="*80)
            print("PASO 2: ESPERANDO SPA")
            print("="*80)
            
            time.sleep(5)
            print("✓ SPA debería estar cargada")
            
            # INYECTAR LOGGER DE EVENTOS
            print("\n" + "="*80)
            print("PASO 3: INTERCEPTANDO EVENTOS")
            print("="*80)
            
            page.evaluate("""
            window.__events = [];
            
            // Capturar clicks
            document.addEventListener('click', (e) => {
                const target = e.target;
                const info = {
                    type: 'click',
                    tag: target.tagName,
                    text: target.textContent.substring(0, 50),
                    id: target.id,
                    class: target.className,
                    xpath: getElementXPath(target),
                    timestamp: new Date().toISOString()
                };
                window.__events.push(info);
                console.log('EVENTO_CAPTURADO:', JSON.stringify(info));
            }, true);
            
            // Capturar cambios en inputs
            document.addEventListener('change', (e) => {
                const target = e.target;
                const info = {
                    type: 'change',
                    tag: target.tagName,
                    name: target.name,
                    value: target.value,
                    id: target.id,
                    timestamp: new Date().toISOString()
                };
                window.__events.push(info);
                console.log('EVENTO_CAPTURADO:', JSON.stringify(info));
            }, true);
            
            // Helper para XPath
            function getElementXPath(element) {
                if (element.id !== '')
                    return "//*[@id='" + element.id + "']";
                if (element === document.body)
                    return element.tagName.toLowerCase();
                
                var ix = 0;
                var siblings = element.parentNode.childNodes;
                for (var i = 0; i < siblings.length; i++) {
                    var sibling = siblings[i];
                    if (sibling === element)
                        return getElementXPath(element.parentNode) + "/" + element.tagName.toLowerCase() + "[" + (ix + 1) + "]";
                    if (sibling.nodeType === 1 && sibling.tagName.toLowerCase() === element.tagName.toLowerCase())
                        ix++;
                }
            }
            """)
            
            print("✓ Event listeners inyectados")
            print("\n🔴 AHORA INTERACTÚA CON LA PÁGINA:")
            print("   1. Cambia de mes/año si es necesario")
            print("   2. Haz click en 'Consultar'")
            print("   3. Haz click en 'Descargar Detalles'")
            print("   4. Presiona Enter cuando termines\n")
            
            input("👉 Presiona Enter cuando hayas terminado de interactuar...")
            
            # RECUPERAR EVENTOS CAPTURADOS
            print("\n" + "="*80)
            print("PASO 4: EVENTOS CAPTURADOS")
            print("="*80)
            
            events = page.evaluate("() => window.__events")
            
            print(f"\nTotal de eventos capturados: {len(events)}")
            print("\nDetalle de eventos:")
            for i, event in enumerate(events, 1):
                print(f"\n[{i}] {event['type'].upper()}")
                print(f"    Tag: {event['tag']}")
                if event['type'] == 'click':
                    print(f"    Texto: {event['text']}")
                    print(f"    ID: {event['id']}")
                    print(f"    Class: {event['class']}")
                elif event['type'] == 'change':
                    print(f"    Valor: {event['value']}")
            
            # GUARDAR JSON
            with open('captured_events.json', 'w', encoding='utf-8') as f:
                json.dump(events, f, ensure_ascii=False, indent=2)
            print("\n✓ Eventos guardados en captured_events.json")
            
            print("\nPresiona Enter para cerrar...")
            input()
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()

if __name__ == "__main__":
    capture_user_interaction()
