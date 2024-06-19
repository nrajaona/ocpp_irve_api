# Utilise une image officielle de Python comme image de base
FROM python:3.9-slim

# Définit le répertoire de travail
WORKDIR /app

# Copie les fichiers de dépendances dans le répertoire de travail
COPY requirements.txt .

# Installe les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copie le reste de l'application dans le répertoire de travail
COPY . .

# Expose le port sur lequel l'application va tourner
EXPOSE 8001

# Commande pour démarrer l'application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]