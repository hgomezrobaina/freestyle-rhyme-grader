# 🐳 Guía de Docker para Backend

## Archivos Creados

Tu backend ahora tiene todo configurado para Docker:

### 📄 Dockerfile

- **Multi-stage build**: Optimiza el tamaño de la imagen (builder + runtime)
- **Python 3.11-slim**: Imagen ligera y segura
- **FFmpeg incluido**: Necesario para análisis de audio
- **Health check**: Verifica que la API esté viva
- **Directorio /app**: Punto de trabajo

### 📄 .dockerignore

Excluye archivos innecesarios de la imagen Docker:

- Logs, caché de Python, .git
- Variables de entorno locales
- Directorios temporales

### 📄 docker-compose.yml (Actualizado)

Ahora incluye 3 servicios integrados:

1. **postgres**: Base de datos
2. **redis**: Cache y mensaje broker
3. **backend**: Tu servidor FastAPI

## 🚀 Cómo Usar

### Opción 1: Construcción y ejecución manual

```bash
# Construir imagen Docker
docker build -t freestyle-backend .

# Ejecutar contenedor
docker run -p 8000:8000 \
  --env DATABASE_URL="postgresql://freestyle_user:freestyle_password@localhost:5432/freestyle_callificator" \
  --env REDIS_URL="redis://localhost:6379/0" \
  freestyle-backend
```

### Opción 2: Docker Compose (RECOMENDADO) ⭐

```bash
# Iniciar todos los servicios
docker-compose up

# Ejecutar en segundo plano
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Detener servicios
docker-compose down

# Eliminar volúmenes (limpia todo)
docker-compose down -v
```

## 📋 Requisitos Previos

- Docker Desktop instalado
- En Windows: WSL2 configurado
- En la carpeta `backend/` del proyecto

## ✅ Verificación

Una vez levantado el contenedor, accede a:

```
http://localhost:8000/          → API raíz
http://localhost:8000/docs      → Documentación Swagger
http://localhost:8000/redoc     → ReDoc
http://localhost:8000/health    → Health check
```

## 📊 Servicios Internos

Cuando usas `docker-compose`, los servicios se comunican por:

```
Backend → postgres:5432  (Base de datos)
Backend → redis:6379     (Cache/Queue)
```

**No** necesitas especificar `localhost` en las URLs internas.

## 🔧 Configuración

El archivo `docker-compose.yml` establece automáticamente estas variables:

```yaml
DATABASE_URL: postgresql://freestyle_user:freestyle_password@postgres:5432/freestyle_callificator
REDIS_URL: redis://redis:6379/0
CELERY_BROKER_URL: redis://redis:6379/0
```

Si necesitas cambiar credenciales, edita el archivo `docker-compose.yml`.

## 💾 Volúmenes Persistentes

Los siguientes directorios se persisten en tu máquina:

- `uploads/` → Archivos subidos por usuarios
- `temp/` → Archivos temporales
- `logs/` → Logs de la aplicación
- `postgres_data` → Base de datos (volumen Docker)

## 🛑 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'pkg_resources'"

**Causa:** setuptools o dependencias de compilación no están disponibles

**Solución:** Este error se ha corregido en el Dockerfile actualizado. Si aún lo ves:

```bash
# Borrar imagen anterior y reconstruir
docker-compose down
docker system prune -a  # Elimina imágenes antiguas
docker-compose up --build
```

### Error: "Connection refused"

```bash
# Verifica que los servicios estén corriendo
docker-compose ps

# Reinicia los servicios
docker-compose restart
```

### Error: "Database connection failed"

```bash
# Espera a que PostgreSQL esté listo
docker-compose logs postgres

# Podría tardar 10-20 segundos en inicializar
```

### Limpiar todo y empezar de cero

```bash
docker-compose down -v
docker-compose up -d
```

### Ver logs en tiempo real

```bash
docker-compose logs -f backend          # Solo backend
docker-compose logs -f                  # Todos los servicios
```

## 🚢 Producción

Para producción, considera:

1. **Usar variables de entorno seguras** (no hardcodeadas)
2. **Configurar HTTPS** con reverse proxy (Nginx)
3. **Limitar recursos** con memoria/CPU límites
4. **Usar arquitectura escalable** con orquestador (Kubernetes)
5. **Monitoreo y logging centralizado** (ELK Stack, etc.)

## 📝 Notas

- La imagen se construye automáticamente con `docker-compose up`
- El recompilado ocurre si cambias `requirements.txt`
- Los logs están disponibles con `docker-compose logs`
- El reinicio automático está habilitado (`restart: unless-stopped`)
