# Usa imagen base ligera
FROM python:3.11-slim

WORKDIR /app

# Instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código
COPY app/ ./app/

# Expone el puerto que Code Engine espera (8080)
EXPOSE 8080

# Comando de arranque
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
