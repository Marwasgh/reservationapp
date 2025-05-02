from confluent_kafka import Producer
import json
import os

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "kafka:9092")

conf = {'bootstrap.servers': KAFKA_BROKER}
producer = Producer(**conf)

def delivery_report(err, msg):
    if err is not None:
        print(f"Échec de livraison : {err}")
    else:
        print(f"Message livré à {msg.topic()} [{msg.partition()}]")

def envoyer_evenement(topic: str, message: dict):
    producer.produce(
        topic=topic,
        value=json.dumps(message).encode('utf-8'),
        callback=delivery_report
    )
    producer.flush()