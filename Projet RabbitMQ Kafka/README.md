# Projet RabbitMQ - Système de Calcul Distribué

## 🎯 Description

Ce projet implémente un **système de calcul distribué avancé** utilisant RabbitMQ pour orchestrer des opérations mathématiques entre plusieurs workers spécialisés. Le système comprend :

- **Interface Web moderne** avec séparation des sources (utilisateur/automatique)
- **Workers spécialisés** pour chaque type d'opération (add, sub, mul, div)
- **Clients producteurs** automatiques et interactifs
- **Monitoring en temps réel** avec statistiques et état des queues
- **Support Docker** pour déploiement simplifié
- **Opération "all"** qui distribue vers tous les types de workers

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │  Auto Producer  │    │ Interactive CLI │
│   (Port 5000)   │    │   (Background)  │    │    (Manual)     │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────▼──────────────┐
                    │        RabbitMQ           │
                    │   (admin/admin123)        │
                    │  ┌─────────────────────┐   │
                    │  │ Task Queues         │   │
                    │  │ • task_queue_add    │   │
                    │  │ • task_queue_sub    │   │
                    │  │ • task_queue_mul    │   │
                    │  │ • task_queue_div    │   │
                    │  │ Exchange: all_ops   │   │
                    │  └─────────────────────┘   │
                    └─────────────┬──────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
    ┌─────▼──────┐    ┌─────▼──────┐    ┌─────▼──────┐  ┌─────▼──────┐
    │Worker ADD  │    │Worker SUB  │    │Worker MUL  │  │Worker DIV  │
    │(x2 workers)│    │            │    │            │  │            │
    └────────────┘    └────────────┘    └────────────┘  └────────────┘
          │                      │                      │                │
          └──────────────────────┼──────────────────────┘────────────────┘
                                 │
                    ┌─────────────▼──────────────┐
                    │      Result Queue         │
                    │    (result_queue)         │
                    └─────────────┬──────────────┘
                                 │
                    ┌─────────────▼──────────────┐
                    │   Result Consumer         │
                    │  (Interface Web Only)     │
                    │ ┌─────────────────────────┐ │
                    │ │ • web_results[]         │ │
                    │ │ • auto_results[]        │ │
                    │ │ • recent_results[]      │ │
                    │ │ • statistics            │ │
                    │ └─────────────────────────┘ │
                    └───────────────────────────┘
```

## 🚀 Installation et Configuration

### Prérequis

1. **Docker** et **Docker Compose** (méthode recommandée)
2. **Python 3.8+** (pour installation locale)
3. **Git** pour cloner le projet

### 🎯 Installation Ultra-Rapide (Script Automatique)

**Le moyen le plus simple pour tout démarrer en une seule commande :**

```bash
# Cloner le projet
git clone <repository-url>
cd "Projet RabbitMQ Kafka"

# Script automatique qui fait tout
./setup_and_run.sh
```

**✨ Le script `setup_and_run.sh` automatise complètement :**

1. ✅ **Vérification des prérequis** : Python 3, pip3, Docker, Docker Compose
2. 📦 **Installation dépendances** : `pip install -r requirements.txt`
3. 🐳 **Démarrage Docker** : Vérification que le daemon Docker fonctionne
4. 🚀 **Lancement système** : `docker-compose up --build -d`
5. 📋 **Instructions finales** : URLs d'accès et commandes utiles

**Après exécution :**
- ✅ **Interface Web** : http://localhost:5001
- ✅ **RabbitMQ Management** : http://localhost:15672 (admin/admin123)
- ✅ Tous les services démarrés automatiquement

### 📦 Installation Rapide avec Docker (Alternative)

```bash
# Cloner le projet
git clone <repository-url>
cd "Projet RabbitMQ Kafka"

# Démarrer tout le système d'un coup
docker-compose up -d

# Vérifier l'état
docker-compose ps
```

**✅ Accès immédiat :**
- **Interface Web** : http://localhost:5001
- **RabbitMQ Management** : http://localhost:15672 (admin/admin123)

### 🛠️ Installation Locale (Développement)

```bash
# Installation des dépendances
pip install -r requirements.txt

# Démarrer RabbitMQ avec Docker
docker run -d --name rabbitmq-server \
  -p 5672:5672 -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=admin \
  -e RABBITMQ_DEFAULT_PASS=admin123 \
  rabbitmq:3-management

# Script de démarrage assisté
python start_system.py --mode local
```

## 🎮 Utilisation

### 🌐 Interface Web (Principal)

```bash
# Démarrer l'interface web tout-en-un
python src/web_interface.py

