# Utiliser une image officielle de Python
FROM python:3.11-slim

# Installer quelques outils utiles
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get clean

# Définir le répertoire de travail
WORKDIR /app

# Copier le code
COPY ./app ./app
COPY requirements.txt .
COPY wait-for-postgres.sh .
COPY start.sh .  

# Donner les permissions d'exécution aux scripts
RUN chmod +x /app/wait-for-postgres.sh && chmod +x /app/start.sh  



# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port
EXPOSE 8000

# Commande de démarrage (attend que Postgres soit prêt)
#CMD ["/app/wait-for-postgres.sh", "postgres", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
CMD ["./start.sh"]