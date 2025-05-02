#!/bin/bash

# Attendre que Postgres soit prêt
/app/wait-for-postgres.sh postgres

# Attendre que Kafka soit prêt (port 9092 sur kafka)
echo "Waiting for Kafka..."
while ! nc -z kafka 9092; do
  sleep 1
done
echo "Kafka is up!"

# Lancer le consumer Kafka en arrière-plan
python /app/app/consumer.py &

# Lancer FastAPI
uvicorn app.main:app --host 0.0.0.0 --port 8000