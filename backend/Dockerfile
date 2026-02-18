# Dockerfile simplificado - Una sola etapa
FROM python:3.12

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    libsndfile1-dev \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Actualizar pip y herramientas
RUN pip install --upgrade pip setuptools wheel

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Crear directorios
RUN mkdir -p uploads temp logs

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
