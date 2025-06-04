#!/usr/bin/env python3
"""
Client producteur qui envoie des requêtes de calcul automatiquement
Usage: python client_producer.py [--interval SECONDS] [--count NUMBER]
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

# Initialiser colorama
init()


class TaskProducer:
    def __init__(self, interval: float = CLIENT_SEND_INTERVAL):
        self.interval = interval
        self.sent_count = 0
        self.connection = None
        self.channel = None
        
        print(f"{Fore.GREEN}🚀 Client producteur démarré (intervalle: {interval}s){Style.RESET_ALL}")
        
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
                
                # Déclarer toutes les queues
                for operation, queue_name in TASK_QUEUES.items():
                    self.channel.queue_declare(queue=queue_name, durable=True)
                
                # Déclarer l'exchange pour les opérations "all"
                self.channel.exchange_declare(exchange=ALL_OPERATIONS_EXCHANGE, exchange_type='fanout')
                
                print(f"{Fore.CYAN}✅ Connexion à RabbitMQ établie{Style.RESET_ALL}")
                return True
                
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️  Tentative {attempt + 1}/{max_retries} échouée: {e}{Style.RESET_ALL}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    
        print(f"{Fore.RED}❌ Impossible de se connecter à RabbitMQ après {max_retries} tentatives{Style.RESET_ALL}")
        return False
    
    def generate_random_task(self):
        """Génère une tâche aléatoire"""
        operations = ['add', 'sub', 'mul', 'div', 'all']
        operation = random.choice(operations)
        
        # Générer des nombres aléatoires
        n1 = round(random.uniform(1, 100), 2)
        n2 = round(random.uniform(1, 100), 2)
        
        # Éviter la division par zéro
        if operation == 'div' and n2 == 0:
            n2 = 1
            
        return n1, n2, operation
    
    def send_task(self, n1: float, n2: float, operation: str):
        """Envoie une tâche de calcul"""
        try:
            if operation == 'all':
                # Pour l'opération "all", envoyer à toutes les queues via l'exchange
                for op in ['add', 'sub', 'mul', 'div']:
                    task_message = create_task_message(n1, n2, op)
                    
                    # Publier via l'exchange fanout
                    self.channel.basic_publish(
                        exchange=ALL_OPERATIONS_EXCHANGE,
                        routing_key='',
                        body=serialize_message(task_message),
                        properties=pika.BasicProperties(delivery_mode=2)
                    )
                    
                print(f"{Fore.BLUE}📤 Tâche 'all' envoyée: {n1} × 4_opérations × {n2}{Style.RESET_ALL}")
                self.sent_count += 4  # Compter les 4 opérations
                
            else:
                # Opération normale
                task_message = create_task_message(n1, n2, operation)
                queue_name = TASK_QUEUES[operation]
                
                self.channel.basic_publish(
                    exchange='',
                    routing_key=queue_name,
                    body=serialize_message(task_message),
                    properties=pika.BasicProperties(delivery_mode=2)
                )
                
                print(f"{Fore.BLUE}📤 Tâche envoyée: {n1} {operation} {n2} (ID: {task_message['request_id'][:8]}){Style.RESET_ALL}")
                self.sent_count += 1
                
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de l'envoi: {e}{Style.RESET_ALL}")
    
    def start_automatic_sending(self, max_count: int = None):
        """Démarre l'envoi automatique de tâches"""
        if not self.connect_to_rabbitmq():
            return
        
        print(f"{Fore.CYAN}🔄 Envoi automatique démarré (CTRL+C pour arrêter){Style.RESET_ALL}")
        
        try:
            while True:
                if max_count and self.sent_count >= max_count:
                    print(f"{Fore.GREEN}✅ Nombre maximum de tâches envoyées ({max_count}){Style.RESET_ALL}")
                    break
                
                # Générer et envoyer une tâche aléatoire
                n1, n2, operation = self.generate_random_task()
                self.send_task(n1, n2, operation)
                
                # Attendre avant le prochain envoi
                time.sleep(self.interval)
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⏹️  Arrêt du client producteur...{Style.RESET_ALL}")
        finally:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            print(f"{Fore.GREEN}✅ Client arrêté. Total envoyé: {self.sent_count} tâches{Style.RESET_ALL}")
    
    def send_manual_task(self, n1: float, n2: float, operation: str):
        """Envoie une tâche manuelle"""
        if not self.connect_to_rabbitmq():
            return False
        
        self.send_task(n1, n2, operation)
        self.connection.close()
        return True


def main():
    parser = argparse.ArgumentParser(description='Client producteur de tâches de calcul')
    parser.add_argument('--interval', type=float, default=CLIENT_SEND_INTERVAL,
                        help=f'Intervalle entre les envois en secondes (défaut: {CLIENT_SEND_INTERVAL})')
    parser.add_argument('--count', type=int, 
                        help='Nombre maximum de tâches à envoyer (illimité par défaut)')
    parser.add_argument('--manual', nargs=3, metavar=('N1', 'N2', 'OP'),
                        help='Envoyer une tâche manuelle: N1 N2 OPERATION')
    
    args = parser.parse_args()
    
    producer = TaskProducer(args.interval)
    
    if args.manual:
        try:
            n1 = float(args.manual[0])
            n2 = float(args.manual[1])
            operation = args.manual[2]
            
            if operation not in ['add', 'sub', 'mul', 'div', 'all']:
                print(f"{Fore.RED}❌ Opération non supportée: {operation}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Opérations disponibles: add, sub, mul, div, all{Style.RESET_ALL}")
                return
            
            if producer.send_manual_task(n1, n2, operation):
                print(f"{Fore.GREEN}✅ Tâche manuelle envoyée avec succès{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Échec de l'envoi de la tâche manuelle{Style.RESET_ALL}")
                
        except ValueError:
            print(f"{Fore.RED}❌ N1 et N2 doivent être des nombres{Style.RESET_ALL}")
    else:
        producer.start_automatic_sending(args.count)


if __name__ == '__main__':
    main() 