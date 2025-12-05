# PlusContable API SII

Backend server para integración de libros de compras y ventas desde el SII (Servicio de Impuestos Internos de Chile).

## 📁 Estructura

```
├── backend/          # Servidor Flask (Python)
├── frontend/         # App React (próximo paso)
└── README.md
```

## 🚀 Backend (Este proyecto)

Ver `backend/README.md` para detalles de instalación y uso.

### Stack

- **Framework**: Flask 3.0.0
- **Scraping**: Playwright 1.40.0
- **Python**: 3.12+
- **Hosting**: Railway.app

### API Endpoints

- `GET /health` - Health check
- `POST /api/sync-sii` - Sincronizar libros SII
- `POST /api/test-connection` - Testear credenciales

## 📖 Documentación

- [Backend README](./backend/README.md)
- [Knowledge Base](../KNOWLEDGE_BASE.md)
- [Conversation Summary](../CONVERSATION_SUMMARY.md)

## 🔗 Links

- GitHub: https://github.com/dgonzaleztagle-hub/apipluscontable
- Railway: [Tu proyecto en Railway]

## ⚡ Quick Start

```bash
cd backend
python -m venv venv
source venv/bin/activate  # o: venv\Scripts\activate en Windows
pip install -r requirements.txt
playwright install chromium
python app.py
```

Servidor disponible en `http://localhost:5000`

## 📝 Notas

- Este es solo el backend. El frontend en React se desarrollará en Lovable.
- Las credenciales del SII se pasan en cada request (no se guardan en el servidor).
- El scraping puede tardar 30-60 segundos por sincronización.
# Rebuild trigger
