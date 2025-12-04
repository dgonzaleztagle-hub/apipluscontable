# 🔧 CONFIGURACIÓN RENDER - PASOS MANUALES

## Lo que ves en Render es que busca un Dockerfile que no existe.

La solución es cambiar la configuración para que use Python directamente.

### PASO 1: Root Directory
1. Scroll UP en la página
2. Busca **"Root Directory"** (optional)
3. Click el Edit (lápiz)
4. Pon: `backend`
5. Save

### PASO 2: Dockerfile Path
1. Scroll down un poco
2. Busca **"Dockerfile Path"**
3. Click el Edit (lápiz)
4. Borra todo y pon: `/dev/null` (esto hace que ignore Dockerfile)
5. Save

### PASO 3: Build Command
1. Busca **"Build & Deploy"** en el settings
2. Si hay un campo "Build Command", pon:
```
pip install -r requirements.txt && pip install gunicorn && playwright install chromium
```

### PASO 4: Start Command (o Docker Command)
Si ves "Docker Command", pon:
```
gunicorn app:app --bind 0.0.0.0:$PORT --timeout 120 --workers 1
```

Si ves "Start Command", pon lo mismo.

### PASO 5: Manual Deploy
Una vez guardado todo, click en **"Manual Deploy"** o espera a que auto-deploy.

---

## ¿Por qué funciona?
- Root Directory = `backend` → Render corre desde `backend/`
- Dockerfile Path = `/dev/null` → Ignora Docker, usa Python nativo
- Build + Start commands → Python instala dependencias y corre gunicorn

---

## Test después
```bash
curl https://apipluscontable.onrender.com/health
```

Debería ver `/api/sync-books` en la lista de endpoints.
