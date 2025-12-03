# 📚 PlusContableAPISII - Knowledge Base

## Proyecto: Integración de Libros SII (Compras y Ventas)

**Fecha**: 28 de Noviembre 2025  
**Stack**: React 18 + Vite (SPA) + Supabase Edge Functions (Deno)  
**Arquitectura**: Scraping bajo demanda con servidor Python en Railway.app

---

## 📋 Contexto General

Este es un proyecto **separado de SuperPanel 3.0** para una app de contabilidad chilena que obtiene automáticamente los libros de compras y ventas desde el SII (Servicio de Impuestos Internos de Chile).

**Objetivo**: El usuario ingresa credenciales SII → Su app obtiene bajo demanda los 2 libros → Se guardan en Supabase → Se muestran en la UI.

---

## 🌐 URLs del SII

**1. Página de Login (obtener cookies iniciales):**
```
https://zeusr.sii.cl/AUT2000/InicioAutenticacion/IngresoRutClave.html
```

**2. Endpoint de autenticación (POST con credenciales):**
```
https://zeusr.sii.cl/cgi_AUT2000/CAutInicio.cgi?https://www4.sii.cl/consdcvinternetui/
```

**3. API de resumen COMPRAS:**
```
https://www4.sii.cl/consdcvinternetui/services/data/facadeService/getResumen/COMPRAS/{mes}/{año}
```

**4. API de resumen VENTAS:**
```
https://www4.sii.cl/consdcvinternetui/services/data/facadeService/getResumen/VENTAS/{mes}/{año}
```

**Parámetros requeridos:**
- `{mes}`: 1-12 (mes a descargar)
- `{año}`: YYYY (año a descargar)

---

## 🔑 Características Críticas

### ✅ Sin CAPTCHA
El SII **no tiene CAPTCHA en el login**, solo credenciales estándar (RUT + contraseña). Esto simplifica mucho el scraping.

### ✅ Bajo Demanda (No Automático)
- Usuario hace clic en botón "Sincronizar Libros"
- Se envía request al servidor Python
- Se descarga COMPRAS + VENTAS
- Se guarda en BD
- Se muestra en pantalla

**Ventaja**: No consume recursos constantemente, solo cuando se necesita.

---

## 🛠️ Stack Técnico

### Frontend (React 18 + Vite)
```
/src
  /components
    SiiSyncButton.tsx        → Botón "Sincronizar"
    BooksViewer.tsx          → Vista de libros descargados
  /lib
    api.ts                   → Llamadas a Railway server
    types.ts                 → Interfaces para libros SII
  /pages
    Books.tsx                → Página principal
```

### Backend (Servidor Python en Railway.app)
```
Tecnología: Python 3.11+ con Playwright/Selenium
Función: Scraping de SII bajo demanda
- Recibe: RUT, contraseña, mes, año
- Retorna: JSON con libros COMPRAS + VENTAS
- Timeout: ~30-60 segundos por sincronización
```

### Base de Datos (Supabase PostgreSQL)
```sql
-- Tabla: sii_books
CREATE TABLE sii_books (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  rut_empresa VARCHAR(20),
  tipo_libro VARCHAR(20),        -- 'COMPRAS' o 'VENTAS'
  mes INTEGER,
  año INTEGER,
  datos JSONB,                   -- Datos completos del libro
  sync_date TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE
);

-- Tabla: sii_credentials (encriptadas)
CREATE TABLE sii_credentials (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL,
  rut_encrypted VARCHAR(255),    -- Hash/Encriptado
  password_encrypted VARCHAR(255),
  created_at TIMESTAMP WITH TIME ZONE
);
```

---

## 🔄 Flujo de Sincronización

