#!/usr/bin/env python3
"""
Client consommateur qui lit et affiche les résultats des calculs
Usage: python result_consumer.py [--verbose]
"""

import sys
import os
import argparse
import pika
from colorama import init, Fore, Style
from collections import defaultdict
import time

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.rabbitmq_config import *
from utils.message_utils import *

# Initialiser colorama
init()


class ResultConsumer:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.processed_count = 0
        self.connection = None
        self.channel = None
        self.stats = defaultdict(int)
        self.start_time = time.time()
        
        print(f"{Fore.GREEN}🚀 Client consommateur de résultats démarré{Style.RESET_ALL}")
        
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
                
                # Déclarer la queue des résultats
                self.channel.queue_declare(queue=RESULT_QUEUE, durable=True)
                
                print(f"{Fore.CYAN}✅ Connexion à RabbitMQ établie{Style.RESET_ALL}")
                return True
                
            except Exception as e:
                print(f"{Fore.YELLOW}⚠️  Tentative {attempt + 1}/{max_retries} échouée: {e}{Style.RESET_ALL}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    
        print(f"{Fore.RED}❌ Impossible de se connecter à RabbitMQ après {max_retries} tentatives{Style.RESET_ALL}")
        return False
    
    def process_result(self, channel, method, properties, body):
        """Traite un message de résultat"""
        try:
            # Désérialiser le message de résultat
            message_str = body.decode('utf-8')
            result_message = deserialize_message(message_str)
            
            # Valider le message de résultat
            required_fields = ["n1", "n2", "op", "result", "request_id", "worker_id", "processing_time", "timestamp"]
            if not all(field in result_message for field in required_fields):
                print(f"{Fore.RED}❌ Message de résultat invalide reçu{Style.RESET_ALL}")
                channel.basic_ack(delivery_tag=method.delivery_tag)
                return
            
            # Afficher le résultat formaté
            display_text = format_result_display(result_message)
            
            # Choisir la couleur selon l'opération
            operation_colors = {
                'add': Fore.GREEN,
                'sub': Fore.BLUE,
                'mul': Fore.MAGENTA,
                'div': Fore.CYAN
            }
            color = operation_colors.get(result_message['op'], Fore.WHITE)
            
            print(f"{color}{display_text}{Style.RESET_ALL}")
            
            # Afficher des détails supplémentaires en mode verbose
            if self.verbose:
                print(f"{Fore.WHITE}   📊 Détails: {serialize_message(result_message)}{Style.RESET_ALL}")
            
            # Mettre à jour les statistiques
            self.processed_count += 1
            self.stats[result_message['op']] += 1
            self.stats['total_processing_time'] += result_message['processing_time']
            
            # Afficher les statistiques périodiquement
            if self.processed_count % 10 == 0:
                self.display_stats()
            
            # Acquitter le message
            channel.basic_ack(delivery_tag=method.delivery_tag)
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors du traitement du résultat: {e}{Style.RESET_ALL}")
            channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    
    def display_stats(self):
        """Affiche les statistiques en temps réel"""
        elapsed_time = time.time() - self.start_time
        avg_processing_time = self.stats['total_processing_time'] / max(self.processed_count, 1)
        
        print(f"\n{Fore.YELLOW}📊 === STATISTIQUES ==={Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   Total traité: {self.processed_count} résultats{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   Temps écoulé: {elapsed_time:.1f}s{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   Débit: {self.processed_count/elapsed_time:.2f} résultats/s{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   Temps de traitement moyen: {avg_processing_time:.1f}s{Style.RESET_ALL}")
        
        # Statistiques par opération
        for op in ['add', 'sub', 'mul', 'div']:
            count = self.stats[op]
            if count > 0:
                print(f"{Fore.YELLOW}   {op.upper()}: {count} résultats{Style.RESET_ALL}")
        
        print(f"{Fore.YELLOW}========================{Style.RESET_ALL}\n")
    
    def start_consuming(self):
        """Démarre l'écoute des résultats"""
        if not self.connect_to_rabbitmq():
            return
        
        # Configuration du consumer
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=RESULT_QUEUE,
            on_message_callback=self.process_result
        )
        
        print(f"{Fore.CYAN}👂 En écoute des résultats sur la queue '{RESULT_QUEUE}'...{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   Pour arrêter, appuyez sur CTRL+C{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   Statistiques affichées toutes les 10 réceptions{Style.RESET_ALL}\n")
        
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⏹️  Arrêt du consommateur de résultats...{Style.RESET_ALL}")
            self.channel.stop_consuming()
            self.connection.close()
            
            # Afficher les statistiques finales
            print(f"\n{Fore.GREEN}✅ Statistiques finales:{Style.RESET_ALL}")
            self.display_stats()
    
    def get_queue_info(self):
        """Obtient des informations sur la queue des résultats"""
        if not self.connect_to_rabbitmq():
            return None
        
        try:
            method = self.channel.queue_declare(queue=RESULT_QUEUE, durable=True, passive=True)
            message_count = method.method.message_count
            self.connection.close()
            return message_count
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de la récupération des infos de queue: {e}{Style.RESET_ALL}")
            return None


def main():
    parser = argparse.ArgumentParser(description='Client consommateur de résultats de calculs')
    parser.add_argument('--verbose', action='store_true',
                        help='Mode verbose avec détails complets des messages')
    parser.add_argument('--info', action='store_true',
                        help='Afficher les informations sur la queue et quitter')
    
    args = parser.parse_args()
    
    consumer = ResultConsumer(args.verbose)
    
    if args.info:
        count = consumer.get_queue_info()
        if count is not None:
            print(f"{Fore.CYAN}📊 Messages en attente dans la queue '{RESULT_QUEUE}': {count}{Style.RESET_ALL}")
        return
    
    consumer.start_consuming()


if __name__ == '__main__':
    main() 