# Imagen base ligera de Python
FROM python:3.11-slim

# Instalar dependencias del sistema (para pygame necesita estas libs)
RUN apt-get update && apt-get install -y \
    python3-dev \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libportmidi-dev \
    libfreetype6-dev \
    libjpeg-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar dependencias e instalarlas
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de archivos
COPY . .

# Comando de inicio
CMD ["python", "main.py"]
