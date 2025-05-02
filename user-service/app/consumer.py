import time
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from confluent_kafka import Consumer, KafkaException, KafkaError
import json
def wait_for_kafka():
    while True:
        try:
            consumer = KafkaConsumer(bootstrap_servers='kafka:9092')
            consumer.close()
            print("✅ Kafka est prêt !")
            break
        except NoBrokersAvailable:
            print("⏳ En attente de Kafka...")
            time.sleep(3)


wait_for_kafka()




# Configuration du consommateur
conf = {
    'bootstrap.servers': 'kafka:9092',  # Adresse de ton broker Kafka
    'group.id': 'auth-consumer-group',  # Identifiant du groupe de consommateurs
    'auto.offset.reset': 'earliest'     # Commencer à consommer à partir du début du topic
}

# Création du consommateur
consumer = Consumer(conf)

# Liste des topics à consommer
topics = ['reservation.created', 'reservation.cancelled']  

# S'abonner aux topics
consumer.subscribe(topics)

# Fonction pour traiter les messages reçus
def process_message(message):
    try:
        # Décoder le message JSON
        data = json.loads(message.value().decode('utf-8'))
        print(f"Message reçu: {data}")
        # Ici tu peux ajouter ton code pour traiter le message
    except Exception as e:
        print(f"Erreur lors du traitement du message: {e}")

# Boucle pour consommer les messages
try:
    while True:
        # Récupérer les messages (les messages seront récupérés en bloc)
        msg = consumer.poll(timeout=1.0)  # Attend 1 seconde si aucun message

        if msg is None:
            continue  # Aucun message disponible

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                print(f"Atteint la fin de la partition {msg.partition}, offset {msg.offset()}")
            else:
                raise KafkaException(msg.error())
        else:
            # Traiter le message
            process_message(msg)

except KeyboardInterrupt:
    print("Arrêt du consommateur")

finally:
    # Fermeture du consommateur pour libérer les ressources
    consumer.close()