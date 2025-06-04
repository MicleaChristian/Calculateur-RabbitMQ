"""Configuration pour RabbitMQ"""

import os

# Configuration de connexion RabbitMQ
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')

# Noms des queues
TASK_QUEUES = {
    'add': 'task_queue_add',
    'sub': 'task_queue_sub',
    'mul': 'task_queue_mul',
    'div': 'task_queue_div'
}

RESULT_QUEUE = 'result_queue'

# Configuration des workers
WORKER_PROCESSING_TIME = {
    'min': 5,  # secondes
    'max': 15  # secondes
}

# Configuration du client producteur
CLIENT_SEND_INTERVAL = 5  # secondes entre chaque envoi automatique

# Exchange pour les opérations "all"
ALL_OPERATIONS_EXCHANGE = 'all_operations' 