#!/usr/bin/env python3
"""
Script de démarrage facile pour le système de calcul distribué
Usage: python start_system.py [--mode MODE]
"""

import subprocess
import sys
import time
import signal
import os
from colorama import init, Fore, Style

init()


def log(message, color=Fore.WHITE):
    """Affiche un message avec couleur"""
    print(f"{color}{message}{Style.RESET_ALL}")


def check_docker():
    """Vérifie si Docker est installé et disponible"""
    try:
        subprocess.run(['docker', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def check_rabbitmq():
    """Vérifie si RabbitMQ fonctionne"""
    try:
        import pika
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        connection.close()
        return True
    except Exception:
        return False


def start_rabbitmq_docker():
    """Démarre RabbitMQ avec Docker"""
    log("🐰 Démarrage de RabbitMQ avec Docker...", Fore.CYAN)
    
    try:
        # Vérifier si le conteneur existe déjà
        result = subprocess.run(['docker', 'ps', '-a', '--format', '{{.Names}}'], 
                              capture_output=True, text=True)
        
        if 'rabbitmq-server' in result.stdout:
            log("📦 Conteneur RabbitMQ trouvé, redémarrage...", Fore.YELLOW)
            subprocess.run(['docker', 'start', 'rabbitmq-server'], check=True)
        else:
            log("📦 Création du conteneur RabbitMQ...", Fore.BLUE)
            subprocess.run([
                'docker', 'run', '-d',
                '--name', 'rabbitmq-server',
                '-p', '5672:5672',
                '-p', '15672:15672',
                'rabbitmq:3-management'
            ], check=True)
        
        # Attendre que RabbitMQ soit prêt
        log("⏳ Attente du démarrage de RabbitMQ...", Fore.YELLOW)
        for i in range(30):
            if check_rabbitmq():
                log("✅ RabbitMQ est prêt!", Fore.GREEN)
                return True
            time.sleep(2)
            print(".", end="", flush=True)
        
        log("\n❌ RabbitMQ n'a pas démarré dans les temps", Fore.RED)
        return False
        
    except subprocess.CalledProcessError as e:
        log(f"❌ Erreur Docker: {e}", Fore.RED)
        return False


def start_local_mode():
    """Démarre le système en mode local"""
    log("🚀 === DÉMARRAGE EN MODE LOCAL ===", Fore.YELLOW)
    
    # Vérifier les prérequis
    if not check_docker():
        log("❌ Docker n'est pas disponible", Fore.RED)
        log("   Veuillez installer Docker ou utiliser un serveur RabbitMQ existant", Fore.CYAN)
        return False
    
    # Démarrer RabbitMQ
    if not check_rabbitmq():
        if not start_rabbitmq_docker():
            return False
    else:
        log("✅ RabbitMQ déjà disponible", Fore.GREEN)
    
    log("\n🎯 Système prêt! Commandes disponibles:", Fore.GREEN)
    log("", Fore.WHITE)
    log("🔧 Workers (lancez-en plusieurs):", Fore.CYAN)
    log("   python src/worker.py add", Fore.WHITE)
    log("   python src/worker.py sub", Fore.WHITE)
    log("   python src/worker.py mul", Fore.WHITE)
    log("   python src/worker.py div", Fore.WHITE)
    log("", Fore.WHITE)
    log("📤 Clients producteurs:", Fore.CYAN)
    log("   python src/client_producer.py                    # Automatique", Fore.WHITE)
    log("   python src/client_producer.py --manual 10 5 add  # Manuel", Fore.WHITE)
    log("   python src/interactive_client.py                 # Interactif", Fore.WHITE)
    log("", Fore.WHITE)
    log("📥 Consommateur de résultats:", Fore.CYAN)
    log("   python src/result_consumer.py", Fore.WHITE)
    log("", Fore.WHITE)
    log("🌐 Interface web:", Fore.CYAN)
    log("   python src/web_interface.py", Fore.WHITE)
    log("   Puis ouvrir: http://localhost:5001", Fore.WHITE)
    log("", Fore.WHITE)
    log("🧪 Tests:", Fore.CYAN)
    log("   python tests/test_system.py       # Test automatique", Fore.WHITE)
    log("   python tests/test_system.py --demo  # Démonstration", Fore.WHITE)
    log("", Fore.WHITE)
    log("📊 RabbitMQ Management:", Fore.CYAN)
    log("   http://localhost:15672 (guest/guest)", Fore.WHITE)
    
    return True


def start_docker_compose():
    """Démarre le système avec Docker Compose"""
    log("🐳 === DÉMARRAGE AVEC DOCKER COMPOSE ===", Fore.YELLOW)
    
    if not check_docker():
        log("❌ Docker n'est pas disponible", Fore.RED)
        return False
    
    try:
        # Vérifier si docker-compose est disponible
        subprocess.run(['docker-compose', '--version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        try:
            subprocess.run(['docker', 'compose', '--version'], capture_output=True, check=True)
            compose_cmd = ['docker', 'compose']
        except (subprocess.CalledProcessError, FileNotFoundError):
            log("❌ Docker Compose n'est pas disponible", Fore.RED)
            return False
    else:
        compose_cmd = ['docker-compose']
    
    log("🏗️  Construction et démarrage des conteneurs...", Fore.BLUE)
    
    try:
        # Construire et démarrer
        subprocess.run(compose_cmd + ['up', '--build', '-d'], check=True)
        
        log("✅ Système démarré avec succès!", Fore.GREEN)
        log("", Fore.WHITE)
        log("🌐 Interface web: http://localhost:5001", Fore.CYAN)
        log("📊 RabbitMQ Management: http://localhost:15672 (admin/admin123)", Fore.CYAN)
        log("", Fore.WHITE)
        log("📋 Commandes utiles:", Fore.YELLOW)
        log(f"   {' '.join(compose_cmd)} logs -f                    # Voir les logs", Fore.WHITE)
        log(f"   {' '.join(compose_cmd)} ps                         # État des conteneurs", Fore.WHITE)
        log(f"   {' '.join(compose_cmd)} down                       # Arrêter le système", Fore.WHITE)
        log(f"   {' '.join(compose_cmd)} down -v                    # Arrêter et supprimer les volumes", Fore.WHITE)
        
        return True
        
    except subprocess.CalledProcessError as e:
        log(f"❌ Erreur Docker Compose: {e}", Fore.RED)
        return False


def start_demo():
    """Démarre une démonstration interactive"""
    log("🎭 === MODE DÉMONSTRATION ===", Fore.YELLOW)
    
    if not start_local_mode():
        return False
    
    log("\n🎬 Lancement de la démonstration...", Fore.BLUE)
    
    try:
        subprocess.run([sys.executable, 'tests/test_system.py', '--demo'])
    except KeyboardInterrupt:
        log("⏹️  Démonstration arrêtée", Fore.YELLOW)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Démarrage du système de calcul distribué')
    parser.add_argument('--mode', choices=['local', 'docker', 'demo'], default='local',
                        help='Mode de démarrage (défaut: local)')
    
    args = parser.parse_args()
    
    log("🧮 === SYSTÈME DE CALCUL DISTRIBUÉ - RABBITMQ ===", Fore.YELLOW)
    log("   Institut NGI - Projet de systèmes distribués", Fore.CYAN)
    log("", Fore.WHITE)
    
    try:
        if args.mode == 'local':
            success = start_local_mode()
        elif args.mode == 'docker':
            success = start_docker_compose()
        elif args.mode == 'demo':
            success = start_demo()
        else:
            log(f"❌ Mode inconnu: {args.mode}", Fore.RED)
            success = False
        
        if not success:
            log("\n❌ Échec du démarrage du système", Fore.RED)
            sys.exit(1)
        
    except KeyboardInterrupt:
        log("\n⏹️  Interruption par l'utilisateur", Fore.YELLOW)
    except Exception as e:
        log(f"\n❌ Erreur inattendue: {e}", Fore.RED)
        sys.exit(1)


if __name__ == '__main__':
    main() 