# 📚 Documentation Technique - Système de Calcul Distribué RabbitMQ

## 📋 Table des Matières

1. [Vue d'Ensemble du Projet](#-vue-densemble-du-projet)
2. [Architecture et Patterns](#️-architecture-et-patterns)
3. [Technologies et Frameworks](#️-technologies-et-frameworks)
4. [Structure du Code](#-structure-du-code)
5. [Interface Web Avancée](#-interface-web-avancée)
6. [Configuration et Déploiement](#️-configuration-et-déploiement)
7. [Sécurité et Bonnes Pratiques](#-sécurité-et-bonnes-pratiques)
8. [Performance et Scalabilité](#-performance-et-scalabilité)
9. [Tests et Qualité](#-tests-et-qualité)
10. [Questions Fréquentes](#-questions-fréquentes)

---

## 🎯 Vue d'Ensemble du Projet

### Objectif
Système de calcul distribué avancé utilisant RabbitMQ pour orchestrer des opérations mathématiques entre plusieurs workers spécialisés, avec une interface web moderne complète et une séparation intelligente des sources de tâches.

### Fonctionnalités Principales

#### ✨ Interface Web Avancée
- **Interface tout-en-un** : Template HTML intégré de 760+ lignes
- **Design moderne** : CSS Grid, flexbox, gradients, animations
- **Séparation des sources** : Distinction web/automatique
- **Filtrage temps réel** : "Tous", "Mes tâches", "Automatiques"
- **Auto-refresh** : Mise à jour toutes les 3 secondes
- **Responsive** : Compatible mobile/desktop

#### 🔧 Workers Spécialisés
- **1 worker par opération** : add, sub, mul, div
- **Load balancing** : 2 workers ADD pour haute charge
- **Processing simulé** : 5-15 secondes par tâche
- **Logs colorés** : Émojis et couleurs pour debugging
- **Reconnexion automatique** : Gestion des déconnexions

#### 📤 Producteurs Multiples
- **Client automatique** : Génération aléatoire continue
- **Interface web** : Soumission manuelle utilisateur
- **Client interactif** : CLI pour tests
- **Support "all"** : Diffusion vers toutes les opérations

#### 📊 Monitoring Complet
- **Statistiques temps réel** : Tâches envoyées/reçues par source
- **État des queues** : Messages en attente par queue
- **Métriques par opération** : Compteurs ADD, SUB, MUL, DIV
- **RabbitMQ Management** : Interface d'administration

---

## 🏗️ Architecture et Patterns

### Pattern Architectural Principal
**Message-Driven Microservices avec Séparation des Sources**

```mermaid
graph TB
    WEB[Interface Web<br/>port 5000] 
    AUTO[Client Auto<br/>Background]
    CLI[Client CLI<br/>Interactif]
    
    WEB --> |source: web| RABBIT
    AUTO --> |source: auto| RABBIT
    CLI --> |source: web| RABBIT
    
    RABBIT{RabbitMQ<br/>Message Broker}
    
    RABBIT --> |task_queue_add| W1[Worker ADD 1]
    RABBIT --> |task_queue_add| W2[Worker ADD 2]
    RABBIT --> |task_queue_sub| W3[Worker SUB]
    RABBIT --> |task_queue_mul| W4[Worker MUL]
    RABBIT --> |task_queue_div| W5[Worker DIV]
    
    W1 --> |result_queue| CONSUMER[Result Consumer<br/>Interface Web]
    W2 --> |result_queue| CONSUMER
    W3 --> |result_queue| CONSUMER
    W4 --> |result_queue| CONSUMER
    W5 --> |result_queue| CONSUMER
    
    CONSUMER --> |web_results[]| WEBRES[Résultats Web]
    CONSUMER --> |auto_results[]| AUTORES[Résultats Auto]
    CONSUMER --> |recent_results[]| ALLRES[Tous Résultats]
```

### Patterns de Conception Utilisés

#### 1. **Producer-Consumer Pattern avec Séparation des Sources**
```python
# Message avec source
{
  "n1": 42, "n2": 7, "operation": "add",
  "source": "web",  # ou "auto"
  "request_id": "abc123",
  "timestamp": "2024-12-03T15:30:45"
}
```

#### 2. **Command Pattern avec Métadonnées**
- Encapsulation des requêtes avec informations de traçabilité
- Support pour audit et debugging avancé

#### 3. **Strategy Pattern pour Workers**
```python
operations = {
    'add': lambda x, y: x + y,
    'sub': lambda x, y: x - y,
    'mul': lambda x, y: x * y,
    'div': lambda x, y: x / y if y != 0 else float('inf')
}
```

#### 4. **Observer Pattern pour Interface Web**
- Auto-refresh des statistiques
- Mise à jour temps réel des résultats
- Notifications visuelles

#### 5. **Publish-Subscribe avec Fanout Exchange**
```python
# Opération "all" via exchange fanout
self.channel.basic_publish(
    exchange=ALL_OPERATIONS_EXCHANGE,
    routing_key='',
    body=serialize_message(task_message)
)
```

---

## 🛠️ Technologies et Frameworks

### Backend Core
| Technologie | Version | Usage | Justification |
|-------------|---------|-------|---------------|
| **Python** | 3.8+ | Langage principal | Écosystème riche, async support, simplicité |
| **RabbitMQ** | 3.x | Message broker | Fiabilité, patterns avancés, management UI |
| **Pika** | 1.3.2 | Client RabbitMQ | Client officiel, API simple, robuste |

### Framework Web
| Technologie | Version | Usage | Justification |
|-------------|---------|-------|---------------|
| **Flask** | 2.3.3 | Framework web | Léger, flexible, rapide prototypage |
| **Flask-CORS** | 4.0.0 | CORS support | API REST cross-origin, sécurité |

### Frontend Intégré
| Technologie | Usage | Justification |
|-------------|-------|---------------|
| **HTML5** | Structure sémantique | Standards modernes, accessibilité |
| **CSS3** | Styling avancé | Grid, flexbox, animations, gradients |
| **JavaScript ES6+** | Interactivité | Async/await, fetch API, modules |
| **Template intégré** | Simplicité déploiement | Pas de fichiers séparés |

### Infrastructure
| Technologie | Version | Usage | Justification |
|-------------|---------|-------|---------------|
| **Docker** | Latest | Containerisation | Isolation, reproductibilité |
| **Docker Compose** | Latest | Orchestration | Multi-services, networking |

### Outils de Développement
| Outil | Version | Usage |
|-------|---------|-------|
| **colorama** | 0.4.6 | Logs colorés |
| **pytest** | 7.4.2 | Tests unitaires |
| **requests** | 2.31.0 | Tests HTTP |

---

## 📁 Structure du Code

### Organisation des Fichiers
```
Projet RabbitMQ Kafka/
├── 📄 Documentation/
│   ├── README.md                     # Documentation utilisateur
│   ├── DOCUMENTATION_TECHNIQUE.md    # Cette documentation
│   ├── AIDE_MEMOIRE_TECHNIQUE.md     # Aide-mémoire
│   └── DOCUMENTATION_TECHNIQUE.html  # Export HTML
├── 📄 Configuration/
│   ├── docker-compose.yml            # Orchestration complète
│   ├── requirements.txt              # Dépendances Python
│   └── Dockerfile.*                  # Images Docker spécialisées
├── 📁 config/
│   └── rabbitmq_config.py           # Configuration centralisée
├── 📁 src/
│   ├── web_interface.py              # 🌟 Interface web complète (1050 lignes)
│   ├── worker.py                     # Workers avec logs colorés
│   ├── client_producer.py            # Client automatique
│   ├── result_consumer.py            # Consumer séparé (optionnel)
│   └── interactive_client.py         # CLI interactif
├── 📁 utils/
│   └── message_utils.py              # Utilitaires sérialisation
├── 📁 tests/
│   └── test_system.py                # Tests d'intégration
└── 📁 Scripts/
    ├── start_system.py               # Démarrage assisté
    ├── setup_and_run.sh             # Installation auto
    └── test_rabbitmq.py             # Test connexion
```

### Modules Principaux

#### `config/rabbitmq_config.py`
```python
# Configuration centralisée avec variables d'environnement
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
TASK_QUEUES = {
    'add': 'task_queue_add',
    'sub': 'task_queue_sub', 
    'mul': 'task_queue_mul',
    'div': 'task_queue_div'
}
ALL_OPERATIONS_EXCHANGE = 'all_operations'
WORKER_PROCESSING_TIME = {'min': 5, 'max': 15}
```

#### `utils/message_utils.py`
```python
# Fonctions utilitaires avec support des sources
def create_task_message(n1, n2, operation, source="auto")
def create_result_message(task, result, worker_id, processing_time)
def serialize_message(message) / deserialize_message(message_str)
def perform_operation(operation, n1, n2)
def validate_task_message(message)
def format_result_display(result_message)
```

#### `src/web_interface.py` - Classe Principale
**RabbitMQWebInterface** (Interface complète)
- `connect_to_rabbitmq()` : Gestion connexion avec retry
- `send_task()` : Envoi avec support "all" et sources
- `start_result_consumer()` : Consumer en thread daemon
- `get_queue_status()` : Monitoring queues

**APIs REST Complètes :**
- `POST /api/send_task` : Soumission tâches
- `GET /api/stats` : Statistiques globales
- `GET /api/queue_status` : État des queues
- `GET /api/recent_results` : Tous les résultats
- `GET /api/web_results` : Résultats tâches web uniquement
- `GET /api/auto_results` : Résultats tâches automatiques
- `POST /api/clear_stats` : Reset statistiques

**Template HTML Intégré :**
- 760+ lignes de HTML/CSS/JS
- Interface responsive complète
- Auto-refresh configurable
- Filtrage temps réel

---

## 🌐 Interface Web Avancée

### Architecture Frontend

#### Structure HTML
```html
<div class="container">
  <div class="header">                    <!-- En-tête avec titre -->
  <div class="grid">                      <!-- Layout CSS Grid -->
    <div class="card">                    <!-- Formulaire soumission -->
    <div class="card">                    <!-- Statistiques -->
  <div class="card">                      <!-- État des queues -->
  <div class="card">                      <!-- Résultats avec filtres -->
    <div id="webResultsSection">          <!-- Résultats web -->
    <div id="autoResultsSection">         <!-- Résultats auto -->
    <div id="allResultsSection">          <!-- Tous résultats -->
```

#### Styles CSS Avancés
```css
/* Design moderne avec gradients */
body {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Grid responsive */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

/* Animations et transitions */
.card:hover {
  transform: translateY(-5px);
}

/* Styles par opération */
.result-add { border-color: #00b894; }
.result-sub { border-color: #74b9ff; }
.result-mul { border-color: #a29bfe; }
.result-div { border-color: #fd79a8; }
```

#### JavaScript Interactif
```javascript
// Gestion des vues de résultats
function showResults(type) {
  currentResultsView = type;
  // Logique de filtrage et affichage
}

// Auto-refresh configurable
function toggleAutoRefresh() {
  if (autoRefreshActive) {
    clearInterval(autoRefreshInterval);
  } else {
    autoRefreshInterval = setInterval(refreshCurrentResults, 3000);
  }
}

// Soumission de tâches avec feedback
async function handleFormSubmit(e) {
  // Gestion loading, validation, erreurs
}
```

### Fonctionnalités UX

#### Filtrage des Résultats
- **"Tous"** : `stats['recent_results']` - Tous les résultats mélangés
- **"Mes tâches"** : `stats['web_results']` - Tâches soumises via interface
- **"Automatiques"** : `stats['auto_results']` - Tâches du client auto

#### Auto-refresh Intelligent
- **Intervalle** : 3 secondes configurable
- **Scope** : Refresh seulement la vue courante
- **Indicateur visuel** : 🟢 ACTIF quand activé
- **Performance** : Pas de refresh inutile

#### Génération Aléatoire
```javascript
function generateRandom() {
  document.getElementById('n1').value = Math.round(Math.random() * 100 * 100) / 100;
  document.getElementById('n2').value = Math.round(Math.random() * 100 * 100) / 100;
  const operations = ['add', 'sub', 'mul', 'div', 'all'];
  document.getElementById('operation').value = operations[Math.floor(Math.random() * operations.length)];
}
```

---

## ⚙️ Configuration et Déploiement

### Variables d'Environnement
```bash
# Configuration RabbitMQ
RABBITMQ_HOST=rabbitmq           # Service Docker ou localhost
RABBITMQ_PORT=5672               # Port AMQP standard
RABBITMQ_USER=admin              # Utilisateur (guest par défaut)
RABBITMQ_PASSWORD=admin123       # Mot de passe

# Configuration Workers
WORKER_OPERATION=add             # Type d'opération (add/sub/mul/div)

# Configuration Client
CLIENT_SEND_INTERVAL=3           # Intervalle envoi auto (secondes)
```

### Docker Compose - Architecture Complète

#### Services Définis
```yaml
services:
  # Infrastructure
  rabbitmq:                      # Message broker + management UI
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: admin123
    healthcheck:                 # Health check intégré
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5

  # Interface utilisateur
  web-interface:                 # Interface web principale
    build: {context: ., dockerfile: Dockerfile.web}
    ports: ["5001:5000"]
    depends_on:
      rabbitmq: {condition: service_healthy}

  # Workers (load balancing)
  worker-add-1:                  # Premier worker addition
  worker-add-2:                  # Deuxième worker addition
  worker-sub:                    # Worker soustraction
  worker-mul:                    # Worker multiplication
  worker-div:                    # Worker division

  # Clients
  producer:                      # Client automatique
  consumer:                      # Consumer séparé (optionnel)
```

#### Réseau et Volumes
```yaml
networks:
  rabbitmq-network:
    driver: bridge               # Réseau privé

volumes:
  rabbitmq_data:                 # Persistance RabbitMQ
```

### Dockerfiles Spécialisés

#### Dockerfile.web
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY config/ ./config/
COPY utils/ ./utils/
COPY src/web_interface.py ./
EXPOSE 5000
CMD ["python", "web_interface.py"]
```

#### Dockerfile.worker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY config/ ./config/
COPY utils/ ./utils/
COPY src/worker.py ./
CMD ["python", "worker.py", "${WORKER_OPERATION}"]
```

---

## 🔒 Sécurité et Bonnes Pratiques

### Sécurité Réseau
```yaml
# Isolation Docker
networks:
  rabbitmq-network:
    driver: bridge               # Réseau privé isolé

# Ports exposés minimaux
ports:
  - "5001:5000"                 # Interface web uniquement
  - "5672:5672"                 # AMQP (nécessaire)
  - "15672:15672"               # Management (développement)
```

### Authentification RabbitMQ
```bash
# Credentials sécurisés (pas guest/guest)
RABBITMQ_DEFAULT_USER=admin
RABBITMQ_DEFAULT_PASS=admin123

# En production : utiliser secrets Docker
echo "motdepasse_securise" | docker secret create rabbitmq_password -
```

### Gestion des Erreurs Robuste
```python
def connect_to_rabbitmq(self):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            self.connection = pika.BlockingConnection(connection_params)
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                print(f"❌ Connexion impossible après {max_retries} tentatives")
                return False
```

### Validation des Données
```python
# Validation côté serveur
if operation not in ['add', 'sub', 'mul', 'div', 'all']:
    return jsonify({'success': False, 'error': 'Opération non supportée'})

# Validation côté client
const n1 = parseFloat(document.getElementById('n1').value);
if (isNaN(n1)) {
    showAlert('taskAlert', 'N1 doit être un nombre', 'error');
    return;
}
```

### Threading Safety
```python
# Consumer en thread daemon pour cleanup automatique
self.result_consumer_thread = threading.Thread(target=consume_results, daemon=True)

# Stats protégées par GIL Python (suffisant pour ce cas)
stats['received_results'] += 1

# Connexions RabbitMQ : une par thread
def consume_results():
    if not self.connect_to_rabbitmq():
        return  # Chaque thread sa connexion
```

---

## 🚀 Performance et Scalabilité

### Optimisations Implémentées

#### 1. **Load Balancing Workers**
```yaml
worker-add-1:                    # 2 workers pour additions
worker-add-2:                    # (charge plus importante)
worker-sub:                      # 1 worker par autres opérations
worker-mul:
worker-div:
```

#### 2. **QoS et Acknowledgments**
```python
self.channel.basic_qos(prefetch_count=1)      # Fair dispatch
self.channel.basic_consume(
    queue=task_queue,
    on_message_callback=self.process_message   # Manual ack
)
channel.basic_ack(delivery_tag=method.delivery_tag)
```

#### 3. **Messages Persistants**
```python
self.channel.basic_publish(
    exchange='',
    routing_key=queue_name,
    body=serialize_message(task_message),
    properties=pika.BasicProperties(delivery_mode=2)  # Persistant
)
```

#### 4. **Connexions Optimisées**
- **Interface web** : Connexion par requête (courte durée)
- **Workers** : Connexion persistante avec reconnexion
- **Consumer** : Thread dédié avec gestion d'erreurs

### Métriques de Performance

#### Capacité Théorique
```python
# Temps de traitement simulé
WORKER_PROCESSING_TIME = {'min': 5, 'max': 15}  # secondes

# Throughput par worker
throughput_per_worker = 3600 / 10  # ~360 tâches/heure/worker (moyenne 10s)

# Capacité totale avec 5 workers
total_capacity = 5 * 360  # ~1800 tâches/heure
```

#### Optimisations Frontend
```javascript
// Auto-refresh optimisé
setInterval(refreshCurrentResults, 3000);    // Seulement vue courante

// Limitation résultats
if (len(stats['recent_results']) > 50:
    stats['recent_results'].pop(0)           # FIFO, max 50 résultats
```

### Points de Scalabilité

#### Scaling Horizontal
```yaml
# Ajouter des workers facilement
worker-add-3:
  <<: *worker-template
  container_name: worker-add-3
  environment:
    - WORKER_OPERATION=add

# Load balancer pour interface web
nginx:
  image: nginx
  ports: ["80:80"]
  depends_on: [web-interface-1, web-interface-2]
```

#### Clustering RabbitMQ
```bash
# RabbitMQ cluster pour HA
docker run -d --name rabbitmq-1 --hostname rabbit-1 rabbitmq:3-management
docker run -d --name rabbitmq-2 --hostname rabbit-2 rabbitmq:3-management
# Rejoindre le cluster
docker exec rabbitmq-2 rabbitmqctl join_cluster rabbit@rabbit-1
```

---

## 🧪 Tests et Qualité

### Types de Tests Implémentés

#### 1. **Tests d'Intégration** (`tests/test_system.py`)
```python
class SystemTester:
    def start_workers(self):              # Démarre tous les workers
    def send_test_tasks(self):            # Envoie tâches de test
    def verify_results(self, timeout=60): # Vérifie réception résultats
    def validate_calculations(self):      # Vérifie exactitude calculs
```

#### 2. **Tests de Connectivité** (`test_rabbitmq.py`)
```python
def test_rabbitmq_connection():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    assert connection.is_open
```

#### 3. **Health Checks Docker**
```yaml
healthcheck:
  test: ["CMD", "rabbitmq-diagnostics", "ping"]
  interval: 30s
  timeout: 10s
  retries: 5
```

### Structure des Tests Automatisés

#### Test de Bout en Bout
```python
def run_test(self):
    """Test automatique complet"""
    print("🧪 === TEST AUTOMATIQUE DU SYSTÈME ===")
    
    if not self.start_workers():
        return False
    
    self.start_result_consumer()
    
    if not self.send_test_tasks():
        return False
    
    if not self.verify_results():
        return False
    
    if not self.validate_calculations():
        return False
    
    print("✅ TOUS LES TESTS SONT PASSÉS!")
    return True
```

#### Cas de Test Couverts
```python
test_cases = [
    (10, 5, 'add'),    # 10 + 5 = 15
    (20, 3, 'sub'),    # 20 - 3 = 17  
    (7, 4, 'mul'),     # 7 × 4 = 28
    (15, 3, 'div'),    # 15 ÷ 3 = 5
    (100, 10, 'all')   # 4 opérations
]
# Total attendu : 8 résultats (4 + 4 via "all")
```

### Logging et Debugging

#### Logs Colorés avec Émojis
```python
print(f"{Fore.GREEN}🚀 Worker {self.worker_id} démarré{Style.RESET_ALL}")
print(f"{Fore.BLUE}📨 Message reçu: {task_message}{Style.RESET_ALL}")
print(f"{Fore.MAGENTA}⏳ Traitement de {n1} {op} {n2}{Style.RESET_ALL}")
print(f"{Fore.GREEN}✅ Calcul terminé: {result}{Style.RESET_ALL}")
print(f"{Fore.RED}❌ Erreur: {error}{Style.RESET_ALL}")
```

#### Debugging Interface Web
```javascript
console.log('=== FORM SUBMIT TRIGGERED ===');
console.log('Sending data:', data);
console.log('Response status:', response.status);
console.log('Response data:', result);
```

---

## ❓ Questions Fréquentes

### Q: Pourquoi avoir intégré le template HTML dans le Python ?
**R:** **Simplicité de déploiement** : Le script `web_interface.py` est complètement autonome (1050 lignes). Pas besoin de gérer des fichiers séparés, templates, static files. Déployable en un seul fichier.

### Q: Comment fonctionne la séparation des sources ?
**R:** 
```python
# Tâches marquées à la création
task_message = create_task_message(n1, n2, operation, source="web")   # Interface
task_message = create_task_message(n1, n2, operation, source="auto")  # Client auto

# Tri à la réception
source = result_message.get('source', 'auto')
if source == 'web':
    stats['web_results'].append(result_message)
else:
    stats['auto_results'].append(result_message)
```

### Q: Gestion de la concurrence entre workers ?
**R:** 
- **RabbitMQ** : Round-robin automatique entre workers d'une même queue
- **QoS** : `prefetch_count=1` pour distribution équitable
- **Acknowledgments** : Messages retraités en cas d'échec worker

### Q: Pourquoi avoir arrêté le consumer principal ?
**R:** **Éviter la compétition** : Deux consumers sur `result_queue` créaient une situation où certains résultats allaient au consumer CLI et d'autres à l'interface web. Solution : **Un seul consumer** (interface web) pour éviter la perte de messages.

### Q: Comment assurer la résilience ?
**R:**
```python
# Messages persistants
properties=pika.BasicProperties(delivery_mode=2)

# Reconnexion automatique
max_retries = 5
for attempt in range(max_retries):
    try:
        self.connection = pika.BlockingConnection(connection_params)
        break
    except Exception:
        time.sleep(2)

# Health checks Docker
healthcheck:
  test: ["CMD", "rabbitmq-diagnostics", "ping"]
```

### Q: Performance attendue du système ?
**R:**
- **Latence** : 5-15 secondes par tâche (simulation)
- **Throughput** : ~360 tâches/heure/worker (~1800 total avec 5 workers)
- **Scalabilité** : Linéaire avec nombre de workers
- **Mémoire** : ~50MB par service Docker

### Q: Comment monitorer en production ?
**R:**
- **Interface web** : http://localhost:5001 - Statistiques temps réel
- **RabbitMQ Management** : http://localhost:15672 - Métriques avancées
- **Docker logs** : `docker-compose logs -f` - Logs applicatifs
- **Health checks** : `docker-compose ps` - État des services

### Q: Déploiement en production ?
**R:**
```bash
# Sécurisation
- Changer credentials RabbitMQ
- Utiliser secrets Docker
- Reverse proxy (nginx)
- HTTPS avec certificats

# Monitoring
- Prometheus + Grafana
- ELK stack pour logs
- Alerting sur échecs

# Scalabilité  
- Load balancer pour interface web
- Clustering RabbitMQ
- Auto-scaling workers
```

### Q: Extensions possibles ?
**R:**
- **Base de données** : PostgreSQL pour persistance résultats
- **Cache** : Redis pour résultats fréquents  
- **Auth** : JWT tokens, OAuth2
- **API** : REST API complète
- **Mobile** : App React Native
- **Cloud** : Déploiement Kubernetes

---

## 📊 Métriques et KPIs

### Métriques Fonctionnelles Actuelles
```python
stats = {
    'sent_tasks': 0,              # Compteur global tâches envoyées
    'received_results': 0,        # Compteur global résultats reçus
    'operations': {               # Par type d'opération
        'add': 0, 'sub': 0, 'mul': 0, 'div': 0
    },
    'recent_results': [],         # 50 derniers résultats (tous)
    'web_results': [],            # 50 derniers résultats web
    'auto_results': [],           # 50 derniers résultats auto
    'queue_status': {},           # Messages en attente par queue
    'last_update': '...'          # Timestamp dernière MAJ
}
```

### Métriques Techniques Docker
```bash
# Utilisation ressources
docker stats

# Logs par service
docker-compose logs worker-add-1
docker-compose logs web-interface

# État des services
docker-compose ps
```

### KPIs Recommandés pour Production
- **Disponibilité** : % uptime des services
- **Latence** : Temps moyen de traitement
- **Throughput** : Tâches/minute traité
- **Taux d'erreur** : % échecs/total tâches
- **Utilisation queues** : Messages en attente
- **Ressources** : CPU, mémoire, disque

---

*Documentation générée le 03/12/2024 - Version 2.0*  
*Projet Institut NGI - Systèmes Distribués* 

### 🛠️ Scripts et Outils

#### Script d'Installation Automatique (setup_and_run.sh/bat/ps1)
**Scripts "Do It All" pour démarrage ultra-rapide multi-plateforme**

```bash
# Linux / macOS / WSL
./setup_and_run.sh

# Windows Command Prompt
setup_and_run.bat

# Windows PowerShell (recommandé)
.\setup_and_run.ps1
```

**Fonctionnalités automatisées (identiques sur toutes les plateformes) :**

1. **🔍 Vérification des prérequis**
   ```bash
   # Vérifie Python 3 et pip
   python3 --version  # Linux/macOS
   python --version   # Windows
   pip3 --version || python3 -m pip --version  # Linux/macOS
   pip --version || python -m pip --version    # Windows
   
   # Vérifie Docker et Docker Compose
   docker --version
   docker info  # Daemon actif
   docker-compose --version || docker compose version
   ```

2. **📦 Installation des dépendances**
   ```bash
   # Installation automatique
   pip3 install -r requirements.txt  # Linux/macOS
   pip install -r requirements.txt   # Windows
   
   # Gestion d'erreurs et feedback coloré
   ```

3. **🐳 Validation de l'environnement Docker**
   ```bash
   # Vérifications automatiques
   - Docker installé et accessible
   - Daemon Docker en fonctionnement
   - Docker Compose disponible (v1 ou v2)
   - Fichier docker-compose.yml présent
   ```

4. **🚀 Démarrage complet du système**
   ```bash
   # Lancement avec construction
   docker-compose up --build -d
   
   # Ou selon la version disponible
   docker compose up --build -d
   ```

5. **📋 Instructions post-installation**
   ```bash
   # Affichage coloré des URLs d'accès
   🌐 Interface Web: http://localhost:5001
   🐰 RabbitMQ Management: http://localhost:15672 (admin/admin123)
   
   # Commandes utiles affichées
   docker-compose logs -f    # Voir les logs
   docker-compose down      # Arrêter le système
   ```

**Spécificités par plateforme :**

| Script | Plateforme | Couleurs | Pause finale |
|--------|------------|----------|--------------|
| `setup_and_run.sh` | Linux/macOS/WSL | ✅ Bash colors | ❌ |
| `setup_and_run.bat` | Windows CMD | ❌ Basique | ✅ pause |
| `setup_and_run.ps1` | Windows PowerShell | ✅ PowerShell colors | ✅ Read-Host |

**Gestion d'erreurs robuste :**
- Vérifications séquentielles avec arrêt en cas d'échec
- Messages d'erreur explicites avec suggestions de résolution
- Logs colorés avec émojis pour navigation visuelle (sauf .bat)
- Support Docker Compose v1 et v2 automatique
- Instructions d'installation spécifiques par OS

#### Script de Démarrage Assisté (start_system.py) 