#!/usr/bin/env python3
"""
Client interactif pour envoyer des tâches de calcul manuellement
Usage: python interactive_client.py
"""

import sys
import os
import pika
from colorama import init, Fore, Style

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.rabbitmq_config import *
from utils.message_utils import *

# Initialiser colorama
init()


class InteractiveClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.sent_count = 0
        
        print(f"{Fore.GREEN}🚀 Client interactif démarré{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   Tapez 'help' pour voir les commandes disponibles{Style.RESET_ALL}")
        
    def connect_to_rabbitmq(self):
        """Établit la connexion à RabbitMQ"""
        if self.connection and not self.connection.is_closed:
            return True
            
        connection_params = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        )
        
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
            print(f"{Fore.RED}❌ Impossible de se connecter à RabbitMQ: {e}{Style.RESET_ALL}")
            return False
    
    def send_task(self, n1: float, n2: float, operation: str):
        """Envoie une tâche de calcul"""
        if not self.connect_to_rabbitmq():
            return False
            
        try:
            if operation == 'all':
                # Pour l'opération "all", envoyer à toutes les queues
                sent_ops = []
                for op in ['add', 'sub', 'mul', 'div']:
                    task_message = create_task_message(n1, n2, op)
                    
                    self.channel.basic_publish(
                        exchange=ALL_OPERATIONS_EXCHANGE,
                        routing_key='',
                        body=serialize_message(task_message),
                        properties=pika.BasicProperties(delivery_mode=2)
                    )
                    sent_ops.append(op)
                    
                print(f"{Fore.GREEN}✅ Tâche 'all' envoyée: {n1} × [{', '.join(sent_ops)}] × {n2}{Style.RESET_ALL}")
                self.sent_count += 4
                
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
                
                print(f"{Fore.GREEN}✅ Tâche envoyée: {n1} {operation} {n2} (ID: {task_message['request_id'][:8]}){Style.RESET_ALL}")
                self.sent_count += 1
                
            return True
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de l'envoi: {e}{Style.RESET_ALL}")
            return False
    
    def show_help(self):
        """Affiche l'aide"""
        print(f"\n{Fore.YELLOW}📋 === COMMANDES DISPONIBLES ==={Style.RESET_ALL}")
        print(f"{Fore.CYAN}  calc <n1> <op> <n2>   - Envoie un calcul (ex: calc 5 add 3){Style.RESET_ALL}")
        print(f"{Fore.CYAN}  all <n1> <n2>         - Envoie aux 4 opérations (ex: all 10 2){Style.RESET_ALL}")
        print(f"{Fore.CYAN}  random                - Génère et envoie un calcul aléatoire{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  batch <count>         - Envoie plusieurs calculs aléatoires{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  stats                 - Affiche les statistiques{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  queue                 - Vérifie l'état des queues{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  help                  - Affiche cette aide{Style.RESET_ALL}")
        print(f"{Fore.CYAN}  quit/exit             - Quitte le programme{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}📝 Opérations supportées: add, sub, mul, div, all{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Exemples:{Style.RESET_ALL}")
        print(f"{Fore.WHITE}   calc 15.5 mul 2.3{Style.RESET_ALL}")
        print(f"{Fore.WHITE}   all 100 5{Style.RESET_ALL}")
        print(f"{Fore.WHITE}   batch 10{Style.RESET_ALL}\n")
    
    def generate_random_calculation(self):
        """Génère et envoie un calcul aléatoire"""
        import random
        operations = ['add', 'sub', 'mul', 'div', 'all']
        operation = random.choice(operations)
        n1 = round(random.uniform(1, 100), 2)
        n2 = round(random.uniform(1, 100), 2)
        
        # Éviter la division par zéro
        if operation == 'div' and n2 == 0:
            n2 = 1
            
        print(f"{Fore.BLUE}🎲 Calcul aléatoire généré: {n1} {operation} {n2}{Style.RESET_ALL}")
        return self.send_task(n1, n2, operation)
    
    def send_batch(self, count: int):
        """Envoie plusieurs calculs aléatoires"""
        import random
        successful = 0
        
        print(f"{Fore.BLUE}🔄 Envoi de {count} calculs aléatoires...{Style.RESET_ALL}")
        
        for i in range(count):
            if self.generate_random_calculation():
                successful += 1
            
        print(f"{Fore.GREEN}✅ Batch terminé: {successful}/{count} calculs envoyés avec succès{Style.RESET_ALL}")
    
    def show_stats(self):
        """Affiche les statistiques"""
        print(f"\n{Fore.YELLOW}📊 === STATISTIQUES ==={Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   Total envoyé: {self.sent_count} tâches{Style.RESET_ALL}")
        
        if self.connection and not self.connection.is_closed:
            print(f"{Fore.YELLOW}   État de la connexion: Connecté{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}   État de la connexion: Déconnecté{Style.RESET_ALL}")
            
        print(f"{Fore.YELLOW}===================={Style.RESET_ALL}\n")
    
    def check_queues(self):
        """Vérifie l'état des queues"""
        if not self.connect_to_rabbitmq():
            return
            
        print(f"\n{Fore.YELLOW}📊 === ÉTAT DES QUEUES ==={Style.RESET_ALL}")
        
        try:
            # Vérifier les queues de tâches
            for operation, queue_name in TASK_QUEUES.items():
                method = self.channel.queue_declare(queue=queue_name, durable=True, passive=True)
                count = method.method.message_count
                print(f"{Fore.CYAN}   {operation.upper()}: {count} messages en attente{Style.RESET_ALL}")
            
            # Vérifier la queue des résultats
            method = self.channel.queue_declare(queue=RESULT_QUEUE, durable=True, passive=True)
            count = method.method.message_count
            print(f"{Fore.GREEN}   RÉSULTATS: {count} messages en attente{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"{Fore.RED}❌ Erreur lors de la vérification: {e}{Style.RESET_ALL}")
            
        print(f"{Fore.YELLOW}========================={Style.RESET_ALL}\n")
    
    def parse_command(self, command_line: str):
        """Parse et exécute une commande"""
        parts = command_line.strip().split()
        if not parts:
            return True
            
        cmd = parts[0].lower()
        
        if cmd in ['quit', 'exit', 'q']:
            return False
            
        elif cmd == 'help' or cmd == 'h':
            self.show_help()
            
        elif cmd == 'calc':
            if len(parts) != 4:
                print(f"{Fore.RED}❌ Usage: calc <n1> <operation> <n2>{Style.RESET_ALL}")
                return True
                
            try:
                n1 = float(parts[1])
                operation = parts[2].lower()
                n2 = float(parts[3])
                
                if operation not in ['add', 'sub', 'mul', 'div']:
                    print(f"{Fore.RED}❌ Opération non supportée: {operation}{Style.RESET_ALL}")
                    return True
                    
                self.send_task(n1, n2, operation)
                
            except ValueError:
                print(f"{Fore.RED}❌ n1 et n2 doivent être des nombres{Style.RESET_ALL}")
                
        elif cmd == 'all':
            if len(parts) != 3:
                print(f"{Fore.RED}❌ Usage: all <n1> <n2>{Style.RESET_ALL}")
                return True
                
            try:
                n1 = float(parts[1])
                n2 = float(parts[2])
                self.send_task(n1, n2, 'all')
                
            except ValueError:
                print(f"{Fore.RED}❌ n1 et n2 doivent être des nombres{Style.RESET_ALL}")
                
        elif cmd == 'random':
            self.generate_random_calculation()
            
        elif cmd == 'batch':
            if len(parts) != 2:
                print(f"{Fore.RED}❌ Usage: batch <count>{Style.RESET_ALL}")
                return True
                
            try:
                count = int(parts[1])
                if count <= 0:
                    print(f"{Fore.RED}❌ Le nombre doit être positif{Style.RESET_ALL}")
                    return True
                    
                self.send_batch(count)
                
            except ValueError:
                print(f"{Fore.RED}❌ Le nombre doit être un entier{Style.RESET_ALL}")
                
        elif cmd == 'stats':
            self.show_stats()
            
        elif cmd == 'queue':
            self.check_queues()
            
        else:
            print(f"{Fore.RED}❌ Commande inconnue: {cmd}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}   Tapez 'help' pour voir les commandes disponibles{Style.RESET_ALL}")
            
        return True
    
    def start_interactive_mode(self):
        """Démarre le mode interactif"""
        self.show_help()
        
        try:
            while True:
                try:
                    command = input(f"{Fore.GREEN}> {Style.RESET_ALL}")
                    if not self.parse_command(command):
                        break
                        
                except EOFError:
                    break
                    
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}⏹️  Interruption détectée{Style.RESET_ALL}")
            
        finally:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            print(f"{Fore.GREEN}✅ Client interactif fermé. Total envoyé: {self.sent_count} tâches{Style.RESET_ALL}")


def main():
    client = InteractiveClient()
    client.start_interactive_mode()


if __name__ == '__main__':
    main() 