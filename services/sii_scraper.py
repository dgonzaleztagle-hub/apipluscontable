"""
SII Scraper - Módulo para scrapear libros de compras y ventas del SII
"""

import logging
import tempfile
import os
import csv
from io import StringIO

# Configurar logger PRIMERO
logger = logging.getLogger(__name__)

try:
    from playwright.sync_api import sync_playwright, Download
    try:
        from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    except ImportError:
        PlaywrightTimeoutError = TimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Playwright no disponible: {e}")
    PLAYWRIGHT_AVAILABLE = False
    PlaywrightTimeoutError = TimeoutError
    
from typing import Optional, Tuple, List, Dict, Any


class SIIScraper:
    """Scraper para obtener libros de compras y ventas del SII"""
    
    # URLs del SII
    LOGIN_URL = "https://zeusr.sii.cl/AUT2000/InicioAutenticacion/IngresoRutClave.html"
    AUTH_URL = "https://zeusr.sii.cl/cgi_AUT2000/CAutInicio.cgi"
    # Nueva URL de la SPA de consulta de libros
    BOOKS_URL = "https://www4.sii.cl/consdcvinternetui/#/index"
    BASE_API_URL = "https://www4.sii.cl/consdcvinternetui/services/data/facadeService/getResumen"
    
    def __init__(self, headless: bool = True, timeout: int = 60000):
        """
        Inicializar el scraper
        
        Args:
            headless: Ejecutar navegador sin interfaz gráfica
            timeout: Timeout en milisegundos para operaciones
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright no está instalado. Ejecuta: pip install playwright && playwright install chromium")
            
        self.headless = headless
        self.timeout = timeout
    
    def test_credentials(self, rut: str, password: str) -> bool:
        """
        Testear si las credenciales son válidas
        
        Args:
            rut: RUT sin formato (ej: "77956294-8")
            password: Contraseña del SII
            
        Returns:
            True si las credenciales son válidas, False en caso contrario
        """
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright no disponible")
            return False
            
        try:
            logger.info(f"Testeando credenciales para RUT: {rut}")
            
            with sync_playwright() as p:
                # Usar Chrome en lugar de Chromium para evitar detección de bot
                browser = p.chromium.launch(
                    headless=self.headless,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-gpu',
                        '--disable-web-resources',
                        '--disable-extensions',
                    ]
                )
                page = browser.new_page()
                
                # Anti-bot stealth
                page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false,
                    });
                """)
                
                try:
                    # Ir a página de login
                    page.goto(self.LOGIN_URL, wait_until="networkidle", timeout=self.timeout)
                    logger.info("Página de login cargada")
                    
                    # Llenar formulario de login
                    page.fill('input[name="rutclave"]', rut)
                    page.fill('input[name="password"]', password)
                    
                    # Hacer click en botón de login
                    page.click('button[type="submit"]')
                    
                    # Esperar respuesta
                    page.wait_for_load_state("networkidle", timeout=self.timeout)
                    
                    # Verificar si hay error de autenticación
                    if "Usuario no existe" in page.content() or "Clave incorrecta" in page.content():
                        logger.warning(f"Credenciales inválidas para RUT: {rut}")
                        return False
                    
                    logger.info(f"Credenciales válidas para RUT: {rut}")
                    return True
                    
                finally:
                    browser.close()
                    
        except PlaywrightTimeoutError:
            logger.error("Timeout al testear credenciales")
            return False
        except Exception as e:
            logger.error(f"Error al testear credenciales: {str(e)}")
            return False
    
    def fetch_books(self, rut: str, password: str, mes: int, ano: int, book_type: str = "COMPRAS") -> Optional[List[Dict[str, Any]]]:
        """
        Obtener libros del SII (COMPRAS o VENTAS)
        
        Args:
            rut: RUT sin formato (ej: "77956294-8")
            password: Contraseña del SII
            mes: Mes (1-12)
            ano: Año (YYYY)
            book_type: "COMPRAS" o "VENTAS" (default: COMPRAS)
            
        Returns:
            Lista de registros del libro o None si hay error
        """
        try:
            logger.info(f"Iniciando fetch de {book_type} para RUT: {rut}, mes: {mes}, año: {ano}")
            
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=self.headless,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-gpu',
                    ]
                )
                context = browser.new_context()
                page = context.new_page()
                
                # Anti-bot stealth
                page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false,
                    });
                """)
                
                try:
                    # Realizar login
                    if not self._login(page, rut, password):
                        logger.error("Fallo en login")
                        return None
                    
                    # Obtener libros (solo COMPRAS por ahora)
                    books = self._fetch_book_data(page, book_type, mes, ano)
                    
                    logger.info(f"{book_type} obtenidos: {len(books) if books else 0} registros")
                    
                    return books
                    
                finally:
                    browser.close()
                    
        except Exception as e:
            logger.error(f"Error al obtener {book_type}: {str(e)}", exc_info=True)
            return None
    
    def _login(self, page, rut: str, password: str) -> bool:
        """
        Realizar login en el SII
        
        Args:
            page: Página de Playwright
            rut: RUT
            password: Contraseña
            
        Returns:
            True si el login fue exitoso, False en caso contrario
        """
        try:
            logger.info(f"Iniciando login para RUT: {rut}")
            
            # Anti-bot measures: Ocultar que es Playwright
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => false,
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['es-CL'],
                });
            """)
            logger.info("Script anti-bot inyectado")
            
            # Ir a página de login
            page.goto(self.LOGIN_URL, wait_until="networkidle", timeout=self.timeout)
            logger.info(f"Página de login cargada. URL actual: {page.url}")
            
            # Llenar formulario
            page.fill('input[name="rutclave"]', rut)
            page.fill('input[name="password"]', password)
            logger.info(f"Formulario llenado con RUT y contraseña")
            
            # Enviar login
            page.click('button[type="submit"]')
            logger.info("Click en submit realizado, esperando respuesta...")
            
            # Esperar respuesta
            page.wait_for_load_state("networkidle", timeout=self.timeout)
            logger.info(f"Login completado. URL actual: {page.url}")
            
            # Log del contenido de la página para debugging
            page_content = page.content()
            logger.info(f"Contenido de página (primeros 500 chars): {page_content[:500]}")
            
            # Verificar errores comunes
            if "Usuario no existe" in page_content:
                logger.error(f"Error del SII: Usuario no existe")
                return False
            if "Clave incorrecta" in page_content:
                logger.error(f"Error del SII: Clave incorrecta")
                return False
            if "Usuario inactivo" in page_content:
                logger.error(f"Error del SII: Usuario inactivo")
                return False
            if "Acceso denegado" in page_content:
                logger.error(f"Error del SII: Acceso denegado")
                return False
            if "Bloqueado" in page_content:
                logger.error(f"Error del SII: Usuario bloqueado (¿Bot detection?)")
                return False
            
            # Si llegamos aquí sin errores, asumir login exitoso
            logger.info(f"Login aparentemente exitoso para RUT: {rut}")
            return True
            
        except PlaywrightTimeoutError as e:
            logger.error(f"Timeout durante login: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error durante login: {str(e)}", exc_info=True)
            return False
    
    def _fetch_book_data(self, page, book_type: str, mes: int, ano: int) -> Optional[List[Dict[str, Any]]]:
        """
        Obtener datos de un libro (COMPRAS o VENTAS) descargando el CSV
        
        Args:
            page: Página de Playwright
            book_type: "COMPRAS" o "VENTAS"
            mes: Mes (1-12)
            ano: Año (YYYY)
            
        Returns:
            Lista de registros del libro parseados desde CSV o None si hay error
        """
        try:
            logger.info(f"Obteniendo datos de {book_type} para mes: {mes}, año: {ano}")
            
            # Primero, navegar a la página de libros si no estamos allá
            current_url = page.url
            if "consdcvinternetui" not in current_url:
                page.goto("https://www4.sii.cl/consdcvinternetui/#/index", wait_until="networkidle", timeout=self.timeout)
                logger.info("Navegado a página de libros")
            
            # Esperar a que se cargue el formulario
            page.wait_for_selector('select[name*="periodo"], [data-testid*="periodo"]', timeout=self.timeout)
            logger.info("Formulario cargado")
            
            # Convertir número de mes a nombre en español
            meses = {
                1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
            }
            mes_nombre = meses.get(mes, str(mes))
            
            # Seleccionar el tipo de libro (COMPRA o VENTA)
            if book_type == "COMPRAS":
                page.click("text=COMPRA")
                logger.info("Tab COMPRA seleccionado")
            elif book_type == "VENTAS":
                page.click("text=VENTA")
                logger.info("Tab VENTA seleccionado")
            
            page.wait_for_timeout(1000)  # Esperar a que se cargue el tab
            
            # Seleccionar mes
            page.select_option("select[name*='periodo'], select", mes_nombre)
            logger.info(f"Mes seleccionado: {mes_nombre}")
            
            # Seleccionar año
            page.select_option("select[name*='ano'], select", str(ano))
            logger.info(f"Año seleccionado: {ano}")
            
            # Hacer click en Consultar
            page.click("button:has-text('Consultar')")
            logger.info("Click en Consultar realizado")
            
            # Esperar a que se carguen los resultados
            page.wait_for_timeout(2000)
            
            # Ahora interceptar la descarga del CSV
            logger.info("Esperando click en 'Descargar Detalles'...")
            
            # Usar expect_download para capturar la descarga
            with page.expect_download() as download_info:
                page.click("button:has-text('Descargar Detalles')")
                logger.info("Click en 'Descargar Detalles' realizado")
            
            download = download_info.value
            logger.info(f"Descarga capturada: {download.suggested_filename}")
            
            # Leer contenido del CSV sin guardarlo a disco
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = os.path.join(temp_dir, download.suggested_filename)
                download.save_as(file_path)
                
                # Leer y parsear el CSV
                records = []
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        records.append(dict(row))
                
                logger.info(f"{book_type}: {len(records)} registros obtenidos del CSV")
                return records
                    
        except PlaywrightTimeoutError as e:
            logger.error(f"Timeout obteniendo {book_type}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error obteniendo {book_type}: {str(e)}", exc_info=True)
            return None
