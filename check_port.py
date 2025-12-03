#!/usr/bin/env python
import socket
import time

time.sleep(1)

try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 5000))
    sock.close()
    
    if result == 0:
        print("✅ Servidor está escuchando en puerto 5000")
    else:
        print(f"❌ Servidor NO está escuchando. Error: {result}")
except Exception as e:
    print(f"❌ Error: {e}")
