"""
Script para debuggear por qué no funciona el click en Consultar
"""
import logging
import getpass
from services.sii_scraper import SIIScraper
from playwright.sync_api import sync_playwright

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Credenciales
RUT = "77956294-8"
PASSWORD = getpass.getpass("Ingresa tu contraseña de SII: ")  # Pide contraseña sin mostrarla
MES = 10
ANO = 2025

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # No headless para ver qué pasa
    page = browser.new_page()
    
    try:
        scraper = SIIScraper(headless=False, timeout=60000)
        
        # Navegar a login
        page.goto(f"{scraper.LOGIN_URL}?{scraper.DESTINATION_URL}", wait_until="networkidle", timeout=60000)
        logger.info("✓ Página de login cargada")
        
        # Login
        page.locator("input#rutcntr").fill(RUT)
        page.locator("input#clave").fill(PASSWORD)
        page.locator("button#bt_ingresar").click()
        
        logger.info("Esperando redirección después del login...")
        page.wait_for_url("**/consdcvinternetui/**", timeout=30000)
        logger.info("✓ Login completado")
        
        # Esperar a que cargue la página
        page.wait_for_timeout(3000)
        
        # Verificar que los selects estén disponibles
        selects = page.locator("select")
        select_count = selects.count()
        logger.info(f"Selects encontrados: {select_count}")
        
        if select_count >= 2:
            # Seleccionar mes
            logger.info(f"Seleccionando mes: {MES}")
            mes_select = selects.nth(0)
            
            # Ver opciones disponibles
            options = mes_select.locator("option")
            logger.info(f"Opciones en primer select: {options.count()}")
            for i in range(min(5, options.count())):
                opt_text = options.nth(i).inner_text()
                opt_value = options.nth(i).get_attribute("value")
                logger.info(f"  Opción {i}: value='{opt_value}', text='{opt_text}'")
            
            # Seleccionar el mes
            mes_select.select_option(str(MES))
            logger.info(f"✓ Mes {MES} seleccionado")
            page.wait_for_timeout(800)
            
            # Seleccionar año
            logger.info(f"Seleccionando año: {ANO}")
            ano_select = selects.nth(1)
            ano_select.select_option(str(ANO))
            logger.info(f"✓ Año {ANO} seleccionado")
            page.wait_for_timeout(800)
        
        # AHORA BUSCAR EL BOTÓN CONSULTAR
        logger.info("\n=== BUSCANDO BOTÓN CONSULTAR ===")
        
        # Todos los botones
        all_buttons = page.locator("button")
        button_count = all_buttons.count()
        logger.info(f"Total de botones en página: {button_count}")
        
        for i in range(button_count):
            btn = all_buttons.nth(i)
            text = btn.inner_text()
            visible = btn.is_visible()
            enabled = btn.is_enabled()
            logger.info(f"  Botón {i}: text='{text}', visible={visible}, enabled={enabled}")
        
        # Buscar específicamente "Consultar"
        logger.info("\nBuscando botón con texto 'Consultar'...")
        consultar_locator = page.locator("button").filter(has_text="Consultar")
        consultar_count = consultar_locator.count()
        logger.info(f"Botones con 'Consultar': {consultar_count}")
        
        if consultar_count > 0:
            consultar_btn = consultar_locator.first
            logger.info(f"Botón encontrado!")
            logger.info(f"  - Visible: {consultar_btn.is_visible()}")
            logger.info(f"  - Enabled: {consultar_btn.is_enabled()}")
            logger.info(f"  - Texto: {consultar_btn.inner_text()}")
            
            # Intentar hacerle scroll y clic
            logger.info("\nIntentando hacer clic...")
            consultar_btn.scroll_into_view_if_needed()
            page.wait_for_timeout(500)
            
            logger.info("Haciendo clic en Consultar...")
            consultar_btn.click()
            logger.info("✓ Clic realizado")
            
            # Esperar cambios
            page.wait_for_timeout(4000)
            logger.info("✓ Esperando 4 segundos para carga de resultados...")
            
            # Verificar si hay cambios en el HTML
            html = page.content()
            logger.info(f"HTML size después de clic: {len(html)} chars")
            
            # Buscar links con data URI
            download_links = page.locator('a[href*="data:"]')
            download_count = download_links.count()
            logger.info(f"\nLinks con data URI encontrados: {download_count}")
            
            if download_count > 0:
                href = download_links.first.get_attribute("href")
                logger.info(f"Primer link: {href[:100]}...")
            
        else:
            logger.error("NO se encontró botón con texto 'Consultar'")
            
            # Buscar con otros patrones
            logger.info("\nIntentando búsquedas alternativas...")
            
            # Input type submit
            submits = page.locator("input[type='submit']")
            logger.info(f"Input submit: {submits.count()}")
            
            # Links que podrían ser botones
            links = page.locator("a")
            logger.info(f"Total links: {links.count()}")
            for i in range(min(10, links.count())):
                text = links.nth(i).inner_text()
                if text.strip():
                    logger.info(f"  Link {i}: {text}")
        
        page.wait_for_timeout(5000)
        
    except Exception as e:
        logger.error(f"ERROR: {e}", exc_info=True)
    
    finally:
        # Dejar abierto para ver
        logger.info("\n=== Presiona Enter en la consola para cerrar el navegador ===")
        input()
        browser.close()
