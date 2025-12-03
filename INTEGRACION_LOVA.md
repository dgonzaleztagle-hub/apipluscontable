# Integración del Botón "Sinc" en Lova

## 📱 Objetivo

Cuando el usuario hace click en el botón "Sinc" (Sincronizar), descarga COMPRAS y VENTAS del mes seleccionado del SII.

---

## 🔌 Endpoint del Backend

**URL:** `POST https://tu-backend.com/api/sync-books`

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "rut": "77956294-8",
  "password": "Tr7795629.",
  "mes": 10,
  "ano": 2025
}
```

**Response (200 OK):**
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

---

## 💻 Código en Lova

### Opción 1: JavaScript/TypeScript Vanilla

```javascript
async function sincronizarLibros() {
  const botón = document.getElementById('btn-sinc');
  const rut = document.getElementById('input-rut').value;
  const password = document.getElementById('input-password').value;
  const mes = parseInt(document.getElementById('select-mes').value);
  const ano = parseInt(document.getElementById('select-ano').value);
  
  // Mostrar loading
  botón.disabled = true;
  botón.textContent = 'Sincronizando...';
  
  try {
    const response = await fetch('https://tu-backend.com/api/sync-books', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        rut: rut,
        password: password,
        mes: mes,
        ano: ano
      })
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || 'Error en sincronización');
    }
    
    // Éxito
    console.log('Libros descargados:', data.data);
    
    // Guardar los datos en la BD local
    guardarCompras(data.data.COMPRAS.registros, mes, ano);
    guardarVentas(data.data.VENTAS.registros, mes, ano);
    
    // Mostrar notificación
    mostrarNotificacion(
      'Éxito',
      `Se sincronizaron ${data.data.COMPRAS.cantidad} COMPRAS y ${data.data.VENTAS.cantidad} VENTAS`,
      'success'
    );
    
  } catch (error) {
    console.error('Error:', error);
    mostrarNotificacion(
      'Error',
      `No se pudieron sincronizar los libros: ${error.message}`,
      'error'
    );
  } finally {
    // Restaurar botón
    botón.disabled = false;
    botón.textContent = 'Sinc';
  }
}

// Guardar COMPRAS en Supabase
async function guardarCompras(registros, mes, ano) {
  for (const registro of registros) {
    await supabase
      .from('compras')
      .insert({
        empresa_id: currentUser.id,
        mes: mes,
        ano: ano,
        tipo_documento: registro['Tipo Documento'],
        total_documentos: parseInt(registro['Total Documentos']),
        monto_exento: parseFloat(registro['Monto Exento']),
        monto_neto: parseFloat(registro['Monto Neto']),
        iva_recuperable: parseFloat(registro['IVA Recuperable']),
        iva_uso_comun: parseFloat(registro['IVA Uso Comun']),
        iva_no_recuperable: parseFloat(registro['IVA No Recuperable']),
        monto_total: parseFloat(registro['Monto Total']),
        fecha_sincronizacion: new Date().toISOString()
      });
  }
}

// Guardar VENTAS en Supabase
async function guardarVentas(registros, mes, ano) {
  for (const registro of registros) {
    await supabase
      .from('ventas')
      .insert({
        empresa_id: currentUser.id,
        mes: mes,
        ano: ano,
        tipo_documento: registro['Tipo Documento'],
        total_documentos: parseInt(registro['Total Documentos']),
        monto_exento: parseFloat(registro['Monto Exento']),
        monto_neto: parseFloat(registro['Monto Neto']),
        iva_recuperable: parseFloat(registro['IVA Recuperable']),
        iva_uso_comun: parseFloat(registro['IVA Uso Comun']),
        iva_no_recuperable: parseFloat(registro['IVA No Recuperable']),
        monto_total: parseFloat(registro['Monto Total']),
        fecha_sincronizacion: new Date().toISOString()
      });
  }
}

// Llamar función cuando se clickea botón
document.getElementById('btn-sinc').addEventListener('click', sincronizarLibros);
```

---

### Opción 2: React (si Lova usa React)

```jsx
import { useState } from 'react';
import { supabase } from './supabase';

export function SincButton({ mes, ano, onSuccess }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const handleSync = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Obtener credenciales del usuario
      const { data: { user } } = await supabase.auth.getUser();
      const { data: profile } = await supabase
        .from('profiles')
        .select('rut, password')
        .eq('id', user.id)
        .single();
      
      // Llamar endpoint
      const response = await fetch('https://tu-backend.com/api/sync-books', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          rut: profile.rut,
          password: profile.password,
          mes: mes,
          ano: ano
        })
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.error);
      }
      
      // Guardar en Supabase
      await Promise.all([
        guardarCompras(data.data.COMPRAS.registros, mes, ano, user.id),
        guardarVentas(data.data.VENTAS.registros, mes, ano, user.id)
      ]);
      
      onSuccess?.({
        compras: data.data.COMPRAS.cantidad,
        ventas: data.data.VENTAS.cantidad
      });
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <button
      onClick={handleSync}
      disabled={loading}
      className="btn btn-primary"
    >
      {loading ? 'Sincronizando...' : 'Sinc'}
    </button>
  );
}

async function guardarCompras(registros, mes, ano, userId) {
  const compras = registros.map(r => ({
    usuario_id: userId,
    mes,
    ano,
    tipo_documento: r['Tipo Documento'],
    total_documentos: parseInt(r['Total Documentos']),
    monto_exento: parseFloat(r['Monto Exento']),
    monto_neto: parseFloat(r['Monto Neto']),
    iva_recuperable: parseFloat(r['IVA Recuperable']),
    iva_uso_comun: parseFloat(r['IVA Uso Comun']),
    iva_no_recuperable: parseFloat(r['IVA No Recuperable']),
    monto_total: parseFloat(r['Monto Total']),
    fecha_sincronizacion: new Date().toISOString()
  }));
  
  return supabase
    .from('compras')
    .insert(compras);
}

