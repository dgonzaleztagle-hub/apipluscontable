#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test script para sincronización SII - SIMPLE"""
import json
import sys
import time

output_file = 'd:\\proyectos\\pluscontableapisii\\backend\\test_output_simple.txt'

with open(output_file, 'w', encoding='utf-8') as f:
    try:
        f.write("Iniciando test de sincronizacion SII (versión simple)...\n")
        f.write("=" * 60 + "\n\n")
        
        import requests
        
        payload = {
            "rut": "77956294-8",
            "password": "Tr7795629.",
            "mes": 11,
            "ano": 2025
        }
        
        f.write("Enviando POST a http://localhost:5000/api/sync-sii\n")
        f.write(f"Payload: {json.dumps(payload, indent=2)}\n\n")
        f.write("Conectando...\n")
        f.flush()
        
        response = requests.post(
            'http://localhost:5000/api/sync-sii',
            json=payload,
            timeout=10
        )
        
        f.write(f"\nStatus Code: {response.status_code}\n\n")
        f.write("Response completo:\n")
        f.write(json.dumps(response.json(), indent=2, ensure_ascii=False))
        f.write("\n\nTEST EXITOSO!\n")
        
    except Exception as e:
        f.write(f"\nERROR: {type(e).__name__}: {str(e)}\n")
        import traceback
        f.write("\n" + traceback.format_exc())

print("Archivo guardado en test_output_simple.txt")
