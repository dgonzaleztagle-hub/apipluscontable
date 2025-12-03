# 🚀 Deploy a Render.com - Paso a Paso

## Paso 1: Verificar que GitHub está configurado

Necesitas que tu repositorio esté en GitHub. Ve a:
```
https://github.com/dgonzaleztagle-hub/apipluscontable
```

Si no ves el repositorio allí, necesitas hacer:

```bash
cd D:\proyectos\pluscontableapisii

# Agregar remote a GitHub
git remote add origin https://github.com/dgonzaleztagle-hub/apipluscontable.git

# Push inicial
git branch -M main
git push -u origin main
```

**Nota:** Reemplaza `dgonzaleztagle-hub` con tu usuario de GitHub real.

---

## Paso 2: Ir a Render.com

1. Abrir https://render.com
2. Login con GitHub (si no tienes cuenta, créala)
3. Autorizar Render a acceder a tu GitHub

---

## Paso 3: Crear nuevo servicio en Render

1. Click en "+ New" → "Web Service"
2. Conectar GitHub repository: `apipluscontable`
3. Seleccionar branch: `main`

---

## Paso 4: Configurar Build

**En la página de creación del servicio, llenar:**

```
Name:                pluscontable-api
Environment:         Python 3.12
Region:              Oregon (us-west-1)
Branch:              main
Root Directory:      (dejar vacío)
```

---

## Paso 5: Configurar Build Command

En "Build Command", poner exactamente:

```bash
pip install -r backend/requirements.txt && pip install gunicorn && playwright install chromium
```

**Importante:** Incluye `playwright install chromium` porque Playwright necesita descargar el navegador.

---

## Paso 6: Configurar Start Command

En "Start Command", poner:

```bash
cd backend && gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 1
```

**Explicación:**
- `cd backend`: Entrar a carpeta backend
- `gunicorn app:app`: Ejecutar Flask app
- `--bind 0.0.0.0:$PORT`: Escuchar en puerto (Render lo define)
- `--timeout 120`: Timeout de 120 segundos (para scraping lento)
- `--workers 1`: Solo 1 worker (Playwright no soporta múltiples)

---

## Paso 7: Variables de Entorno

Click en "Environment" y agregar:

```
FLASK_ENV = production
FLASK_DEBUG = False
PYTHONUNBUFFERED = 1
CORS_ORIGINS = https://app-lova.vercel.app,https://lova.app
```

**Importante:**
- `PYTHONUNBUFFERED=1` asegura que los logs aparezcan en tiempo real
- `CORS_ORIGINS` son los dominios de tu app frontend

---

## Paso 8: Plan

Dejar en plan **"Free"** (está bien para testing):
- ✅ Auto-sleep deshabilitado (NO HAY DELAYS)
- ✅ Suficiente CPU/RAM para Playwright
- ✅ 100GB/mes de bandwidth

Si necesitas garantía de disponibilidad, cambiar a plan pagado ($7-12/mes).

---

## Paso 9: Deploy

Click en "Create Web Service" y esperar ~5-10 minutos.

Verás:
1. Build iniciando
2. Descargando dependencias (Playwright tarda ~2 min)
3. Instalando Chromium (tarda ~3 min)
4. Build completado
5. Servicio corriendo

---

## Paso 10: Verificar que Funciona

Una vez que esté "Live", verás URL como:
```
https://pluscontable-api.onrender.com
```

### Test 1: Health Check
```bash
curl https://pluscontable-api.onrender.com/health
```

Debe retornar:
```json
{
  "status": "ok",
  "service": "PlusContableAPISII",
  "timestamp": "..."
}
```

### Test 2: Test de conexión
```bash
curl -X POST https://pluscontable-api.onrender.com/api/test-connection \
  -H "Content-Type: application/json" \
  -d '{
    "rut": "77956294-8",
    "password": "Tr7795629."
  }'
```

Debe retornar:
```json
{
  "success": true,
  "message": "Conexión exitosa con SII"
}
```

### Test 3: Descargar libros
```bash
curl -X POST https://pluscontable-api.onrender.com/api/sync-books \
  -H "Content-Type: application/json" \
  -d '{
    "rut": "77956294-8",
    "password": "Tr7795629.",
    "mes": 10,
    "ano": 2025
  }'
```

Debe retornar data de COMPRAS y VENTAS.

---

## 🔍 Troubleshooting

### Error: "Build failed"

**Ver logs:** Click en servicio → "Logs" → scroll hacia abajo

**Causas comunes:**
1. `requirements.txt` con dependencias incorrectas
   - Solución: Verificar que `flask`, `playwright`, `gunicorn` están
2. Timeout durante `playwright install chromium`
   - Solución: Aumentar timeout o usar plan pagado
3. Ruta incorrecta en Start Command
   - Solución: Verificar que `backend/` existe

### Error: "Timeout esperando elemento"

**Problema:** El SII tarda más de 120 segundos

**Solución:** En Start Command cambiar a:
```bash
cd backend && gunicorn app:app --bind 0.0.0.0:$PORT --timeout 180 --workers 1
```

### Error: "CORS error"

**Problema:** Frontend no puede conectar

**Solución:** Actualizar `CORS_ORIGINS` en Render para incluir dominio de Lova

---

## 📊 Monitoreo en Render

### Ver Logs
```
Dashboard → pluscontable-api → Logs
```

Aparecen en tiempo real (gracias a `PYTHONUNBUFFERED=1`).

### Ver Metrics
```
Dashboard → pluscontable-api → Metrics
```

Ver CPU, Memoria, Network.

### Alertas
```
Dashboard → pluscontable-api → Notifications
```

Configurar email para:
- Deploy failed
- Build failed
- Instance crashed

---

## 🔄 Desplegar Cambios

Si cambias código:

```bash
git add .
git commit -m "Fix: xyz"
git push origin main
```

Render detecta el push automáticamente y redeploy (~5 min).

---

## Alternativas si Render Falla

Si Render tiene problemas o es lento:

### Option 1: Railway.app (Similar a Render)
```
https://railway.app
- Plan free: $5/mes
- Sin auto-sleep
- Muy similar a Render
```

### Option 2: PythonAnywhere (Específico para Python)
```
https://www.pythonanywhere.com
- Plan free: Limitado
- Plan pagado: $5/mes
- Muy simple de usar
```

### Option 3: DigitalOcean App Platform
```
https://www.digitalocean.com/products/app-platform
- $5/mes
- Muy poderoso
- Mejor control
```

---

## ✅ Checklist

- [ ] Repositorio GitHub creado
- [ ] Code pushed a GitHub
- [ ] Cuenta Render creada
- [ ] Nuevo Web Service creado
- [ ] Build Command correcto
- [ ] Start Command correcto
- [ ] Variables de entorno configuradas
- [ ] Deploy completado
- [ ] Health check retorna 200
- [ ] Sync-books retorna datos

---

**¡Cuando esté deployado, la URL será:**
```
https://pluscontable-api.onrender.com/api/sync-books
```

**Esta es la URL que Lova debe usar en el botón "Sinc".**

---

## 📞 Soporte

Si algo no funciona:

1. **Ver Logs en Render** → Ahí dice exactamente qué falló
2. **Testear localmente** → `python test_sync_endpoint.py`
3. **Verificar variables de entorno** → En Render dashboard
4. **Contactar Render support** → https://render.com/support

---

**¡Adelante con el deploy! 🚀**