async function guardarVentas(registros, mes, ano, userId) {
  const ventas = registros.map(r => ({
    usuario_id: userId,
    mes,
    ano,
    tipo_documento: r['Tipo Documento'],
    total_documentos: parseInt(r['Total Documentos']),
    monto_exento: parseFloat(r['Monto Exento']),
    monto_neto: parseFloat(r['Monto Neto']),
    iva_recuperable: parseFloat(r['IVA Recuperable']),
    iva_uso_comun: parseFloat(r['IVA Uso Comun']),
    iva_no_recuperable: parseFloat(r['IVA No Recuperable']),
    monto_total: parseFloat(r['Monto Total']),
    fecha_sincronizacion: new Date().toISOString()
  }));
  
  return supabase
    .from('ventas')
    .insert(ventas);
}
```

---

### Opción 3: Vue (si Lova usa Vue)

```vue
<template>
  <button
    @click="sincronizar"
    :disabled="loading"
    class="btn btn-primary"
  >
    {{ loading ? 'Sincronizando...' : 'Sinc' }}
  </button>
</template>

<script>
export default {
  props: {
    mes: Number,
    ano: Number
  },
  data() {
    return {
      loading: false,
      error: null
    };
  },
  methods: {
    async sincronizar() {
      this.loading = true;
      this.error = null;
      
      try {
        const rut = this.$store.state.user.rut;
        const password = this.$store.state.user.password;
        
        const response = await fetch('https://tu-backend.com/api/sync-books', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            rut,
            password,
            mes: this.mes,
            ano: this.ano
          })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.error);
        }
        
        // Guardar en Supabase
        await this.guardarDatos(data.data);
        
        this.$emit('success', {
          compras: data.data.COMPRAS.cantidad,
          ventas: data.data.VENTAS.cantidad
        });
        
      } catch (error) {
        this.error = error.message;
        this.$emit('error', error);
      } finally {
        this.loading = false;
      }
    },
    
    async guardarDatos(data) {
      // Guardar en Supabase...
    }
  }
};
</script>
```

---

## 🔐 Variables de Entorno en Lova

Agregar a `.env.local`:
```
VITE_API_URL=https://tu-backend.com
VITE_API_TIMEOUT=60000
```

---

## 📊 Estructura de BD Supabase Recomendada

### Tabla `compras`
```sql
CREATE TABLE compras (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  usuario_id UUID NOT NULL REFERENCES auth.users(id),
  mes INTEGER NOT NULL CHECK(mes >= 1 AND mes <= 12),
  ano INTEGER NOT NULL,
  tipo_documento TEXT,
  total_documentos INTEGER,
  monto_exento DECIMAL(15,2),
  monto_neto DECIMAL(15,2),
  iva_recuperable DECIMAL(15,2),
  iva_uso_comun DECIMAL(15,2),
  iva_no_recuperable DECIMAL(15,2),
  monto_total DECIMAL(15,2),
  fecha_sincronizacion TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_compras_usuario_periodo ON compras(usuario_id, ano, mes);
```

### Tabla `ventas`
```sql
CREATE TABLE ventas (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  usuario_id UUID NOT NULL REFERENCES auth.users(id),
  mes INTEGER NOT NULL CHECK(mes >= 1 AND mes <= 12),
  ano INTEGER NOT NULL,
  tipo_documento TEXT,
  total_documentos INTEGER,
  monto_exento DECIMAL(15,2),
  monto_neto DECIMAL(15,2),
  iva_recuperable DECIMAL(15,2),
  iva_uso_comun DECIMAL(15,2),
  iva_no_recuperable DECIMAL(15,2),
  monto_total DECIMAL(15,2),
  fecha_sincronizacion TIMESTAMP DEFAULT NOW(),
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_ventas_usuario_periodo ON ventas(usuario_id, ano, mes);
```

---

## ⚙️ Flujo Completo

1. **Usuario abre Lova**
   - Selecciona mes/año
   - Hace click en botón "Sinc"

2. **Frontend (Lova)**
   - Captura RUT, contraseña, mes, año
   - Envía POST a `/api/sync-books`
   - Muestra "Sincronizando..."

3. **Backend**
   - Descarga COMPRAS (paralelo)
   - Descarga VENTAS (paralelo)
   - Retorna JSON con datos

4. **Frontend recibe datos**
   - Guarda COMPRAS en Supabase
   - Guarda VENTAS en Supabase
   - Muestra notificación de éxito

5. **BD actualizada**
   - Tablas compras y ventas tienen registros nuevos
   - Índices permiten consultas rápidas por usuario/periodo

---

## 🧪 Test Manual

Desde consola del navegador:

```javascript
// Test del endpoint
fetch('https://tu-backend.com/api/sync-books', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    rut: '77956294-8',
    password: 'Tr7795629.',
    mes: 10,
    ano: 2025
  })
})
.then(r => r.json())
.then(data => {
  console.log('COMPRAS:', data.data.COMPRAS.cantidad);
  console.log('VENTAS:', data.data.VENTAS.cantidad);
})
.catch(e => console.error('Error:', e));
```

---

## ✅ Checklist de Integración

- [ ] Backend deployado en Render.com / Railway.app
- [ ] Endpoint `/api/sync-books` respondiendo correctamente
- [ ] CORS configurado para permitir dominio de Lova
- [ ] Variables de entorno configuradas en producc ión
- [ ] Código integrado en Lova
- [ ] Tablas creadas en Supabase
- [ ] Test manual realizado
- [ ] Documentación compartida con equipo

---

**¡Listo para integrar!** 🚀
