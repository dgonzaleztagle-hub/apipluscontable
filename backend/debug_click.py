"""
Debug: Ver qué pasa después de clickear Consultar
"""
import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

RUT = "77956294-8"
PASSWORD = "Tr7795629."
LOGIN_URL = "https://zeusr.sii.cl/AUT2000/InicioAutenticacion/IngresoRutClave.html"
DESTINATION_URL = "https://www4.sii.cl/consdcvinternetui/#/index"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    try:
        # Login
        page.goto(f"{LOGIN_URL}?{DESTINATION_URL}", wait_until="networkidle", timeout=60000)
        page.locator("input#rutcntr").fill(RUT)
        page.locator("input#clave").fill(PASSWORD)
        page.locator("button#bt_ingresar").click()
        page.wait_for_url("**/consdcvinternetui/**", timeout=30000)
        page.wait_for_timeout(3000)
        
        logger.info("✓ Login completado")
        
        # Seleccionar mes y año
        selects = page.locator("select")
        selects.nth(1).select_option("10")  # Mes
        page.wait_for_timeout(500)
        selects.nth(2).select_option("2025")  # Año
        page.wait_for_timeout(500)
        
        logger.info("✓ Mes y año seleccionados")
        
        # CLICKEAR CONSULTAR y OBSERVAR
        logger.info("\n=== ANTES DE CLICKEAR ===")
        html_before = page.content()
        logger.info(f"HTML size: {len(html_before)}")
        
        # Registrar network requests
        def handle_response(response):
            if "data" in response.url.lower() or "download" in response.url.lower() or response.status != 200:
                logger.info(f"Response: {response.status} - {response.url}")
        
        page.on("response", handle_response)
        
        # Clickear
        logger.info("\nClickeando Consultar...")
        consultar_btn = page.locator("button").filter(has_text="Consultar").first
        consultar_btn.click()
        
        logger.info("Esperando eventos de red/Angular...")
        page.wait_for_timeout(5000)
        
        logger.info("\n=== DESPUES DE CLICKEAR ===")
        logger.info("El navegador está ABIERTO. Observa y cuando hayas visto todo, presiona Enter.")
        logger.info("Verifica si aparecen:")
        logger.info("  - Un modal o popup")
        logger.info("  - Nuevos botones (Descargar, Descargar Detalles)")
        logger.info("  - Contenido nuevo en la página")
        logger.info("")
        
        input(">>> PRESIONA ENTER cuando hayas observado todo <<<")
        
        html_after = page.content()
        logger.info(f"\nHTML size: {len(html_after)}")
        logger.info(f"Diferencia: {len(html_after) - len(html_before)} chars")
        
        # Buscar datos URI
        if "data:" in html_after:
            logger.info("✓ Encontré 'data:' en el HTML")
            # Buscar posición y contexto
            idx = html_after.find("data:")
            logger.info(f"Contexto: ...{html_after[max(0, idx-50):idx+100]}...")
        
        # Buscar links
        links = page.locator('a[href*="data:"]')
        logger.info(f"\nLinks con data URI: {links.count()}")
        
        # Buscar botones Descargar
        download_btns = page.locator("button").filter(has_text="Descargar")
        logger.info(f"Botones 'Descargar': {download_btns.count()}")
        
        # Ver todos los botones
        logger.info("\nTodos los botones visibles:")
        all_btns = page.locator("button")
        for i in range(all_btns.count()):
            btn = all_btns.nth(i)
            text = btn.inner_text().strip()
            if text and btn.is_visible():
                logger.info(f"  - {text}")
        
        logger.info("\n=== Presiona Enter para cerrar ===")
        input()
        
    except Exception as e:
        logger.error(f"ERROR: {e}", exc_info=True)
    finally:
        browser.close()
