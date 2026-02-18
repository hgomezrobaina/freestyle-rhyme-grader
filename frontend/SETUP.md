# Setup Frontend - Integración con Backend

## 1️⃣ Configuración del Archivo .env.local

### Paso 1: Copiar el template

```bash
cd frontend
cp .env.local.example .env.local
```

### Paso 2: Configurar según tu entorno

#### Para Desarrollo Local (Recomendado con Docker)

Si ejecutas el backend con Docker Compose:

```bash
# En la carpeta backend/
docker-compose up
```

Entonces tu `.env.local` debe ser:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

#### Para Producción

Si tu backend está en un dominio/servidor remoto:

```env
NEXT_PUBLIC_API_URL=https://tu-dominio.com
```

**OJO:** Asegúrate de que el backend permita CORS desde tu dominio frontend (verificar `app/main.py`).

---

## 2️⃣ Iniciar el Frontend

### Instalar dependencias (primera vez)

```bash
cd frontend
npm install
```

### Ejecutar servidor de desarrollo

```bash
npm run dev
```

La aplicación estará en: **http://localhost:3000**

### Acceder a la página de upload

```
http://localhost:3000/upload
```

---

## 3️⃣ Flujo de Upload y Procesamiento

### Opción A: Subir Archivo Local

1. Ve a `/upload`
2. Selecciona **"Subir Video"**
3. Arrastra o selecciona tu archivo (video)
4. Completa los datos:
   - **Título** (obligatorio): ej. "Chuty vs Aczino"
   - **MC 1** (obligatorio): ej. "Chuty"
   - **MC 2** (obligatorio): ej. "Aczino"
   - **Evento** (opcional): ej. "FMS Internacional"
   - **Rounds** (1-5)
5. Click **"Subir Batalla"**
6. ✅ Se redirige a `/battle/{id}` donde puedes ver el progreso

### Opción B: Desde YouTube

1. Ve a `/upload`
2. Selecciona **"Link de YouTube"** (opción por defecto)
3. Pega el URL del video:
   - ✅ Acepta: `https://www.youtube.com/watch?v=...`
   - ✅ Acepta: `https://youtu.be/...`
   - ✅ Acepta: `https://youtube.com/shorts/...`
4. Se mostrará preview con thumbnail
5. Completa los datos (igual que en Opción A)
6. Click **"Agregar desde YouTube"**
7. ✅ Se redirige a `/battle/{id}` donde puedes ver el progreso

---

## 4️⃣ Página de Batalla en Procesamiento

Cuando se redirige a `/battle/{id}?uploading=true`, el frontend:

1. **Activa polling automático** cada 2 segundos
2. **Muestra el estado:**
   - 🔄 "Descargando video..."
   - 🔄 "Transcribiendo..."
   - 🔄 "Analizando rimas..."
   - ✅ "Procesamiento completo"
3. **Cuando termina:**
   - ✅ Muestra versos extraídos
   - ✅ Muestra métricas de rimas
   - ✅ Permite votar calificaciones

---

## 5️⃣ Estructura de Carpetas Frontend

```
frontend/
├── app/
│   ├── upload/page.tsx           ← Página de upload (INTEGRADA ✅)
│   ├── battle/[id]/page.tsx      ← Página de batalla (necesita polling)
│   └── ...
├── components/
│   ├── upload-dropzone.tsx       ← Drag & drop
│   ├── battle-view.tsx           ← Vista de batalla
│   └── ...
├── lib/
│   ├── api.ts                    ← Cliente HTTP (NUEVO ✅)
│   ├── youtube.ts                ← Validación YouTube
│   └── ...
├── hooks/
│   └── use-battle-status.ts      ← Polling (NUEVO ✅)
└── .env.local.example            ← Template (NUEVO ✅)
```

---

## 6️⃣ Troubleshooting

### Error: "API Error: 404" o "Connection refused"

**Causa:** El backend no está corriendo

**Solución:**

```bash
# En otra terminal, dentro de backend/
docker-compose up

# O sin Docker, si tienes Python:
python -m uvicorn app.main:app --reload
```

### Error: "CORS policy"

**Causa:** El backend no permite conexiones desde tu dominio frontend

**Solución:** Verificar `backend/app/main.py` línea de CORS:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En desarrollo está permitido todo
    # En producción, especificar: ["https://tu-dominio.com"]
)
```

### El upload queda en "processing" indefinidamente

**Causa:** El procesamiento de background en el backend está fallando

**Solución:** Ver logs del backend:

```bash
docker-compose logs backend
# o
docker logs freestyle_backend
```

### Timeout o error en el upload

**Causa:** Archivo muy grande o conexión lenta

**Solución:**

- Máximo permitido: 1GB
- Frontend valida en 500MB por UX
- Verificar velocidad de internet

---

## 7️⃣ Desarrollo y Debugging

### Ver requests en tiempo real

Abre **DevTools del navegador** (F12):

1. Pestaña **Network**
2. Filtra por **Fetch/XHR**
3. Cada request muestra método, URL, status, response

### Variables de entorno

El frontend usa `process.env.NEXT_PUBLIC_API_URL` que es:

```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
```

Solo variables con prefijo `NEXT_PUBLIC_` son visibles en el navegador.

### Build para producción

```bash
npm run build   # Compilar
npm run start   # Ejecutar versión producción
```

---

## 8️⃣ Próximos Pasos para Completar

Para que la experiencia sea completa, también necesitas:

1. **Actualizar `/battle/[id]/page.tsx`** para usar el hook `useBattleStatus()`
2. **Mostrar los versos** cuando el status sea "completed"
3. **Implementar votación/ratings** en los versos (opcional)

---

## ✅ Resumen Rápido

```bash
# 1. Setup
cd frontend
cp .env.local.example .env.local
npm install

# 2. Asegurar que el backend esté corriendo (otra terminal)
cd backend
docker-compose up

# 3. Iniciar frontend
cd frontend
npm run dev

# 4. Ir a http://localhost:3000/upload
```

¡Listo! El upload está integrado con el backend.
