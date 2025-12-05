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
    # URL de destino tras login - se pasará como parámetro a LOGIN_URL
    DESTINATION_URL = "https://www4.sii.cl/consdcvinternetui/#/index"
    BOOKS_API_URL = "https://www4.sii.cl/consdcvinternetui/services/data/facadeService/getResumen"
    
    def __init__(self, headless: bool = True, timeout: int = 120000):
        """
        Inicializar el scraper
        
        Args:
            headless: Ejecutar navegador sin interfaz gráfica
            timeout: Timeout en milisegundos para operaciones (aumentado a 120s para Render)
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
                    # Ir a página de login (usando networkidle para mejor estabilidad en Railway)
                    page.goto(self.LOGIN_URL, wait_until="networkidle", timeout=self.timeout)
                    logger.info("Página de login cargada")
                    
                    # Llenar formulario de login
                    page.fill('input[name="rutclave"]', rut)
                    page.fill('input[name="password"]', password)
                    
                    # Hacer click en botón de login
                    page.click('button[type="submit"]')
                    
                    # Esperar respuesta
                    page.wait_for_load_state("domcontentloaded", timeout=self.timeout)
                    
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
            logger.info(f"Playwright disponible: {PLAYWRIGHT_AVAILABLE}")
            
            logger.info("Iniciando Playwright...")
            with sync_playwright() as p:
                logger.info("Playwright context creado, lanzando Chromium...")
                try:
                    browser = p.chromium.launch(
                        headless=self.headless,
                        args=[
                            '--disable-blink-features=AutomationControlled',
                            '--disable-dev-shm-usage',
                            '--no-sandbox',
                            '--disable-gpu',
                        ]
                    )
                    logger.info("Chromium lanzado exitosamente")
                except Exception as e:
                    logger.error(f"FALLO al lanzar Chromium: {str(e)}", exc_info=True)
                    return None
                    
                try:
                    context = browser.new_context()
                    page = context.new_page()
                    logger.info("Página de navegador creada")
                    
                    # Anti-bot stealth
                    page.add_init_script("""
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => false,
                        });
                    """)
                    
                    # Realizar login
                    logger.info("Iniciando procedimiento de login...")
                    if not self._login(page, rut, password):
                        logger.error("Fallo en login")
                        return None
                    
                    logger.info("Login exitoso, obteniendo datos de libros...")
                    # Obtener libros (solo COMPRAS por ahora)
                    books = self._fetch_book_data(page, book_type, mes, ano)
                    
                    logger.info(f"{book_type} obtenidos: {len(books) if books else 0} registros")
                    
                    return books
                    
                finally:
                    logger.info("Cerrando navegador...")
                    browser.close()
                    
        except Exception as e:
            logger.error(f"EXCEPCIÓN al obtener {book_type}: {str(e)}", exc_info=True)
            import traceback
            logger.error(f"Traceback completo: {traceback.format_exc()}")
            return None
    
    def _login(self, page, rut: str, password: str) -> bool:
        """
        Realizar login en el SII
        
        Args:
            page: Página de Playwright
            rut: RUT con guión (ej: 77956294-8)
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
            
            # Ir a página de login CON parámetro de redirección a la página de libros
            login_url_with_redirect = f"{self.LOGIN_URL}?{self.DESTINATION_URL}"
            page.goto(login_url_with_redirect, wait_until="domcontentloaded", timeout=self.timeout)
            logger.info(f"Página de login cargada con redirección. URL: {page.url}")
            
            # Esperar a que cargue el formulario
            page.wait_for_selector("input#rutcntr", timeout=self.timeout)
            logger.info("Formulario listo")
            
            # Llenar formulario
            page.fill('input#rutcntr', rut)  # RUT
            page.fill('input#clave', password)  # Password
            logger.info(f"Formulario llenado con RUT y contraseña")
            
            # Enviar login
            page.click('button#bt_ingresar')
            logger.info("Click en submit realizado, esperando respuesta...")
            
            # Esperar a que se cargue la página de libros (domcontentloaded es más rápido para Render)
            page.wait_for_load_state("domcontentloaded", timeout=self.timeout)
            logger.info(f"Login completado. URL actual: {page.url}")
            
            # Verificar si estamos en la página de libros
            current_url = page.url
            if "consdcvinternetui" in current_url:
                logger.info(f"✓ Navegado exitosamente a página de libros")
                return True
            elif "CAutInicio.cgi" in current_url:
                # Todavía en la página de autenticación, esto significa que el login falló
                page_content = page.content()
                logger.error("Estamos en página de autenticación post-submit. Buscando errores...")
                
                if "Usuario no existe" in page_content or "usuario no existe" in page_content.lower():
                    logger.error(f"Error del SII: Usuario no existe")
                    return False
                if "Clave incorrecta" in page_content or "clave incorrecta" in page_content.lower():
                    logger.error(f"Error del SII: Clave incorrecta")
                    return False
                if "Usuario inactivo" in page_content or "usuario inactivo" in page_content.lower():
                    logger.error(f"Error del SII: Usuario inactivo")
                    return False
                if "Bloqueado" in page_content or "bloqueado" in page_content.lower():
                    logger.error(f"Error del SII: Usuario bloqueado (¿Bot detection?)")
                    return False
                    
                logger.error(f"Login falló - URL no cambió a consdcvinternetui")
                return False
            else:
                logger.warning(f"URL inesperada después de login: {current_url}")
                # Todavía intentar proseguir - tal vez simplemente hay un redirect en progreso
                page.wait_for_timeout(2000)
                if "consdcvinternetui" in page.url:
                    logger.info(f"✓ Finalmente llegamos a página de libros")
                    return True
                else:
                    logger.error(f"No llegamos a página de libros. URL final: {page.url}")
                    return False
            
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
            
            # Asegurarse de que estamos en la página de libros
            current_url = page.url
            if "consdcvinternetui" not in current_url:
                logger.warning(f"No estamos en la página de libros. URL actual: {current_url}")
                page.goto("https://www4.sii.cl/consdcvinternetui/#/index", wait_until="networkidle", timeout=self.timeout)
                logger.info("Navegado a página de libros")
            
            # Convertir número de mes a nombre en español
            meses = {
                1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
                5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
                9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
            }
            mes_nombre = meses.get(mes, str(mes))
            
            logger.info("PASO 0: Esperando a que los selects estén disponibles en el DOM...")
            # ESPERAR ACTIVAMENTE a que los selects aparezcan - esto es CRÍTICO
            try:
                page.locator("select").first.wait_for(state="attached", timeout=30000)
                logger.info("✓ Selectores detectados en el DOM")
            except PlaywrightTimeoutError:
                logger.error("Timeout esperando selectores - página no renderizó correctamente")
                return None
            
            # Dar tiempo adicional para que Angular termide de renderizar
            page.wait_for_timeout(3000)
            logger.info("✓ Página lista para interactuar")
            
            # PASO 1: Seleccionar tab correcto (COMPRAS o VENTA)
            if book_type == "VENTAS":
                try:
                    logger.info("PASO 1: Buscando y clickeando tab VENTA...")
                    # Buscar el elemento que contiene el texto "VENTA" exacto
                    venta_tab = page.locator('text="VENTA"')
                    if venta_tab.count() > 0:
                        logger.info("  ✓ Tab VENTA encontrado, clickeando...")
                        venta_tab.click()
                        page.wait_for_timeout(1500)  # Esperar a que Angular renderice el cambio
                        logger.info("  ✓ Tab VENTA clickeado")
                    else:
                        logger.warning("  ⚠ Tab VENTA no encontrado por texto")
                except Exception as e:
                    logger.warning(f"  ⚠ Error clickeando tab VENTA: {e}")
                    # Continuar de todas formas, quizás ya estamos en VENTA
            else:
                logger.info("PASO 1: Usando tab COMPRA (por defecto)")
            
            # PASO 2: Seleccionar mes
            try:
                logger.info(f"PASO 2: Seleccionando mes: {mes_nombre}")
                
                # Encontrar todos los selects
                selects = page.locator("select")
                select_count = selects.count()
                logger.info(f"Encontrados {select_count} selects")
                
                if select_count >= 2:
                    # El SEGUNDO select (índice 1) es el de mes (ng-model="periodoMes")
                    # NO el primero que es RUT
                    periodo_select = selects.nth(1)
                    periodo_select.wait_for(state="visible", timeout=5000)
                    
                    # Convertir mes a formato "01", "02", etc
                    mes_value = f"{mes:02d}"
                    logger.info(f"Seleccionando valor: '{mes_value}'")
                    
                    # Seleccionar por valor (no por texto)
                    periodo_select.select_option(mes_value)
                    logger.info(f"✓ Mes {mes:02d} ({mes_nombre}) seleccionado")
                    
                    page.wait_for_timeout(800)
                else:
                    logger.error(f"No hay selects disponibles")
                    return None
                    
            except Exception as e:
                logger.error(f"Error en paso de mes: {e}")
                return None
            
            # PASO 3: Seleccionar año
            try:
                logger.info(f"PASO 3: Seleccionando año: {ano}")
                
                selects = page.locator("select")
                
                if selects.count() >= 3:
                    # El TERCER select (índice 2) es el de año (ng-model="periodoAnho")
                    ano_select = selects.nth(2)
                    ano_select.wait_for(state="visible", timeout=5000)
                    ano_select.select_option(str(ano))
                    logger.info(f"✓ Año {ano} seleccionado")
                    page.wait_for_timeout(800)
                else:
                    logger.warning(f"Solo hay {selects.count()} selects, esperado al menos 3")
                    
            except Exception as e:
                logger.error(f"Error en paso de año: {e}")
                return None
            
            # PASO 4: Hacer click en Consultar
            try:
                logger.info("PASO 4: Buscando botón Consultar...")
                
                consultar_btn = page.locator("button").filter(has_text="Consultar").first
                consultar_btn.wait_for(state="visible", timeout=5000)
                
                logger.info("Clickeando Consultar...")
                consultar_btn.click()
                logger.info("✓ Consultar clickeado")
                
                # ESPERA CRÍTICA: El modal (#esperaDialog) aparece cuando se inicia la consulta
                # Debemos esperar a que Angular lo cierre, lo que significa que terminó de renderizar
                logger.info("Esperando a que desaparezca el modal de carga...")
                try:
                    page.locator("#esperaDialog").wait_for(state="hidden", timeout=20000)
                    logger.info("✓ Modal desapareció - Angular terminó de renderizar")
                except PlaywrightTimeoutError:
                    logger.warning("⚠ Modal no desapareció en 20s, continuando de todas formas...")
                    page.wait_for_timeout(2000)
                
            except Exception as e:
                logger.error(f"Error clickeando Consultar: {e}")
                return None
            
            # PASO 5: Extraer CSV desde el data URI del link
            try:
                logger.info("PASO 5: Buscando link de descarga con data URI...")
                
                # Primero, esperar a que el botón "Descargar" sea visible
                # (así como esperamos a que "Consultar" fuera visible en PASO 4)
                logger.info("  Esperando a que aparezca el botón 'Descargar'...")
                try:
                    descargar_btn = page.locator("button").filter(has_text="Descargar").first
                    descargar_btn.wait_for(state="visible", timeout=10000)
                    logger.info("  ✓ Botón 'Descargar' encontrado")
                except PlaywrightTimeoutError:
                    logger.warning("  ⚠ Botón 'Descargar' no apareció en 10s")
                
                # Estrategia 1: Buscar elemento <a> con href que empiece con "data:"
                download_links = page.locator('a[href*="data:"]')
                count = download_links.count()
                logger.info(f"  Estrategia 1 - Links a[href*='data:']: {count}")
                
                # Estrategia 2: Si no hay, buscar cualquier <a> que sea visible
                if count == 0:
                    visible_links = page.locator('a')
                    count2 = visible_links.count()
                    logger.info(f"  Estrategia 2 - Links totales encontrados: {count2}")
                    
                    if count2 > 0:
                        for i in range(min(5, count2)):
                            try:
                                link = visible_links.nth(i)
                                href = link.get_attribute("href") or ""
                                text = link.inner_text()
                                if text.strip():  # Solo si tiene texto
                                    logger.info(f"    Link {i}: {text[:50]} → {href[:80]}")
                            except:
                                pass
                
                # Estrategia 3: Buscar botones "Descargar" o "Descargar Detalles"
                if count == 0:
                    descargar_btns = page.locator("button").filter(has_text="Descargar")
                    count3 = descargar_btns.count()
                    logger.info(f"  Estrategia 3 - Botones 'Descargar': {count3}")
                    
                    if count3 > 0:
                        # Si hay botón Descargar, clickearlo
                        logger.info("    Clickeando botón Descargar...")
                        descargar_btns.first.click()
                        
                        # Esperar a que Angular renderice después del click
                        logger.info("    Esperando a que Angular renderice después del click...")
                        page.wait_for_timeout(3000)
                        
                        # Buscar links de nuevo
                        download_links = page.locator('a[href*="data:"]')
                        count = download_links.count()
                        logger.info(f"    Después del click - Links con data URI: {count}")
                
                # Si aún no hay nada, examinar el HTML
                if count == 0:
                    logger.warning("  No se encontró link de descarga en ninguna estrategia")
                    html = page.content()
                    
                    # Buscar "data:" en el HTML
                    if "data:" in html:
                        logger.info("    ✓ 'data:' ENCONTRADO en el HTML")
                        idx = html.find("data:")
                        context = html[max(0, idx-100):idx+200]
                        logger.info(f"    Contexto: ...{context}...")
                    else:
                        logger.error("    ✗ 'data:' NO encontrado en el HTML")
                    
                    return None
                
                logger.info(f"✓ Encontrados {count} links con data URI")
                
                # Obtener el href del primer link
                href_value = download_links.first.get_attribute("href")
                logger.info(f"Link obtenido (primeros 150 chars): {href_value[:150] if href_value else 'None'}")
                
                if not href_value or not href_value.startswith("data:"):
                    logger.error(f"El href no es un data URI válido")
                    return None
                
                # Parsear el data URI
                logger.info("Decodificando data URI...")
                try:
                    import base64
                    from urllib.parse import unquote
                    
                    # Formato: data:text/csv;charset=utf-8,<URL-encoded-content>
                    # o       : data:text/csv;charset=utf-8;base64,<base64-content>
                    if ",base64," in href_value.lower():
                        # Base64 encoded
                        data_part = href_value.split(",", 1)[1] if "," in href_value else ""
                        csv_content = base64.b64decode(data_part).decode('utf-8')
                        logger.info("  Decodificación: base64")
                    else:
                        # URL encoded (formato: data:text/csv;charset=utf-8,contenido%20URL%20encoded)
                        data_part = href_value.split(",", 1)[1] if "," in href_value else ""
                        try:
                            # Primero intentar decodificar como base64
                            csv_content = base64.b64decode(data_part).decode('utf-8')
                            logger.info("  Decodificación: base64 (fallback)")
                        except:
                            # Si falla, es URL-encoded
                            csv_content = unquote(data_part)
                            logger.info("  Decodificación: URL-encoded")
                    
                    logger.info(f"✓ CSV decodificado ({len(csv_content)} chars)")
                    logger.info(f"  Primeras líneas: {csv_content[:200]}")
                    
                    # Parsear como CSV
                    records = []
                    reader = csv.DictReader(StringIO(csv_content), delimiter=';')
                    if reader.fieldnames:
                        for row in reader:
                            records.append(dict(row))
                    
                    logger.info(f"✓ {book_type}: {len(records)} registros parseados del CSV")
                    return records
                    
                except Exception as decode_error:
                    logger.error(f"Error decodificando data URI: {decode_error}", exc_info=True)
                    return None
                    
            except PlaywrightTimeoutError as e:
                logger.error(f"Timeout esperando elemento de descarga: {e}")
                return None
            except Exception as e:
                logger.error(f"Error en descarga desde data URI: {e}", exc_info=True)
                return None
                    
        except Exception as e:
            logger.error(f"Error obteniendo {book_type}: {str(e)}", exc_info=True)
            return None
