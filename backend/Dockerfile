FROM python:3.9-slim

WORKDIR /app

# Copiar requirements desde backend/ (porque context es la raíz)
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar TODO el proyecto (backend/, frontend/, database/)
COPY . /app/

WORKDIR /app/backend

CMD ["python", "app.py"]
