FROM python:3.10-slim

WORKDIR /app

# Dépendances système pour psycopg2 / Postgres
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier les dépendances Python
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du code
COPY . .

# Optionnel mais OK : mode prod + logs non bufferisés
ENV PYTHONUNBUFFERED=1

# Le port utilisé par Flask
EXPOSE 5000

# Lancement de l'app comme dans l’énoncé (python app.py)
# CMD ["python", "app.py"]
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:create_app()"]
