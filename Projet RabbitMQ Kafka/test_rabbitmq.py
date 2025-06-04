#!/usr/bin/env python3
"""Script de test pour vérifier RabbitMQ directement"""

import pika
import json
import sys
import os

# Ajouter le répertoire courant au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.rabbitmq_config import *
from utils.message_utils import *

def test_rabbitmq():
    print("🔧 Test de connectivité RabbitMQ...")
    
    try:
        # Connexion
        connection_params = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        )
        
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()
        print("✅ Connexion RabbitMQ réussie")
        
        # Déclarer les queues
        for operation, queue_name in TASK_QUEUES.items():
            channel.queue_declare(queue=queue_name, durable=True)
            print(f"✅ Queue {queue_name} déclarée")
        
        # Envoyer une tâche test
        test_message = create_task_message(100, 25, "add", source="web")
        queue_name = TASK_QUEUES["add"]
        
        channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            body=serialize_message(test_message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        
        print(f"✅ Message test envoyé vers {queue_name}:")
        print(f"📨 {test_message}")
        
        # Vérifier les queues
        print("\n📊 État des queues:")
        for operation, queue_name in TASK_QUEUES.items():
            method = channel.queue_declare(queue=queue_name, durable=True, passive=True)
            count = method.method.message_count
            print(f"  {queue_name}: {count} messages")
        
        connection.close()
        print("🎉 Test terminé avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_rabbitmq() 