# Accéder à http://localhost:5000
```

**Fonctionnalités de l'interface :**
- ✨ **Interface moderne** avec CSS Grid et animations
- 📊 **Statistiques en temps réel** (tâches envoyées/reçues par opération)
- 🔍 **Filtrage des résultats** :
  - "Tous" : Tous les résultats
  - "Mes tâches" : Résultats des tâches soumises via l'interface
  - "Automatiques" : Résultats des tâches du client automatique
- 🔄 **Auto-refresh** configurable (toutes les 3 secondes)
- 📋 **État des queues** avec nombre de messages en attente
- 🎲 **Génération aléatoire** de valeurs de test
- 🗑️ **Effacement des statistiques**

### 🔧 Démarrage des Workers (Mode Local)

```bash
# Démarrer les workers (lancez plusieurs terminaux)
python src/worker.py add     # Worker pour additions (lancez-en 2)
python src/worker.py sub     # Worker pour soustractions  
python src/worker.py mul     # Worker pour multiplications
python src/worker.py div     # Worker pour divisions

# Mode verbose pour debugging
python src/worker.py add --verbose
```

### 📤 Clients Producteurs

```bash
# Client automatique (génère des tâches aléatoirement)
python src/client_producer.py                    # Intervalle par défaut
python src/client_producer.py --interval 2       # Toutes les 2 secondes
python src/client_producer.py --count 20         # Limiter à 20 tâches

# Tâche manuelle
python src/client_producer.py --manual 10 5 add  # 10 + 5
python src/client_producer.py --manual 50 10 all # 50 avec toutes les opérations

# Client interactif (mode CLI)
python src/interactive_client.py
```

### 📥 Consommateur de Résultats (Optionnel)

```bash
# Consumer séparé (optionnel, l'interface web en fait un)
python src/result_consumer.py
```

### 🧪 Tests et Validation

```bash
# Test automatique complet
python tests/test_system.py

# Démonstration interactive
python tests/test_system.py --demo

# Script de démarrage avec modes
python start_system.py --mode demo     # Démonstration
python start_system.py --mode docker   # Docker Compose
python start_system.py --mode local    # Mode local
```

## 📁 Structure du Projet

```
Projet RabbitMQ Kafka/
├── 📄 README.md                      # Ce fichier  
├── 📄 DOCUMENTATION_TECHNIQUE.md     # Documentation détaillée
├── 📄 requirements.txt               # Dépendances Python
├── 📄 docker-compose.yml             # Orchestration complète
├── 📄 setup_and_run.sh              # 🌟 Script d'installation automatique
├── 📄 start_system.py                # Script de démarrage assisté
├──📁 config/
│   └── rabbitmq_config.py           # Configuration centralisée
├──📁 src/
│   ├── web_interface.py              # 🌟 Interface web tout-en-un (1050 lignes)
│   ├── worker.py                     # Workers spécialisés avec couleurs
│   ├── client_producer.py            # Client producteur automatique
│   ├── result_consumer.py            # Consommateur de résultats 
│   └── interactive_client.py         # Interface CLI interactive
├──📁 utils/
│   └── message_utils.py              # Utilitaires et sérialisation
├──📁 tests/
│   └── test_system.py                # Tests d'intégration complets
├──📁 Dockerfiles
│   ├── Dockerfile.web                # Image interface web
│   ├── Dockerfile.worker             # Image workers
│   ├── Dockerfile.producer           # Image producteur
│   └── Dockerfile.consumer           # Image consommateur
└──📁 Documentation/
    ├── AIDE_MEMOIRE_TECHNIQUE.md     # Aide-mémoire
    └── DOCUMENTATION_TECHNIQUE.html  # Doc HTML exportée
```

## ⚙️ Fonctionnalités Avancées

### 🔍 Séparation des Sources

Le système distingue deux types de tâches :
- **`source: "web"`** : Tâches soumises via l'interface web
- **`source: "auto"`** : Tâches du client producteur automatique

Chaque type a sa propre vue dans l'interface web.

### 📊 Format des Messages

**Message de Tâche :**
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

**Message de Résultat :**
```json
{
  "n1": 42.5,
  "n2": 7.2,
  "op": "add",
  "result": 49.7,
  "source": "web",
  "request_id": "abc12345",
  "worker_id": "worker_add_1234",
  "processing_time": 8.7,
  "timestamp": "2024-12-03T15:30:53.891234"
}
```

### 🎯 Opérations Supportées

| Opération | Description | Queue | Symbole |
|-----------|-------------|-------|---------|
| **add** | Addition | `task_queue_add` | + |
| **sub** | Soustraction | `task_queue_sub` | - |
| **mul** | Multiplication | `task_queue_mul` | × |
| **div** | Division | `task_queue_div` | ÷ |
| **all** | Toutes les opérations | `all_operations` exchange | 🔄 |

### 🌐 APIs REST de l'Interface Web

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Interface web principale |
| `/api/send_task` | POST | Envoyer une tâche |
| `/api/stats` | GET | Statistiques globales |
| `/api/queue_status` | GET | État des queues |
| `/api/recent_results` | GET | Tous les résultats récents |
| `/api/web_results` | GET | Résultats des tâches web uniquement |
| `/api/auto_results` | GET | Résultats des tâches automatiques |
| `/api/clear_stats` | POST | Effacer les statistiques |

## 🐳 Docker Compose - Architecture Complète

```yaml
services:
  rabbitmq:          # Message broker avec management UI
  web-interface:     # Interface web (port 5001)
  worker-add-1:      # Premier worker addition
  worker-add-2:      # Deuxième worker addition (load balancing)
  worker-sub:        # Worker soustraction
  worker-mul:        # Worker multiplication  
  worker-div:        # Worker division
  producer:          # Client producteur automatique
  consumer:          # Consommateur de résultats (optionnel)
