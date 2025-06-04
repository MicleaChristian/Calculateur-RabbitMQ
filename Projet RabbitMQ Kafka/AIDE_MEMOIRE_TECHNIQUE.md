# 🚀 Aide-Mémoire Technique - Système de Calcul Distribué

## 📋 Commandes Essentielles

### 🎯 Installation Ultra-Rapide (Script Automatique)
```bash
# Linux / macOS / WSL
./setup_and_run.sh

# Windows Command Prompt
setup_and_run.bat

# Windows PowerShell (recommandé - avec couleurs)
.\setup_and_run.ps1

# Le script automatise tout :
# ✅ Vérifications des prérequis (Python, Docker, Docker Compose)
# 📦 Installation des dépendances (pip install -r requirements.txt)
# 🚀 Démarrage complet du système (docker-compose up --build -d)
# 📋 Affichage des URLs d'accès et commandes utiles
```

### 🐳 Docker Compose (Recommandé)
```bash
# Démarrage complet du système
docker-compose up -d

# Vérifier l'état des services
docker-compose ps

# Logs en temps réel
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f web-interface
docker-compose logs -f worker-add-1

# Redémarrer un service
docker-compose restart web-interface

# Arrêter le système
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v

# Reconstruire les images
docker-compose up --build -d
```

### 🖥️ Mode Local (Développement)
```bash
# Démarrage assisté
python start_system.py --mode local

# RabbitMQ avec Docker
docker run -d --name rabbitmq-server \
  -p 5672:5672 -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=admin \
  -e RABBITMQ_DEFAULT_PASS=admin123 \
  rabbitmq:3-management

# Interface web (principal)
python src/web_interface.py

# Workers (dans des terminaux séparés)
python src/worker.py add --verbose
python src/worker.py sub
python src/worker.py mul  
python src/worker.py div

# Client automatique
python src/client_producer.py --interval 2

# Client interactif
python src/interactive_client.py

# Tests
python tests/test_system.py
python tests/test_system.py --demo
```

## 🌐 URLs d'Accès

| Service | URL | Credentials |
|---------|-----|-------------|
| **Interface Web** | http://localhost:5000 | - |
| **Interface Web (Docker)** | http://localhost:5001 | - |
| **RabbitMQ Management** | http://localhost:15672 | admin/admin123 |

## 📊 APIs REST

### Interface Web - Endpoints
```bash
# Statistiques globales
curl http://localhost:5000/api/stats

# État des queues
curl http://localhost:5000/api/queue_status

# Tous les résultats
curl http://localhost:5000/api/recent_results

# Résultats tâches web uniquement
curl http://localhost:5000/api/web_results

# Résultats tâches automatiques
curl http://localhost:5000/api/auto_results

# Envoyer une tâche
curl -X POST http://localhost:5000/api/send_task \
  -H "Content-Type: application/json" \
  -d '{"n1": 10, "n2": 5, "operation": "add"}'

# Effacer les statistiques
curl -X POST http://localhost:5000/api/clear_stats
```

## 🔧 Configuration

### Variables d'Environnement
```bash
# RabbitMQ
export RABBITMQ_HOST=localhost
export RABBITMQ_PORT=5672
export RABBITMQ_USER=admin
export RABBITMQ_PASSWORD=admin123

# Workers
export WORKER_OPERATION=add

# Client automatique
export CLIENT_SEND_INTERVAL=3
```

### Structure des Messages
```json
{
  "n1": 42.5,
  "n2": 7.2, 
  "operation": "add",
  "source": "web",
  "request_id": "abc12345",
  "timestamp": "2024-12-03T15:30:45.123456"
}
```

## 🚨 Dépannage Rapide

### Problèmes Courants
```bash
# Port occupé
lsof -i :5000
lsof -i :5001

# Arrêter tous les processus Python
pkill -f "python src/"

# Nettoyer Docker
docker system prune -f
docker volume prune -f

# Redémarrer RabbitMQ
docker restart rabbitmq-server

# Vérifier connexion RabbitMQ
python test_rabbitmq.py
```

### Logs Utiles
```bash
# Docker Compose
docker-compose logs --tail=50 web-interface
docker-compose logs --tail=50 worker-add-1

# Docker standard
docker logs -f rabbitmq-server
docker logs --tail=50 rabbitmq-server

# RabbitMQ diagnostics
docker exec rabbitmq-server rabbitmq-diagnostics ping
docker exec rabbitmq-server rabbitmqctl list_queues
```

## 📁 Fichiers Importants

