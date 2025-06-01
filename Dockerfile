# Usamos Python 3.11 slim como base
FROM python:3.11-slim-bookworm

# Establecemos el directorio de trabajo
WORKDIR /app

# Instalamos las dependencias necesarias para compilar Pillow y otras libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libffi-dev \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Actualizamos pip, setuptools y wheel
RUN pip install --upgrade pip setuptools wheel

# Copiamos el archivo requirements
COPY requirements.txt .

# Instalamos las dependencias Python
RUN pip install -r requirements.txt

# Copiamos el resto del proyecto
COPY . .

# Puerto que expones (opcional, depende de tu app)
EXPOSE 8000

# Comando por defecto (ajusta según tu app)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
