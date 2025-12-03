# 🔧 PROBLEMA CON RENDER - SOLUCIÓN MANUAL

## Situación Actual

✅ **Código en GitHub**: El endpoint `/api/sync-books` EXISTE en GitHub (confirmado)
✅ **Rutas en app.py**: Verificadas localmente - todas las 5 rutas cargadas correctamente
❌ **Render**: Sigue devolviendo 404 para `/api/sync-books` (usa versión vieja en caché)

## Razón del Problema

Render no está leyendo correctamente los cambios. Es posible que:
1. Render.yaml no se esté aplicando
2. Hay un caché en Render
3. El deploy se detuvo a mitad

## Solución - Manual Deploy en Render

### Opción 1: Forzar Redeploy Desde Render Dashboard

1. Ve a https://dashboard.render.com
2. Click en "pluscontable-api"
3. Scroll down → Click en "Deploy latest commit" o "Manual Deploy"
4. Espera 5-10 minutos
5. Test: `curl https://apipluscontable.onrender.com/health`

### Opción 2: Si el Manual Deploy No Funciona

1. En Render Dashboard → Settings
2. Scroll down → "Deploys"
3. Click en el último deploy con el icono ❌ o ⏸️
4. Click en "Redeploy"

### Opción 3: Si Render Sigue Sin Actualizar

Probablemente hay un problema con render.yaml. En ese caso:

1. En Render Dashboard → Settings
2. Build Command → Reemplaza con:
```bash
pip install -r backend/requirements.txt && pip install gunicorn && playwright install chromium
```

3. Start Command → Reemplaza con:
```bash
cd backend && gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 1
```

4. Click Save
5. Click "Manual Deploy"

---

## ✅ Verificación Después del Deploy

Cuando Render esté actualizado, verás:

```bash
curl -X POST "https://apipluscontable.onrender.com/api/sync-books" \
  -H "Content-Type: application/json" \
  -d '{
    "rut": "77956294-8",
    "password": "Tr7795629.",
    "mes": 12,
    "ano": 2025
  }'
```

Debería retornar: `{"success": true, "data": {...}}` (no 404)

---

## 📝 Notas

- El código LOCAL está 100% correcto
- GitHub tiene el código correcto
- Render es el único problema
- Esto es un error de sincronización Render ↔ GitHub

---

**Siguiente**: Una vez Render esté actualizado, corremos el test completo.
