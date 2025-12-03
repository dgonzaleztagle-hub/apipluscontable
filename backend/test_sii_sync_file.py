#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test script para sincronización SII - Guarda output en archivo"""
import json
import sys
import os

# Cambiar al directorio backend
os.chdir('d:\\proyectos\\pluscontableapisii\\backend')
sys.path.insert(0, '.')

output_file = 'd:\\proyectos\\pluscontableapisii\\backend\\test_output.txt'

try:
    with open(output_file, 'w', encoding='utf-8') as f:
        import requests
        
        f.write("Iniciando test de sincronizacion SII...\n")
        f.write("=" * 60 + "\n\n")
        
        payload = {
            "rut": "77956294-8",
            "password": "Tr7795629.",
            "mes": 11,
            "ano": 2025
        }
        
        f.write("Enviando POST a http://localhost:5000/api/sync-sii\n")
        f.write(f"Payload: {json.dumps(payload, indent=2)}\n\n")
        f.write("Esperando respuesta (30-60 segundos)...\n")
        f.flush()
        
        response = requests.post(
            'http://localhost:5000/api/sync-sii',
            json=payload,
            timeout=120
        )
        
        f.write(f"\nStatus Code: {response.status_code}\n\n")
        f.write("Response:\n")
        f.write(json.dumps(response.json(), indent=2, ensure_ascii=False))
        f.write("\n\nTest completado exitosamente!\n")
        
except requests.exceptions.Timeout:
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write("\nTimeout - El servidor tardo demasiado\n")
except requests.exceptions.ConnectionError:
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write("\nError de conexion - El servidor no esta escuchando\n")
except Exception as e:
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(f"\nError: {type(e).__name__}: {e}\n")
        import traceback
        f.write(traceback.format_exc())

print(f"Output guardado en: {output_file}")

