# PlusContableAPISII - Backend Scraper para SII

## ✅ Estado: FUNCIONANDO (Diciembre 2025)

Backend Flask que proporciona un API REST para scrapear libros de compras y ventas del SII de Chile.

### ✨ Características

- 🔐 Autenticación con credenciales del SII
- 📥 Descarga de libros COMPRAS y VENTAS
- ⚡ **Descarga simultánea (paralela) de ambos libros**
- 🤖 Automatización con Playwright
- 🎯 Soporte para cualquier mes/año
- 📊 Retorna datos en JSON
- 🚀 Endpoint especial para app Lova: `/api/sync-books`

## 🚀 Inicio Rápido

### 1. Crear entorno virtual
```bash
python -m venv venv
venv\Scripts\activate  # En Windows
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 4. Ejecutar servidor localmente
```bash
python app.py
```

El servidor estará disponible en `http://localhost:5000`

## 📡 API Endpoints

### 1. Health Check ✅
```bash
GET /health
```

Respuesta:
```json
{
  "status": "ok",
  "service": "PlusContableAPISII",
  "timestamp": "2025-12-03T..."
}
```

### 2. Descargar COMPRAS y VENTAS Simultáneamente ⭐ (Para app Lova - Botón "Sinc")
```bash
POST /api/sync-books
Content-Type: application/json

{
  "rut": "77956294-8",
  "password": "Tr7795629.",
  "mes": 10,
  "ano": 2025
}
```

Respuesta exitosa (200 OK):
```json
{
  "success": true,
  "data": {
    "COMPRAS": {
      "registros": [
        {
          "Tipo Documento": "Factura Electrónica(33)",
          "Total Documentos": "6",
          "Monto Exento": "0",
          "Monto Neto": "168420",
          "IVA Recuperable": "31999",
          "IVA Uso Comun": "0",
          "IVA No Recuperable": "0",
          "Monto Total": "219487"
        }
      ],
      "cantidad": 1,
      "sync_date": "2025-12-03T19:39:15.437485"
    },
    "VENTAS": {
      "registros": [
        {
          "Tipo Documento": "Factura Electrónica(33)",
          "Total Documentos": "6",
          "Monto Exento": "0",
          "Monto Neto": "168420",
          "IVA Recuperable": "31999",
          "IVA Uso Comun": "0",
          "IVA No Recuperable": "0",
          "Monto Total": "219487"
        }
      ],
      "cantidad": 1,
      "sync_date": "2025-12-03T19:39:15.580965"
    },
    "mes": 10,
    "ano": 2025,
    "rut": "77956294-8"
  }
}
```

**Características:**
- ⚡ Descarga COMPRAS y VENTAS **en paralelo** (simultáneamente)
- 🎯 Un solo mes a la vez (no múltiples meses)
- 📊 Retorna JSON con ambos tipos de libros
- 🚀 Es el endpoint usado por el botón "Sinc" de la app Lova

### 3. Descargar Libro Individual
```bash
POST /api/sync-sii
Content-Type: application/json

{
  "rut": "77956294-8",
  "password": "Tr7795629.",
  "mes": 11,
  "ano": 2025,
  "tipo": "COMPRAS"
}
```

Respuesta exitosa:
```json
{
  "success": true,
  "data": {
    "tipo": "COMPRAS",
    "registros": [...],
    "cantidad": 5,
    "mes": 11,
    "ano": 2025
  }
}
```

### 4. Testear Conexión
```bash
POST /api/test-connection
Content-Type: application/json

{
  "rut": "77956294-8",
  "password": "Tr7795629."
}
```

Respuesta exitosa:
```json
{
  "success": true,
  "message": "Conexión exitosa con SII"
}
```

## 📁 Estructura del Proyecto

```
backend/
├── app.py                 # App principal de Flask
├── requirements.txt       # Dependencias Python
├── .env.example          # Variables de entorno de ejemplo
├── .gitignore            # Archivos a ignorar en Git
├── services/
│   ├── sii_scraper.py    # Lógica de scraping con Playwright
│   ├── sii_parser.py     # Parseo y normalización de datos
│   └── __init__.py
└── README.md             # Este archivo
```

## 🔒 Seguridad

- Las credenciales se pasan solo por POST (nunca en URL)
- Se configura CORS para controlar qué dominios pueden acceder
- Las credenciales NO se guardan en el servidor (se pasan cada vez)
- Las variables de entorno se configuran localmente

## ⚙️ Configuración

### Variables de entorno (.env)

```
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000

SII_RUT=77956294-8
SII_PASSWORD=Tr7795629.

SUPABASE_URL=https://...
SUPABASE_KEY=...

CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

## 🧪 Testing

### Test manual con curl
```bash
# Health check
curl http://localhost:5000/health

# Sincronizar
curl -X POST http://localhost:5000/api/sync-sii \
  -H "Content-Type: application/json" \
  -d '{
    "rut": "77956294-8",
    "password": "Tr7795629.",
    "mes": 11,
    "ano": 2025
  }'

# Test conexión
curl -X POST http://localhost:5000/api/test-connection \
  -H "Content-Type: application/json" \
  -d '{
    "rut": "77956294-8",
    "password": "Tr7795629."
  }'
```

## 🚢 Desplegar a Railway.app

### 1. Conectar GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/tu-usuario/pluscontable-api
git push -u origin main
```

### 2. En Railway.app
1. Crear nuevo proyecto
2. Conectar repo GitHub
3. Railway automáticamente detectará Python y usará requirements.txt
4. Agregar variables de entorno en settings
5. Deploy automático

### 3. Variables en Railway
```
FLASK_ENV=production
PORT=5000
CORS_ORIGINS=https://tu-app.com
SII_RUT=tu-rut
SII_PASSWORD=tu-password
```

## 📝 Notas

- El scraping puede tardar 30-60 segundos por sincronización
- Recomendable limitar a 1 sincronización por usuario por día
- El SII podría bloquear si hay demasiadas solicitudes desde la misma IP

## 🐛 Troubleshooting

### Error: "Playwright not installed"
```bash
playwright install chromium
```

### Error: "Module not found"
```bash
pip install -r requirements.txt
```

### Error: "Connection timeout"
El SII podría estar bloqueando la IP o tener problemas. Espera unos minutos y reintenta.

## 📚 Referencias

- [Playwright Docs](https://playwright.dev)
- [Flask Docs](https://flask.palletsprojects.com)
- [SII Chile](https://www.sii.cl)