### Configuration
- `config/rabbitmq_config.py` - Configuration centralisée
- `docker-compose.yml` - Orchestration complète
- `requirements.txt` - Dépendances Python

### Code Principal
- `src/web_interface.py` - Interface web complète (1050 lignes)
- `src/worker.py` - Workers avec logs colorés
- `src/client_producer.py` - Client automatique

### Scripts Utiles
- `setup_and_run.sh` - 🌟 Installation automatique complète (Linux/macOS)
- `setup_and_run.bat` - 🌟 Installation automatique complète (Windows CMD)
- `setup_and_run.ps1` - 🌟 Installation automatique complète (Windows PowerShell)
- `start_system.py` - Démarrage assisté
- `tests/test_system.py` - Tests d'intégration

## 🔍 Monitoring

### Interface Web
- **Statistiques** : Tâches envoyées/reçues par source
- **Queues** : Messages en attente par queue
- **Filtres** : "Tous", "Mes tâches", "Automatiques"
- **Auto-refresh** : Toutes les 3 secondes

### RabbitMQ Management
- **Queues** : task_queue_add, task_queue_sub, task_queue_mul, task_queue_div, result_queue
- **Exchange** : all_operations (fanout)
- **Connexions** : Par worker et client
- **Métriques** : Messages/sec, consumers actifs

### Docker
```bash
# Utilisation ressources
docker stats

# État des conteneurs
docker ps

# Santé des services
docker-compose ps
```

## ⚡ Raccourcis de Développement

### Commandes Rapides
```bash
# Installation et démarrage ultra-rapide
alias quick-start="./setup_and_run.sh"          # Linux/macOS
alias quick-start-win="setup_and_run.bat"       # Windows CMD
alias quick-start-ps=".\setup_and_run.ps1"      # Windows PowerShell

# Démarrage rapide développement
alias rabbitmq-start="docker start rabbitmq-server"
alias web-start="python src/web_interface.py"
alias worker-all="python src/worker.py add & python src/worker.py sub & python src/worker.py mul & python src/worker.py div &"

# Tests rapides
alias test-system="python tests/test_system.py"
alias test-demo="python tests/test_system.py --demo"

# Docker Compose
alias dc="docker-compose"
alias dc-up="docker-compose up -d"
alias dc-down="docker-compose down"
alias dc-logs="docker-compose logs -f"
```

### Environnement de Développement
```bash
# .env local
cat > .env << EOF
RABBITMQ_HOST=localhost
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=admin123
CLIENT_SEND_INTERVAL=2
EOF

source .env
```

## 🎯 Opérations Supportées

| Operation | Queue | Description | Exemple |
|-----------|-------|-------------|---------|
| `add` | task_queue_add | Addition | 10 + 5 = 15 |
| `sub` | task_queue_sub | Soustraction | 10 - 5 = 5 |
| `mul` | task_queue_mul | Multiplication | 10 × 5 = 50 |
| `div` | task_queue_div | Division | 10 ÷ 5 = 2 |
| `all` | all_operations exchange | Toutes les opérations | 4 résultats |

## 🔄 Workflow Typique

### 1. Développement Local
```bash
# Démarrer RabbitMQ
docker run -d --name rabbitmq-server -p 5672:5672 -p 15672:15672 rabbitmq:3-management

# Démarrer l'interface web
python src/web_interface.py

# Démarrer quelques workers
python src/worker.py add &
python src/worker.py sub &

# Tester via l'interface : http://localhost:5000
```

### 2. Tests Complets
```bash
# Test automatique
python tests/test_system.py

# Démonstration
python start_system.py --mode demo
```

### 3. Déploiement Production
```bash
# Docker Compose
docker-compose up -d

# Vérification
curl http://localhost:5001/api/stats
```

## 📈 Métriques Clés

### Performance
- **Latence** : 5-15 secondes par tâche (simulation)
- **Throughput** : ~360 tâches/heure/worker
- **Capacité totale** : ~1800 tâches/heure (5 workers)

### Ressources
- **Mémoire** : ~50MB par conteneur
- **CPU** : Faible (simulation)
- **Réseau** : Messages JSON légers

### Disponibilité
- **Health checks** : Intégrés Docker
- **Reconnexion** : Automatique workers
- **Persistence** : Messages RabbitMQ

---

📚 **Documentation complète** : Voir `DOCUMENTATION_TECHNIQUE.md`  
🎬 **Démonstration** : `python start_system.py --mode demo`  
🔧 **Support** : Créer une issue sur le repository 