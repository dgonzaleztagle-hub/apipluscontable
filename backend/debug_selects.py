"""
Script para examinar todos los selects en la página
"""
import logging
import getpass
from playwright.sync_api import sync_playwright

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
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
        logger.info("✓ Página de login cargada")
        
        page.locator("input#rutcntr").fill(RUT)
        page.locator("input#clave").fill(PASSWORD)
        page.locator("button#bt_ingresar").click()
        
        page.wait_for_url("**/consdcvinternetui/**", timeout=30000)
        logger.info("✓ Login completado")
        
        page.wait_for_timeout(3000)
        
        # Examinar todos los selects
        logger.info("\n=== EXAMINANDO TODOS LOS SELECTS ===\n")
        
        selects = page.locator("select")
        select_count = selects.count()
        logger.info(f"Total de selects: {select_count}\n")
        
        for i in range(select_count):
            select = selects.nth(i)
            name = select.get_attribute("name") or "sin-name"
            ng_model = select.get_attribute("ng-model") or "sin-ng-model"
            classes = select.get_attribute("class") or ""
            
            logger.info(f"--- SELECT #{i} ---")
            logger.info(f"  name: {name}")
            logger.info(f"  ng-model: {ng_model}")
            logger.info(f"  class: {classes}")
            
            options = select.locator("option")
            option_count = options.count()
            logger.info(f"  Opciones: {option_count}")
            
            for j in range(min(5, option_count)):
                opt = options.nth(j)
                text = opt.inner_text()
                value = opt.get_attribute("value") or ""
                logger.info(f"    [{j}] value='{value}' → '{text}'")
            
            if option_count > 5:
                logger.info(f"    ... y {option_count - 5} más")
            
            logger.info("---")
        
        # Examinar botones
        logger.info("\n=== EXAMINANDO BOTONES ===\n")
        buttons = page.locator("button")
        button_count = buttons.count()
        
        for i in range(button_count):
            btn = buttons.nth(i)
            text = btn.inner_text().strip()
            if text:  # Solo si tiene texto
                visible = btn.is_visible()
                enabled = btn.is_enabled()
                logger.info(f"[{i}] '{text}' - visible={visible}, enabled={enabled}")
        
        logger.info("\n=== Presiona Enter para cerrar ===")
        input()
        
    except Exception as e:
        logger.error(f"ERROR: {e}", exc_info=True)
    finally:
        browser.close()
