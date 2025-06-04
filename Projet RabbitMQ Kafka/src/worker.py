#!/usr/bin/env python3
"""
Worker pour effectuer les calculs distribués
Usage: python worker.py <operation> [--verbose]
"""

import sys
import os
import time
import random
import argparse
import pika
from colorama import init, Fore, Style

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.rabbitmq_config import *
from utils.message_utils import *

# Initialiser colorama pour les couleurs dans le terminal
init()


class CalculationWorker:
    def __init__(self, operation: str, verbose: bool = False):
        self.operation = operation
        self.verbose = verbose
        self.worker_id = f"worker_{operation}_{random.randint(1000, 9999)}"
        self.processed_count = 0
        self.connection = None
        self.channel = None
        
        print(f"{Fore.GREEN}🚀 Worker {self.worker_id} démarré pour l'opération '{operation}'{Style.RESET_ALL}")
        
    def connect_to_rabbitmq(self):
        """Établit la connexion à RabbitMQ"""
        connection_params = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        )
        
        max_retries = 5
        for attempt in range(max_retries):
            try:
                self.connection = pika.BlockingConnection(connection_params)
                self.channel = self.connection.channel()
                
                # Déclarer les queues
                task_queue = TASK_QUEUES[self.operation]
                self.channel.queue_declare(queue=task_queue, durable=True)
                self.channel.queue_declare(queue=RESULT_QUEUE, durable=True)
                
                # Déclarer l'exchange pour les opérations "all"
                self.channel.exchange_declare(exchange=ALL_OPERATIONS_EXCHANGE, exchange_type='fanout')
                
                # Lier la queue à l'exchange pour les opérations "all"
                self.channel.queue_bind(exchange=ALL_OPERATIONS_EXCHANGE, queue=task_queue)
                
                print(f"{Fore.CYAN}✅ Connexion à RabbitMQ établie{Style.RESET_ALL}")
                return True
                
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️  Tentative {attempt + 1}/{max_retries} échouée: {e}{Style.RESET_ALL}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    
        print(f"{Fore.RED}❌ Impossible de se connecter à RabbitMQ après {max_retries} tentatives{Style.RESET_ALL}")
        return False
    
    def process_message(self, channel, method, properties, body):
        """Traite un message de calcul"""
        try:
            # Désérialiser le message
            message_str = body.decode('utf-8')
            task_message = deserialize_message(message_str)
            
            if self.verbose:
                print(f"{Fore.BLUE}📨 Message reçu: {serialize_message(task_message)}{Style.RESET_ALL}")
            
            # Valider le message
            if not validate_task_message(task_message):
                print(f"{Fore.RED}❌ Message invalide reçu{Style.RESET_ALL}")
                channel.basic_ack(delivery_tag=method.delivery_tag)
                return
            
            # Vérifier que l'opération correspond
            if task_message["operation"] != self.operation:
                if self.verbose:
                    print(f"{Fore.YELLOW}⚠️  Message pour une autre opération ignoré: {task_message['operation']}{Style.RESET_ALL}")
                channel.basic_ack(delivery_tag=method.delivery_tag)
                return
            
            # Simuler le temps de traitement (5-15 secondes)
            processing_time = random.uniform(
                WORKER_PROCESSING_TIME['min'], 
                WORKER_PROCESSING_TIME['max']
            )
            
            print(f"{Fore.MAGENTA}⏳ Traitement de {task_message['n1']} {self.operation} {task_message['n2']} "
                  f"(temps estimé: {processing_time:.1f}s){Style.RESET_ALL}")
            
            start_time = time.time()
            time.sleep(processing_time)
            actual_processing_time = time.time() - start_time
            
            # Effectuer le calcul
            result = perform_operation(
                task_message["operation"], 
                task_message["n1"], 
                task_message["n2"]
            )
            
            # Créer le message de résultat
            result_message = create_result_message(
                task_message, result, self.worker_id, actual_processing_time
            )
            
            # Envoyer le résultat dans la queue des résultats
            self.channel.basic_publish(
                exchange='',
                routing_key=RESULT_QUEUE,
                body=serialize_message(result_message),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            
            self.processed_count += 1
            print(f"{Fore.GREEN}✅ Calcul terminé: {task_message['n1']} {self.operation} {task_message['n2']} = {result} "
                  f"(Total traité: {self.processed_count}){Style.RESET_ALL}")
            
            # Acquitter le message
            channel.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors du traitement: {e}{Style.RESET_ALL}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def start_consuming(self):
        """Démarre l'écoute des messages"""
        if not self.connect_to_rabbitmq():
            return
        
        # Configuration du consumer
        task_queue = TASK_QUEUES[self.operation]
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=task_queue,
            on_message_callback=self.process_message
        )
        
        print(f"{Fore.CYAN}👂 En écoute des messages sur la queue '{task_queue}'...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   Pour arrêter, appuyez sur CTRL+C{Style.RESET_ALL}")
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⏹️  Arrêt du worker {self.worker_id}...{Style.RESET_ALL}")
            self.channel.stop_consuming()
            self.connection.close()
            print(f"{Fore.GREEN}✅ Worker arrêté proprement. Total traité: {self.processed_count}{Style.RESET_ALL}")


def main():
    parser = argparse.ArgumentParser(description='Worker pour calculs distribués')
    parser.add_argument('operation', choices=['add', 'sub', 'mul', 'div'],
                        help='Type d\'opération à traiter')
    parser.add_argument('--verbose', action='store_true',
                        help='Mode verbose avec plus de détails')
    
    args = parser.parse_args()
    
    worker = CalculationWorker(args.operation, args.verbose)
    worker.start_consuming()


if __name__ == '__main__':
    main() 