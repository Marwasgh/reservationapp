#!/bin/sh

# Attendre que Postgres soit prêt
echo "Waiting for postgres..."

while ! nc -z $1 5432; do
  sleep 0.1
done

echo "PostgreSQL started."

# Lancer la commande suivante
shift
exec "$@"