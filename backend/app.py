"""
PlusContableAPISII - Backend Server
Servidor Python para scraping de libros SII (COMPRAS y VENTAS)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Cargar variables de entorno
load_dotenv()

# Configurar logging PRIMERO
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)

# Configurar CORS
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')
CORS(app, resources={r"/api/*": {"origins": cors_origins}})

# Importar servicios de scraping
from services.sii_scraper import SIIScraper
from services.sii_parser import SIIParser

scraper = SIIScraper()
parser = SIIParser()
logger.info("Servicios SII importados correctamente")


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    endpoints = []
    for rule in app.url_map.iter_rules():
        endpoints.append(str(rule))
    
    return jsonify({
        'status': 'ok',
        'service': 'PlusContableAPISII v2.0',
        'timestamp': datetime.now().isoformat(),
        'endpoints': sorted(endpoints)
    }), 200


@app.route('/api/sync-sii', methods=['POST'])
def sync_sii():
    """
    Endpoint para sincronizar libros SII
    
    Body esperado:
    {
        "rut": "77956294-8",
        "password": "Tr7795629.",
        "mes": 12,
        "ano": 2025,
        "tipo": "COMPRAS"  # opcional, default: COMPRAS
    }
    """
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['rut', 'password', 'mes', 'ano']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido faltante: {field}'
                }), 400
        
        rut = data.get('rut')
        password = data.get('password')
        mes = int(data.get('mes'))
        ano = int(data.get('ano'))
        book_type = data.get('tipo', 'COMPRAS')  # Default a COMPRAS
        
        if book_type not in ['COMPRAS', 'VENTAS']:
            return jsonify({
                'success': False,
                'error': 'tipo debe ser COMPRAS o VENTAS'
            }), 400
        
        logger.info(f"Iniciando sincronización de {book_type} para RUT: {rut}, mes: {mes}, año: {ano}")
        
        # Realizar scraping con Playwright
        logger.info(f"Conectándose al SII con Playwright para obtener {book_type}...")
        try:
            books = scraper.fetch_books(rut, password, mes, ano, book_type)
        except TimeoutError as e:
            logger.error(f"Timeout conectándose al SII: {str(e)}")
            raise TimeoutError(f"SII no respondió en tiempo: {str(e)}")
        except Exception as e:
            logger.error(f"Error en scraping: {str(e)}", exc_info=True)
            raise
        
        if books is None:
            error_msg = f'No se pudieron obtener los {book_type} del SII'
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"{book_type} obtenidos exitosamente: {len(books)} registros")
        
        return jsonify({
            'success': True,
            'data': {
                'tipo': book_type,
                'registros': books,
                'mes': mes,
                'ano': ano,
                'rut': rut,
                'cantidad': len(books),
                'sync_date': datetime.now().isoformat()
            }
        }), 200
        
    except ValueError as e:
        logger.error(f"Error de validación: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error de validación: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }), 500


@app.route('/api/sync-books', methods=['POST'])
def sync_books():
    """
    Endpoint para sincronizar COMPRAS y VENTAS simultáneamente (por un mes específico)
    Este es el endpoint usado por el botón "Sinc" de la app Lova
    
    Body esperado:
    {
        "rut": "77956294-8",
        "password": "Tr7795629.",
        "mes": 10,
        "ano": 2025
    }
    
    Respuesta:
    {
        "success": true,
        "data": {
            "COMPRAS": {
                "registros": [...],
                "cantidad": 5,
                "sync_date": "2025-12-03T10:30:00"
            },
            "VENTAS": {
                "registros": [...],
                "cantidad": 3,
                "sync_date": "2025-12-03T10:30:00"
            }
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validar datos requeridos
        required_fields = ['rut', 'password', 'mes', 'ano']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido faltante: {field}'
                }), 400
        
        rut = data.get('rut')
        password = data.get('password')
        mes = int(data.get('mes'))
        ano = int(data.get('ano'))
        
        logger.info(f"Iniciando sincronización de COMPRAS y VENTAS para RUT: {rut}, mes: {mes}, año: {ano}")
        
        # Descargar COMPRAS y VENTAS en paralelo usando ThreadPoolExecutor
        books_result = {}
        errors = []
        
        def fetch_book_type(book_type):
            """Función para descargar un tipo de libro"""
            try:
                logger.info(f"Descargando {book_type}...")
                books = scraper.fetch_books(rut, password, mes, ano, book_type)
                
                if books is None:
                    error = f'No se pudieron obtener los {book_type} del SII'
                    logger.error(error)
                    errors.append(error)
                    return None
                
                logger.info(f"{book_type} obtenidos exitosamente: {len(books)} registros")
                return {
                    'registros': books,
                    'cantidad': len(books),
                    'sync_date': datetime.now().isoformat()
                }
            except Exception as e:
                error = f'Error descargando {book_type}: {str(e)}'
                logger.error(error, exc_info=True)
                errors.append(error)
                return None
        
        # Ejecutar descargas en paralelo
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_compras = executor.submit(fetch_book_type, 'COMPRAS')
            future_ventas = executor.submit(fetch_book_type, 'VENTAS')
            
            books_result['COMPRAS'] = future_compras.result()
            books_result['VENTAS'] = future_ventas.result()
        
        # Verificar si hubo errores
        if errors:
            logger.error(f"Errores durante la sincronización: {errors}")
        
        # Si ambos fueron None, retornar error
        if books_result['COMPRAS'] is None and books_result['VENTAS'] is None:
            return jsonify({
                'success': False,
                'error': 'No se pudieron obtener ni COMPRAS ni VENTAS del SII',
                'errors': errors
            }), 500
        
        # Si al menos uno fue exitoso, retornar con data parcial
        return jsonify({
            'success': True,
            'data': {
                'COMPRAS': books_result['COMPRAS'],
                'VENTAS': books_result['VENTAS'],
                'mes': mes,
                'ano': ano,
                'rut': rut
            }
        }), 200
        
    except ValueError as e:
        logger.error(f"Error de validación: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error de validación: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }), 500


@app.route('/api/test-connection', methods=['POST'])
def test_connection():
    """
    Endpoint para testear la conexión con SII
    Solo verifica si las credenciales son válidas
    """
    try:
        data = request.get_json()
        rut = data.get('rut')
        password = data.get('password')
        
        if not rut or not password:
            return jsonify({
                'success': False,
                'error': 'RUT y contraseña requeridos'
            }), 400
        
        logger.info(f"Testeando conexión para RUT: {rut}")
        
        # Intentar conexión REAL - sin fallback
        try:
            is_valid = scraper.test_credentials(rut, password)
        except TimeoutError as e:
            logger.error(f"Timeout en test de conexión: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'SII no respondió en tiempo: {str(e)}'
            }), 504
        except Exception as e:
            logger.error(f"Error en test de credenciales: {str(e)}", exc_info=True)
            return jsonify({
                'success': False,
                'error': f'Error conectando a SII: {str(e)}'
            }), 500
        
        if is_valid:
            return jsonify({
                'success': True,
                'message': 'Conexión exitosa con SII'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Credenciales inválidas o SII rechazó la autenticación'
            }), 401
            
    except Exception as e:
        logger.error(f"Error en test de conexión: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error al testear conexión: {str(e)}'
        }), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({
        'success': False,
        'error': 'Endpoint no encontrado'
    }), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor'
    }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False') == 'True'
    app.run(host='0.0.0.0', port=port, debug=debug)
