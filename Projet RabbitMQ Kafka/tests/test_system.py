#!/usr/bin/env python3
"""
Script de test pour vérifier le bon fonctionnement du système de calcul distribué
Usage: python test_system.py
"""

import sys
import os
import time
import subprocess
import signal
import threading
from collections import defaultdict

# Ajouter le répertoire parent au path pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.client_producer import TaskProducer
from src.result_consumer import ResultConsumer
from colorama import init, Fore, Style

# Initialiser colorama
init()


class SystemTester:
    def __init__(self):
        self.results_received = []
        self.test_passed = False
        self.worker_processes = []
        self.consumer_thread = None
        self.stop_consumer = False
        
    def log(self, message, color=Fore.WHITE):
        """Affiche un message avec couleur"""
        print(f"{color}{message}{Style.RESET_ALL}")
    
    def start_workers(self):
        """Démarre les workers pour tous les types d'opérations"""
        self.log("🚀 Démarrage des workers...", Fore.CYAN)
        
        operations = ['add', 'sub', 'mul', 'div']
        
        for op in operations:
            try:
                # Démarrer un worker pour chaque opération
                process = subprocess.Popen(
                    [sys.executable, 'src/worker.py', op],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    preexec_fn=os.setsid  # Pour pouvoir tuer le groupe de processus
                )
                self.worker_processes.append(process)
                self.log(f"  ✅ Worker {op} démarré (PID: {process.pid})", Fore.GREEN)
                
            except Exception as e:
                self.log(f"  ❌ Erreur lors du démarrage du worker {op}: {e}", Fore.RED)
                return False
        
        # Attendre un peu pour que les workers se connectent
        time.sleep(3)
        return True
    
    def stop_workers(self):
        """Arrête tous les workers"""
        self.log("⏹️  Arrêt des workers...", Fore.YELLOW)
        
        for process in self.worker_processes:
            try:
                # Envoyer SIGTERM au groupe de processus
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                process.wait(timeout=5)
                self.log(f"  ✅ Worker {process.pid} arrêté", Fore.GREEN)
            except subprocess.TimeoutExpired:
                # Si le processus ne répond pas, forcer l'arrêt
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                self.log(f"  ⚠️  Worker {process.pid} forcé à s'arrêter", Fore.YELLOW)
            except Exception as e:
                self.log(f"  ❌ Erreur lors de l'arrêt du worker {process.pid}: {e}", Fore.RED)
        
        self.worker_processes.clear()
    
    def start_result_consumer(self):
        """Démarre le consommateur de résultats en arrière-plan"""
        def consume_results():
            class TestConsumer(ResultConsumer):
                def __init__(self, tester):
                    super().__init__(verbose=False)
                    self.tester = tester
                
                def process_result(self, channel, method, properties, body):
                    # Traitement normal
                    super().process_result(channel, method, properties, body)
                    
                    # Enregistrer le résultat pour le test
                    try:
                        from utils.message_utils import deserialize_message
                        message_str = body.decode('utf-8')
                        result_message = deserialize_message(message_str)
                        self.tester.results_received.append(result_message)
                    except Exception:
                        pass
            
            consumer = TestConsumer(self)
            
            try:
                consumer.start_consuming()
            except Exception:
                pass  # Arrêt normal
        
        self.consumer_thread = threading.Thread(target=consume_results, daemon=True)
        self.consumer_thread.start()
        self.log("👂 Consommateur de résultats démarré", Fore.CYAN)
    
    def send_test_tasks(self):
        """Envoie des tâches de test"""
        self.log("📤 Envoi des tâches de test...", Fore.BLUE)
        
        producer = TaskProducer()
        
        # Test des opérations individuelles
        test_cases = [
            (10, 5, 'add'),
            (20, 3, 'sub'),
            (7, 4, 'mul'),
            (15, 3, 'div'),
        ]
        
        for n1, n2, operation in test_cases:
            success = producer.send_manual_task(n1, n2, operation)
            if success:
                self.log(f"  ✅ Tâche envoyée: {n1} {operation} {n2}", Fore.GREEN)
            else:
                self.log(f"  ❌ Erreur lors de l'envoi: {n1} {operation} {n2}", Fore.RED)
                return False
        
        # Test de l'opération "all"
        success = producer.send_manual_task(100, 10, 'all')
        if success:
            self.log(f"  ✅ Tâche 'all' envoyée: 100 × 4_opérations × 10", Fore.GREEN)
        else:
            self.log(f"  ❌ Erreur lors de l'envoi de la tâche 'all'", Fore.RED)
            return False
        
        return True
    
    def verify_results(self, timeout=60):
        """Vérifie que tous les résultats attendus sont reçus"""
        self.log("⏳ Attente des résultats...", Fore.YELLOW)
        
        expected_results = 8  # 4 opérations individuelles + 4 opérations de "all"
        start_time = time.time()
        
        while len(self.results_received) < expected_results:
            if time.time() - start_time > timeout:
                self.log(f"❌ Timeout: seulement {len(self.results_received)}/{expected_results} résultats reçus", Fore.RED)
                return False
            
            time.sleep(1)
            self.log(f"  📊 Résultats reçus: {len(self.results_received)}/{expected_results}", Fore.CYAN)
        
        # Vérifier que nous avons tous les types d'opérations
        operations_received = defaultdict(int)
        for result in self.results_received:
            operations_received[result['op']] += 1
        
        self.log("📊 Résultats par opération:", Fore.YELLOW)
        for op, count in operations_received.items():
            self.log(f"  {op.upper()}: {count} résultats", Fore.CYAN)
        
        # Vérifier que nous avons au moins un résultat de chaque opération
        expected_operations = ['add', 'sub', 'mul', 'div']
        for op in expected_operations:
            if operations_received[op] < 2:  # Au moins 2 (1 individuel + 1 de "all")
                self.log(f"❌ Manque de résultats pour l'opération '{op}': {operations_received[op]}/2", Fore.RED)
                return False
        
        return True
    
    def validate_calculations(self):
        """Valide que les calculs sont corrects"""
        self.log("🧮 Validation des calculs...", Fore.BLUE)
        
        errors = 0
        for result in self.results_received:
            n1 = result['n1']
            n2 = result['n2']
            op = result['op']
            calculated_result = result['result']
            
            # Calculer le résultat attendu
            if op == 'add':
                expected = n1 + n2
            elif op == 'sub':
                expected = n1 - n2
            elif op == 'mul':
                expected = n1 * n2
            elif op == 'div':
                expected = n1 / n2 if n2 != 0 else float('inf')
            else:
                self.log(f"  ❌ Opération inconnue: {op}", Fore.RED)
                errors += 1
                continue
            
            # Vérifier le résultat (avec tolérance pour les flottants)
            if abs(calculated_result - expected) < 0.0001:
                self.log(f"  ✅ {n1} {op} {n2} = {calculated_result} ✓", Fore.GREEN)
            else:
                self.log(f"  ❌ {n1} {op} {n2} = {calculated_result} (attendu: {expected})", Fore.RED)
                errors += 1
        
        if errors == 0:
            self.log("✅ Tous les calculs sont corrects!", Fore.GREEN)
            return True
        else:
            self.log(f"❌ {errors} erreurs de calcul détectées", Fore.RED)
            return False
    
    def run_test(self):
        """Lance le test complet du système"""
        self.log("🧪 === DÉBUT DU TEST SYSTÈME ===", Fore.YELLOW)
        
        try:
            # 1. Démarrer les workers
            if not self.start_workers():
                return False
            
            # 2. Démarrer le consommateur de résultats
            self.start_result_consumer()
            
            # 3. Envoyer les tâches de test
            if not self.send_test_tasks():
                return False
            
            # 4. Attendre et vérifier les résultats
            if not self.verify_results():
                return False
            
            # 5. Valider les calculs
            if not self.validate_calculations():
                return False
            
            self.log("🎉 === TEST SYSTÈME RÉUSSI ===", Fore.GREEN)
            self.test_passed = True
            return True
            
        except KeyboardInterrupt:
            self.log("⏹️  Test interrompu par l'utilisateur", Fore.YELLOW)
            return False
            
        except Exception as e:
            self.log(f"❌ Erreur lors du test: {e}", Fore.RED)
            import traceback
            traceback.print_exc()
            return False
            
        finally:
            # Nettoyer
            self.stop_workers()
    
    def run_interactive_test(self):
        """Lance un test interactif pour démonstration"""
        self.log("🎭 === DÉMONSTRATION INTERACTIVE ===", Fore.YELLOW)
        
        try:
            # Démarrer les workers
            if not self.start_workers():
                return False
            
            # Démarrer le consommateur
            self.start_result_consumer()
            
            self.log("✅ Système prêt! Vous pouvez maintenant:", Fore.GREEN)
            self.log("  1. Utiliser le client interactif: python src/interactive_client.py", Fore.CYAN)
            self.log("  2. Utiliser l'interface web: python src/web_interface.py", Fore.CYAN)
            self.log("  3. Envoyer des tâches manuelles: python src/client_producer.py --manual 10 5 add", Fore.CYAN)
            self.log("", Fore.WHITE)
            self.log("Appuyez sur Ctrl+C pour arrêter la démonstration", Fore.YELLOW)
            
            # Attendre l'interruption
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.log("⏹️  Démonstration arrêtée", Fore.YELLOW)
        finally:
            self.stop_workers()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Test du système de calcul distribué')
    parser.add_argument('--demo', action='store_true',
                        help='Lancer en mode démonstration interactive')
    
    args = parser.parse_args()
    
    tester = SystemTester()
    
    if args.demo:
        tester.run_interactive_test()
    else:
        success = tester.run_test()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main() 