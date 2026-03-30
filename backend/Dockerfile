# Dockerfile con soporte CUDA para diarización con GPU
# Usar imagen con cuDNN (requerido por onnxruntime-gpu)
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

WORKDIR /app

# Evitar prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive

# Instalar Python 3.12 y dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y --no-install-recommends \
    python3.12 \
    python3.12-venv \
    python3.12-dev \
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
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libswresample-dev \
    espeak-ng \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Configurar python3.12 como default
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.12 1 \
    && update-alternatives --install /usr/bin/python python /usr/bin/python3.12 1

# Instalar pip
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.12

# Copiar requirements
COPY requirements.txt .

# Actualizar pip y herramientas
RUN pip install --upgrade pip setuptools wheel

# Instalar PyTorch con CUDA primero
RUN pip install --no-cache-dir torch torchaudio --index-url https://download.pytorch.org/whl/cu121

# Instalar onnxruntime-gpu compatible con CUDA 12.x (antes de requirements para evitar conflictos)
RUN pip install --no-cache-dir onnxruntime-gpu

# Instalar el resto de dependencias (sin onnxruntime-gpu, ya instalado arriba)
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
