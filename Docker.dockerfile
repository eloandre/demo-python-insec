# Dockerfile para insecure-python-app
FROM python:3.11-slim

WORKDIR /app

# Copia requirements e instala (dependências antigas/inseguras intencionais)
COPY requirements.txt .

# Instalar sem cache para reduzir tamanho
RUN pip install --no-cache-dir -r requirements.txt

# Copia app
COPY app.py .

EXPOSE 3000

CMD ["python", "app.py"]

