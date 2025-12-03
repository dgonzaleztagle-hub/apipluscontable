# 🚀 LISTO PARA DESPLEGAR - INSTRUCCIONES FINALES

## ✅ Todo Verificado y Preparado

El repositorio está completamente listo para desplegar a **Render.com**.

**Status:** 16/16 checks pasaron ✅

---

## 📋 Qué Necesitas Hacer

### PASO 1: Push a GitHub (si aún no lo hiciste)

```bash
cd D:\proyectos\pluscontableapisii

# Verificar remote
git remote -v

# Si no tiene remote, agregar:
git remote add origin https://github.com/dgonzaleztagle-hub/apipluscontable.git

# Push
git push -u origin main
```

**Verifica que el código esté en GitHub:**
```
https://github.com/dgonzaleztagle-hub/apipluscontable
```

---

### PASO 2: Ir a Render.com

1. Abre https://render.com
2. Login con GitHub (o crea cuenta)
3. Autoriza Render a acceder a tus repos

---

### PASO 3: Crear New Web Service

En el dashboard de Render:
- Click en "+ New"
- Selecciona "Web Service"

---

### PASO 4: Conectar GitHub

1. Selecciona el repositorio: `apipluscontable`
2. Selecciona branch: `main`
3. Click "Connect"

---

### PASO 5: Configuración del Servicio

**Llenar los siguientes campos:**

```
Name:           pluscontable-api
Environment:    Python 3.12
Region:         Oregon (us-west)
Plan:           Free (sin auto-sleep)
```

---

### PASO 6: Build Command

Copiar exactamente (incluir todas las líneas):

```bash
pip install -r backend/requirements.txt && pip install gunicorn && playwright install chromium
```

**Importante:**
- No olvides `playwright install chromium`
- Esto descarga Chromium (tarda ~2-3 minutos)

---

### PASO 7: Start Command

Copiar exactamente:

```bash
cd backend && gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 1
```

---

### PASO 8: Environment Variables

Click en "Environment" y agregar:

```
FLASK_ENV          = production
FLASK_DEBUG         = False
PYTHONUNBUFFERED    = 1
CORS_ORIGINS        = https://app-lova.vercel.app
```

---

### PASO 9: Crear

Click en "Create Web Service" y espera.

**Tiempo total:** ~7-10 minutos

Verás en los logs:
```
Building...
Downloading dependencies...
Installing Playwright...
Installing Chromium...
Build successful!
Service running at: https://pluscontable-api.onrender.com
```

---

## ✅ Después del Deploy

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

### Test 2: Descargar Libros

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

Debe retornar:
```json
{
  "success": true,
  "data": {
    "COMPRAS": { "cantidad": 1, "registros": [...] },
    "VENTAS": { "cantidad": 1, "registros": [...] }
  }
}
```

---

## 🔗 URL Final

Una vez deployado, la URL será:

```
https://pluscontable-api.onrender.com
```

**Esta es la URL que debes usar en Lova.**

---

## 🎯 Próximo Paso en Lova

En la app Lova, cambiar el endpoint del botón "Sinc" a:

```javascript
// ANTES (local)
fetch('http://localhost:5000/api/sync-books', ...)

// DESPUÉS (producción)
fetch('https://pluscontable-api.onrender.com/api/sync-books', ...)
```

---

## ⚡ Diferencias: Local vs Render

| Aspecto | Local | Render |
|---------|-------|--------|
| URL | http://localhost:5000 | https://pluscontable-api.onrender.com |
| HTTPS | ❌ No | ✅ Sí (automático) |
| Auto-sleep | N/A | ❌ No |
| Timeout | Variable | ✅ Configurable |
| Chromium | En tu PC | ✅ En servidor |
| Performance | Depende tu PC | ✅ Consistente |
| Costo | Gratis | ✅ Gratis (free tier) |

---

## 🆘 Troubleshooting

### "Build failed"
→ Ver logs en Render dashboard, scroll down

### "Timeout esperando elemento"
→ En Start Command, cambiar `--timeout 120` a `--timeout 180`

### "CORS error" en Lova
→ Actualizar `CORS_ORIGINS` en Render para incluir dominio de Lova

### "Conexión rechazada"
→ Esperar 5 minutos después de deploy, Render está iniciando

---

## 📞 Documentación

- **DEPLOY_RENDER_PASO_A_PASO.md** - Guía completa (más detalles)
- **INTEGRACION_LOVA.md** - Cómo integrar en Lova
- **backend/README.md** - Documentación de API

---

## ✅ Checklist Final

- [ ] GitHub remoto configurado
- [ ] Código pusheado a main
- [ ] Cuenta Render creada
- [ ] Web Service creado
- [ ] Build Command pegado
- [ ] Start Command pegado
- [ ] Variables de entorno configuradas
- [ ] Deploy iniciado
- [ ] Health check respondiendo 200
- [ ] Sync-books descargando datos
- [ ] URL del servidor anotada

---

## 🎉 ¡Listo!

**Cuando veas el mensaje en Render:**
```
✓ Service is live at: https://pluscontable-api.onrender.com
```

**Es hora de integrar en Lova y probar el botón "Sinc" en producción. 🚀**

---

*Fecha: 3 de diciembre de 2025*  
*Status: ✅ LISTO PARA DESPLEGAR*
