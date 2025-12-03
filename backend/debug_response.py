"""
Debug: Capturar la respuesta JSON del backend
"""
import logging
import json
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

RUT = "77956294-8"
PASSWORD = "Tr7795629."
LOGIN_URL = "https://zeusr.sii.cl/AUT2000/InicioAutenticacion/IngresoRutClave.html"
DESTINATION_URL = "https://www4.sii.cl/consdcvinternetui/#/index"

responses_captured = []

def handle_response(response):
    """Capturar todas las respuestas"""
    if "facadeService" in response.url:
        logger.info(f"\n📥 RESPUESTA CAPTURADA: {response.url}")
        logger.info(f"   Status: {response.status}")
        logger.info(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
        
        try:
            # Intentar parsear como JSON
            body = response.json()
            logger.info(f"   JSON válido. Keys: {list(body.keys()) if isinstance(body, dict) else 'array'}")
            responses_captured.append(body)
            
            # Mostrar primeras líneas
            logger.info(f"   Contenido: {json.dumps(body)[:500]}...")
            
        except:
            # Si no es JSON, mostrar como texto
            try:
                body = response.text()
                logger.info(f"   Texto: {body[:200]}...")
            except:
                logger.info("   No se pudo leer el contenido")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    # Registrar el manejador ANTES de hacer login
    page.on("response", handle_response)
    
    try:
        # Login
        page.goto(f"{LOGIN_URL}?{DESTINATION_URL}", wait_until="networkidle", timeout=60000)
        page.locator("input#rutcntr").fill(RUT)
        page.locator("input#clave").fill(PASSWORD)
        page.locator("button#bt_ingresar").click()
        page.wait_for_url("**/consdcvinternetui/**", timeout=30000)
        page.wait_for_timeout(3000)
        
        logger.info("✓ Login completado\n")
        
        # Seleccionar mes y año
        selects = page.locator("select")
        selects.nth(1).select_option("10")  # Mes
        page.wait_for_timeout(500)
        selects.nth(2).select_option("2025")  # Año
        page.wait_for_timeout(500)
        
        logger.info("✓ Mes y año seleccionados")
        logger.info("Clickeando Consultar... (observa las respuestas)\n")
        
        # Clickear
        consultar_btn = page.locator("button").filter(has_text="Consultar").first
        consultar_btn.click()
        
        # Esperar a que lleguen respuestas
        page.wait_for_timeout(5000)
        
        logger.info(f"\n\n=== RESUMEN ===")
        logger.info(f"Respuestas capturadas: {len(responses_captured)}")
        
        if responses_captured:
            logger.info("\nÚltima respuesta:")
            logger.info(json.dumps(responses_captured[-1], indent=2)[:1000])
        
        logger.info("\n\n>>> El navegador sigue abierto. Presiona Enter para cerrar. <<<")
        input()
        
    except Exception as e:
        logger.error(f"ERROR: {e}", exc_info=True)
    finally:
        browser.close()
