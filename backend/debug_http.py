"""
Script para obtener datos SII usando peticiones HTTP directas
en lugar de Playwright + JavaScript
"""
import logging
import requests
import json
import csv
from io import StringIO
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

RUT = "77956294-8"
PASSWORD = "Tr7795629."

# URLs
LOGIN_URL = "https://zeusr.sii.cl/AUT2000/InicioAutenticacion/IngresoRutClave.html"
DESTINATION_URL = "https://www4.sii.cl/consdcvinternetui/#/index"
RESUMEN_URL = "https://www4.sii.cl/consdcvinternetui/services/data/facadeService/getResumen"

session = requests.Session()

try:
    # PASO 1: Login
    logger.info("PASO 1: Haciendo login...")
    
    login_data = {
        "rutcntr": RUT,
        "clave": PASSWORD,
        "submit": "Ingresar"
    }
    
    # Primera petición: ir al formulario
    session.get(f"{LOGIN_URL}?{DESTINATION_URL}")
    
    # Segunda petición: enviar credenciales
    response = session.post(
        "https://zeusr.sii.cl/AUT2000/InicioAutenticacion/IngresoAut.html",
        data=login_data,
        allow_redirects=True
    )
    
    logger.info(f"✓ Login completado. Status: {response.status_code}")
    logger.info(f"  URL actual: {response.url}")
    
    # PASO 2: Hacer petición al endpoint de datos
    logger.info("\nPASO 2: Obteniendo datos...")
    
    # Payload típico para getResumen
    payload = {
        "metaData": {
            "namespace": "com.sii.soap.facilitador",
            "conversationId": "test-session",
            "transactionId": "test-transaction",
            "page": 0
        },
        "data": {
            "rut": RUT,
            "periodoMes": "10",
            "periodoAnho": "2025",
            "tipoOperacion": "COMPRAS"  # o VENTAS
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    response = session.post(
        RESUMEN_URL,
        json=payload,
        headers=headers
    )
    
    logger.info(f"Response Status: {response.status_code}")
    logger.info(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            logger.info(f"\n✓ Datos recibidos en JSON")
            logger.info(f"  Keys: {list(data.keys())}")
            logger.info(f"\n  Contenido completo:")
            logger.info(json.dumps(data, indent=2)[:2000])
            
            # Buscar datos de facturas
            if "data" in data:
                logger.info(f"\n  Dentro de 'data': {list(data['data'].keys()) if isinstance(data['data'], dict) else type(data['data'])}")
            
        except json.JSONDecodeError:
            logger.info(f"Response no es JSON. Primeros 500 chars:")
            logger.info(response.text[:500])
    else:
        logger.error(f"Error en respuesta: {response.status_code}")
        logger.error(response.text[:500])
    
except Exception as e:
    logger.error(f"ERROR: {e}", exc_info=True)
