# ✅ LISTO PARA DESPLEGAR EN RENDER

## El código ya está en GitHub

**Repositorio:** https://github.com/dgonzaleztagle-hub/apipluscontable

Verificar que ves el código ahí.

---

## 🚀 Pasos para Desplegar en Render

### 1. Ir a Render.com

https://render.com

### 2. Login con GitHub

Click en "Sign up" o "Log in" con GitHub.

### 3. Autorizar Render a acceder a tus repos

Render va a pedir permiso. Click "Authorize".

### 4. En el dashboard de Render

Click en "+ New" → "Web Service"

### 5. Conectar repositorio

1. Click en "Connect a repository"
2. Seleccionar: `apipluscontable`
3. Click "Connect"

### 6. Llenar configuración

```
Name:           pluscontable-api
Environment:    Python 3.12
Region:         Oregon (us-west)
Plan:           Free (no auto-sleep)
```

### 7. Build Command

Pega exactamente esto:

```bash
pip install -r backend/requirements.txt && pip install gunicorn && playwright install chromium
```

### 8. Start Command

Pega exactamente esto:

```bash
cd backend && gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 1
```

### 9. Environment Variables

Click en "Environment" y agrega:

```
FLASK_ENV = production
FLASK_DEBUG = False
PYTHONUNBUFFERED = 1
CORS_ORIGINS = https://app-lova.vercel.app
```

### 10. Click "Create Web Service"

Espera 7-10 minutos.

---

## ✅ Después del Deploy

Una vez que veas "✓ Your service is live", la URL será algo como:

```
https://pluscontable-api.onrender.com
```

### Test rápido

```bash
curl https://pluscontable-api.onrender.com/health
```

Debe retornar JSON con `"status": "ok"`.

---

## 🎯 URL para Lova

Usa esta URL en el botón "Sinc" de Lova:

```
https://pluscontable-api.onrender.com/api/sync-books
```

**¡Eso es todo!**

---

*Nota: Render automáticamente redeploya cuando haces push a GitHub.*
