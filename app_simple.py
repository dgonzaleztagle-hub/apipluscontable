"""
PlusContableAPISII - Backend Server (Versión Simplificada para Testing)
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

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar Flask
app = Flask(__name__)

# Configurar CORS
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://localhost:5173').split(',')
CORS(app, resources={r"/api/*": {"origins": cors_origins}})


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    logger.info("Health check")
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
        "mes": 11,
        "ano": 2025
    }
    """
    try:
        logger.info("Recibido request de sync-sii")
        
        data = request.get_json()
        logger.info(f"Data recibida: {data}")
        
        # Validar datos requeridos
        required_fields = ['rut', 'password', 'mes', 'ano']
        for field in required_fields:
            if field not in data:
                logger.warning(f"Campo faltante: {field}")
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido faltante: {field}'
                }), 400
        
        rut = data.get('rut')
        password = data.get('password')
        mes = int(data.get('mes'))
        ano = int(data.get('ano'))
        
        logger.info(f"Datos validados. RUT: {rut}, mes: {mes}, año: {ano}")
        
        # MOCK DATA - Datos de prueba
        mock_compras = [
            {
                'rut_proveedor': '12.345.678-9',
                'razon_social': 'Proveedor Test S.A.',
                'tipo_documento': 'Factura',
                'numero_documento': '001-2025',
                'fecha_documento': '2025-11-15',
                'monto_neto': 1000000,
                'impuesto_iva': 190000,
                'monto_total': 1190000,
                'estado': 'Aceptado'
            }
        ]
        
        mock_ventas = [
            {
                'rut_cliente': '98.765.432-1',
                'razon_social': 'Cliente Test Ltda.',
                'tipo_documento': 'Boleta',
                'numero_documento': '1001',
                'fecha_documento': '2025-11-20',
                'monto_neto': 500000,
                'impuesto_iva': 95000,
                'monto_total': 595000,
                'estado': 'Aceptado'
            }
        ]
        
        logger.info(f"Retornando mock data. Compras: {len(mock_compras)}, Ventas: {len(mock_ventas)}")
        
        return jsonify({
            'success': True,
            'data': {
                'compras': mock_compras,
                'ventas': mock_ventas,
                'mes': mes,
                'ano': ano,
                'rut': rut,
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
        
        # MOCK - Simular conexión exitosa
        return jsonify({
            'success': True,
            'message': 'Conexión exitosa con SII'
        }), 200
            
    except Exception as e:
        logger.error(f"Error en test de conexión: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Error al testear conexión: {str(e)}'
        }), 500


@app.errorhandler(404)
def not_found(e):
    logger.warning(f"404: {e}")
    return jsonify({
        'success': False,
        'error': 'Endpoint no encontrado'
    }), 404


@app.errorhandler(500)
def internal_error(e):
    logger.error(f"500: {e}")
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor'
    }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False') == 'True'
    logger.info(f"Iniciando servidor en puerto {port}, debug={debug}")
    app.run(host='0.0.0.0', port=port, debug=debug)
