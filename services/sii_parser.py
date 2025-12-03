"""
SII Parser - Módulo para parsear y normalizar datos del SII
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class SIIParser:
    """Parser para procesar datos del SII"""
    
    def parse_compras(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parsear datos de compras
        
        Args:
            raw_data: Datos crudos del SII
            
        Returns:
            Datos normalizados de compras
        """
        parsed = []
        
        try:
            for item in raw_data:
                parsed_item = {
                    'rut_proveedor': item.get('rutProveedor', ''),
                    'razon_social': item.get('nombreProveedor', ''),
                    'tipo_documento': item.get('tipoDocumento', ''),
                    'numero_documento': item.get('numeroDocumento', ''),
                    'fecha_documento': item.get('fechaDocumento', ''),
                    'monto_neto': float(item.get('montoNeto', 0)),
                    'impuesto_iva': float(item.get('impuestoIva', 0)),
                    'monto_total': float(item.get('montoTotal', 0)),
                    'estado': item.get('estado', ''),
                }
                parsed.append(parsed_item)
                
            logger.info(f"Parseadas {len(parsed)} compras")
            return parsed
            
        except Exception as e:
            logger.error(f"Error parseando compras: {str(e)}")
            return []
    
    def parse_ventas(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Parsear datos de ventas
        
        Args:
            raw_data: Datos crudos del SII
            
        Returns:
            Datos normalizados de ventas
        """
        parsed = []
        
        try:
            for item in raw_data:
                parsed_item = {
                    'rut_cliente': item.get('rutCliente', ''),
                    'razon_social': item.get('nombreCliente', ''),
                    'tipo_documento': item.get('tipoDocumento', ''),
                    'numero_documento': item.get('numeroDocumento', ''),
                    'fecha_documento': item.get('fechaDocumento', ''),
                    'monto_neto': float(item.get('montoNeto', 0)),
                    'impuesto_iva': float(item.get('impuestoIva', 0)),
                    'monto_total': float(item.get('montoTotal', 0)),
                    'estado': item.get('estado', ''),
                }
                parsed.append(parsed_item)
                
            logger.info(f"Parseadas {len(parsed)} ventas")
            return parsed
            
        except Exception as e:
            logger.error(f"Error parseando ventas: {str(e)}")
            return []
    
    def calculate_totals(self, items: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calcular totales de una lista de items
        
        Args:
            items: Lista de items
            
        Returns:
            Dict con totales (neto, iva, total)
        """
        try:
            total_neto = sum(item.get('monto_neto', 0) for item in items)
            total_iva = sum(item.get('impuesto_iva', 0) for item in items)
            total_general = sum(item.get('monto_total', 0) for item in items)
            
            return {
                'total_neto': total_neto,
                'total_iva': total_iva,
                'total_general': total_general,
                'cantidad_registros': len(items)
            }
            
        except Exception as e:
            logger.error(f"Error calculando totales: {str(e)}")
            return {}
