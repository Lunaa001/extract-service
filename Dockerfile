# Stage 1: Builder
FROM python:3.12-slim as builder

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar pyproject.toml
COPY pyproject.toml .

# Instalar dependencias en un directorio virtual
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir .

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Instalar paquetes de sistema en tiempo de ejecución
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar el venv desde el builder
COPY --from=builder /opt/venv /opt/venv

# Copiar el código de la aplicación
COPY . .

# Establecer variables de entorno
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Exponer puerto
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/docs')" || exit 1

# Comando por defecto
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "5000"]