```

**Réseau :** `rabbitmq-network` (bridge)
**Volumes :** `rabbitmq_data` (persistance)

## 📊 Monitoring et Statistiques

### Interface Web
- **Tâches envoyées** : Compteur global
- **Résultats reçus** : Par source (web/auto)
- **Opérations par type** : ADD, SUB, MUL, DIV
- **État des queues** : Messages en attente
- **Temps de traitement** : Affiché par résultat

### RabbitMQ Management
- **URL** : http://localhost:15672
- **Credentials** : admin/admin123
- **Fonctionnalités** : Queues, exchanges, connexions, métriques

### Logs Colorés
- 🚀 Démarrage (vert)
- 📨 Messages reçus (bleu)
- ✅ Succès (vert)
- ❌ Erreurs (rouge)
- ⚠️ Avertissements (jaune)
- 📊 Statistiques (cyan)

## 🚨 Dépannage

### Problèmes Courants

1. **Port 5001 déjà utilisé**
   ```bash
   # Changer le port dans docker-compose.yml
   ports:
     - "5002:5000"
   ```

2. **RabbitMQ ne démarre pas**
   ```bash
   # Vérifier Docker
   docker logs rabbitmq-server
   
   # Redémarrer
   docker restart rabbitmq-server
   ```

3. **Workers ne reçoivent pas de messages**
   ```bash
   # Vérifier la connexion RabbitMQ
   python test_rabbitmq.py
   
   # Vérifier les queues
   # Via http://localhost:15672 > Queues
   ```

4. **Interface web ne se connecte pas**
   ```bash
   # Vérifier les variables d'environnement
   export RABBITMQ_HOST=localhost
   export RABBITMQ_USER=admin
   export RABBITMQ_PASSWORD=admin123
   ```

### Commandes Utiles

```bash
# Docker Compose
docker-compose logs -f                    # Logs en temps réel
docker-compose ps                         # État des conteneurs
docker-compose restart web-interface      # Redémarrer un service
docker-compose down -v                    # Tout supprimer

# Local
docker ps                                 # Conteneurs actifs
docker logs -f rabbitmq-server            # Logs RabbitMQ
pkill -f "python src/"                    # Arrêter tous les scripts Python
```

## 🔧 Variables d'Environnement

| Variable | Défaut | Description |
|----------|--------|-------------|
| `RABBITMQ_HOST` | localhost | Adresse du serveur RabbitMQ |
| `RABBITMQ_PORT` | 5672 | Port AMQP |
| `RABBITMQ_USER` | guest | Nom d'utilisateur |
| `RABBITMQ_PASSWORD` | guest | Mot de passe |
| `CLIENT_SEND_INTERVAL` | 5 | Intervalle envoi auto (secondes) |
| `WORKER_OPERATION` | add | Type d'opération du worker |

## 🎯 Améliorations Implémentées

- [x] ✨ Interface web moderne avec CSS Grid
- [x] 🔍 Séparation des résultats par source (web/auto)
- [x] 📊 Statistiques en temps réel avec auto-refresh
- [x] 🔄 Gestion de l'opération "all" via exchange fanout
- [x] 🐳 Docker Compose complet avec 8 services
- [x] 🎨 Logs colorés avec émojis
- [x] 🧪 Tests d'intégration automatisés
- [x] 📋 Monitoring des queues
- [x] 🛠️ Script de démarrage assisté
- [x] 📱 Interface responsive
- [x] 🔒 Authentification RabbitMQ
- [x] 💾 Persistance des données RabbitMQ
- [x] ⚡ Health checks Docker

## 👥 Auteurs

**Projet réalisé dans le cadre du cours de systèmes distribués**
- **Institut** : NGI (Nouvelle Génération Informatique)
- **Sujet** : Implémentation d'un système de calcul distribué avec RabbitMQ
- **Technologies** : Python, RabbitMQ, Docker, Flask, HTML/CSS/JS

---

📚 **Documentation complète** : Voir `DOCUMENTATION_TECHNIQUE.md`  
🎬 **Démonstration** : `python start_system.py --mode demo`  
🐛 **Issues** : Créer une issue sur le repository  
⭐ **Feedback** : Vos retours sont les bienvenus ! 