```
┌─────────────────────────────────────┐
│ 1. Usuario en React hace clic        │
│    "Sincronizar Libros SII"         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 2. React envía POST a Railway:      │
│    /sync-sii                        │
│    body: {                          │
│      rut: "12.345.678-9",           │
│      password: "***",               │
│      mes: 11,                       │
│      año: 2025                      │
│    }                                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 3. Servidor Python en Railway:      │
│    - Abre navegador (Playwright)    │
│    - Login a SII                    │
│    - Descarga COMPRAS + VENTAS      │
│    - Parsea JSON                    │
│    - Retorna resultado              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 4. React recibe JSON:               │
│    {                                │
│      success: true,                 │
│      compras: [...],                │
│      ventas: [...]                  │
│    }                                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 5. React guarda en Supabase         │
│    INSERT INTO sii_books            │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 6. UI muestra libros descargados    │
│    (tablas con datos)               │
└─────────────────────────────────────┘
```

---

## 💰 Recursos Necesarios (Todos Gratis)

| Recurso | Herramienta | Costo | Notas |
|---------|-------------|-------|-------|
| **Frontend** | React 18 + Vite | Gratis | SPA sin backend Node.js |
| **Backend** | Python 3.11 | Gratis | Scraping con Playwright |
| **Hosting Backend** | Railway.app | $5/mes créditos gratis | Free tier suficiente para bajo demanda |
| **BD** | Supabase PostgreSQL | Gratis | Free tier incluye 500MB |
| **Scraping** | Playwright | Gratis | Librería Python libre |

**Total mensual**: ~$0 (si solo usas bajo demanda)

---

## 📊 Datos Obtenidos

### Libro de COMPRAS
```json
{
  "rut_proveedor": "12.345.678-9",
  "razon_social": "Empresa Proveedor Ltda.",
  "monto_neto": 1000000,
  "impuesto_iva": 190000,
  "monto_total": 1190000,
  "tipo_documento": "Factura",
  "fecha_documento": "2025-11-15"
}
```

### Libro de VENTAS
```json
{
  "rut_cliente": "98.765.432-1",
  "razon_social": "Cliente S.A.",
  "monto_neto": 500000,
  "impuesto_iva": 95000,
  "monto_total": 595000,
  "tipo_documento": "Boleta",
  "fecha_documento": "2025-11-20"
}
```

---

## ⚙️ Configuración Inicial

### Paso 1: Crear Proyecto Python
```bash
mkdir pluscontable-api
cd pluscontable-api
python -m venv venv
source venv/bin/activate  # o: venv\Scripts\activate en Windows
pip install flask playwright python-dotenv requests
playwright install chromium
```

### Paso 2: Crear app.py básico
```python
from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright
import os

app = Flask(__name__)

@app.route('/sync-sii', methods=['POST'])
def sync_sii():
    data = request.json
    rut = data.get('rut')
    password = data.get('password')
    mes = data.get('mes')
    año = data.get('año')
    
    # Lógica de scraping aquí
    return jsonify({...})

if __name__ == '__main__':
    app.run(debug=False, port=5000)
```

### Paso 3: Desplegar en Railway.app
1. Crear cuenta en railway.app
2. Conectar repo GitHub
3. Deployar automáticamente

---

## 🚀 Próximos Pasos

1. **Crear servidor Python** con endpoints de scraping
2. **Integrar Playwright** para automatización del navegador
3. **Crear tablas Supabase** para guardar libros
4. **Crear componentes React** para UI de sincronización
5. **Conectar credenciales encriptadas** (guardar RUT + contraseña safe)
6. **Desplegar en Railway.app**
7. **Testear flujo completo**

---

## 📝 Notas Importantes

- **Sin CAPTCHA**: Simplifica el scraping significativamente
- **Bajo demanda**: No consume recursos constantemente
- **Encripción de credenciales**: Guardar RUT + contraseña de forma segura
- **Timeout**: El scraping puede tardar 20-60 segundos por libro
- **Rate Limiting**: Espaciar solicitudes para no bloquear con SII
- **Error Handling**: Mostrar mensajes claros si falla la sincronización

---

**Estado**: Listo para iniciar implementación
