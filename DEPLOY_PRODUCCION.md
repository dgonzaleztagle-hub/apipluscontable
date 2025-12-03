# Deploy a Producción - Guía Completa

## 🚀 Paso 1: Preparar Código para Deploy

### 1.1 Verificar que todo funciona localmente

```bash
cd backend

# Activar venv
.\venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
pip install playwright
playwright install chromium

# Correr tests
python test_csv_download.py
python test_sync_endpoint.py
```

### 1.2 Crear archivo `.env.production`

```
FLASK_ENV=production
FLASK_DEBUG=False
PORT=5000
CORS_ORIGINS=https://app-lova.vercel.app,https://lova.app,https://tu-dominio.com
```

### 1.3 Actualizar `requirements.txt`

```bash
pip freeze > requirements.txt
```

Debe incluir:
- Flask==3.0.0
- Flask-CORS
- Playwright==1.56.0
- python-dotenv
- gunicorn==21.2.0  (para deploy)

---

## 🚀 Paso 2: Desplegar en Render.com

### 2.1 Conectar GitHub

1. Hacer push a GitHub:
```bash
git add .
git commit -m "Deploy v1.0 - SII scraper funcional"
git push origin main
```

2. Ir a https://render.com
3. Login con GitHub
4. Crear nuevo "Web Service"
5. Seleccionar repositorio

### 2.2 Configurar Build en Render

**Environment:** Python 3.12

**Build Command:**
```bash
pip install -r requirements.txt && playwright install chromium
```

**Start Command:**
```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

### 2.3 Variables de Entorno en Render

En el dashboard de Render, ir a "Environment" y agregar:

```
FLASK_ENV=production
FLASK_DEBUG=False
CORS_ORIGINS=https://app-lova.vercel.app
```

### 2.4 Deploy

Click en "Deploy" y esperar ~3-5 minutos.

La URL será algo como: `https://pluscontable-api.onrender.com`

---

## 🚀 Paso 3: Verificar Deploy

### 3.1 Test Health Check

```bash
curl https://tu-api.onrender.com/health
```

Debe retornar:
```json
{
  "status": "ok",
  "service": "PlusContableAPISII",
  "timestamp": "..."
}
```

### 3.2 Test Endpoint

```bash
curl -X POST https://tu-api.onrender.com/api/sync-books \
  -H "Content-Type: application/json" \
  -d '{
    "rut": "77956294-8",
    "password": "Tr7795629.",
    "mes": 10,
    "ano": 2025
  }'
```

Debe retornar datos de COMPRAS y VENTAS.

---

## 🔐 Paso 4: Seguridad en Producción

### 4.1 HTTPS obligatorio

Render.com proporciona SSL automáticamente. Verificar que siempre se usa HTTPS.

### 4.2 Rate Limiting

Agregar a `app.py`:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/sync-books', methods=['POST'])
@limiter.limit("5 per hour")  # Max 5 syncros por hora
def sync_books():
    ...
```

### 4.3 Headers de Seguridad

```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

### 4.4 Logging de Errores

```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://xxxxx@xxxxx.ingest.sentry.io/xxxxx",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

---

## 📊 Paso 5: Monitoreo

### 5.1 Ver logs en Render

```
Render Dashboard → tu-servicio → Logs
```

### 5.2 Alertas

Configurar en Render para notificaciones por email de:
- Deploy failed
- Build failed
- Runtime error

### 5.3 Health Check Automático

Render.com automáticamente hace ping a `/health` cada minuto.

Si falla 3 veces, marca el servicio como "down".

---

## 🔄 Paso 6: Actualizaciones y Rollback

### 6.1 Hacer cambios

```bash
# En local
git add .
git commit -m "Fix: mejorar logging"
git push origin main
```

### 6.2 Automático

Render.com detecta el push y hace redeploy automáticamente (~3 min).

### 6.3 Rollback (si algo sale mal)

En Render Dashboard → Deployments → Click en versión anterior → "Redeploy"

---

## 📈 Paso 7: Performance & Escalado

### 7.1 Problema: Timeout en Render

Si el scraping tarda >30 segundos, aumentar timeout de Render:

```
Render Dashboard → Settings → HTTP Timeout → 90 segundos
```

### 7.2 Problema: Múltiples sincros simultáneas

Solución 1: Rate limiting (máx 5 por hora)
Solución 2: Upgrade a plan pagado de Render
Solución 3: Usar Cola de Jobs (Redis/Celery)

### 7.3 Monitorear uso de recursos

```
Render Dashboard → tu-servicio → Metrics
```

Ver: CPU, Memoria, Conexiones

---

## 🐛 Troubleshooting

### Error: "Playwright not found"

**Problema:** `playwright install chromium` no ejecutó correctamente en Render

**Solución:**
```dockerfile
# En lugar de gunicorn, usar custom start command
pip install -r requirements.txt && \
playwright install chromium && \
gunicorn app:app --bind 0.0.0.0:$PORT
```

### Error: "Timeout esperando elemento"

**Problema:** SII muy lento o Render server débil

**Solución:** Aumentar timeout en `SIIScraper`:
```python
scraper = SIIScraper(timeout=120000)  # 2 minutos
```

### Error: "CORS error"

**Problema:** `CORS_ORIGINS` no incluye dominio de Lova

**Solución:** Actualizar en Render:
```
CORS_ORIGINS=https://app-lova.vercel.app,https://lova.app
```

### Error: "Invalid credentials"

**Problema:** RUT o contraseña incorrecta del usuario

**Solución:** Verificar que el usuario está enviando credenciales correctas

---

## ✅ Checklist de Deploy

- [ ] `.env.production` creado con valores correctos
- [ ] `requirements.txt` actualizado
- [ ] `gunicorn` agregado a requirements
- [ ] Código testeado localmente
- [ ] Push a GitHub
- [ ] Render conectado a GitHub
- [ ] Build command correcto
- [ ] Start command correcto
- [ ] Variables de entorno configuradas en Render
- [ ] Deploy ejecutado exitosamente
- [ ] Health check respondiendo 200
- [ ] Endpoint `/api/sync-books` funcionando
- [ ] CORS configurado correctamente
- [ ] Rate limiting implementado (opcional)
- [ ] Sentry configurado (opcional)
- [ ] Logs monitoreados

---

## 📞 Soporte Render

- **Chat:** https://render.com/support
- **Docs:** https://render.com/docs
- **Status:** https://status.render.com

---

## 🎯 URL Final

```
https://pluscontable-api.onrender.com/api/sync-books
```

Esta es la URL que debe usar Lova en el botón "Sinc".

---

**Deploy completado! 🎉**
