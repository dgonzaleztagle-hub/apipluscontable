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
    return jsonify({
        'status': 'ok',
        'service': 'PlusContableAPISII',
        'timestamp': datetime.now().isoformat()
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
